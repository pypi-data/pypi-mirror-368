import httpx
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_vertex import GoogleVertexProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.settings import ModelProvider, agent_settings


class VertexModelName(ModelNameBase):
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_5_PRO = "gemini-2.5-pro"


class VertexAgent(AgentBase):
    def create_client(self) -> httpx.AsyncClient:
        raise NotImplementedError("VertexAgent does not support create_client")

    def create_model(self) -> GeminiModel:
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        return GeminiModel(
            model_name=self.credential.model_name,
            provider=GoogleVertexProvider(
                service_account_info=self.credential.account_info,
                http_client=httpx.AsyncClient(timeout=self.timeout),
            ),
        )

    def embedding(self, input: str, dimensions: int = 1024):
        raise NotImplementedError("VertexAgent does not support embedding")


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await VertexAgent.create(credential=credential)
    return await agent.validate_credential()


class VertexCredentialPool(CredentialPoolBase):
    def __init__(self, target_model: VertexModelName):
        super().__init__(
            model_provider=ModelProvider.VERTEX.value,
            target_model=target_model,
            account_credentials=agent_settings.vertex.credentials,
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
            credential_pool_cls=VertexCredentialPool,
            agent_cls=VertexAgent,
            target_model=VertexModelName.GEMINI_2_0_FLASH,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=VertexModelName,
            model_settings=model_settings,
            credential_pool_cls=VertexCredentialPool,
            agent_cls=VertexAgent,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
