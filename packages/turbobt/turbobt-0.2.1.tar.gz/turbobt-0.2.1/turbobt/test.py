tempo = 360
block = 1067
netuid = 13


def get_epoch_containing_block(block: int, netuid: int, tempo: int = 360) -> range:
    """
    Reimplementing the logic from subtensor's Rust function:
        pub fn blocks_until_next_epoch(netuid: u16, tempo: u16, block_number: u64) -> u64
    See https://github.com/opentensor/subtensor.

    See also: https://github.com/opentensor/bittensor/pull/2168/commits/9e8745447394669c03d9445373920f251630b6b8

    The beginning of an epoch is the first block when values like "dividends" are different
    (before an epoch they are constant for a full tempo).
    """
    assert tempo > 0

    interval = tempo + 1
    next_epoch = block + tempo - (block + netuid + 1) % interval

    if next_epoch == block:
        prev_epoch = next_epoch
        next_epoch = prev_epoch + interval
    else:
        prev_epoch = next_epoch - interval

    return range(prev_epoch, next_epoch)


def asd(netuid, tempo, block_number):
    netuid_plus_one = netuid + 1
    tempo_plus_one = tempo + 1
    adjusted_block = block_number + netuid_plus_one
    remainder = adjusted_block % tempo_plus_one

    block_number + tempo

    if remainder == tempo:
        remainder = -1

    return range(
        block_number - remainder - 1,
        block_number - remainder + tempo,
    )


print(get_epoch_containing_block(block, netuid, tempo))
print(asd(netuid, tempo, block))