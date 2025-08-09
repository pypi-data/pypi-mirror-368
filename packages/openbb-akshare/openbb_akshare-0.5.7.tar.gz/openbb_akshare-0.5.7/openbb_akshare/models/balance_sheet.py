"""AKShare Balance Sheet Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class AKShareBalanceSheetQueryParams(BalanceSheetQueryParams):
    """AKShare Balance Sheet Query.

    Source: https://akshare.akfamily.xyz/data/stock/stock.html#id180
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[int] = Field(
        default=5,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
        le=5,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )


class AKShareBalanceSheetData(BalanceSheetData):
    """AKShare Balance Sheet Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "totalEquity": "TOTAL_EQUITY",
        "totalDebt": "TOTAL_LIABILITIES",
        "totalAssets": "TOTAL_ASSETS"
    }

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class AKShareBalanceSheetFetcher(
    Fetcher[
        AKShareBalanceSheetQueryParams,
        list[AKShareBalanceSheetData],
    ]
):
    """AKShare Balance Sheet Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> AKShareBalanceSheetQueryParams:
        """Transform the query parameters."""
        return AKShareBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareBalanceSheetQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the AKShare endpoints."""
        # pylint: disable=import-outside-toplevel
        em_df = get_data(query.symbol, query.period, query.use_cache)

        return em_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareBalanceSheetQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AKShareBalanceSheetData]:
        """Transform the data."""
        return [AKShareBalanceSheetData.model_validate(d) for d in data]

def get_data(symbol: str, period: str = "annual", use_cache: bool = True) -> pd.DataFrame:
    from openbb_akshare import project_name
    from mysharelib.blob_cache import BlobCache
    cache = BlobCache(table_name="balance_sheet", project=project_name)
    return cache.load_cached_data(symbol, period, use_cache, get_ak_data)

def get_ak_data(symbol: str, period: str = "annual", api_key : Optional[str] = "") -> pd.DataFrame:
    import akshare as ak
    from openbb_akshare.utils.helpers import normalize_symbol
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    symbol_em = f"{market}{symbol_b}"

    if period == "annual":
        return ak.stock_balance_sheet_by_yearly_em(symbol=symbol_em)
    elif period == "quarter":
        return ak.stock_balance_sheet_by_report_em(symbol=symbol_em)
    else:
        raise ValueError("Invalid period. Please use 'annual' or 'quarter'.")