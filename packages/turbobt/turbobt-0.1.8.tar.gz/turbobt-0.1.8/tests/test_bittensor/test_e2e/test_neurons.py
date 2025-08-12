import ipaddress
import pytest
import pytest_asyncio

import turbobt
from turbobt.simulator import MockedSubtensor
from turbobt.substrate.transports.mock import MockTransport
from turbobt.subtensor.exceptions import (
    HotKeyAlreadyRegisteredInSubNet,
    NotEnoughBalanceToStake,
)


@pytest_asyncio.fixture
async def subtensor():
    subtensor = MockedSubtensor()
    await subtensor.init()
    return subtensor


@pytest_asyncio.fixture
async def bittensor(subtensor, alice_wallet):
    async with turbobt.Bittensor(
        # "ws://127.0.0.1:9944",
        # transport=MockTransport(subtensor),
        # "finney",
        wallet=alice_wallet,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def subnet(bittensor, alice_wallet):
    subnet = bittensor.subnet(12)

    # try:
    #     await bittensor.subnets.register(
    #         alice_wallet,
    #     )
    # except NotEnoughBalanceToStake:
    #     pass

    return subnet


@pytest.mark.asyncio
async def test_serve(bittensor, alice_wallet):
    subnet = bittensor.subnet(2)

    # https://www.notion.so/Bittensor-subnet-template-1fdb63b4ef1e80acb26cde12ef1aa60d
    # https://github.com/opentensor/bittensor/pull/2876/files
    try:
        await subnet.neurons.register(alice_wallet.hotkey, wallet=alice_wallet)
    except HotKeyAlreadyRegisteredInSubNet:
        pass

    await subnet.neurons.serve(
        ip="192.168.0.2",
        port=1983,
        certificate=b"MyCert",
    )

    neurons = await subnet.list_neurons()
    neuron = neurons[0]

    assert neuron.axon_info.ip == ipaddress.IPv4Address("192.168.0.2")
    assert neuron.axon_info.port == 1983

    cert = await subnet.neuron(
        hotkey=alice_wallet.hotkey.ss58_address
    ).get_certificate()

    assert cert == {
        "algorithm": 77,
        "public_key": "yCert",
    }


def test_old():
    import bittensor

    bt = bittensor.Subtensor()
    v = bt.substrate.query(
        module="System",
        storage_function="Events",
        params=[],
        block_hash=None,
    )

    print(v)




@pytest.mark.asyncio
async def test_asso(bittensor: turbobt.Bittensor):

    # subscription = await bittensor.subtensor.chain.subscribeFinalizedHeads()
    subscription = await bittensor.subtensor.system.Events.subscribe()

    async for block in subscription:
        # v = await bittensor.subtensor.state.unsubscribeStorage(subscription.id)
        print(block)

    subnet = bittensor.subnet(12)
    now = await bittensor.subtensor.timestamp.Now.get()
    block = await bittensor.block(5909118).get()
    block_time = await block.get_timestamp()
    pass
    (5909119, '2025-07-02T13:41:12+00:00')
    # asso = await bittensor.subtensor.SubtensorModule.AssociatedEvmAddress.fetch(
    #     12,
    #     block_hash="0x25bafe3abd4f7b601a50d55f384e7b6ff7645b884bf124c7b7f405a9c7693f67",
    # )
    # asso = await subnet.evm_addresses.fetch(
    #     # block_hash="0x25bafe3abd4f7b601a50d55f384e7b6ff7645b884bf124c7b7f405a9c7693f67"
    # )

    # assert len(asso) == 4

    asso = await subnet.evm_addresses.get(
        66,
        block_hash="0x25bafe3abd4f7b601a50d55f384e7b6ff7645b884bf124c7b7f405a9c7693f67"
    )

    assert len(asso) == 2
