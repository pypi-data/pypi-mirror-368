import scalecodec
import scalecodec.utils.ss58
import sqlalchemy

from turbobt.simulator import db
from turbobt.simulator.pallets._base import Pallet
from turbobt.substrate._hashers import HASHERS, xxh128

STORAGE_KEYS = {
    "0x" + (xxh128(pallet) + xxh128(storage)).hex(): f"{pallet}.{storage}"
    for pallet, storage in (
        ("System", "Events"),
        # TODO
        ("SubtensorModule", "Weights"),
        ("SubtensorModule", "NeuronCertificates"),
    )
}


class State(Pallet):
    async def getKeys(
        self,
        prefix: str,
        hash=None,
    ) -> list:
        raise NotImplementedError
    
    async def getKeysPaged(
        self,
        prefix: str,
        count: int,
        startKey: str | None = "",
        hash=None,
    ) -> list:
        raise NotImplementedError

    async def getRuntimeVersion(self, hash):
        return {
            "specName": "node-subtensor",
            "implName": "node-subtensor",
            "authoringVersion": 1,
            "specVersion": 264,
            "implVersion": 1,
            "apis": [
                ["0xdf6acb689907609b", 5],
                ["0x37e397fc7c91f5e4", 2],
                ["0x40fe3ad401f8959a", 6],
                ["0xfbc577b9d747efd6", 1],
                ["0xd2bc9897eed08f15", 3],
                ["0xf78b278be53f454c", 2],
                ["0xdd718d5cc53262d4", 1],
                ["0xab3c0572291feb8b", 1],
                ["0xed99c5acb25eedf5", 3],
                ["0xbc9d89904f5b923f", 1],
                ["0x37c8bb1350a9a2a8", 4],
                ["0xf3ff14d5ab527059", 3],
                ["0x582211f65bb14b89", 5],
                ["0xe65b00e46cedd0aa", 2],
                ["0x42e62be4a39e5b60", 1],
                ["0x806df4ccaa9ed485", 1],
                ["0x8375104b299b74c5", 1],
                ["0x5d1fbfbe852f2807", 1],
                ["0xc6886e2f8e598b0a", 1],
            ],
            "transactionVersion": 1,
            "stateVersion": 1,
        }

    async def getStorage(self, key, hash=None):
        try:
            storage_function = next(
                value
                for prefix, value in STORAGE_KEYS.items()
                if key.startswith(prefix)
            )
        except StopIteration:
            raise NotImplementedError(f"Unknown Storage: {key}")

        if storage_function == "System.Events":
            cls = self.substrate._registry.create_scale_object("scale_info::19")

            async with self.substrate.db_session() as session:
                events = await session.scalars(
                    sqlalchemy.select(db.SystemEvent).filter_by(
                        block=db.Block.query(hash).with_only_columns(db.Block.number).scalar_subquery(),
                    ),
                )

            return "0x" + cls.encode([
                {
                    "phase": {
                        "ApplyExtrinsic": i,
                    },
                    "event": {
                        event.module_id: {
                            event.event_id: {
                                "dispatch_error": {
                                    "Unavailable": None,
                                },
                                "dispatch_info": {
                                    "weight": {
                                        "ref_time": 0,
                                        "proof_size": 0,
                                    },
                                    "class": "Normal",
                                    "pays_fee": "No",
                                },
                            },
                        }
                    },
                    "extrinsic_idx": i,
                    "topics": [],
                }
                for i, event in enumerate(events)    # block.extrinsics
            ]).data.hex()

        if storage_function == "SubtensorModule.NeuronCertificates":
            key_type_string = ['[u8; 0]', 'scale_info::39', '[u8; 16]', 'scale_info::0']
            key_type = self.substrate._registry.create_scale_object(
                f"({', '.join(key_type_string)})",
            )
            key_wo = key.removeprefix("0x658faa385070e074c85bf6b568cf0555805f1c4b7f54d8f4208070bfc777e2db")
            key = key_type.decode(scalecodec.ScaleBytes("0x" + key_wo))

            key = (key[1], key[3])
            netuid = key[0]
            hotkey = scalecodec.utils.ss58.ss58_encode(key[1][2:])

            async with self.substrate.db_session() as session:
                certificate = await session.scalar(
                    db.NeuronCertificate.get(
                        netuid=netuid,
                        hotkey=hotkey,
                    ),
                )
            
            if not certificate:
                return "0x00"

            cls = self.substrate._registry.create_scale_object("scale_info::184")

            return "0x" + cls.encode({
                "public_key": certificate.public_key,
                "algorithm": certificate.algorithm,
            }).data.hex()

    async def call(self, name, bytes, hash=None):
        api, method = name.split("_", 1)
        api = self.substrate._apis[api]
        method = api["methods"][method]

        if bytes.startswith("0x"):
            bytes = bytes[2:]

        params_type = self.substrate._registry.create_scale_object(
            f"({', '.join(f"scale_info::{arg["type"]}" for arg in method["inputs"])})",
            data=scalecodec.ScaleBytes(bytearray.fromhex(bytes)),
            # metadata=self._metadata,
        )
        params = params_type.decode()

        # XXX list as 1st arg?
        if not isinstance(params, list):
            params = [params]

        try:
            api_obj = getattr(self.substrate, api["name"])
            method_obj = getattr(api_obj, method["name"])
        except AttributeError:
            raise NotImplementedError(f"RPC {name} not implemented")

        result = await method_obj(*params, block_hash=hash)
        return result
        result_type = self.substrate._registry.create_scale_object(
            f"scale_info::{method['output']}",
        )

        return "0x" + result_type.encode(result).data.hex()

    async def queryStorageAt(
        self,
        keys: list[str],
        hash=None,
    ):# -> list[StorageChangeSet]:
        async with self.substrate.db_session() as session:
            # TODO keys
            weights = await session.scalars(
                sqlalchemy.select(db.Weights).filter_by(
                    block=1,  # TODO
                    netuid=1,  # TODO
                ),
            )

            return [
                {
                    "block": "0xe9670fb7fa6fbfd6cad6010501a3b4780f200a9977c802f1eac15bf935cfba48",
                    "changes": [
                        [
                            self._storage_key(
                                "SubtensorModule",
                                "Weights",
                                [weights.netuid, weights.validator],
                            ),
                            "0x" + self.substrate._registry.create_scale_object("scale_info::182").encode([
                                (
                                    weights.uid,
                                    weights.weight,
                                ),
                            ]).data.hex(),
                        ]
                        for weights in weights
                    ],
                },
            ]   

    # TODO Shared
    # TODO pallet storage_function are strings now!
    def _storage_key(self, pallet, storage_function, params):
        pallet = self.substrate._metadata.get_metadata_pallet(pallet)
        storage_function = pallet.get_storage_function(storage_function)

        param_types = storage_function.get_params_type_string()
        param_hashers = storage_function.get_param_hashers()

        storage_hash = xxh128(pallet.value["storage"]["prefix"].encode()) + xxh128(
            storage_function.value["name"].encode()
        )

        if param_types:
            params = tuple(
                self.substrate._registry.create_scale_object(
                    param_type,
                ).encode(
                    param_value,
                )
                for param_value, param_type in zip(params, param_types)
            )

            for param_value, param_hash in zip(params, param_hashers):
                try:
                    hasher = HASHERS[param_hash]
                except KeyError:
                    raise NotImplementedError(param_hash)

                storage_hash += hasher.function(param_value.data)

        return f"0x{storage_hash.hex()}"
