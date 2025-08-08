import time
import traceback
from typing import Any, Callable

from pydantic_ai import Agent, BinaryContent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import Usage

from agent_tools._log import log


class AgentRunner:
    """
    AgentRunner is a class that
    1. keep model settings.
    2. runs an agent and returns the result.
    3. keep attempts, usage, and time_elapsed.
    """

    def __init__(
        self,
        elapsed_time: float = 0.0,
        attempts: int = 0,
        usage: Usage = Usage(),
        model_settings: ModelSettings = ModelSettings(),
    ):
        self.elapsed_time = elapsed_time
        self.attempts = attempts
        self.model_settings = model_settings
        self.usage = usage
        self.result: Any | None = None

    def _raise_error(self, e: Exception, start_time: float):
        self.attempts = self.attempts + 1
        self.elapsed_time += time.perf_counter() - start_time
        log.error(f'AgentRunner failed: {self.attempts} attempts: {traceback.format_exc()}')
        raise e

    def _get_content(self, prompt: str, images: list[BinaryContent]) -> list[str | BinaryContent]:
        content: list[str | BinaryContent] = [prompt]
        content.extend(images)
        return content

    async def run(
        self,
        agent: Agent[Any, str],
        prompt: str,
        images: list[BinaryContent] = [],
        postprocess_fn: Callable[[str], str] | None = None,
        **kwargs: Any,
    ) -> None:
        start_time = time.perf_counter()
        try:
            log.info(f"Model provider: {agent.model}")
            model_name = (
                getattr(agent.model, 'model_name', str(agent.model)) if agent.model else 'unknown'
            )
            log.info(f"Model name: {model_name}")
            log.info(f"Model settings: {self.model_settings}")
            result = await agent.run(
                self._get_content(prompt, images),
                model_settings=self.model_settings,
            )
            log.info(f"Finished: {result.output}")
            self.usage += result.usage()
            self.elapsed_time += time.perf_counter() - start_time
            self.result = result.output
        except Exception as e:
            self._raise_error(e, start_time)

        if postprocess_fn and self.result is not None:
            try:
                self.result = postprocess_fn(self.result, **kwargs)
            except Exception as e:
                self._raise_error(e, start_time)

    async def run_stream(
        self,
        agent: Agent[Any, str],
        prompt: str,
        images: list[BinaryContent] = [],
        postprocess_fn: Callable[[str], str] | None = None,
        **kwargs: Any,
    ) -> None:
        start_time = time.perf_counter()
        try:
            async with agent.run_stream(
                self._get_content(prompt, images),
                model_settings=self.model_settings,
            ) as result:
                async for message in result.stream_text(debounce_by=3):
                    self.result = message
            self.usage += result.usage()
            self.elapsed_time += time.perf_counter() - start_time
        except Exception as e:
            self._raise_error(e, start_time)

        if postprocess_fn and self.result is not None:
            try:
                self.result = postprocess_fn(self.result, **kwargs)
            except Exception as e:
                self._raise_error(e, start_time)

    async def embedding(
        self,
        client: Any,
        model_name: str,
        input: str,
        dimensions: int = 1024,
    ) -> None:
        start_time = time.perf_counter()
        try:
            response = await client.embeddings.create(
                model=model_name,
                input=input,
                dimensions=dimensions,
            )
            self.usage += response.usage()
            self.elapsed_time = self.elapsed_time + (time.perf_counter() - start_time)
            self.result = response.data[0].embedding
        except Exception as e:
            self._raise_error(e, start_time)
