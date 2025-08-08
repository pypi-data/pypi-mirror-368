from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.settings import ModelProvider, agent_settings


class ArkModelName(ModelNameBase):
    DEEPSEEK_R1_250528 = "deepseek-r1-250528"
    DEEPSEEK_V3_250324 = "deepseek-v3-250324"
    DOUBAO_SEED_1_6_250615 = "doubao-seed-1-6-250615"
    DOUBAO_SEED_1_6_THINKING_250615 = "doubao-seed-1-6-thinking-250615"
    DOUBAO_SEED_1_6_FLASH_250615 = "doubao-seed-1-6-flash-250615"


class ArkEmbeddingModelName(ModelNameBase):
    DOUBAO_EMBEDDING_VISION_250328 = "doubao-embedding-vision-250328"
    DOUBAO_EMBEDDING_LARGE_TEXT_240915 = "doubao-embedding-large-text-240915"


class ArkAgent(AgentBase):
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


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await ArkAgent.create(credential=credential)
    return await agent.validate_credential()


class ArkCredentialPool(CredentialPoolBase):
    def __init__(self, target_model: ArkModelName):
        super().__init__(
            model_provider=ModelProvider.ARK.value,
            target_model=target_model,
            account_credentials=agent_settings.ark.credentials,
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
            credential_pool_cls=ArkCredentialPool,
            agent_cls=ArkAgent,
            target_model=ArkModelName.DOUBAO_SEED_1_6_250615,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=ArkModelName,
            model_settings=model_settings,
            credential_pool_cls=ArkCredentialPool,
            agent_cls=ArkAgent,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
