import scalecodec.utils.ss58
import sqlalchemy
import sqlalchemy.orm

from turbobt.simulator import db


class NeuronInfoRuntimeApi:
    def __init__(self, substrate):
        self.substrate = substrate

    async def get_neurons_lite(self, netuid: int, block_hash: str | None):
        async with self.substrate.db_session() as session:
            block = (
                db.Block.query(block_hash)
                .with_only_columns(db.Block.number)
                .scalar_subquery()
            )
            neurons = await session.scalars(
                sqlalchemy.select(db.Neuron)
                .filter(
                    db.Neuron.netuid == netuid,
                    db.Neuron.block <= block,
                )
                .order_by(
                    db.Neuron.uid,
                    sqlalchemy.desc(db.Neuron.block),
                )
                .group_by(
                    db.Neuron.uid,
                    # db.Neuron.id,
                )
                .having(db.Neuron.block == sqlalchemy.func.max(db.Neuron.block))
                .options(
                    sqlalchemy.orm.joinedload(db.Neuron.axon_info)
                )
            )

        return [
            {
                "active": neuron.active,
                "coldkey": "0x" + scalecodec.utils.ss58.ss58_decode(neuron.coldkey),
                "hotkey": "0x" + scalecodec.utils.ss58.ss58_decode(neuron.hotkey),
                "uid": neuron.uid,
                "netuid": neuron.netuid,
                "stake": [
                    (
                        "0x"
                        + scalecodec.utils.ss58.ss58_decode(
                            neuron.coldkey
                        ),  # coldkey?
                        0,
                    ),
                ],
                "axon_info": {
                    "ip": neuron.axon_info.ip,
                    "port": neuron.axon_info.port,
                    "protocol": neuron.axon_info.protocol,
                }
                if neuron.axon_info
                # if False
                else {
                    "ip": "0.0.0.0",
                    "port": 0,
                    "protocol": 0,
                },
                "consensus": neuron.consensus,
                "dividends": neuron.dividends,
                "emission": neuron.emission,
                "incentive": neuron.incentive,
                "last_update": neuron.last_update,
                "prometheus_info": {
                    "ip": "0.0.0.0",
                    "port": 0,
                },
                "pruning_score": neuron.pruning_score,
                "rank": neuron.rank,
                "trust": neuron.trust,
                "validator_permit": neuron.validator_permit,
                "validator_trust": neuron.validator_trust,
            }
            for neuron in neurons
            if neuron.active is not None
        ]
