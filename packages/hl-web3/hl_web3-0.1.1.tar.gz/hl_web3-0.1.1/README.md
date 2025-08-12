# hl-web3-py

A Python Web3 client library for interacting with the Hyperliquid DEX on both mainnet and testnet.

## Features

- **Trading Operations**: Place and cancel orders on Hyperliquid perpetual markets
- **Account Management**: Query positions, balances, and account information
- **Vault Operations**: Deposit and withdraw from HLP vaults
- **Staking & Delegation**: Stake HYPE tokens and delegate to validators
- **Spot Trading**: Transfer spot tokens and manage spot balances
- **Market Data**: Access real-time pricing, order book, and market information
- **Multi-Network Support**: Works with both Hyperliquid mainnet and testnet

## Installation

```bash
pip install hl-web3
```

For development:

```bash
git clone https://github.com/oneforalone/hl-web3-py
cd hl-web3-py
uv sync
```

## Quick Start

### Environment Setup

Create a `.env` file with your private key:

```bash
PRIVATE_KEY=your_private_key_here
```

### Basic Usage

```python
import asyncio
from hl_web3.info import Info
from hl_web3.exchange import Exchange
from hl_web3.utils.constants import HL_TESTNET_RPC_URL, SCALE_FACTOR
from hl_web3.utils.types import Tif

async def main():
    # Initialize info client (read-only)
    info = Info(HL_TESTNET_RPC_URL)

    # Initialize exchange client (requires private key)
    exchange = Exchange(HL_TESTNET_RPC_URL, "your_private_key")

    # Get market data
    btc_price = await info.get_mark_px(3)  # BTC perp asset ID
    print(f"BTC Mark Price: ${btc_price / SCALE_FACTOR}")

    # Place a limit order
    asset = 3  # BTC perp
    is_buy = True
    price = int(50000 * SCALE_FACTOR)  # $50,000
    size = int(0.001 * SCALE_FACTOR)   # 0.001 BTC
    reduce_only = False
    time_in_force = Tif.Gtc
    client_order_id = 12345

    tx = await exchange.place_order(
        asset, is_buy, price, size, reduce_only, time_in_force, client_order_id
    )
    print(f"Order placed: {tx}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Components

### Info Client

The `Info` class provides read-only access to market data and account information:

```python
from hl_web3.info import Info

info = Info("https://rpc.hyperliquid-testnet.xyz/evm")

# Market data
mark_price = await info.get_mark_px(asset_id)
oracle_price = await info.get_oracle_px(asset_id)
spot_price = await info.get_spot_px(spot_id)
best_bid_offer = await info.get_bbo(asset_id)

# Account information
position = await info.get_user_position(user_address, asset_id)
spot_balance = await info.get_user_spot_balance(user_address, spot_id)
vault_equity = await info.get_user_vault_equity(user_address, vault_address)
withdrawable = await info.get_user_withdrawable(user_address)

# Asset information
perp_info = await info.get_perp_asset_info(asset_id)
spot_info = await info.get_spot_info(spot_id)
token_info = await info.get_token_info(token_id)
```

### Exchange Client

The `Exchange` class enables trading and account management operations:

```python
from hl_web3.exchange import Exchange

exchange = Exchange("https://rpc.hyperliquid-testnet.xyz/evm", private_key)

# Trading
tx = await exchange.place_order(asset, is_buy, price, size, reduce_only, tif, cloid)
tx = await exchange.cancel_order_by_oid(asset, order_id)
tx = await exchange.cancel_order_by_cloid(asset, client_order_id)

# Vault operations
tx = await exchange.vault_transfer(vault_address, is_deposit, usd_amount)

# Staking
tx = await exchange.staking_deposit(hype_amount)
tx = await exchange.staking_withdraw(hype_amount)
tx = await exchange.token_delegate(validator_address, hype_amount, is_undelegate)

# Spot transfers
tx = await exchange.spot_send(destination_address, token_id, amount)
tx = await exchange.send_usd_class_transfer(amount, to_perp)

# API wallet management
tx = await exchange.add_api_wallet(api_address, name)
```

## Supported Networks

### Mainnet
- RPC URL: `https://rpc.hyperliquid.xyz/evm`
- Use `HL_RPC_URL` constant

### Testnet
- RPC URL: `https://rpc.hyperliquid-testnet.xyz/evm`
- Use `HL_TESTNET_RPC_URL` constant

### Connection Types
- HTTPS (recommended)
- WebSocket
- IPC (limited support)

## Data Types

The library includes comprehensive type definitions for all Hyperliquid data structures:

### Trading Types
- `ActionType`: Enum for different action types (LimitOrder, VaultTransfer, etc.)
- `Tif`: Time in Force options (Alo, Gtc, Ioc)
- `AssetType`: Perp or Spot assets

### Account Data
- `Position`: Perpetual position information
- `SpotBalance`: Spot token balances
- `UserVaultEquity`: Vault equity and lock information
- `Delegation`: Staking delegation details

### Market Data
- `PerpAssetInfo`: Perpetual asset metadata
- `SpotInfo`: Spot market information
- `TokenInfo`: Token contract details
- `Bbo`: Best bid/offer prices

## Constants and Scaling

### Price and Size Scaling
- `SCALE_FACTOR = 10**8`: Used for perpetual prices and sizes
- `USD_SCALE_FACTOR = 10**6`: Used for USD amounts

### Example Asset IDs (Testnet)
- BTC Perp: `3`
- BTC Spot: `50`
- BTC Token: `69`

## Testing

The library includes comprehensive tests covering all functionality:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_info.py      # Market data tests
pytest tests/test_exchange.py  # Trading tests
pytest tests/test_endpoint.py  # Connection tests
pytest tests/test_utils.py     # Utility tests
```

### Test Environment

Tests require a `.env` file with:
```bash
PRIVATE_KEY=your_testnet_private_key
```

Some tests are skipped by default due to balance requirements:
- Token delegation tests (require HYPE tokens)
- Staking tests (require HYPE tokens)

## Error Handling

The library provides proper error handling for common scenarios:

- Invalid asset IDs
- Insufficient balances
- Network connectivity issues
- Invalid action types

## Development

### Requirements
- Python 3.10+
- uv (for dependency management)
- web3.py 7.13.0+
- eth-abi 5.2.0+

### Setup
```bash
git clone https://github.com/oneforalone/hl-web3-py
cd hl-web3-py
uv sync
```

### Code Quality
The project uses:
- pre-commit hooks
- pytest for testing
- ruff for linting
- pytest-cov for coverage

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: https://github.com/oneforalone/hl-web3-py/issues
