import asyncio
import json

import scalecodec
import scalecodec.utils.ss58

from turbobt.simulator import db
from turbobt.substrate.pallets._base import Pallet


class Author(Pallet):
    async def unwatchExtrinsic(self, bytes):
        self.substrate._subscriptions.pop(bytes, None)

    async def submitAndWatchExtrinsic(self, bytes):
        extrinsic_cls = self.substrate._registry.get_decoder_class("Extrinsic")
        extrinsic_obj = extrinsic_cls(
            data=scalecodec.ScaleBytes(bytes),
            metadata=self.substrate._metadata,
        )
        extrinsic = extrinsic_obj.decode()

        async with self.substrate.db_session.begin() as session:
            block = await session.scalar(db.Block.query()) # TODO
            extrinsic_model = db.Extrinsic(
                account_id=scalecodec.utils.ss58.ss58_encode(extrinsic["address"]),
                block=block.number + 1, # TODO param
                call_args=json.dumps(extrinsic["call"]["call_args"]),
                call_function=extrinsic["call"]["call_function"],
                call_module=extrinsic["call"]["call_module"],
                era_current=extrinsic["era"][1],
                era_period=extrinsic["era"][0],
                nonce=extrinsic["nonce"],
                signature=extrinsic["signature"]["Sr25519"],
                tip=extrinsic["tip"],
            )

            session.add(extrinsic_model)

        extrinsic_id = f"0x{extrinsic_model.id.to_bytes().hex()}"

        self.substrate._subscriptions[extrinsic_id] = asyncio.Queue()

        return extrinsic_id
