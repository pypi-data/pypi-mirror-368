from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml
from pydantic import BaseModel, Field

from ..base import Tool, ToolResult
from ..builtin.shell import RunCommand
from ...core.unified_config import get_config


class HardwareInfoArgs(BaseModel):
    detailed: bool = Field(default=True, description="Include detailed fields when available")


class HardwareInfo(Tool):
    def get_name(self) -> str:
        return "hardware_info"

    def get_description(self) -> str:
        return "Detect and report local hardware and environment details (OS, CPU, RAM, GPU if available)."

    def get_args_schema(self) -> Type[BaseModel]:
        return HardwareInfoArgs

    async def run(self, **kwargs) -> ToolResult:
        try:
            self.validate_args(kwargs)

            info: Dict[str, Any] = {}
            # OS / Platform
            info["os"] = platform.platform()
            info["python_version"] = platform.python_version()
            info["architecture"] = platform.machine()
            info["processor"] = platform.processor() or platform.uname().processor

            # CPU count
            try:
                import multiprocessing

                info["cpu_count"] = multiprocessing.cpu_count()
            except Exception:
                pass

            # Memory detection (no psutil dependency)
            mem_total_bytes: Optional[int] = None
            try:
                if hasattr(os, "sysconf"):
                    if os.sysconf_names.get("SC_PAGE_SIZE") and os.sysconf_names.get("SC_PHYS_PAGES"):
                        mem_total_bytes = int(os.sysconf("SC_PAGE_SIZE")) * int(os.sysconf("SC_PHYS_PAGES"))
            except Exception:
                pass

            if mem_total_bytes is None:
                # Try vm_stat on macOS
                try:
                    out = subprocess.run(["/usr/bin/vm_stat"], capture_output=True, text=True)
                    if out.returncode == 0:
                        _pages_line = next((line for line in out.stdout.splitlines() if "Pages free" in line), None)
                        page_size_line = next((line for line in out.stdout.splitlines() if "page size of" in line), None)
                        if page_size_line:
                            _page_size = int(page_size_line.split("page size of")[-1].strip().split()[0])
                        else:
                            _page_size = 4096  # default page size
                        # vm_stat doesn't give total pages; fallback to system_profiler
                        sp = subprocess.run(["/usr/sbin/sysctl", "hw.memsize"], capture_output=True, text=True)
                        if sp.returncode == 0 and ":" in sp.stdout:
                            mem_total_bytes = int(sp.stdout.split(":")[-1].strip())
                except Exception:
                    pass

            if mem_total_bytes is not None:
                info["memory_total_bytes"] = mem_total_bytes
                info["memory_total_gb"] = round(mem_total_bytes / (1024 ** 3), 2)

            # GPU detection
            gpu_info: Dict[str, Any] = {}
            try:
                if shutil.which("nvidia-smi"):
                    q = [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total,driver_version",
                        "--format=csv,noheader,nounits",
                    ]
                    res = subprocess.run(q, capture_output=True, text=True)
                    if res.returncode == 0:
                        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
                        gpus = []
                        for line in lines:
                            parts = [p.strip() for p in line.split(",")]
                            if len(parts) >= 2:
                                gpus.append(
                                    {
                                        "name": parts[0],
                                        "memory_mb": int(parts[1]) if parts[1].isdigit() else parts[1],
                                        "driver_version": parts[2] if len(parts) > 2 else None,
                                    }
                                )
                        gpu_info["nvidia"] = gpus
                else:
                    # macOS integrated GPU info
                    if platform.system().lower() == "darwin":
                        sp = subprocess.run([
                            "/usr/sbin/system_profiler",
                            "SPDisplaysDataType",
                        ], capture_output=True, text=True)
                        if sp.returncode == 0:
                            models = []
                            for raw_line in sp.stdout.splitlines():
                                if "Chipset Model:" in raw_line or "Chipset Model" in raw_line:
                                    models.append(raw_line.split(":", 1)[-1].strip())
                            if models:
                                gpu_info["apple_displays"] = models
            except Exception:
                pass

            info["gpu"] = gpu_info

            return ToolResult(success=True, data=info)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CreateNotebookArgs(BaseModel):
    path: str = Field(..., description="Path to write the .ipynb file")
    cells: List[str] = Field(default_factory=list, description="List of code cell sources")
    kernel_name: str = Field(default="python3", description="Kernel name for the notebook")


class CreateNotebook(Tool):
    def get_name(self) -> str:
        return "create_notebook"

    def get_description(self) -> str:
        return "Create a minimal Jupyter notebook (.ipynb) with provided code cells."

    def get_args_schema(self) -> Type[BaseModel]:
        return CreateNotebookArgs

    async def run(self, **kwargs) -> ToolResult:
        try:
            args = self.validate_args(kwargs)
            nb_path = Path(args.path)
            nb_path.parent.mkdir(parents=True, exist_ok=True)

            notebook = {
                "cells": [
                    {
                        "cell_type": "code",
                        "metadata": {},
                        "source": cell,
                        "outputs": [],
                        "execution_count": None,
                    }
                    for cell in args.cells
                ],
                "metadata": {
                    "kernelspec": {
                        "name": args.kernel_name,
                        "display_name": args.kernel_name,
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 5,
            }

            nb_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
            return ToolResult(success=True, data={"path": str(nb_path), "cells": len(args.cells)})
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class RunNotebookArgs(BaseModel):
    path: str = Field(..., description="Path to the notebook file (.ipynb)")
    timeout: int = Field(default=600, description="Execution timeout in seconds")


class RunNotebook(Tool):
    def get_name(self) -> str:
        return "run_notebook"

    def get_description(self) -> str:
        return "Execute a Jupyter notebook and save executed output to a new file. Prefers nbclient, falls back to nbconvert if available."

    def get_args_schema(self) -> Type[BaseModel]:
        return RunNotebookArgs

    async def run(self, **kwargs) -> ToolResult:
        try:
            args = self.validate_args(kwargs)
            nb_path = Path(args.path)
            if not nb_path.exists():
                return ToolResult(success=False, error=f"Notebook not found: {nb_path}")

            executed_path = nb_path.with_name(nb_path.stem + "-executed.ipynb")
            start = time.time()
            # Try nbclient first (preferred)
            try:
                import nbformat  # type: ignore
                from nbclient import NotebookClient  # type: ignore

                nb = nbformat.read(nb_path, as_version=4)
                kernel = (
                    nb.metadata.get("kernelspec", {}).get("name")
                    if isinstance(nb.metadata, dict)
                    else None
                ) or "python3"
                client = NotebookClient(nb, timeout=args.timeout, kernel_name=kernel)
                client.execute()
                nbformat.write(client.nb, executed_path)
                duration = round(time.time() - start, 2)
                return ToolResult(
                    success=True,
                    data={
                        "executed_path": str(executed_path),
                        "duration_sec": duration,
                        "engine": "nbclient",
                    },
                )
            except ImportError:
                # Fall back to nbconvert via jupyter CLI
                if shutil.which("jupyter"):
                    cmd = [
                        "jupyter",
                        "nbconvert",
                        "--to",
                        "notebook",
                        "--execute",
                        "--ExecutePreprocessor.timeout={}".format(args.timeout),
                        "--output",
                        str(executed_path.name),
                        str(nb_path),
                    ]
                    proc = subprocess.run(cmd, cwd=str(nb_path.parent), capture_output=True, text=True)
                    duration = round(time.time() - start, 2)
                    if proc.returncode == 0 and executed_path.exists():
                        return ToolResult(
                            success=True,
                            data={
                                "executed_path": str(executed_path),
                                "duration_sec": duration,
                                "engine": "nbconvert",
                                "stdout": proc.stdout,
                            },
                        )
                    return ToolResult(
                        success=False,
                        error=f"nbconvert failed (code {proc.returncode})",
                        data={"stdout": proc.stdout, "stderr": proc.stderr},
                    )
                else:
                    return ToolResult(
                        success=False,
                        error=(
                            "Notebook execution requires either 'nbclient' and 'nbformat' packages or the 'jupyter' CLI. "
                            "Please install with: pip install nbclient nbformat jupyter"
                        ),
                    )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class RunExperimentsArgs(BaseModel):
    config_path: str = Field(..., description="Path to experiments YAML file")
    stop_on_fail: bool = Field(default=False, description="Stop after the first failing experiment")


class RunExperiments(Tool):
    def get_name(self) -> str:
        return "run_experiments"

    def get_description(self) -> str:
        return "Run a sequence of shell-based experiments described in a YAML config and report pass/fail."

    def get_args_schema(self) -> Type[BaseModel]:
        return RunExperimentsArgs

    async def run(self, **kwargs) -> ToolResult:
        try:
            args = self.validate_args(kwargs)
            cfg_path = Path(args.config_path)
            if not cfg_path.exists():
                return ToolResult(success=False, error=f"Experiments config not found: {cfg_path}")

            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            experiments: List[Dict[str, Any]] = cfg.get("experiments", [])
            if not isinstance(experiments, list) or not experiments:
                return ToolResult(success=False, error="No experiments defined in config")

            results: List[Dict[str, Any]] = []
            all_passed = True

            # Determine sandbox mode
            sandbox_type = get_config('sandbox.type', 'local')
            use_venv = sandbox_type == 'venv'
            runner = RunCommand()

            for exp in experiments:
                name = exp.get("name") or exp.get("id") or f"exp_{len(results)+1}"
                command = exp.get("command")
                if not command:
                    results.append({"name": name, "error": "Missing command", "passed": False})
                    all_passed = False
                    if args.stop_on_fail:
                        break
                    continue
                cwd = exp.get("cwd") or str(cfg_path.parent)
                timeout = int(exp.get("timeout", 900))
                # Respect cwd by inlining cd; honor sandbox via use_venv
                full_cmd = f"cd {cwd} && {command}"
                tr = await runner.run(command=full_cmd, timeout=timeout, use_venv=use_venv)
                rc = (tr.data or {}).get("return_code", 1) if tr.success else 1
                stdout = (tr.data or {}).get("stdout", "") if tr.data else ""
                stderr = (tr.data or {}).get("stderr", tr.error or "")

                passed = rc == 0
                all_passed = all_passed and passed

                results.append({
                    "name": name,
                    "command": command,
                    "cwd": cwd,
                    "return_code": rc,
                    "passed": passed,
                    "stdout": stdout[-4000:],
                    "stderr": (stderr or "")[-4000:],
                })

                if args.stop_on_fail and not passed:
                    break

            return ToolResult(success=True, data={"all_passed": all_passed, "results": results})
        except subprocess.TimeoutExpired as te:
            return ToolResult(success=False, error=f"Experiment timed out: {te}")
        except Exception as e:
            return ToolResult(success=False, error=str(e)) 