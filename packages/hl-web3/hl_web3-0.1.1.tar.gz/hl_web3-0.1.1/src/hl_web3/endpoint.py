from logging import getLogger

from web3 import AsyncWeb3


class Endpoint:
    def __init__(self, rpc_url: str):
        if rpc_url.startswith("http"):
            provider = AsyncWeb3.AsyncHTTPProvider(rpc_url)
        elif rpc_url.startswith("ws"):
            provider = AsyncWeb3.WebSocketProvider(rpc_url)
        else:
            raise ValueError(f"Invalid RPC URL: {rpc_url}")

        self._w3 = AsyncWeb3(provider)  # type: ignore
        self.logger = getLogger("hl_web3.endpoint")

    async def _call(self, tx: dict):
        self.logger.debug(f"Eth call: {tx}")
        resp = await self._w3.eth.call(tx)  # type: ignore
        self.logger.debug(f"Eth call response: {resp.hex()}")
        return resp
