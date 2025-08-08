import pytest


@pytest.mark.asyncio
async def test_now(substrate, mocked_transport, alice_wallet):
    mocked_transport.responses["system_accountNextIndex"] = {
        "result": 1,
    }

    account_next_index = await substrate.system.accountNextIndex(
        alice_wallet.hotkey.ss58_address,
    )

    assert account_next_index == 1
