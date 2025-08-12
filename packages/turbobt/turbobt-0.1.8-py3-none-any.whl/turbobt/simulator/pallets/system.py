from turbobt.simulator.pallets._base import Pallet


class System(Pallet):
    async def accountNextIndex(self, account):
        return 1
