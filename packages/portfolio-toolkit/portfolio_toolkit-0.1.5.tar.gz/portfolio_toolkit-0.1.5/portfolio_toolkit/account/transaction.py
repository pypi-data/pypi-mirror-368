from dataclasses import dataclass
from datetime import date
from typing import List, Optional

import pandas as pd


@dataclass
class AccountTransaction:
    """
    Represents a transaction in an account.
    """

    transaction_date: date
    transaction_type: str
    amount: float
    description: Optional[str] = None

    def __post_init__(self):
        allowed_types = {"buy", "sell", "deposit", "withdrawal", "income"}
        if self.transaction_type not in allowed_types:
            raise ValueError(f"Invalid transaction type: {self.transaction_type}")

    @classmethod
    def to_list(cls, transactions: List["AccountTransaction"]) -> List[dict]:
        """Convert a list of AccountTransaction objects to a list of dictionaries."""
        if not transactions:
            return []

        data = []
        for tx in transactions:
            data.append(
                {
                    "date": tx.transaction_date,
                    "type": tx.transaction_type,
                    "amount": tx.amount,
                    "description": tx.description,
                }
            )

        return data

    @classmethod
    def to_dataframe(cls, transactions: List["AccountTransaction"]) -> pd.DataFrame:
        """Convert a list of AccountTransaction objects to a pandas DataFrame."""

        data = cls.to_list(transactions)
        return pd.DataFrame(data)

    def __repr__(self):
        return (
            f"AccountTransaction(date={self.transaction_date}, "
            f"type={self.transaction_type}, amount={self.amount}, "
            f"description={self.description})"
        )
