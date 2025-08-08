from pydantic_ai.settings import ModelSettings

from agent_tools._log import log
from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolProtocol, LocalCredentialPool


async def test_credential_pool_manager(
    credential_pool_cls: type[CredentialPoolProtocol],
    agent_cls: type[AgentBase],
    target_model: str,
    model_settings: ModelSettings,
):
    credential_pool = credential_pool_cls(target_model=target_model)
    if isinstance(credential_pool, LocalCredentialPool):
        await credential_pool.start()

    agent = await agent_cls.create(
        credential_pool=credential_pool,
        model_settings=model_settings,
    )
    log.info("Agent created.")

    runner = await agent.run("中国的首都是哪里？")
    print(runner.result)

    if isinstance(credential_pool, LocalCredentialPool):
        credential_pool.stop()


async def test_all_credentials(
    model_name_enum: type[ModelNameBase],
    model_settings: ModelSettings,
    credential_pool_cls: type[CredentialPoolProtocol],
    agent_cls: type[AgentBase],
):
    for model_name in model_name_enum:
        credential_pool = credential_pool_cls(target_model=model_name)
        for credential in credential_pool.get_model_credentials():
            if "embedding" in model_name.value:
                continue
            try:
                agent = await agent_cls.create(
                    credential=credential,
                    model_settings=model_settings,
                )
                result = await agent.validate_credential()
                if result is True:
                    print(f"{credential.id} is valid.")
                else:
                    print(f"{credential.id} is invalid!")
            except Exception as e:
                print(f"error: {e}")
                continue
