"""Tushare Equity Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class TushareEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Tushare Equity Historical Price Query.

    Source: https://tushare.pro/document/2?doc_id=27
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "period": {"choices": ["daily", "weekly", "monthly"]},
    }

    period: Literal["daily", "weekly", "monthly"] = Field(
        default="daily", description=QUERY_DESCRIPTIONS.get("period", "")
    )

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )

class TushareEquityHistoricalData(EquityHistoricalData):
    """Tushare Equity Historical Price Data."""

    amount: Optional[float] = Field(
        default=None,
        description="Amount.",
    )
    change: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close.",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class TushareEquityHistoricalFetcher(
    Fetcher[
        TushareEquityHistoricalQueryParams,
        List[TushareEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tushare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TushareEquityHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TushareEquityHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: TushareEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tushare endpoint."""
        from openbb_tushare.utils.ts_equity_historical import get_from_cache

        api_key = credentials.get("tushare_api_key") if credentials else ""
        data = get_from_cache(ts_code=query.symbol, start_date=query.start_date, end_date=query.end_date, 
                           api_key=api_key, period="daily", use_cache=query.use_cache)

        if data.empty:
            raise EmptyDataError()

        return data.to_dict(orient="records")


    @staticmethod
    def transform_data(
        query: TushareEquityHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TushareEquityHistoricalData]:
        """Return the transformed data."""

        return [
            TushareEquityHistoricalData.model_validate(d)
            for d in data
        ]
