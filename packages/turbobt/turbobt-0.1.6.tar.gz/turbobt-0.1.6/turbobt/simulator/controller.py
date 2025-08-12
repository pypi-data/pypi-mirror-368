import asyncio
import datetime
import json
import unittest.mock

import sqlalchemy

from turbobt.neuron import Neuron
from turbobt.simulator import MockedSubtensor, db


class Controller:
    def __init__(
        self,
        subtensor: MockedSubtensor,
        start_block: int = 0,
        block_duration: datetime.timedelta = datetime.timedelta(seconds=1), # 0.25 for fast-blocks, 12 for mainnet
    ):
        self.subtensor = subtensor
        self._minting = None
        self._block_duration = block_duration

    async def __aenter__(self):
        self._minting = asyncio.create_task(self._mint_blocks())
        return self

    async def __aexit__(self, *args, **kwargs):
        self._minting.cancel()
        pass

    def change_block_duration(self, block_duration: datetime.timedelta):
        """
        Change the block duration.

        :param block_duration: The new block duration.
        :type block_duration: datetime.timedelta
        """
        self._block_duration = block_duration

    async def get_all_extrinsics(self):
        """
        Returns all extrinsics from the database.

        :return: A list of extrinsics.
        :rtype: list
        """
        async with self.subtensor.db_session() as session:
            extrinsics = await session.scalars(
                sqlalchemy.select(db.Extrinsic).filter_by(
                    # call_module="SubtensorModule",
                    # call_function="commit_crv3_weights",
                ).order_by(
                    db.Extrinsic.block.asc(),
                )
            )

            return list(extrinsics)

    async def get_commitment_extrinsics(self):
        """
        Returns all commitment extrinsics from the database.

        :return: A list of commitment extrinsics.
        :rtype: list
        """
        async with self.subtensor.db_session() as session:
            extrinsics = await session.scalars(
                sqlalchemy.select(db.Extrinsic).filter_by(
                    call_module="SubtensorModule",
                    call_function="commit_crv3_weights",
                ).order_by(
                    db.Extrinsic.block.asc(),
                )
            )

            return [
                unittest.mock.call(
                    extrinsic.call_module,
                    extrinsic.call_function,
                    # account_id=extrinsic.account_id,
                    # block=extrinsic.block,
                    **extrinsic.call_args_dict | {
                        "commit": json.loads(extrinsic.call_args_dict["commit"]),
                    },
                )
                for extrinsic in extrinsics
            ]

    def start_block_autoincrement(self):
        """
        Starts the block autoincrementing task.
        """
        if not self._minting:
            self._minting = asyncio.create_task(self._mint_blocks())
    
    def stop_block_autoincrement(self):
        """
        Stops the block autoincrementing task.
        """
        if self._minting:
            self._minting.cancel()
            self._minting = None

    async def create_subnet_from_dump(self, subnet_dump: dict):
        """
        Creates a subnet from the provided dump.

        :param subnet_dump: The subnet dump to create the subnet from.
        :type subnet_dump: dict
        """
        async with self.subtensor.db_session.begin() as session:
            block = await session.scalar(db.Block.query())

            subnet = db.Subnet(
                block=block.number,
                netuid=subnet_dump["netuid"],
                name=subnet_dump["name"],
                token_symbol=subnet_dump["symbol"],
                owner_coldkey=subnet_dump["owner_coldkey"],
                owner_hotkey=subnet_dump["owner_hotkey"],
                tempo=subnet_dump["tempo"],
                identity=subnet_dump["identity"],
            )
            subnet_hyperparams = db.SubnetHyperparams(
                block=subnet.block,
                netuid=subnet.netuid,
                **subnet_dump.get("hyperparameters", {}),
            )

            session.add(subnet)
            session.add(subnet_hyperparams)
            session.add_all([
                db.Neuron(
                    active=neuron["active"],
                    block=subnet.block,
                    coldkey=neuron["coldkey"],
                    hotkey=neuron["hotkey"],
                    netuid=subnet.netuid,
                    uid=neuron["uid"],
                    # stake=neuron["stake"],
                    # axon_info=neuron["axon_info"],
                    # prometheus_info=neuron["prometheus_info"],
                    consensus=neuron["consensus"],
                    incentive=neuron["incentive"],
                    dividends=neuron["dividends"],
                    emission=neuron["emission"],
                    trust=neuron["trust"],
                    pruning_score=neuron["pruning_score"],
                    rank=neuron["rank"],
                    last_update=neuron["last_update"],
                    validator_permit=neuron["validator_permit"],
                    validator_trust=neuron["validator_trust"],
                )
                for neuron in subnet_dump.get("neurons", [])
            ])

        return SubnetController(
            self,
            subnet.netuid,
        )

    # async def skip_to_block(self, block_number: int):
    #     """
    #     Skips to a specific block number.

    #     :param block_number: The block number to skip to.
    #     :type block_number: int
    #     """
    #     async with self.subtensor.db_session() as session:
    #         current_block = await db.Block.get_current_block(session)

    #         if current_block.number >= block_number:
    #             return

    #         while current_block.number < block_number:
    #             await db.Block.new_block(session)
    #             current_block = await db.Block.get_current_block(session)

    #         await session.commit()

    async def _mint_blocks(self):
        # TODO prevent simultaneous minting from multiple controllers
        while True:
            await asyncio.sleep(self._block_duration.total_seconds())

            async with self.subtensor.db_session() as session:
                block = await db.Block.new_block(session)

                extrinsics = await session.scalars(
                    sqlalchemy.select(db.Extrinsic).filter_by(block=block.number)
                )

            await self._execute(block, extrinsics)

    # TODO pytest.raises (for testing extrinsics)
    # TODO pytest-httpx?    !!!!!!!!!! mockowanie bazy na daną chwilę

    async def wait_for_epoch(self):
        await self._on_epoch()

    async def _execute(self, block, extrinsics):
        # TODO lock?
        for extrinsic in extrinsics:
            # TODO AttributeError
            try:
                call_module = getattr(self.subtensor, extrinsic.call_module)
                call_function = getattr(call_module, extrinsic.call_function)
            except AttributeError:
                async with self.subtensor.db_session.begin() as session:
                    event = db.SystemEvent(
                        block=block.number,
                        module_id="System",
                        event_id="ExtrinsicFailed",
                    )
                    session.add(event)
            else:
                await call_function(
                    extrinsic.account_id,
                    **extrinsic.call_args_dict,
                )

                async with self.subtensor.db_session.begin() as session:
                    event = db.SystemEvent(
                        block=block.number,
                        module_id="System",
                        event_id="ExtrinsicSuccess",
                    )
                    session.add(event)

            extrinsic_id = f"0x{extrinsic.id.to_bytes().hex()}"

            try:
                subscription = self.subtensor._subscriptions[extrinsic_id]
            except KeyError:
                continue

            subscription.put_nowait("ready")
            subscription.put_nowait(
                {
                    "broadcast": [
                        extrinsic.create_scale_object(self.subtensor).extrinsic_hash.hex(),
                    ],
                },
            )
            subscription.put_nowait(
                {
                    "inBlock": block.hash,
                },
            )
            subscription.put_nowait(
                {
                    "finalized": block.hash,
                },
            )

    async def _on_epoch(self):
        async with self.subtensor.db_session() as session:
            subnets = await session.scalars(sqlalchemy.select(db.Subnet))

            for subnet in subnets:
                # https://github.com/opentensor/subtensor/blob/4c9836f8cc199bc323956509f59d86d1761dd021/pallets/subtensor/src/coinbase/run_coinbase.rs#L858
                # TODO No commits to reveal until at least epoch 2.

                reveal_epoch = 1    # TODO

                # TODO
                # expired_commits = session.query(db.CRV3WeightCommits).filter(
                #     db.CRV3WeightCommits.netuid == subnet.netuid,
                #     db.CRV3WeightCommits.reveal_round < reveal_epoch,
                # )
                # expired_commits.delete()

                commits = await session.scalars(
                    sqlalchemy.select(db.CRV3WeightCommits).filter_by(
                        netuid=subnet.netuid,
                        commit_epoch=reveal_epoch,
                    ),
                )

                for commit in commits:
                    commit_data = json.loads(commit.commit)

                    # XXX do_set_weights
                    weights = [
                        db.Weights(
                            block=1,    #TODO
                            netuid=subnet.netuid,
                            validator=0,  # TODO uid
                            uid=uid,
                            weight=weight,
                        )
                        for uid, weight in zip(
                            commit_data["uids"],
                            commit_data["weights"],
                        )
                    ]

                    session.add_all(weights)

                # commits.delete()
                await session.commit()


class SubnetController:
    def __init__(self, controller: Controller, netuid: int):
        self.netuid = netuid
        self._controller = controller
    
    async def remove_neuron(self, uid: int, block: int | None = None):
        """
        Removes a neuron from the subnet.

        :param uid: The unique identifier of the neuron to remove.
        :type uid: int
        """
        async with self._controller.subtensor.db_session.begin() as session:
            if block is None:
                block = await session.scalar(db.Block.query().with_only_columns(db.Block.number)) # TODO scalar subquery?

            neuron = db.Neuron(
                active=None,
                block=block,
                coldkey=None,
                hotkey=None,
                netuid=self.netuid,
                uid=uid,
            )

            session.add(neuron)

    async def replace_neuron(self, neuron: Neuron): # TODO uid? when
        pass

    async def replace_all_neurons(self, neurons):
        pass

    async def update_hyperparam(self, name: str, value: int):
        """
        Updates a hyperparameter of the subnet.

        :param name: The name of the hyperparameter to update.
        :type name: str
        :param value: The new value for the hyperparameter.
        :type value: int
        """
        # if name in ("adjustment_alpha", "max_difficulty", "min_difficulty")
        async with self._controller.subtensor.db_session.begin() as session:
            await session.execute(
                sqlalchemy.update(db.SubnetHyperparams).where(
                    db.SubnetHyperparams.netuid == self.netuid,
                ).values({name: value})
            )
