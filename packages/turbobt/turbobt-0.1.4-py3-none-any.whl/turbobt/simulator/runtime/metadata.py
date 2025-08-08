import json


class Metadata:
    def __init__(self, substrate):
        self.substrate = substrate

    async def metadata_at_version(self, version, block_hash=None):
        with open("tests/test_substrate/data/metadata_at_version.json") as data:
            return json.load(data)
