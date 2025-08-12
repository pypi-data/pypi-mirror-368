import scalecodec.utils.ss58

from turbobt.simulator import db


class SubnetInfoRuntimeApi:
    def __init__(self, substrate):
        self.substrate = substrate

    async def get_dynamic_info(
        self,
        netuid: int,
        block_hash=None,
    ):
        async with self.substrate.db_session() as session:
            subnet = await session.scalar(
                db.Subnet.get(netuid, block_hash),
            )

        if not subnet:
            return None

        return {
            "subnet_name": subnet.name.encode(),
            "token_symbol": subnet.token_symbol.encode(),
            "owner_coldkey": "0x" + scalecodec.utils.ss58.ss58_decode(subnet.owner_coldkey),
            "owner_hotkey": "0x" + scalecodec.utils.ss58.ss58_decode(subnet.owner_hotkey),
            "tempo": subnet.tempo,
            "subnet_identity": subnet.identity,
        }

    async def get_subnet_hyperparams(self, subnet: int, block_hash: str | None):
        async with self.substrate.db_session() as session:
            subnet_hyperparams = await session.scalar(
                db.SubnetHyperparams.get(netuid=subnet, block=block_hash)
            )

        if not subnet_hyperparams:
            return None

        return {
            "activity_cutoff": subnet_hyperparams.activity_cutoff,
            "adjustment_alpha": subnet_hyperparams.adjustment_alpha,
            "adjustment_interval": subnet_hyperparams.adjustment_interval,
            "alpha_high": subnet_hyperparams.alpha_high,
            "alpha_low": subnet_hyperparams.alpha_low,
            "bonds_moving_avg": subnet_hyperparams.bonds_moving_avg,
            "commit_reveal_period": subnet_hyperparams.commit_reveal_period,
            "commit_reveal_weights_enabled": subnet_hyperparams.commit_reveal_weights_enabled,
            "difficulty": subnet_hyperparams.difficulty,
            "immunity_period": subnet_hyperparams.immunity_period,
            "kappa": subnet_hyperparams.kappa,
            "liquid_alpha_enabled": subnet_hyperparams.liquid_alpha_enabled,
            "max_burn": subnet_hyperparams.max_burn,
            "max_difficulty": subnet_hyperparams.max_difficulty,
            "max_regs_per_block": subnet_hyperparams.max_regs_per_block,
            "max_validators": subnet_hyperparams.max_validators,
            "max_weights_limit": subnet_hyperparams.max_weights_limit,
            "min_allowed_weights": subnet_hyperparams.min_allowed_weights,
            "min_burn": subnet_hyperparams.min_burn,
            "min_difficulty": subnet_hyperparams.min_difficulty,
            "registration_allowed": subnet_hyperparams.registration_allowed,
            "rho": subnet_hyperparams.rho,
            "serving_rate_limit": subnet_hyperparams.serving_rate_limit,
            "target_regs_per_interval": subnet_hyperparams.target_regs_per_interval,
            "tempo": subnet_hyperparams.tempo,
            "weights_rate_limit": subnet_hyperparams.weights_rate_limit,
            "weights_version": subnet_hyperparams.weights_version,
        }
