import asyncio
import ctypes
import hashlib
import json

import scalecodec.utils.ss58
from sqlalchemy import ForeignKey, func, select, types
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class UnsignedInteger(types.TypeDecorator):
    """Custom SQLAlchemy type for handling uint64 values as int64 in the database.

    This type automatically converts large unsigned 64-bit integers to signed
    64-bit integers using two's complement representation when storing to the
    database, and handles the reverse conversion when reading from the database.

    This is particularly useful for Bittensor values that may exceed the signed
    int64 range but need to be stored in databases that don't support uint64.
    """

    impl = types.Integer
    cache_ok = True

    def process_bind_param(self, value: int | None, dialect: Dialect) -> int | None:
        """Convert uint64 to int64 when binding to database."""
        if value is not None:
            return ctypes.c_int64(value).value

        return value

    def process_result_value(self, value: int | None, dialect: Dialect) -> int | None:
        """Convert int64 back to uint64 when reading from database."""
        if value is not None and value < 0:
            return ctypes.c_uint64(value).value

        return value

    @property
    def python_type(self) -> type:
        return int


class Base(DeclarativeBase):
    @classmethod
    def get(cls, block: str | int | None = None, **kwargs):
        query = select(cls)

        if isinstance(block, int):
            block_number = block
        elif isinstance(block, str):
            block_query = select(Block.number).filter_by(hash=block)
            block_number = select(block_query.scalar_subquery())
        else:
            block_number = select(func.max(Block.number))

        if kwargs:
            query = query.filter_by(**kwargs)

        return (
            query.filter(cls.block <= block_number).order_by(cls.block.desc()).limit(1)
        )


def default_block_hash(context):
    return Block.get_hash(
        context.get_current_parameters()["number"]
    )  # TODO number autoincrement


class Block(Base):
    __tablename__ = "Block"

    number: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hash: Mapped[str] = mapped_column(
        default=default_block_hash,
        index=True,
        unique=True,
    )

    extrinsics: Mapped[list["Extrinsic"]] = relationship()

    on_created = asyncio.Queue()

    @classmethod
    async def new_block(cls, session):
        block_id = await session.scalar(select(func.max(cls.number)).with_for_update())
        block = cls(
            number=block_id + 1,
        )

        session.add(block)

        await session.commit()

        return block

    @classmethod
    def get_hash(cls, block_number: int):
        return f"0x{hashlib.sha256(bytes(block_number)).hexdigest()}"

    @classmethod
    def query(cls, block: str | int | None = None):
        # TODO limit(1)

        if isinstance(block, int):
            return select(cls).filter_by(number=block).limit(1)

        if isinstance(block, str):
            return select(cls).filter_by(hash=block).limit(1)

        return select(cls).order_by(cls.number.desc()).limit(1)


class Extrinsic(Base):
    __tablename__ = "Extrinsic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block: Mapped[int] = mapped_column(ForeignKey("Block.number"), index=True)

    account_id: Mapped[str]
    call_args: Mapped[str]  # TODO type
    call_function: Mapped[str]
    call_module: Mapped[str]
    era_current: Mapped[int]
    era_period: Mapped[int]
    nonce: Mapped[int]
    signature: Mapped[str]
    tip: Mapped[int]

    @property
    def call_args_dict(self):
        return {
            arg["name"]: (
                scalecodec.utils.ss58.ss58_encode(arg["value"])
                if arg["type"] == "AccountId"
                else arg["value"]
            )
            for arg in json.loads(self.call_args)
        }

    def create_scale_object(self, substrate):
        extrinsic = substrate._registry.create_scale_object(
            "Extrinsic",
            metadata=substrate._metadata,
        )
        extrinsic.encode(
            {
                "account_id": self.account_id,
                "asset_id": {"tip": self.tip, "asset_id": None},
                "call_args": json.loads(self.call_args),
                "call_function": self.call_function,
                "call_module": self.call_module,
                "era": {
                    "current": self.era_current,
                    "period": self.era_period,
                },
                "mode": "Disabled",
                "nonce": self.nonce,
                "signature_version": 1,
                "signature": self.signature,
                "tip": self.tip,
            },
        )

        return extrinsic

    def encode(self, substrate):
        extrinsic = self.create_scale_object(substrate)

        return str(extrinsic.data)


class Subnet(Base):
    __tablename__ = "Subnet"

    block: Mapped[int] = mapped_column(ForeignKey("Block.number"), primary_key=True)
    netuid: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str]
    token_symbol: Mapped[str]
    owner_coldkey: Mapped[str]
    owner_hotkey: Mapped[str]
    tempo: Mapped[int]
    identity: Mapped[str | None]

    @classmethod
    def get(cls, netuid: int, block: str | int | None = None):
        return super().get(block).filter_by(netuid=netuid)


class SubnetHyperparams(Base):
    __tablename__ = "SubnetHyperparams"

    block: Mapped[int] = mapped_column(ForeignKey("Block.number"), primary_key=True)
    netuid: Mapped[int] = mapped_column(primary_key=True)

    activity_cutoff: Mapped[int] = mapped_column(default=5000)
    adjustment_alpha: Mapped[int] = mapped_column(
        UnsignedInteger, default=17893341751498265066,  # 18_446_744_073_709_551_615 * 0.97
    )
    adjustment_interval: Mapped[int] = mapped_column(default=360)
    alpha_high: Mapped[int] = mapped_column(default=58982)
    alpha_low: Mapped[int] = mapped_column(default=45875)
    bonds_moving_avg: Mapped[int] = mapped_column(default=900000)
    commit_reveal_period: Mapped[int] = mapped_column(default=1)
    commit_reveal_weights_enabled: Mapped[bool] = mapped_column(default=False)
    difficulty: Mapped[int] = mapped_column(default=10000000)
    immunity_period: Mapped[int] = mapped_column(default=5000)
    kappa: Mapped[int] = mapped_column(default=32767)
    liquid_alpha_enabled: Mapped[bool] = mapped_column(default=False)
    max_burn: Mapped[int] = mapped_column(default=100000000000)
    max_difficulty: Mapped[int] = mapped_column(
        UnsignedInteger, default=18446744073709551615
    )
    max_regs_per_block: Mapped[int] = mapped_column(default=1)
    max_validators: Mapped[int] = mapped_column(default=64)
    max_weights_limit: Mapped[int] = mapped_column(default=65535)
    min_allowed_weights: Mapped[int] = mapped_column(default=1)
    min_burn: Mapped[int] = mapped_column(default=500000)
    min_difficulty: Mapped[int] = mapped_column(
        UnsignedInteger, default=18446744073709551615
    )
    registration_allowed: Mapped[bool] = mapped_column(default=True)
    rho: Mapped[int] = mapped_column(default=10)
    serving_rate_limit: Mapped[int] = mapped_column(default=50)
    target_regs_per_interval: Mapped[int] = mapped_column(default=1)
    tempo: Mapped[int] = mapped_column(default=100)
    weights_rate_limit: Mapped[int] = mapped_column(default=100)
    weights_version: Mapped[int] = mapped_column(default=0)


class Neuron(Base):
    __tablename__ = "Neuron"

    block: Mapped[int] = mapped_column(
        ForeignKey("Block.number"),
        primary_key=True,
    )
    netuid: Mapped[int] = mapped_column(
        ForeignKey("Subnet.netuid"),
        primary_key=True,
    )
    uid: Mapped[int] = mapped_column(
        primary_key=True,
    )

    active: Mapped[bool | None] = mapped_column()
    coldkey: Mapped[str | None] = mapped_column(default=None)
    hotkey: Mapped[str | None] = mapped_column(default=None)
    consensus: Mapped[int] = mapped_column(default=0)
    dividends: Mapped[int] = mapped_column(default=0)
    emission: Mapped[int] = mapped_column(default=0)
    incentive: Mapped[int] = mapped_column(default=0)
    last_update: Mapped[int] = mapped_column(default=0)
    pruning_score: Mapped[int] = mapped_column(default=65535)
    rank: Mapped[int] = mapped_column(default=0)
    trust: Mapped[int] = mapped_column(default=0)
    validator_permit: Mapped[bool] = mapped_column(default=False)
    validator_trust: Mapped[int] = mapped_column(default=0)

    axon_info: Mapped["AxonInfo"] = relationship(back_populates="neuron")
    certificate: Mapped["NeuronCertificate"] = relationship(back_populates="neuron")


class NeuronCertificate(Base):
    __tablename__ = "NeuronCertificate"

    block: Mapped[int] = mapped_column(ForeignKey("Block.number"), primary_key=True)
    netuid: Mapped[int] = mapped_column(ForeignKey("Subnet.netuid"), primary_key=True)
    hotkey: Mapped[str] = mapped_column(ForeignKey("Neuron.hotkey"), primary_key=True)

    algorithm: Mapped[int]
    public_key: Mapped[bytes]

    neuron: Mapped["Neuron"] = relationship(back_populates="certificate")


class AxonInfo(Base):
    __tablename__ = "AxonInfo"

    block: Mapped[int] = mapped_column(ForeignKey("Block.number"), primary_key=True)
    netuid: Mapped[int] = mapped_column(ForeignKey("Subnet.netuid"), primary_key=True)
    uid: Mapped[int] = mapped_column(ForeignKey("Neuron.uid"), primary_key=True)

    ip: Mapped[str]
    port: Mapped[int]
    protocol: Mapped[int]

    neuron: Mapped["Neuron"] = relationship(back_populates="axon_info")


class CRV3WeightCommits(Base):
    __tablename__ = "CRV3WeightCommits"

    netuid: Mapped[int] = mapped_column(primary_key=True)
    commit_epoch: Mapped[int] = mapped_column(primary_key=True)
    who: Mapped[str]
    commit: Mapped[bytes]
    reveal_round: Mapped[int]


class Weights(Base):
    __tablename__ = "Weights"

    block: Mapped[int] = mapped_column(ForeignKey("Block.number"), primary_key=True)
    netuid: Mapped[int] = mapped_column(primary_key=True)
    validator: Mapped[int] = mapped_column(primary_key=True)

    # TODO list?
    uid: Mapped[int]
    weight: Mapped[int]


class SystemEvent(Base):
    __tablename__ = "SystemEvent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block: Mapped[int] = mapped_column(ForeignKey("Block.number"), index=True)

    module_id: Mapped[str]
    event_id: Mapped[str]
