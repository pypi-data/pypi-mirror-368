import ipaddress
import json
import unittest.mock

import pytest
import pytest_asyncio

import turbobt
from turbobt import Subtensor
from turbobt.neuron import AxonInfo, Neuron, PrometheusInfo
from turbobt.substrate.transports.mock import MockTransport


@pytest.mark.asyncio
async def test_chain(substrate):
    await substrate._init_runtime()
    block_header = await substrate.chain.getHeader()

    assert block_header == {
        "extrinsicsRoot": "0xe5b4ae1cda6591fa8a8026bef64c5d712f7dc6c0dc700f74d1670139e55c220d",
        "number": 1,
        "digest": {
            "logs": [],
        },
        "parentHash": "0x4545454545454545454545454545454545454545454545454545454545454545",
        "stateRoot": "0xfb9e07dd769d95a30ab04e1e801b1400df1261487cddab93dc64628ad95cec56",
    }


# pluggable
@pytest_asyncio.fixture
async def patch_get_encrypted_commit(monkeypatch):
    def get_encrypted_commit(
        uids,
        weights,
        version_key,
        tempo,
        current_block,
        netuid,
        subnet_reveal_period_epochs,
        block_time,
    ):
        import base64
        import json

        return (
            json.dumps({
                "uids": uids,
                "weights": weights,
            }).encode(),
            123,
        )

    monkeypatch.setattr(
        "bittensor_commit_reveal.get_encrypted_commit",
        get_encrypted_commit,
    )

    yield


@pytest_asyncio.fixture
async def bittensor(subtensor, patch_get_encrypted_commit):
    async with turbobt.Bittensor(
        "ws://127.0.0.1:9944",
        subtensor=Subtensor(
            transport=MockTransport(subtensor),
        ),
    ) as client:
        yield client


@pytest_asyncio.fixture
async def subnet_dump():
    return {
        "identity": None,
        "name": "apex",
        "symbol": "α",
        "owner_hotkey": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
        "owner_coldkey": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
        "tempo": 100,

        "netuid": 1,
        "hyperparameters": {
            "activity_cutoff": 5000,
            "adjustment_alpha": 0,
            "adjustment_interval": 100,
            "alpha_high": 58982,
            "alpha_low": 45875,
            "bonds_moving_avg": 900000,
            "commit_reveal_period": 1,
            "commit_reveal_weights_enabled": False,
            "difficulty": 10000000,
            "immunity_period": 4096,
            "kappa": 32767,
            "liquid_alpha_enabled": False,
            "max_burn": 100000000000,
            "max_difficulty": 4611686018427387903,
            "max_regs_per_block": 1,
            "max_validators": 64,
            "max_weights_limit": 65535,
            "min_allowed_weights": 0,
            "min_burn": 500000,
            "min_difficulty": 10000000,
            "registration_allowed": True,
            "rho": 10,
            "serving_rate_limit": 50,
            "target_regs_per_interval": 2,
            "tempo": 100,
            "weights_rate_limit": 100,
            "weights_version": 0,
        },
        "neurons": [
            {
                "active": True,
                "axon_info": {
                    "ip": "0.0.0.0",    # noqa: S104
                    "port": 0,
                    "protocol": 0,
                },
                "coldkey": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
                "consensus": 0,
                "dividends": 0,
                "emission": 0,
                "hotkey": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
                "incentive": 0,
                "last_update": 0,
                "prometheus_info": {
                    "ip": "0.0.0.0",    # noqa: S104
                    "port": 0,
                },
                "pruning_score": 65535,
                "rank": 0,
                "stake": 1.0,
                # "subnet": SubnetReference(
                #     client=bittensor,
                #     netuid=1,
                # ),
                "trust": 0,
                "uid": 0,
                "validator_permit": False,
                "validator_trust": 0,
            },
        ],
    }


@pytest.mark.asyncio
async def test_client(bittensor, subtensor, simulation, subnet_dump, alice_wallet, bob_wallet):
    simulation.start_block_autoincrement()

    subnet_ref = bittensor.subnet(1)
    subnet = await subnet_ref.get()

    assert subnet is None

    # await bittensor.subnets.register(alice_wallet)
    subnet_controller = await simulation.create_subnet_from_dump(subnet_dump)

    async with bittensor.head:
        subnet = await subnet_ref.get()

    assert subnet is not None

    hyperparameters = await subnet.get_hyperparameters()

    assert hyperparameters == {
        "activity_cutoff": 5000,
        "adjustment_alpha": 0,
        "adjustment_interval": 100,
        "alpha_high": 58982,
        "alpha_low": 45875,
        "bonds_moving_avg": 900000,
        "commit_reveal_period": 1,
        "commit_reveal_weights_enabled": False,
        "difficulty": 10000000,
        "immunity_period": 4096,
        "kappa": 32767,
        "liquid_alpha_enabled": False,
        "max_burn": 100000000000,
        "max_difficulty": 4611686018427387903,
        "max_regs_per_block": 1,
        "max_validators": 64,
        "max_weights_limit": 65535,
        "min_allowed_weights": 0,
        "min_burn": 500000,
        "min_difficulty": 10000000,
        "registration_allowed": True,
        "rho": 10,
        "serving_rate_limit": 50,
        "target_regs_per_interval": 2,
        "tempo": 100,
        "weights_rate_limit": 100,
        "weights_version": 0,
    }

    await subnet_controller.update_hyperparam(
        name="immunity_period",
        value=1000,
    )

    hyperparameters = await subnet.get_hyperparameters()

    assert hyperparameters["immunity_period"] == 1000

    neurons = await subnet.list_neurons()

    assert neurons == [
        Neuron(
            active=True,
            axon_info=AxonInfo(
                ip=ipaddress.IPv4Address("0.0.0.0"),  # noqa: S104
                port=0,
                protocol=0,
            ),
            coldkey="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
            consensus=0,
            dividends=0,
            emission=0,
            hotkey="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
            incentive=0,
            last_update=0,
            prometheus_info=PrometheusInfo(
                ip=ipaddress.IPv4Address("0.0.0.0"),  # noqa: S104
                port=0,
            ),
            pruning_score=65535,
            rank=0,
            stake=0,
            subnet=subnet,
            trust=0,
            uid=0,
            validator_permit=False,
            validator_trust=0,
        ),
    ]

    # await subnet.neurons.serve(
    #     ip="192.168.0.2",
    #     port=8080,
    #     certificate=b"MyCert",
    #     wallet=alice_wallet,
    # )
    # await subnet.neurons.register(bob_wallet.hotkey, wallet=bob_wallet)

    # async with bittensor.head:
    #     neurons = await subnet.list_neurons()
    
    # assert neurons == [
    #     Neuron(
    #         active=True,
    #         axon_info=AxonInfo(
    #             ip=ipaddress.IPv4Address("192.168.0.2"),  # noqa: S104
    #             port=8080,
    #             protocol=4,
    #         ),
    #         coldkey="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
    #         consensus=0,
    #         dividends=0,
    #         emission=0,
    #         hotkey="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
    #         incentive=0,
    #         last_update=0,
    #         prometheus_info=PrometheusInfo(
    #             ip=ipaddress.IPv4Address("0.0.0.0"),  # noqa: S104
    #             port=0,
    #         ),
    #         pruning_score=65535,
    #         rank=0,
    #         stake=0,
    #         subnet=subnet,
    #         trust=0,
    #         uid=0,
    #         validator_permit=False,
    #         validator_trust=0,
    #     ),
    #     Neuron(
    #         active=True,
    #         axon_info=AxonInfo(
    #             ip=ipaddress.IPv4Address("0.0.0.0"),  # noqa: S104
    #             port=0,
    #             protocol=0,
    #         ),
    #         coldkey="5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
    #         consensus=0,
    #         dividends=0,
    #         emission=0,
    #         hotkey="5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
    #         incentive=0,
    #         last_update=0,
    #         prometheus_info=PrometheusInfo(
    #             ip=ipaddress.IPv4Address("0.0.0.0"),  # noqa: S104
    #             port=0,
    #         ),
    #         pruning_score=65535,
    #         rank=0,
    #         stake=0,
    #         subnet=subnet,
    #         trust=0,
    #         uid=1,
    #         validator_permit=False,
    #         validator_trust=0,
    #     ),
    # ]


    # await subnet_controller.remove_neuron(uid=1)

    # async with bittensor.head:
    #     neurons = await subnet.list_neurons()

    # assert len(neurons) == 1

    # # certificate = await subnet.neurons["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"].get_certificate()

    # # assert certificate == {
    # #     "public_key": "yCert",
    # #     "algorithm": 77,
    # # }

    # with pytest.raises(NotImplementedError):
    #     weights = await subnet.weights.fetch()
    #     assert weights == {}
    
    # return

    await subnet.weights.commit(
        {
            0: 0.9,
        },
        wallet=alice_wallet,
    )

    extrinsics = await simulation.get_commitment_extrinsics()

    assert extrinsics == [
        unittest.mock.call(
            "SubtensorModule",
            "commit_crv3_weights",
            commit={
                "uids": [0],
                "weights": [65535],
            },
            netuid=1,
            reveal_round=123,
        ),
    ]

    # TODO osobny test z przygotowanym stanem w db
    with pytest.raises(NotImplementedError):
        weights = await subnet.weights.fetch()

        assert weights == {}

        await simulation.wait_for_epoch()

        weights = await subnet.weights.fetch()

        assert weights == {
            0: {
                0: 1.0,
            },
        }

    await subnet.weights.set(
        {
            0: 0.25,
            1: 0.75,
        },
        wallet=alice_wallet,
    )

    await subnet_controller.replace_all_neurons([])

    async with bittensor.head:
        neurons = await subnet.list_neurons()

    # assert len(neurons) == 0

    extrinsics = await simulation.get_commitment_extrinsics()

    assert len(extrinsics) == 1

