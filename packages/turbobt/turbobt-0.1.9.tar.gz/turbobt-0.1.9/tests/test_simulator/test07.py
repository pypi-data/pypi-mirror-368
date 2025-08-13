import turbobt
import pprint
import scalecodec
import bittensor_wallet

from turbobt.substrate._hashers import HASHERS


async def main2():
    async with turbobt.Bittensor() as bt:
        # v = await bt.subtensor.rpc(
        #     "SubtensorModule.get_yuma3_on",
        #     {
        #         "netuid": 12,
        #     }
        # )
        v2 = await bt.subtensor.state.getStorage("SubtensorModule.Yuma3On", 2)
        sub = await bt.subtensor.state.subscribeStorage(["System.Events"])
        async for event in sub:
            print(event)
        #     pallet, storage_function = bt.subtensor["System", "Events"]
        #     param_types = storage_function.get_params_type_string()
        #     param_hashers = storage_function.get_param_hashers()

        #     key_type_string = []

        #     for param_hasher, param_type in zip(param_hashers, param_types):
        #         try:
        #             hasher = HASHERS[param_hasher]
        #         except KeyError:
        #             raise NotImplementedError(param_hasher)

        #         key_type_string.append(f"[u8; {hasher.hash_length}]")
        #         key_type_string.append(param_type)

        #     key_type = bt.subtensor._registry.create_scale_object(
        #         f"({', '.join(key_type_string)})",
        #     )
        #     value_type = bt.subtensor._registry.create_scale_object(
        #         storage_function.get_value_type_string(),
        #     )
        #     prefix = bt.subtensor.state._storage_key(
        #         pallet,
        #         storage_function,
        #         [],
        #     )

        #     results = (
        #         (
        #             bytearray.fromhex(key.removeprefix(prefix)),
        #             bytearray.fromhex(value[2:]),
        #         )
        #         for key, value in event["changes"]
        #     )
        #     results = (
        #         (
        #             key_type.decode(
        #                 scalecodec.ScaleBytes(key),
        #             ),
        #             value_type.decode(
        #                 scalecodec.ScaleBytes(value),
        #             ),
        #         )
        #         for key, value in results
        #     )
        #     results = (
        #         v
        #         for key, value in results
        #         for v in value
        #     )
        #     for value in results:
        #         # pprint.pprint(value)
        #         if value["event_id"] in (
        #             "ExtrinsicSuccess",
        #             "ExtrinsicFailed",
        #         ):
        #             continue
        #         print(value["event_id"], value["event"]["attributes"])
        #     # print(list(results))

        # b = await bt.block(5858264).get()
        # print(await b.get_timestamp())
        # block_hash = await bt.subtensor.chain.getBlockHash(5858264)
        # block = await bt.subtensor.chain.getBlock(block_hash)
        # extrinsics = block["block"]["extrinsics"]
        # calls = [f'{e["call"]["call_module"]}_{e["call"]["call_function"]}' for e in extrinsics]
        # extrinsics = [
        #     extrinsic["call"]
        #     for extrinsic in extrinsics
        #     if extrinsic["call"]["call_module"] == "Multisig" and extrinsic["call"]["call_function"] == "as_multi"
        # ]

        # try:
        #     pprint.pprint(extrinsics[0])
        # except IndexError:
        #     pass
        # calls = [c for c in calls if c not in ("set_weights", "commit_crv3_weights", "add_stake_limit", "set_commitment")]
        # print(calls)
        events = await bt.subtensor.system.Events.get(
            block_hash="0x0e96a0ed9eddf4b401c5e4234c36c41834ffb82c606fd0d92bf68c99f0b8122c",
        )
        # events = await bt.subtensor.state.getStorage(
        #     "System.Events",
        #     # block_hash=block_hash,
        # )
        value = await bt.subtensor.state.getStorage(
            "SubtensorModule.NetworkRateLimit",
            # block_hash=block_hash,
        )

        # assert value == 2628000
        print(value)

        e = await bt.subtensor.admin_utils.sudo_set_network_rate_limit(
            2000,
            wallet=bittensor_wallet.Wallet("alice", "default"),
        )
        await e.wait_for_finalization()


async def main():
    # wallet = bittensor_wallet.Wallet("luxor-validator", "default")
    wallet = bittensor_wallet.Wallet("alice", "default")

    async with turbobt.Bittensor(wallet=wallet) as bt:
    # async with turbobt.Bittensor("ws://localhost:9944", wallet=wallet) as bt:
        # subnet = bt.subnet(388)
        subnet = bt.subnet(12)
        # weights = await subnet.weights.fetch()
        commitments = await subnet.commitments.fetch()
        # neurons = await subnet.list_neurons()

        # await subnet.neurons.serve(
        #     ip="192.168.0.2",
        #     port=8000,
        # )

        # neuron = await subnet.get_neuron(wallet.hotkey.ss58_address)

        # print(neurons)

        await bt.subtensor.admin_utils.sudo_set_commit_reveal_weights_enabled(
            netuid=subnet.netuid,
            enabled=True,
            wallet=wallet,
        )

        # await subnet.weights.commit({
        #     0: 1.0,
        #     # 1: 0.8,
        # })

        for i in range(10):
            weights = await subnet.weights.fetch_pending()
            print(weights)
            # neuron = await bt.subtensor.neuron_info.get_neuron(
            #     netuid=2,
            #     uid=0,
            # )

            # print(neuron["weights"])

            await asyncio.sleep(0.1)


import asyncio

asyncio.run(main2())