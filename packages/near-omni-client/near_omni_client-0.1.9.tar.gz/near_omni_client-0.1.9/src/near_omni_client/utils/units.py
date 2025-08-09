USDC_DECIMALS = 6


def to_usdc_units(amount: float) -> int:
    """Convert a float amount to USDC units (6 decimal places)."""
    return int(amount * (10**USDC_DECIMALS))
