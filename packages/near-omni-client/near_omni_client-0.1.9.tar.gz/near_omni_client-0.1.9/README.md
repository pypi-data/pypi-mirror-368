# near-omni-client

**near-omni-client** is a modular Python library to develop cross chain applications using NEAR's [Chain Signatures].

## Features

- ✅ Wallet abstraction for Ethereum and NEAR
- ✅ Pluggable signing system (MPC via chain signatures, local signing for NEAR and Ethereum)
- ✅ NEAR JSON-RPC API
- ✅ Defi protocol adapters (Aave, CCTP)
- ✅ Transaction crafting and query builders 
- ✅ Provider factory for mainnet and testnet
- ✅ Async-ready, testable, and production-grade structure

## 📦 Modules

- `wallet` - Wallets per chain (EthereumWallet, NearWallet)
- `signers` – Pluggable signer implementations (MPC, local NEAR, local Ethereum)
- `json_rpc` – Low-level JSON-RPC interface
- `wallets` – Chain-safe wallet abstraction
- `adapters` – Protocol adapters (USDC, Aave)
- `providers` – RPC provider factories (Alchemy, FastNEAR)
- `transactions` – Transaction and query builders
- `crypto` - Crypto modules to work with NEAR cryptography
- `utils` - Conversion utilities
- `chain_signatures` - Chain signatures utilities for address derivation

## Concepts

### 🔑 Wallets
Abstractions over per-chain accounts that can build, sign and send transactions. They are signer-agnostic and compatible with NEAR and Ethereum.

### 🔐 Signers
Responsible for producing valid cryptographic signatures, either locally, via MPC, or remote signer APIs. Fully pluggable.

### 📡 RPC
Low-level JSON-RPC client, abstracted via a `ProviderFactory` to switch between testnet, mainnet, or localnet with ease.

## Architecture

<!-- TODO: Include architecture's diagram -->

## Getting Started

Install the latest version of `near-omni-client` by running:

```bash
$ pip install near-omni-client

# or if using uv

$ uv add near-omni-client
```

Create a NEAR account and get your private key using the [NEAR CLI].

## Contributing

If you are thinking about contributing to the **near-omni-client**, first of all thanks a lot ! We would love your contribution ! 

To understand the process for contributing, see [CONTRIBUTING.md].

<!-- REFERENCES -->
[Chain Signatures]: https://docs.near.org/chain-abstraction/chain-signatures
[CONTRIBUTING.md]: ./contributing.md




