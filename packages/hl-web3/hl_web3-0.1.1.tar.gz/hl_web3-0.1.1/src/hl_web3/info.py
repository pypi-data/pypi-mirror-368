from logging import getLogger

from eth_abi import abi

import hl_web3.utils.constants as constants
from hl_web3.utils.types import (
    Bbo,
    Position,
    SpotInfo,
    AssetType,
    TokenInfo,
    Delegation,
    SpotBalance,
    TokenSupply,
    PerpAssetInfo,
    UserVaultEquity,
    DelegatorSummary,
    AccountMarginSummary,
)

from .endpoint import Endpoint
from .utils.abi_types import (
    BboABI,
    PositionABI,
    SpotInfoABI,
    TokenInfoABI,
    DelegationsABI,
    SpotBalanceABI,
    TokenSupplyABI,
    PerpAssetInfoABI,
    UserVaultEquityABI,
    DelegatorSummaryABI,
    AccountMarginSummaryABI,
)


class Info(Endpoint):
    def __init__(self, rpc_url: str):
        super().__init__(rpc_url)
        self.logger = getLogger("hl_web3.info")

    async def get_user_position(self, user: str, asset: int):
        data = abi.encode(["address", "uint16"], [user, asset])
        tx = {"to": constants.HL_POSITION, "data": data}
        resp = await self._call(tx)
        (pos,) = abi.decode([PositionABI], resp)
        return Position(*pos)

    async def get_user_spot_balance(self, user: str, token: int):
        data = abi.encode(["address", "uint64"], [user, token])
        tx = {"to": constants.HL_SPOT_BALANCE, "data": data}
        resp = await self._call(tx)
        (balance,) = abi.decode([SpotBalanceABI], resp)
        return SpotBalance(*balance)

    async def get_user_vault_equity(self, user: str, vault: str):
        data = abi.encode(["address", "address"], [user, vault])
        tx = {"to": constants.HL_VAULT_EQUITY, "data": data}
        resp = await self._call(tx)
        (equity,) = abi.decode([UserVaultEquityABI], resp)
        return UserVaultEquity(*equity)

    async def get_user_withdrawable(self, user: str):
        data = abi.encode(["address"], [user])
        tx = {"to": constants.HL_WITHDRAWABLE, "data": data}
        resp = await self._call(tx)
        (amount,) = abi.decode(["uint64"], resp)

        return amount / constants.USD_SCALE_FACTOR

    async def get_user_delegations(self, user: str):
        data = abi.encode(["address"], [user])
        tx = {"to": constants.HL_DELEGATIONS, "data": data}
        resp = await self._call(tx)

        (delegations,) = abi.decode([DelegationsABI], resp)

        return [Delegation(*delegation) for delegation in delegations]

    async def get_user_delegator_summary(self, user: str):
        data = abi.encode(["address"], [user])
        tx = {"to": constants.HL_DELEGATOR_SUMMARY, "data": data}
        resp = await self._call(tx)
        (summary,) = abi.decode([DelegatorSummaryABI], resp)
        return DelegatorSummary(*summary)

    async def get_mark_px(self, asset: int):
        data = abi.encode(["uint32"], [asset])
        tx = {"to": constants.HL_MARK_PX, "data": data}
        resp = await self._call(tx)
        (px,) = abi.decode(["uint64"], resp)

        scale_factor = await self.get_asset_scale_factor(asset, AssetType.PERP)

        return px / scale_factor

    async def get_oracle_px(self, asset: int):
        data = abi.encode(["uint32"], [asset])
        tx = {"to": constants.HL_ORACLE_PX, "data": data}
        resp = await self._call(tx)
        (px,) = abi.decode(["uint64"], resp)

        scale_factor = await self.get_asset_scale_factor(asset, AssetType.PERP)

        return px / scale_factor

    async def get_spot_px(self, asset: int):
        data = abi.encode(["uint32"], [asset])
        tx = {"to": constants.HL_SPOT_PX, "data": data}
        resp = await self._call(tx)
        (px,) = abi.decode(["uint64"], resp)

        scale_factor = await self.get_asset_scale_factor(asset, AssetType.SPOT)

        return px / scale_factor

    async def get_block_number(self):
        tx = {"to": constants.HL_L1_BLOCK_NUMBER, "data": bytes()}
        resp = await self._call(tx)
        (blk_number,) = abi.decode(["uint64"], resp)
        return blk_number

    async def get_perp_asset_info(self, perp: int):
        data = abi.encode(["uint32"], [perp])
        tx = {"to": constants.HL_PERP_ASSET_INFO, "data": data}
        resp = await self._call(tx)
        (perp_asset,) = abi.decode([PerpAssetInfoABI], resp)
        return PerpAssetInfo(*perp_asset)

    async def get_spot_info(self, spot: int):
        data = abi.encode(["uint32"], [spot])
        tx = {"to": constants.HL_SPOT_INFO, "data": data}
        resp = await self._call(tx)
        (spot_info,) = abi.decode([SpotInfoABI], resp)
        return SpotInfo(*spot_info)

    async def get_token_info(self, token: int):
        data = abi.encode(["uint32"], [token])
        tx = {"to": constants.HL_TOKEN_INFO, "data": data}
        resp = await self._call(tx)
        (token_info,) = abi.decode([TokenInfoABI], resp)
        return TokenInfo(*token_info)

    async def get_token_supply(self, token: int):
        data = abi.encode(["uint32"], [token])
        tx = {"to": constants.HL_TOKEN_SUPPLY, "data": data}
        resp = await self._call(tx)
        (supply,) = abi.decode([TokenSupplyABI], resp)
        return TokenSupply(*supply)

    async def get_bbo(self, asset: int):
        data = abi.encode(["uint32"], [asset])
        tx = {"to": constants.HL_BBO, "data": data}
        resp = await self._call(tx)
        (bbo,) = abi.decode([BboABI], resp)
        return Bbo(*bbo)

    async def get_user_margin_summary(self, dex: int, user: str):
        data = abi.encode(["uint32", "address"], [dex, user])
        tx = {"to": constants.HL_ACCOUNT_MARGIN_SUMMARY, "data": data}
        resp = await self._call(tx)
        (summary,) = abi.decode([AccountMarginSummaryABI], resp)
        return AccountMarginSummary(*summary)

    async def is_core_user(self, user: str):
        data = abi.encode(["address"], [user])
        tx = {"to": constants.HL_CORE_USER, "data": data}
        resp = await self._call(tx)
        (is_core_user,) = abi.decode(["bool"], resp)
        return is_core_user

    async def get_asset_scale_factor(self, asset: int, asset_type: AssetType):
        # based on https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interacting-with-hypercore#read-precompiles
        if asset_type == AssetType.PERP:
            perp_asset = await self.get_perp_asset_info(asset)
            exponent = 6 - perp_asset.sz_decimals
        elif asset_type == AssetType.SPOT:
            spot_info = await self.get_spot_info(asset)
            token_id, _ = spot_info.tokens
            token_info = await self.get_token_info(token_id)
            exponent = 8 - token_info.sz_decimals
        else:  # pragma: no cover
            raise ValueError(f"Invalid asset type: {asset_type}")

        return 10**exponent
