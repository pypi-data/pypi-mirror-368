from dataclasses import dataclass
from enum import Enum


@dataclass
class Position:
    szi: int
    entry_ntl: int
    isolated_raw_usd: int
    leverage: int
    is_isolated: bool


@dataclass
class SpotBalance:
    total: int
    hold: int
    entry_ntl: int


@dataclass
class UserVaultEquity:
    equity: int
    locked_until_timestamp: int


@dataclass
class Delegation:
    validator: str
    amount: int
    locked_until_timestamp: int


@dataclass
class DelegatorSummary:
    delegated: int
    undelegated: int
    total_pending_withdrawal: int
    n_pending_withdrawals: int


@dataclass
class PerpAssetInfo:
    coin: str
    margin_table_id: int
    sz_decimals: int
    max_leverage: int
    only_isolated: bool


@dataclass
class SpotInfo:
    name: str
    tokens: list[int]

    def __post_init__(self):
        assert len(self.tokens) == 2, (
            "SpotInfo.tokens length must be 2"
        )  # prama: no cover


@dataclass
class TokenInfo:
    name: str
    spots: list[int]
    deployer_trading_fee_share: int
    deployer: str
    evm_contract: str
    sz_decimals: int
    wei_decimals: int
    evm_extra_wei_decimals: int


@dataclass
class UserBalance:
    user: str
    balance: int


@dataclass
class TokenSupply:
    max_supply: int
    total_supply: int
    circulating_supply: int
    future_emissions: int
    non_circulating_user_balances: list[UserBalance]


@dataclass
class Bbo:
    bid: int
    ask: int


@dataclass
class AccountMarginSummary:
    account_value: int
    margin_used: int
    ntl_pos: int
    raw_usd: int


class ActionType(Enum):
    LimitOrder = 1
    VaultTransfer = 2
    TokenDelegate = 3
    StakingDeposit = 4
    StakingWithdraw = 5
    SpotSend = 6
    USDClassTransfer = 7
    FinalizeEVMContract = 8
    AddAPIWallet = 9
    CancelOrderByOid = 10
    CancelOrderByCloid = 11


class Tif(Enum):
    Alo = 1
    Gtc = 2
    Ioc = 3


class AssetType(str, Enum):
    PERP = "perp"
    SPOT = "spot"


class FinalizeEvmContractVariant(Enum):
    Create = 1
    FirstStorageSlot = 2
    CustomStorageSlot = 3
