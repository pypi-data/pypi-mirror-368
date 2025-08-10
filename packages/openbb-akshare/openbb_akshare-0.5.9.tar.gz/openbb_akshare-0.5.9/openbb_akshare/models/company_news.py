"""AKShare Company News Model."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from pydantic import Field, field_validator

class AKshareCompanyNewsQueryParams(CompanyNewsQueryParams):
    """AKShare Company News Query.

    Source: https://so.eastmoney.com/news/s
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _symbol_mandatory(cls, v):
        """Symbol mandatory validator."""
        if not v:
            raise ValueError("Required field missing -> symbol")
        return v


class AKShareCompanyNewsData(CompanyNewsData):
    """AKShare Company News Data."""

    source: Optional[str] = Field(
        default=None, description="Source of the news article"
    )


class AKShareCompanyNewsFetcher(
    Fetcher[
        AKshareCompanyNewsQueryParams,
        List[AKShareCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKshareCompanyNewsQueryParams:
        """Define example transform_query.

        Here we can pre-process the query parameters and add any extra parameters that
        will be used inside the extract_data method.
        """
        return AKshareCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKshareCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import get_requests_session
        import akshare as ak

        results: list = []
        symbols = query.symbol.split(",")  # type: ignore
        async def get_one(symbol):
            data = ak.stock_news_em(symbol)
            for idx, d in data.iterrows():
                new_content: dict = {}
                new_content["text"] = d["新闻内容"]
                new_content["url"] = d["新闻链接"]
                new_content["source"] = d["文章来源"]
                new_content["title"] = d["新闻标题"]
                new_content["date"] = d["发布时间"]

                results.append(new_content)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError("No data was returned for the given symbol(s)")

        return results

    @staticmethod
    def transform_data(
        query: AKshareCompanyNewsQueryParams, data: List[dict], **kwargs: Any
    ) -> List[AKShareCompanyNewsData]:
        """Define example transform_data.

        Right now, we're converting the data to fit our desired format.
        You can apply other transformations to it here.
        """
        return [AKShareCompanyNewsData(**d) for d in data]
