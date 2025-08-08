from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.settings import ModelProvider, agent_settings


class ModelRelayModelName(ModelNameBase):
    # GPT_4O = "gpt-4o"
    # GPT_4O_2024_11_20 = "gpt-4o-2024-11-20"
    # GPT_4O_MINI_2024_07_18 = "gpt-4o-mini-2024-07-18"
    # O3_MINI_2025_01_31 = "o3-mini-2025-01-31"
    # TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    # O4_MINI = "o4-mini"
    FT_O4_MINI_ELEMENTS_20250730 = "ft-o4-mini-elements-20250730"


class ModelRelayAgent(AgentBase):
    def create_client(self) -> AsyncOpenAI:
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        return AsyncOpenAI(
            api_key=self.credential.api_key,
            base_url=self.credential.base_url,
            timeout=self.timeout,
        )

    def create_model(self) -> OpenAIModel:
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        client = self.create_client()
        return OpenAIModel(
            model_name=self.credential.model_name,
            provider=OpenAIProvider(openai_client=client),
        )

    def embedding(self, input: str, dimensions: int = 1024):
        raise NotImplementedError("ModelRelayAgent does not support embedding")


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await ModelRelayAgent.create(credential=credential)
    return await agent.validate_credential()


class ModelRelayCredentialPool(CredentialPoolBase):
    def __init__(self, target_model: ModelRelayModelName):
        super().__init__(
            model_provider=ModelProvider.MODEL_RELAY.value,
            target_model=target_model,
            account_credentials=agent_settings.model_relay.credentials,
            validate_fn=validate_fn,
        )


if __name__ == "__main__":
    import asyncio

    from pydantic_ai.settings import ModelSettings

    from agent_tools.test_tool import test_all_credentials, test_credential_pool_manager

    model_settings = ModelSettings(
        temperature=0.0,
        max_tokens=8192,
    )

    async def test():
        """Main function that runs all tests with proper cleanup."""
        await test_credential_pool_manager(
            credential_pool_cls=ModelRelayCredentialPool,
            agent_cls=ModelRelayAgent,
            target_model=ModelRelayModelName.FT_O4_MINI_ELEMENTS_20250730,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=ModelRelayModelName,
            model_settings=model_settings,
            credential_pool_cls=ModelRelayCredentialPool,
            agent_cls=ModelRelayAgent,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
