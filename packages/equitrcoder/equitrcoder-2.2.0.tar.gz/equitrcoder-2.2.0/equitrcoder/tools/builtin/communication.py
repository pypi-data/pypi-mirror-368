# equitrcoder/tools/builtin/communication.py

from typing import List, Optional, Type
from pydantic import BaseModel, Field

from ..base import Tool, ToolResult
from ...core.global_message_pool import global_message_pool

class SendMessageArgs(BaseModel):
    content: str = Field(..., description="The message content to send.")
    recipient: Optional[str] = Field(default=None, description="The ID of the recipient agent. If None, the message is broadcast to all other agents.")

class ReceiveMessagesArgs(BaseModel):
    pass



class SendMessage(Tool):
    """Tool for sending messages to other agents."""
    def __init__(self, sender_id: str):
        self.sender_id = sender_id
        super().__init__()

    def get_name(self) -> str:
        return "send_message"
    def get_description(self) -> str:
        return "Sends a message to another agent or broadcasts to all agents."
    def get_args_schema(self) -> Type[BaseModel]:
        return SendMessageArgs

    async def run(self, **kwargs) -> ToolResult:
        args = self.validate_args(kwargs)
        await global_message_pool.post_message(
            sender=self.sender_id,
            content=args.content,
            recipient=args.recipient
        )
        return ToolResult(success=True, data=f"Message sent to {args.recipient or 'all agents'}.")

class ReceiveMessages(Tool):
    """Tool for receiving messages from other agents."""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        super().__init__()

    def get_name(self) -> str:
        return "receive_messages"
    def get_description(self) -> str:
        return "Receives pending messages addressed to this agent."
    def get_args_schema(self) -> Type[BaseModel]:
        return ReceiveMessagesArgs

    async def run(self, **kwargs) -> ToolResult:
        messages = await global_message_pool.get_messages(agent_id=self.agent_id)
        if not messages:
            return ToolResult(success=True, data="No new messages.")
        
        formatted_messages = [
            {
                "from": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        return ToolResult(success=True, data=formatted_messages)



def create_communication_tools_for_agent(agent_id: str) -> List[Tool]:
    """Factory function to create a set of communication tools for a specific agent."""
    from .ask_supervisor import AskSupervisor
    from ...providers.litellm import LiteLLMProvider
    
    # Create supervisor provider (using same model as orchestrator)
    # This will be passed the correct model when the agent is created
    supervisor_provider = LiteLLMProvider(model="o3")  # Default, will be overridden
    
    return [
        SendMessage(sender_id=agent_id),
        ReceiveMessages(agent_id=agent_id),
        AskSupervisor(provider=supervisor_provider),
    ]