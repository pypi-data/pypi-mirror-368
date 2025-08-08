"""
Contract-related tools for the Crypto.com developer platform.
"""

from crypto_com_developer_platform_client import Contract
from langchain_core.tools import tool


@tool
def get_contract_abi(contract_address: str) -> str:
    """
    Get the ABI for a smart contract.

    This function retrieves the ABI for a specified smart contract
    from the Crypto.com developer platform.

    Args:
        contract_address (str): The address of the smart contract.

    Returns:
        str: A formatted string containing the ABI of the smart contract.

    Example:
        >>> abi = get_contract_abi("0x123...")
        >>> print(abi)
        ABI for contract 0x123...: {...}
    """
    abi = Contract.get_contract_abi(contract_address)
    return f"ABI for contract {contract_address}: {abi}"
