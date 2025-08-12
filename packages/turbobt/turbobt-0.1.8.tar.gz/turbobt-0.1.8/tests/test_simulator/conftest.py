import pytest_asyncio

import turbobt
from turbobt.simulator import MockedSubtensor
from turbobt.substrate.transports.mock import MockTransport


@pytest_asyncio.fixture
async def subtensor():
    client = MockedSubtensor()
    # TODO ctx
    await client.init()
    return client


@pytest_asyncio.fixture
async def simulation(subtensor):
    from turbobt.simulator.controller import Controller

    controller = Controller(
        subtensor,
    )

    yield controller
    # async with controller:
    #     yield controller



@pytest_asyncio.fixture
async def substrate(subtensor):
    async with turbobt.Substrate(
        "ws://127.0.0.1:9944",
        transport=MockTransport(subtensor),
    ) as substrate:
        yield substrate
