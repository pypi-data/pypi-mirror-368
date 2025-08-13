import ipaddress
import typing

import sqlalchemy

from turbobt.simulator import db
from turbobt.subtensor.exceptions import (
    HotKeyAlreadyRegisteredInSubNet,
    HotKeyNotRegisteredInNetwork,
)

AccountId = typing.TypeAlias = str


class SubtensorModule:
    def __init__(self, substrate):
        self.substrate = substrate

    async def burned_register(self, who, netuid: int, hotkey: AccountId):
        async with self.substrate.db_session.begin() as session:
            neuron = await session.scalar(
                sqlalchemy.select(db.Neuron).filter_by(
                    netuid=netuid,
                    hotkey=hotkey,
                    # TODO block
                ),
            )

            if neuron:
                raise HotKeyAlreadyRegisteredInSubNet

            neuron = db.Neuron(
                active=True,    # TODO?
                # block=db.Block.query_current(session).scalar_subquery(),
                block=1,
                coldkey=who,
                hotkey=hotkey,
                netuid=netuid,
                uid=1,  # TODO uid
            )

            session.add(neuron)

    async def commit_crv3_weights(self, who: str, netuid: int, commit: str, reveal_round: int):
        current_epoch = 1   # TODO

        async with self.substrate.db_session.begin() as session:
            commits = await session.scalar(
                sqlalchemy.select(sqlalchemy.func.count()).select_from(db.CRV3WeightCommits).filter_by(
                    commit_epoch=current_epoch,
                    netuid=netuid,
                    who=who,
                ),
            )

            if commits >= 10:
                raise RuntimeError("TooManyUnrevealedCommits")  # TODO Exception

            commit_model = db.CRV3WeightCommits(
                netuid=netuid,
                commit_epoch=current_epoch,
                who=who,
                commit=commit.encode(),
                reveal_round=reveal_round,
            )

            session.add(commit_model)

        # https://github.com/opentensor/subtensor/blob/4c9836f8cc199bc323956509f59d86d1761dd021/pallets/subtensor/src/subnets/weights.rs#L229

    async def commit_timelocked_weights(
        self,
        who: str,
        netuid: int,
        commit: str,
        reveal_round: int,
        commit_reveal_version: int,
    ):
        current_epoch = 1   # TODO

        async with self.substrate.db_session.begin() as session:
            commits = await session.scalar(
                sqlalchemy.select(sqlalchemy.func.count()).select_from(db.CRV3WeightCommits).filter_by(
                    commit_epoch=current_epoch,
                    netuid=netuid,
                    who=who,
                ),
            )

            if commits >= 10:
                raise RuntimeError("TooManyUnrevealedCommits")  # TODO Exception

            commit_model = db.CRV3WeightCommits(
                netuid=netuid,
                commit_epoch=current_epoch,
                who=who,
                commit=commit.encode(),
                reveal_round=reveal_round,
            )

            session.add(commit_model)

    async def register_network(
        self,
        who,
        hotkey: str,
    ):
        # https://github.com/opentensor/subtensor/blob/9f33e759acd763497135043504dc048dcc599c31/pallets/subtensor/src/subnets/subnet.rs#L117

        async with self.substrate.db_session() as session:
            block = await session.scalar(db.Block.query())  # TODO

            # TODO remove_balance_from_coldkey_account

            subnet = db.Subnet(
                block=block.number,
                identity="Test Identity",
                name="Test Network",
                netuid=1,  # TODO netuid
                owner_coldkey=hotkey,
                owner_hotkey=hotkey,
                tempo=360,
                token_symbol="T",
            )

            session.add(subnet)

            await session.commit()

            subnet_hyperparams = db.SubnetHyperparams(
                block=subnet.block,
                netuid=subnet.netuid,
            )

            # Add the caller to the neuron set
            neuron = db.Neuron(
                active=True,    # TODO?
                block=subnet.block,
                coldkey=who,
                hotkey=hotkey,
                netuid=subnet.netuid,
                uid=0,
            )

            session.add(subnet_hyperparams)
            session.add(neuron)

            await session.commit()

    async def serve_axon(
        self,
        who,
        netuid: int,
        version: int,
        ip: int,
        port: int,
        ip_type: int,
        protocol: int,
        placeholder1: int,
        placeholder2: int,
    ):
        async with self.substrate.db_session.begin() as session:
            neuron_id = await session.scalar(
                sqlalchemy.select(db.Neuron.uid).filter_by(
                    netuid=netuid,
                    hotkey=who,    # cold?
                ).order_by(
                    # TODO uid swap
                    db.Neuron.block.desc(),
                ).limit(1)
            )

            if neuron_id is None:
                raise HotKeyNotRegisteredInNetwork
            
            axon_info = db.AxonInfo(
                block=1,  # TODO
                ip=str(ipaddress.ip_address(ip)),
                netuid=netuid,
                port=port,
                protocol=protocol,
                uid=neuron_id,
            )

            session.add(axon_info)

    async def serve_axon_tls(
        self,
        who,
        netuid: int,
        version: int,
        ip: int,
        port: int,
        ip_type: int,
        protocol: int,
        placeholder1: int,
        placeholder2: int,
        certificate: str,
    ):
        await self.serve_axon(
            who,
            netuid,
            version,
            ip,
            port,
            ip_type,
            protocol,
            placeholder1,
            placeholder2,
        )

        async with self.substrate.db_session.begin() as session:
            neuron_certificate = db.NeuronCertificate(
                block=1,  # TODO
                hotkey=who,
                netuid=netuid,
                algorithm=ord(certificate[0]),
                public_key=certificate[1:].encode(),
            )

            session.add(neuron_certificate)

    async def set_weights(
        self,
        who,
        netuid: int,
        dests: list[int],
        weights: list[int],
        version_key: int,
    ):
        return
        # https://github.com/opentensor/subtensor/blob/9f33e759acd763497135043504dc048dcc599c31/pallets/subtensor/src/subnets/weights.rs#L677
        async with self.substrate.db_session.begin() as session:
            session.add_all(
                db.Weights(
                    block=1,
                    netuid=netuid,
                    validator=0,    # TODO uid
                    uid=uid,
                    weight=weight,
                )
                for uid, weight in zip(dests, weights)
            )
