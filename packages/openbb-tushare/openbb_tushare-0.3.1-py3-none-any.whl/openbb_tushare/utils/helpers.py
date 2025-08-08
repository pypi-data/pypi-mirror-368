import os
from dotenv import load_dotenv
from typing import Optional, Union

def get_api_key(api_key : Optional[str] = "") -> str:
    if api_key:
        tushare_api_key = api_key
    else:
        load_dotenv() 
        tushare_api_key = os.environ.get("TUSHARE_API_KEY")
    if tushare_api_key is None:
        raise ValueError("TUSHARE_API_KEY environment variable not set.")

    return tushare_api_key

def get_fiscal_period(end_type:int) -> str:
    end_type = int(end_type)
    if end_type == 1:
        return "Q1"
    elif end_type == 2:
        return "Q2"
    elif end_type == 3:
        return "Q3"
    elif end_type == 4:
        return "FY"
    else:
        return "Unknown"
