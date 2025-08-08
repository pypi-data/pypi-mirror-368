"""
Transaction-related tools for the Crypto.com developer platform.
"""

from crypto_com_developer_platform_client import Transaction
from langchain_core.tools import tool


@tool
def get_transactions_by_address(address: str, startBlock: int, endBlock: int, session: str = "", limit: str = "20") -> str:
    """
    Get transactions associated with a specific blockchain address.

    This function retrieves a list of transactions for the specified blockchain
    address from the Crypto.com developer platform within a specified block range.

    Args:
        address (str): The blockchain address to query (CronosIds with the `.cro` suffix are supported).
        startBlock (int): The starting block number to get transactions from. The maximum range is 10,000 blocks.
        endBlock (int): The ending block number to get transactions to. The maximum range is 10,000 blocks.
        session (str, optional): Session identifier for pagination. Defaults to "".
        limit (str, optional): Maximum number of transactions to return. Defaults to "20".

    Returns:
        str: A formatted string containing the list of transactions.

    Example:
        >>> transactions = get_transactions_by_address("0x123...", 1000000, 1005000)
        >>> print(transactions)
        Transactions for address 0x123...: {...}
    """
    transactions = Transaction.get_transactions_by_address(
        address=address,
        startBlock=startBlock,
        endBlock=endBlock,
        session=session,
        limit=limit
    )
    return f"Transactions for address {address}: {transactions}"


@tool
def get_transaction_by_hash(hash: str) -> str:
    """
    Fetch transaction details using a transaction hash.

    This function retrieves transaction details for the specified hash
    from the Crypto.com developer platform.

    Args:
        hash (str): The hash of the transaction to retrieve.

    Returns:
        str: A formatted string containing the transaction details.

    Example:
        >>> transaction_details = get_transaction_by_hash("0xhash...")
        >>> print(transaction_details)
        Transaction Details: {...}
    """
    transaction = Transaction.get_transaction_by_hash(hash)
    return f"Transaction Details: {transaction}"


@tool
def get_transaction_status(hash: str) -> str:
    """
    Get the current status of a transaction.

    This function retrieves the status of a transaction using its hash
    from the Crypto.com developer platform.

    Args:
        hash (str): The hash of the transaction to check.

    Returns:
        str: A formatted string containing the transaction status.

    Example:
        >>> status = get_transaction_status("0xhash...")
        >>> print(status)
        Transaction Status for 0xhash...: {...}
    """
    status = Transaction.get_transaction_status(hash)
    return f"Transaction Status for {hash}: {status}"
