import pytest


@pytest.mark.asyncio
async def test_get_block(substrate):
    block = await substrate.chain.getBlock()

    assert block == {
        "block": {
            "header": {
                "parentHash": "0x3fe8c77075d8194ed0bb7fd70d7b8cc91c12826c7f04df9f04c4235f0f6a966b",
                "number": 1,
                "stateRoot": "0x7e08c53c205b2d7766884935e96dab4cdd11e7055024603b42023894bec3c33d",
                "extrinsicsRoot": "0x937ca90d15a79bf046edeb94a02ccc65de71b7985e9bb215d5e31bd5fea3b962",
                "digest": {
                    "logs": [],
                },
            },
            "extrinsics": [],
        },
        "justifications": None,
    }


@pytest.mark.asyncio
async def test_get_block_get_by_hash(substrate):
    block = await substrate.chain.getBlock("0x3fe8c77075d8194ed0bb7fd70d7b8cc91c12826c7f04df9f04c4235f0f6a966b")

    assert block == {
        "block": {
            "header": {
                "parentHash": "0x3fe8c77075d8194ed0bb7fd70d7b8cc91c12826c7f04df9f04c4235f0f6a966b",
                "number": 1,
                "stateRoot": "0x7e08c53c205b2d7766884935e96dab4cdd11e7055024603b42023894bec3c33d",
                "extrinsicsRoot": "0x937ca90d15a79bf046edeb94a02ccc65de71b7985e9bb215d5e31bd5fea3b962",
                "digest": {
                    "logs": [],
                },
            },
            "extrinsics": [],
        },
        "justifications": None,
    }


@pytest.mark.asyncio
async def test_get_block_does_not_exist(substrate):
    block = await substrate.chain.getBlock("DOES_NOT_EXIST")

    assert block is None


@pytest.mark.asyncio
async def test_get_block_hash(substrate):
    block = await substrate.chain.getBlockHash(1)

    assert block == "0x3fe8c77075d8194ed0bb7fd70d7b8cc91c12826c7f04df9f04c4235f0f6a966b"

    block = await substrate.chain.getBlockHash(404)

    assert block is None


@pytest.mark.asyncio
async def test_get_header(substrate):
    header = await substrate.chain.getHeader()

    assert header == {
        "parentHash": "0x4545454545454545454545454545454545454545454545454545454545454545",
        "number": 1,
        "stateRoot": "0xfb9e07dd769d95a30ab04e1e801b1400df1261487cddab93dc64628ad95cec56",
        "extrinsicsRoot": "0xe5b4ae1cda6591fa8a8026bef64c5d712f7dc6c0dc700f74d1670139e55c220d",
        "digest": {
            "logs": [],
        },
    }