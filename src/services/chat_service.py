from typing import Dict

from src.llm.claude_agent import ClaudeAgent


class ChatService:
    """
    Manage ClaudeAgent instances for separate conversations.
    """

    def __init__(self):
        self._conversations: Dict[str, ClaudeAgent] = {}

    def get_agent(self, conversation_id: str) -> ClaudeAgent:
        """
        Get an existing agent for a conversation or create a new one.
        """

        if not conversation_id:
            raise ValueError(
                "conversation_id cannot be empty."
            )

        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = ClaudeAgent()

        return self._conversations[conversation_id]

    async def chat(
        self,
        conversation_id: str,
        message: str,
        language: str = "English",
    ) -> str:
        """
        Send a message within a conversation.
        """

        if not message or not message.strip():
            raise ValueError(
                "message cannot be empty."
            )

        agent = self.get_agent(conversation_id)

        return await agent.ask_with_mcp(
            message.strip(),
            language=language,
        )

    def reset_conversation(
        self,
        conversation_id: str,
    ) -> None:
        """
        Reset an existing conversation.
        """

        if conversation_id in self._conversations:
            self._conversations[
                conversation_id
            ].reset_conversation()

    def delete_conversation(
        self,
        conversation_id: str,
    ) -> None:
        """
        Remove a conversation from memory.
        """

        self._conversations.pop(
            conversation_id,
            None
        )