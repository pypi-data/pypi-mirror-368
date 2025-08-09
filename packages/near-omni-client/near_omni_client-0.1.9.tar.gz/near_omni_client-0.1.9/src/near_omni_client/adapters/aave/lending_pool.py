from typing import ClassVar

from web3 import Web3

from near_omni_client.networks import Network
from near_omni_client.wallets import Wallet


class LendingPool:
    """AAVE Lending Pool contract for managing deposits and withdrawals of assets."""

    # addresses obtained from https://aave.com/docs/resources/addresses
    contract_addresses: ClassVar[dict[Network, str]] = {
        Network.ETHEREUM_MAINNET: Web3.to_checksum_address(
            "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
        ),  # https://github.com/bgd-labs/aave-address-book/blob/main/src/AaveV3Ethereum.sol
        Network.ETHEREUM_SEPOLIA: Web3.to_checksum_address(
            "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951"
        ),  # https://github.com/bgd-labs/aave-address-book/blob/main/src/AaveV3Sepolia.sol
        Network.BASE_MAINNET: Web3.to_checksum_address(
            "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"
        ),  # https://github.com/bgd-labs/aave-address-book/blob/main/src/AaveV3Base.sol
        Network.BASE_SEPOLIA: Web3.to_checksum_address(
            "0x8bAB6d1b75f19e9eD9fCe8b9BD338844fF79aE27"
        ),  # https://github.com/bgd-labs/aave-address-book/blob/main/src/AaveV3BaseSepolia.sol
        Network.LOCALHOST: Web3.to_checksum_address(
            "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"  # we use base mainnet address for local fork testing
        ),
        Network.OPTIMISM_SEPOLIA: Web3.to_checksum_address(
            "0xb50201558B00496A145fE76f7424749556E326D8"  # same as sepolia
        ),
        Network.OPTIMISM_MAINNET: Web3.to_checksum_address(
            "0x794a61358D6845594F94dc1DB02A252b5b4814aD"  # same as mainnet
        ),
        Network.ARBITRUM_SEPOLIA: Web3.to_checksum_address(
            "0xBfC91D59fdAA134A4ED45f7B584cAf96D7792Eff"  # same as sepolia
        ),
        Network.ARBITRUM_MAINNET: Web3.to_checksum_address(
            "0x794a61358D6845594F94dc1DB02A252b5b4814aD"  # same as mainnet
        ),
    }

    abi = [
        {
            "name": "supply",
            "type": "function",
            "inputs": [
                {"name": "asset", "type": "address"},
                {"name": "amount", "type": "uint256"},
                {"name": "onBehalfOf", "type": "address"},
                {"name": "referralCode", "type": "uint16"},
            ],
            "outputs": [],
            "stateMutability": "public",
            "constant": False,
            "virtual": True,
            "payable": False,
        },
        {
            "name": "withdraw",
            "type": "function",
            "inputs": [
                {"name": "asset", "type": "address"},
                {"name": "amount", "type": "uint256"},
                {"name": "to", "type": "address"},
            ],
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "public",
            "constant": False,
            "virtual": True,
            "payable": False,
        },
        {
            "name": "getReserveData",
            "type": "function",
            "stateMutability": "view",
            "inputs": [{"internalType": "address", "name": "asset", "type": "address"}],
            "outputs": [
                {
                    "components": [
                        {
                            "internalType": "struct DataTypes.ReserveConfigurationMap",
                            "name": "configuration",
                            "type": "tuple",
                            "components": [
                                {"internalType": "uint256", "name": "data", "type": "uint256"}
                            ],
                        },
                        {"internalType": "uint128", "name": "liquidityIndex", "type": "uint128"},
                        {
                            "internalType": "uint128",
                            "name": "currentLiquidityRate",
                            "type": "uint128",
                        },
                        {
                            "internalType": "uint128",
                            "name": "variableBorrowIndex",
                            "type": "uint128",
                        },
                        {
                            "internalType": "uint128",
                            "name": "currentVariableBorrowRate",
                            "type": "uint128",
                        },
                        {
                            "internalType": "uint128",
                            "name": "currentStableBorrowRate",
                            "type": "uint128",
                        },
                        {"internalType": "uint40", "name": "lastUpdateTimestamp", "type": "uint40"},
                        {"internalType": "uint16", "name": "id", "type": "uint16"},
                        {"internalType": "address", "name": "aTokenAddress", "type": "address"},
                        {
                            "internalType": "address",
                            "name": "stableDebtTokenAddress",
                            "type": "address",
                        },
                        {
                            "internalType": "address",
                            "name": "variableDebtTokenAddress",
                            "type": "address",
                        },
                        {
                            "internalType": "address",
                            "name": "interestRateStrategyAddress",
                            "type": "address",
                        },
                        {"internalType": "uint128", "name": "accruedToTreasury", "type": "uint128"},
                        {"internalType": "uint128", "name": "unbacked", "type": "uint128"},
                        {
                            "internalType": "uint128",
                            "name": "isolationModeTotalDebt",
                            "type": "uint128",
                        },
                    ],
                    "internalType": "struct DataTypes.ReserveDataLegacy",
                    "name": "res",
                    "type": "tuple",
                }
            ],
        },
    ]
    interest_rate_strategy_abi = [
        {
            "name": "getOptimalUsageRatio",
            "type": "function",
            "inputs": [{"name": "reserve", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
        },
        {
            "name": "getVariableRateSlope1",
            "type": "function",
            "inputs": [{"name": "reserve", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
        },
        {
            "name": "getVariableRateSlope2",
            "type": "function",
            "inputs": [{"name": "reserve", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
        },
    ]

    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        },
    ]

    def __init__(self, network: Network, wallet: Wallet):
        self.network = network
        self.contract_address = self.contract_addresses.get(network)
        self.wallet = wallet

        if not self.contract_address:
            raise ValueError(f"Unsupported network: {network}")

        self.contract_address = Web3.to_checksum_address(self.contract_address)
        self.contract = Web3().eth.contract(
            address=self.contract_address, abi=self.abi
        )  # provider not needed here

    @staticmethod
    def get_address_for_network(network: Network) -> str:
        """Get the AAVE Lending Pool contract address for a specific network."""
        address = LendingPool.contract_addresses.get(network)
        if not address:
            raise ValueError(f"Unsupported network: {network}")
        return address

    def get_interest_rate(self, asset_address: str) -> float:
        """Return the current liquidity rate (APR %) for the given asset."""
        w3 = self.wallet.get_web3(self.network)
        contract = w3.eth.contract(address=self.contract_address, abi=self.abi)
        reserve_data = contract.functions.getReserveData(asset_address).call()
        # extract the liquidityRate from the reserve data
        # https://aave.com/docs/developers/smart-contracts/pool#view-methods-getreservedata-return-values
        liquidity_rate_ray = reserve_data[2]  # or 'currentLiquidityRate'
        # Convert from ray to %
        return liquidity_rate_ray / 1e27 * 100

    def get_slope(self, asset_address: str) -> float:
        """Return the correct supply elasticity slope (as %), based on current usage ratio."""
        w3 = self.wallet.get_web3(self.network)

        contract = w3.eth.contract(address=self.contract_address, abi=self.abi)

        # getReserveData
        reserve_data = contract.functions.getReserveData(asset_address).call()

        # extract the aToken, variableDebtToken and strategy address from the reserve data
        # https://aave.com/docs/developers/smart-contracts/pool#view-methods-getreservedata-return-values
        a_token = reserve_data[8]
        variable_debt_token = reserve_data[10]
        strategy_address = reserve_data[11]

        # get real balances
        a_token_contract = w3.eth.contract(address=a_token, abi=self.erc20_abi)
        debt_token_contract = w3.eth.contract(address=variable_debt_token, abi=self.erc20_abi)

        available_liquidity = a_token_contract.functions.balanceOf(self.contract_address).call()
        total_borrow = debt_token_contract.functions.totalSupply().call()

        # get strategy data
        strategy = w3.eth.contract(address=strategy_address, abi=self.interest_rate_strategy_abi)
        slope1_ray = strategy.functions.getVariableRateSlope1(asset_address).call()
        slope2_ray = strategy.functions.getVariableRateSlope2(asset_address).call()
        optimal_usage_ratio_ray = strategy.functions.getOptimalUsageRatio(asset_address).call()

        # determine which slope to use
        total_liquidity = available_liquidity + total_borrow
        usage_ratio = total_borrow / total_liquidity if total_liquidity > 0 else 0
        optimal = optimal_usage_ratio_ray / 1e27

        slope_ray = slope1_ray if usage_ratio <= optimal else slope2_ray
        return slope_ray / 1e27 * 100

    def get_supply_and_borrow(self, asset_address: str) -> tuple[int, int]:
        """Return the total supply and total borrow for a given asset.

        Returns:
            (total_supply, total_borrow): both in base units (e.g. wei)

        """
        w3 = self.wallet.get_web3(self.network)

        contract = w3.eth.contract(address=self.contract_address, abi=self.abi)
        reserve_data = contract.functions.getReserveData(asset_address).call()

        a_token = reserve_data[8]
        variable_debt_token = reserve_data[10]

        a_token_contract = w3.eth.contract(address=a_token, abi=self.erc20_abi)
        debt_token_contract = w3.eth.contract(address=variable_debt_token, abi=self.erc20_abi)

        available_liquidity = a_token_contract.functions.balanceOf(self.contract_address).call()
        total_borrow = debt_token_contract.functions.totalSupply().call()
        total_supply = available_liquidity + total_borrow

        return total_supply, total_borrow

    def supply(
        self,
        asset_address: str,
        amount: int,
        on_behalf_of: str | None = None,
        referral_code: int = 0,
        gas_limit: int = 1000000,
        wait: bool = True,
    ) -> str:
        """Supply assets to the AAVE protocol.

        Args:
            asset_address: Address of the asset to supply
            amount: Amount to supply in base units
            on_behalf_of: Address that will receive the aTokens (defaults to sender)
            referral_code: Code used to register the integrator (0 if none)
            gas_limit: Maximum gas to use
            wait: Whether to wait for transaction confirmation

        """
        if on_behalf_of is None:
            on_behalf_of = self.wallet.get_address()

        tx = self.contract.functions.supply(
            asset_address, amount, on_behalf_of, referral_code
        ).build_transaction(
            {
                "from": self.wallet.get_address(),
                "to": self.contract_address,
                "gas": gas_limit,
                "nonce": self.wallet.get_nonce(self.network),
                "chainId": self.wallet.get_chain_id(self.network),
                "maxFeePerGas": Web3.to_wei(2, "gwei"),
                "maxPriorityFeePerGas": Web3.to_wei(1, "gwei"),
            }
        )

        return self.wallet.sign_and_send_transaction(self.network, tx, wait)

    def withdraw(
        self,
        asset_address: str,
        amount: int,
        to_address: str | None = None,
        gas_limit: int = 1000000,
        wait: bool = True,
    ) -> str:
        """Withdraw assets from the AAVE protocol.

        Args:
            asset_address: Address of the asset to withdraw
            amount: Amount to withdraw in base units
            to_address: Address that will receive the withdrawn assets (defaults to sender)
            gas_limit: Maximum gas to use
            wait: Whether to wait for transaction confirmation

        """
        if to_address is None:
            to_address = self.wallet.get_address()

        tx = self.contract.functions.withdraw(asset_address, amount, to_address).build_transaction(
            {
                "from": self.wallet.get_address(),
                "to": self.contract_address,
                "gas": gas_limit,
                "nonce": self.wallet.get_nonce(self.network),
                "chainId": self.wallet.get_chain_id(self.network),
                "maxFeePerGas": Web3.to_wei(2, "gwei"),
                "maxPriorityFeePerGas": Web3.to_wei(1, "gwei"),
            }
        )

        return self.wallet.sign_and_send_transaction(self.network, tx, wait)
