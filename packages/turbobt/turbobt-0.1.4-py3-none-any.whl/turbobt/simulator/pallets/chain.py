import typing

import sqlalchemy

from turbobt.simulator import db

from ._base import Pallet


class Extrinsic(typing.TypedDict):
    extrinsic_hash: str
    extrinsic_length: int
    # call


class Header(typing.TypedDict):
    number: int
    # ...


class Block(typing.TypedDict):
    extrinsics: Extrinsic
    header: Header


class SignedBlock(typing.TypedDict):
    block: Block
    # justifications


class Chain(Pallet):
    async def getBlock(self, hash: str | None = None) -> SignedBlock | None:
        async with self.substrate.db_session() as session:
            block = await session.scalar(
                db.Block.query(hash).options(
                    sqlalchemy.orm.joinedload(db.Block.extrinsics),
                )
            )

        if not block:
            return None

        return {
            "block": {
                "header": {
                    "parentHash": db.Block.get_hash(block.number - 1),
                    "number": hex(block.number),
                    "stateRoot": "0x7e08c53c205b2d7766884935e96dab4cdd11e7055024603b42023894bec3c33d",
                    "extrinsicsRoot": "0x937ca90d15a79bf046edeb94a02ccc65de71b7985e9bb215d5e31bd5fea3b962",
                    "digest": {
                        "logs": [],
                    },
                },
                "extrinsics": [
                    extrinsic.encode(self.substrate) for extrinsic in block.extrinsics
                ],
            },
            "justifications": None,
        }

    async def getBlockHash(self, hash: int | None = None) -> str | None:
        async with self.substrate.db_session() as session:
            block = await session.scalar(db.Block.query(hash))

        if not block:
            return None

        return block.hash

    async def getHeader(self, hash: str | None = None) -> Header | None:
        async with self.substrate.db_session() as session:
            block = await session.scalar(db.Block.query(hash))

        if not block:
            return None

        return {
            "parentHash": db.Block.get_hash(block.number - 1),
            "number": hex(block.number),
            "stateRoot": "0xfb9e07dd769d95a30ab04e1e801b1400df1261487cddab93dc64628ad95cec56",
            "extrinsicsRoot": "0xe5b4ae1cda6591fa8a8026bef64c5d712f7dc6c0dc700f74d1670139e55c220d",
            "digest": {
                "logs": [],
            },
        }
