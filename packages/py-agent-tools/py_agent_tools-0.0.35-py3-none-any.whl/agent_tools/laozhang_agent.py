import time
from typing import Any, Callable

from openai import AsyncOpenAI
from pydantic_ai import BinaryContent
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools._log import log
from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.agent_runner import AgentRunner
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.settings import ModelProvider, agent_settings


class LaozhangModelName(ModelNameBase):

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O4_MINI = "o4-mini"
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"

    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"

    GROK_4 = "grok-4"
    GROK_4_0709 = "grok-4-0709"

    CLAUDE_SONNET_4_20250514 = "claude-sonnet-4-20250514"
    CLAUDE_SONNET_4_20250514_THINKING = "claude-sonnet-4-20250514-thinking"


class LaozhangEmbeddingModelName(ModelNameBase):
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"


class LaozhangModel(OpenAIModel):
    """Custom model class for Laozhang API that handles missing 'created' field."""

    def _process_response(self, response):
        """Override to handle missing 'created' field in Laozhang API responses."""
        # Check if response is None
        if response is None:
            raise ValueError("Received None response from Laozhang API")

        # Log response structure for debugging
        log.debug(f"Laozhang API response type: {type(response)}")
        log.debug(f"Laozhang API response attributes: {dir(response)}")

        # If the response has no created field or its None, set it to current timestamp
        if not hasattr(response, "created") or response.created is None:
            response.created = int(time.time())
            log.debug("Set missing created field to current timestamp")

        # Check if choices field exists and is not None
        if not hasattr(response, "choices"):
            available_fields = [attr for attr in dir(response) if not attr.startswith('_')]
            log.error(f"Response missing 'choices' field. Available fields: {available_fields}")
            raise ValueError("Response from Laozhang API has no choices field")

        if response.choices is None:
            log.error(f"Full response object: {response!r}")
            log.error("Response choices field is None")
            raise ValueError("Response from Laozhang API has 'choices' field but it is None")

        # Check if choices list is empty
        if len(response.choices) == 0:
            log.error("Response choices list is empty")
            raise ValueError("Response from Laozhang API has empty choices list")

        log.debug(f"Response has {len(response.choices)} choices")
        return super()._process_response(response)


class LaozhangAgent(AgentBase):
    def create_client(self):
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        return AsyncOpenAI(
            api_key=self.credential.api_key,
            base_url=self.credential.base_url,
        )

    def create_model(self):
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        client = self.create_client()
        return LaozhangModel(
            model_name=self.credential.model_name,
            provider=OpenAIProvider(openai_client=client),
        )

    async def run(
        self,
        prompt: str,
        images: list[BinaryContent] = [],
        postprocess_fn: Callable[[str], Any] | None = None,
        **kwargs: Any,
    ) -> AgentRunner:
        agent = self.create_agent()
        try:
            await self.runner.run(
                agent, prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
            )
        except ModelHTTPError as e:
            # Handle specific HTTP errors from Laozhang API
            if e.status_code == 503:
                log.warning(f"Laozhang API server error (503): {e.body}")
                log.warning("This is a server-side issue. Trying to switch credentials...")
                await self._switch_credential()
                return await self.run(
                    prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
                )
            elif e.status_code == 429:
                log.warning(f"Laozhang API rate limit (429): {e.body}")
                log.warning("Rate limited. Trying to switch credentials...")
                await self._switch_credential()
                return await self.run(
                    prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
                )
            else:
                log.error(f"Laozhang API HTTP error ({e.status_code}): {e.body}")
                await self._switch_credential()
                return await self.run(
                    prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
                )
        except Exception as e:
            log.error(f"Unexpected error in Laozhang agent: {e}")
            await self._switch_credential()
            return await self.run(prompt, images=images, postprocess_fn=postprocess_fn, **kwargs)
        return self.runner

    async def run_stream(
        self,
        prompt: str,
        images: list[BinaryContent] = [],
        postprocess_fn: Callable[[str], Any] | None = None,
        **kwargs: Any,
    ) -> AgentRunner:
        agent = self.create_agent()
        try:
            await self.runner.run_stream(
                agent, prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
            )
        except ModelHTTPError as e:
            # Handle specific HTTP errors from Laozhang API
            if e.status_code == 503:
                log.warning(f"Laozhang API server error (503): {e.body}")
                log.warning("This is a server-side issue. Trying to switch credentials...")
                await self._switch_credential()
                return await self.run_stream(
                    prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
                )
            elif e.status_code == 429:
                log.warning(f"Laozhang API rate limit (429): {e.body}")
                log.warning("Rate limited. Trying to switch credentials...")
                await self._switch_credential()
                return await self.run_stream(
                    prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
                )
            else:
                log.error(f"Laozhang API HTTP error ({e.status_code}): {e.body}")
                await self._switch_credential()
                return await self.run_stream(
                    prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
                )
        except Exception as e:
            log.error(f"Unexpected error in Laozhang agent: {e}")
            await self._switch_credential()
            return await self.run_stream(
                prompt, images=images, postprocess_fn=postprocess_fn, **kwargs
            )
        return self.runner


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await LaozhangAgent.create(credential=credential)
    return await agent.validate_credential()


class LaozhangCredentialPool(CredentialPoolBase):
    def __init__(self, target_model: LaozhangModelName):
        super().__init__(
            model_provider=ModelProvider.LAOZHANG.value,
            target_model=target_model,
            account_credentials=agent_settings.laozhang.credentials,
            validate_fn=validate_fn,
        )


if __name__ == "__main__":
    import asyncio

    from pydantic_ai.settings import ModelSettings

    from agent_tools.test_tool import test_all_credentials, test_credential_pool_manager

    model_settings = ModelSettings(
        temperature=1.0,
        max_tokens=8192,
    )

    async def test():
        """Main function that runs all tests with proper cleanup."""
        try:
            await test_credential_pool_manager(
                credential_pool_cls=LaozhangCredentialPool,
                agent_cls=LaozhangAgent,
                # target_model=LaozhangModelName.GROK_4,  # which is forbiden in credential file
                target_model=LaozhangModelName.GPT_5,
                model_settings=model_settings,
            )
        except ValueError as e:
            print(f"模型不支持: {e}")
            pass
        except Exception as e:
            raise e

        await test_all_credentials(
            model_name_enum=LaozhangModelName,
            model_settings=model_settings,
            credential_pool_cls=LaozhangCredentialPool,
            agent_cls=LaozhangAgent,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
