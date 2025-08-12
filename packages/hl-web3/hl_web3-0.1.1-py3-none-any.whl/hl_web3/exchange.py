from logging import getLogger

from web3 import Web3
from eth_abi import abi
from eth_account import Account

from hl_web3.utils.miscs import load_abi, get_raw_action
from hl_web3.utils.constants import HL_CORE_WRITER

from .endpoint import Endpoint
from .utils.types import Tif, ActionType, FinalizeEvmContractVariant


class Exchange(Endpoint):
    def __init__(self, rpc_url: str, private_key: str):
        super().__init__(rpc_url)
        self.account = Account.from_key(private_key)
        self.core_writer = self._w3.eth.contract(
            address=Web3.to_checksum_address(HL_CORE_WRITER),
            abi=load_abi("CoreWriter"),
        )
        self.logger = getLogger("hl_web3.exchange")

    async def _send_raw_action(self, action_type: ActionType, action: bytes):
        raw_action = get_raw_action(action_type, action)

        self.logger.debug(f"Sending raw action: {raw_action.hex()}")

        data = self.core_writer.encode_abi("sendRawAction", args=[raw_action])
        basic_tx = {
            "to": HL_CORE_WRITER,
            "data": data,
            "from": self.account.address,
        }
        tx = {
            **basic_tx,
            "gas": await self._w3.eth.estimate_gas(basic_tx),  # type: ignore
            "gasPrice": await self._w3.eth.gas_price,
            "nonce": await self._w3.eth.get_transaction_count(
                self.account.address
            ),
            "chainId": await self._w3.eth.chain_id,
        }
        signed_tx = self._w3.eth.account.sign_transaction(tx, self.account.key)

        self.logger.debug(f"Sending tx: {signed_tx.raw_transaction.hex()}")

        tx_hash = await self._w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )
        return tx_hash.hex()

    # action 1
    # Cloid encoding: 0 means no cloid, otherwise uses the number as the cloid. Px and sz should be sent as 10^8 * the human readable value
    async def place_order(
        self,
        asset: int,
        is_buy: bool,
        px: int,
        sz: int,
        ro: bool,
        tif: Tif,
        cloid: int = 0,
    ):
        action = abi.encode(
            ["uint32", "bool", "uint64", "uint64", "bool", "uint8", "uint128"],
            [asset, is_buy, px, sz, ro, tif.value, cloid],
        )
        return await self._send_raw_action(ActionType.LimitOrder, action)

    # action 2
    async def vault_transfer(self, vault: str, is_deposit: bool, usd: int):
        action = abi.encode(
            ["address", "bool", "uint64"], [vault, is_deposit, usd]
        )
        return await self._send_raw_action(ActionType.VaultTransfer, action)

    # action 3
    async def token_delegate(
        self, validator: str, amount: int, is_undelegate: bool
    ):
        action = abi.encode(
            ["address", "uint64", "bool"], [validator, amount, is_undelegate]
        )
        return await self._send_raw_action(ActionType.TokenDelegate, action)

    # action 4
    async def staking_deposit(self, amount: int):
        action = abi.encode(["uint64"], [amount])
        return await self._send_raw_action(ActionType.StakingDeposit, action)

    # action 5
    async def staking_withdraw(self, amount: int):
        action = abi.encode(["uint64"], [amount])
        return await self._send_raw_action(ActionType.StakingWithdraw, action)

    # action 6
    async def spot_send(self, dest: str, token: int, amount: int):
        action = abi.encode(
            ["address", "uint64", "uint64"], [dest, token, amount]
        )
        return await self._send_raw_action(ActionType.SpotSend, action)

    # action 7
    async def send_usd_class_transfer(self, ntl: int, to_perp: bool):
        action = abi.encode(["uint64", "bool"], [ntl, to_perp])
        return await self._send_raw_action(ActionType.USDClassTransfer, action)

    # action 8
    # status: 1 for Create, 2 for FirstStorageSlot, 3 for CustomStorageSlot. If Create variant, then createNonce input argument is used.
    async def finalize_evm_contract(
        self,
        token: int,
        variant: FinalizeEvmContractVariant,
        create_nonce: int = 0,
    ):
        if variant == FinalizeEvmContractVariant.Create:
            assert create_nonce > 0, (
                "create_nonce must be greater than 0 for Create variant"
            )

        action = abi.encode(
            ["uint64", "uint8", "uint64"], [token, variant.value, create_nonce]
        )
        return await self._send_raw_action(
            ActionType.FinalizeEVMContract, action
        )

    # action 9
    # If the API wallet name is empty then this becomes the main API wallet / agent
    async def add_api_wallet(self, wallet: str, name: str):
        action = abi.encode(["address", "string"], [wallet, name])
        return await self._send_raw_action(ActionType.AddAPIWallet, action)

    # action 10
    async def cancel_order_by_oid(self, asset: int, oid: int):
        action = abi.encode(["uint32", "uint64"], [asset, oid])
        return await self._send_raw_action(ActionType.CancelOrderByOid, action)

    # action 11
    async def cancel_order_by_cloid(self, asset: int, cloid: int):
        action = abi.encode(["uint32", "uint128"], [asset, cloid])
        return await self._send_raw_action(
            ActionType.CancelOrderByCloid, action
        )
