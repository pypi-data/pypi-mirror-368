from agent_tools.agent_base import ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase
from agent_tools.openai_agent import OpenAIAgent, validate_fn
from agent_tools.settings import ModelProvider, agent_settings


class OpenAIFineTuningModelName(ModelNameBase):
    FT_O4_MINI_ELEMENTS_20250730 = "ft-o4-mini-elements-20250730"


class OpenAIFineTuningCredentialPool(CredentialPoolBase):
    def __init__(self, target_model: OpenAIFineTuningModelName):
        super().__init__(
            model_provider=ModelProvider.OPENAI_FT.value,
            target_model=target_model,
            account_credentials=agent_settings.openai_ft.credentials,
            validate_fn=validate_fn,
        )


if __name__ == "__main__":
    import asyncio

    from pydantic_ai.settings import ModelSettings

    from agent_tools.test_tool import test_all_credentials, test_credential_pool_manager

    model_settings = ModelSettings(
        temperature=0.7,
        max_tokens=8192,
    )

    async def test():
        """Main function that runs all tests with proper cleanup."""
        await test_credential_pool_manager(
            credential_pool_cls=OpenAIFineTuningCredentialPool,
            agent_cls=OpenAIAgent,
            target_model=OpenAIFineTuningModelName.FT_O4_MINI_ELEMENTS_20250730,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=OpenAIFineTuningModelName,
            model_settings=model_settings,
            credential_pool_cls=OpenAIFineTuningCredentialPool,
            agent_cls=OpenAIAgent,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
