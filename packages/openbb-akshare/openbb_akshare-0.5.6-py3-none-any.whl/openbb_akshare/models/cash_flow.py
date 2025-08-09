"""AKShare Cash Flow Statement Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class AKShareCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """AKShare Cash Flow Statement Query.

    Source: https://finance.yahoo.com/
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


class AKShareCashFlowStatementData(CashFlowStatementData):
    """AKShare Cash Flow Statement Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "reported_currency": "CURRENCY",
    }

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class AKShareCashFlowStatementFetcher(
    Fetcher[
        AKShareCashFlowStatementQueryParams,
        list[AKShareCashFlowStatementData],
    ]
):
    """AKShare Cash Flow Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> AKShareCashFlowStatementQueryParams:
        """Transform the query parameters."""
        return AKShareCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareCashFlowStatementQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the AKShare endpoints."""
        # pylint: disable=import-outside-toplevel
        em_df = get_data(query.symbol, query.period, query.use_cache)

        return em_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareCashFlowStatementQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AKShareCashFlowStatementData]:
        """Transform the data."""
        return [AKShareCashFlowStatementData.model_validate(d) for d in data]

def get_data(symbol: str, period: str = "annual", use_cache: bool = True) -> pd.DataFrame:
    from openbb_akshare import project_name
    from mysharelib.blob_cache import BlobCache

    cache = BlobCache(table_name="cash_flow", project=project_name)
    return cache.load_cached_data(symbol, period, use_cache, get_ak_data)

def get_ak_data(symbol: str, period: str = "annual", api_key : Optional[str] = "") -> pd.DataFrame:
    import akshare as ak
    from openbb_akshare.utils.helpers import normalize_symbol
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    symbol_em = f"{market}{symbol_b}"

    if period == "annual":
        return ak.stock_cash_flow_sheet_by_yearly_em(symbol=symbol_em)
    elif period == "quarter":
        return ak.stock_cash_flow_sheet_by_report_em(symbol=symbol_em)
    else:
        raise ValueError("Invalid period. Please use 'annual' or 'quarter'.")