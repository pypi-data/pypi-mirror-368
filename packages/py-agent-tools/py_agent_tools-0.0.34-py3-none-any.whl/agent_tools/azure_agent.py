from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.settings import ModelProvider, agent_settings


class AzureModelName(ModelNameBase):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O3_MINI = "o3-mini"
    O4_MINI = "o4-mini"
    O3 = "o3"


class AzureEmbeddingModelName(ModelNameBase):
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"


class AzureAgent(AgentBase):
    def create_client(self) -> AsyncAzureOpenAI:
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        return AsyncAzureOpenAI(
            api_version=self.credential.api_version,
            azure_endpoint=self.credential.base_url,
            api_key=self.credential.api_key,
            azure_deployment=self.credential.deployment,
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
    agent = await AzureAgent.create(credential=credential)
    return await agent.validate_credential()


class AzureCredentialPool(CredentialPoolBase):
    def __init__(self, target_model: AzureModelName):
        super().__init__(
            model_provider=ModelProvider.AZURE.value,
            target_model=target_model,
            account_credentials=agent_settings.azure.credentials,
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
            credential_pool_cls=AzureCredentialPool,
            agent_cls=AzureAgent,
            target_model=AzureModelName.GPT_4O,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=AzureModelName,
            model_settings=model_settings,
            credential_pool_cls=AzureCredentialPool,
            agent_cls=AzureAgent,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
