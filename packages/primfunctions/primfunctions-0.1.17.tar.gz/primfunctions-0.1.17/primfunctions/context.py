from typing import List, Dict, Any

from .configuration import Configuration, LLMProvider


class Context:
    def __init__(
        self,
        agent_id: str = "",
        environment: str = "",
        session_id: str = "",
        configuration: Configuration = Configuration(),
        data: dict = {},
        variables: dict = {},
    ):
        self.agent_id = agent_id
        self.environment = environment
        self.session_id = session_id
        self.configuration = configuration
        self.data = data
        self.variables = variables
        self.history = []

    def serialize(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "environment": self.environment,
            "session_id": self.session_id,
            "configuration": self.configuration.__dict__(),
            "data": self.data,
            "history": self.history,
            "variables": self.variables,
        }

    def deserialize(self, state: dict):
        self.agent_id = state.get("agent_id", self.agent_id)
        self.environment = state.get("environment", self.environment)
        self.session_id = state.get("session_id", self.session_id)
        self.configuration = Configuration(
            **state.get("configuration", self.configuration.__dict__())
        )
        self.data = state.get("data", self.data)
        self.history = state.get("history", self.history)
        self.variables = state.get("variables", self.variables)

    def set_data(self, key: str, value: Any):
        self.data[key] = value

    def get_data(self, key: str, default: Any = None):
        return self.data.get(key, default)

    # Backward compatible methods - these work with OpenAI format internally
    def add_system_message(self, message: str):
        """Add system message. For Gemini, this will be converted when getting formatted history."""
        self.history.append({"role": "system", "content": message})

    def add_assistant_message(self, message: str):
        """Add assistant message. For Gemini, this will be converted to 'model' role when getting formatted history."""
        self.history.append({"role": "assistant", "content": message})

    def add_user_message(self, message: str):
        """Add user message. Works the same for both OpenAI and Gemini."""
        self.history.append({"role": "user", "content": message})

    # New generic methods for flexibility
    def add_message(self, role: str, content: str):
        """Generic method to add any message with specified role."""
        self.history.append({"role": role, "content": content})

    def get_history(self, turns: int = 0) -> List[Dict[str, str]]:
        """Get history in original OpenAI format for backward compatibility."""
        if turns == 0:
            return self.history
        return self.history[-(turns * 2) :]

    def get_history_message(self, turns: int = 0) -> List[Dict[str, str]]:
        """Get history formatted for the current model provider."""
        history = self.get_history(turns)

        if self.configuration.llm_provider == LLMProvider.OPENAI:
            return history
        elif self.configuration.llm_provider == LLMProvider.GEMINI:
            return self._convert_to_gemini_format(history)
        else:
            return history

    def _convert_to_gemini_format(
        self, history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Convert OpenAI format to Gemini format."""
        converted = []
        system_messages = []

        for message in history:
            role = message["role"]
            content = message["content"]

            if role == "system":
                # Collect system messages to prepend to first user message
                system_messages.append(content)
            elif role == "assistant":
                # Convert assistant to model for Gemini
                converted.append({"role": "model", "content": content})
            elif role == "user":
                # If we have accumulated system messages, prepend them to this user message
                if system_messages:
                    system_context = "\n".join(system_messages)
                    content = f"System: {system_context}\n\nUser: {content}"
                    system_messages = []  # Clear after using
                converted.append({"role": "user", "content": content})
            else:
                # Unknown role, keep as is
                converted.append(message)

        # If there are remaining system messages at the end, add them as a user message
        if system_messages:
            system_content = "\n".join(system_messages)
            converted.append({"role": "user", "content": f"System: {system_content}"})

        return converted

    def set_llm_provider(self, provider: LLMProvider):
        """Change the llm provider for this context."""
        self.configuration.llm_provider = provider

    def get_llm_provider(self) -> LLMProvider:
        """Get the current llm provider."""
        return self.configuration.llm_provider
