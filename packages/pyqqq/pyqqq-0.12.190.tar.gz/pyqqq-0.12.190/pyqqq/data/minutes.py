import datetime
from typing import Dict, Union

import numpy as np
import pandas as pd
import pytz

import pyqqq.config as c
from pyqqq.datatypes import DataExchange
from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.local_cache import DiskCacheManager
from pyqqq.utils.logger import get_logger

logger = get_logger(__name__)
minuteCache = DiskCacheManager("minute_cache")


@minuteCache.memoize()
def get_all_minute_data(
    time: datetime.datetime,
    source: str = "kis",
    adjusted: bool = True,
    exchange: Union[str, DataExchange] = "KRX",
) -> pd.DataFrame:
    """
    모든 종목의 분봉 데이터를 반환합니다.

    2024년 4월 9일 데이터 부터 조회 가능합니다.

    NXT 거래소 데이터의 조회 가능 시작일은 데이터 소스에 따라 다릅니다. kis는 2025년 3월 4일부터, ebest는 2025년 5월 12일부터 데이터를 조회할 수 있습니다.

    Note:
        - KRX, NXT 거래소의 분봉 데이터를 조회할 수 있습니다. UN 거래소는 지원되지 않습니다.

    Args:
        time (datetime.datetime): 조회할 시간
        source (str): 데이터를 검색할 API. 'ebest' 또는 'kis'를 지정할 수 있습니다. 기본값은 'kis'입니다.
        adjusted (bool): 수정주가 여부. 기본값은 True.
        exchange (Union[str, DataExchange]): 거래소. 기본값은 KRX.

    Returns:
        pd.DataFrame: 모든 종목의 분봉 데이터가 포함된 pandas DataFrame.

        DataFrame의 열은 다음과 같습니다:

        - open (int): 시가
        - high (int): 고가
        - low (int): 저가
        - close (int): 종가
        - volume (int): 누적거래량
        - sign (str): 대비부호 (1:상한가 2:상승, 3:보합 4:하한가, 5:하락)
        - change (str): 전일 대비 가격 변화
        - diff (float): 전일 대비 등락율
        - chdegree (float): 체결강도
        - mdvolume (int): 매도체결수량
        - msvolume (int): 매수체결수량
        - revolume (int): 순매수체결량
        - mdchecnt (int): 매도체결건수
        - mschecnt (int): 매수체결건수
        - rechecnt (int): 순체결건수
        - cvolume (int): 체결량
        - mdchecnttm (int): 시간별매도체결건수
        - mschecnttm (int): 시간별매수체결건수
        - totofferrem (int): 매도잔량
        - totbidrem (int): 매수잔량
        - mdvolumetm (int): 시간별매도체결량
        - msvolumetm (int): 시간별매수체결량

    Raises:
        ValueError: 지원하지 않는 거래소 코드가 전달된 경우.

    Examples:
        >>> df = get_all_minute_data(datetime.datetime(2024, 5, 2, 15, 30))
        >>> print(df)
                                    time   open   high    low  ...  totofferrem  totbidrem mdvolumetm  msvolumetm
        code                                             ...
        000020 2024-05-02 15:30:00   8700   8700   8700  ...         8404       4015         35           1
        000040 2024-05-02 15:30:00   1058   1058   1058  ...        13597      24738         20           0
        000050 2024-05-02 15:30:00   7620   7620   7620  ...         2534       2866          0           0
        000070 2024-05-02 15:30:00  69400  69400  69400  ...          606        724          0           3
        000075 2024-05-02 15:30:00  54900  54900  54900  ...          315        308          0           0

        [5 rows x 23 columns]
    """
    tz = pytz.timezone("Asia/Seoul")

    exchange = DataExchange.validate(exchange)
    if exchange == DataExchange.UN:
        raise ValueError("UN 거래소는 지원되지 않습니다.")

    url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/minutes/all/{time.date()}/{time.strftime('%H%M')}"
    params = {
        "brokerage": source,
        "adjusted": "true" if adjusted else "false",
        "current_date": datetime.date.today(),
        "exchange": exchange.value,
    }

    r = send_request("GET", url, params=params)
    if r.status_code != 200 and r.status_code != 201:
        logger.error(f"Failed to get minute data: {r.text}")
        return

    rows = r.json()
    for data in rows:
        time = data["time"].replace("Z", "+00:00")
        time = datetime.datetime.fromisoformat(time).astimezone(tz).replace(tzinfo=None)
        data["time"] = time

    df = pd.DataFrame(rows)
    if not df.empty:
        dtypes = df.dtypes

        for k in [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "change",
            "totofferrem",
            "totbidrem",
        ]:
            if k in dtypes:
                dtypes[k] = np.dtype("int64")

        for k in ["diff", "chdegree"]:
            if k in dtypes:
                dtypes[k] = np.dtype("float64")

        df = df.astype(dtypes)
        df.set_index("code", inplace=True)

    return df


@minuteCache.memoize()
def get_all_day_data(
    date: datetime.date,
    codes: list[str] | str,
    period: datetime.timedelta = datetime.timedelta(minutes=1),
    source: str = "kis",
    adjusted: bool = True,
    ascending: bool = True,
    exchange: Union[str, DataExchange] = "KRX",
) -> dict[str, pd.DataFrame] | pd.DataFrame:
    """
    지정된 날짜에 대해 하나 이상의 주식 코드에 대한 전체 분별 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 검색하여 반환합니다.

    2024년 4월 26일 데이터 부터 조회 가능합니다.

    NXT 거래소 데이터의 조회 가능 시작일은 데이터 소스에 따라 다릅니다. kis는 2025년 3월 4일부터, ebest는 2025년 5월 12일부터 데이터를 조회할 수 있습니다.

    Note:
        - KRX, NXT 거래소의 분봉 데이터를 조회할 수 있습니다. UN 거래소는 지원되지 않습니다.

    Args:
        date (datetime.date): 데이터를 검색할 날짜.
        codes (list[str]): 조회할 주식 코드들의 리스트. 최대 20개까지 지정할 수 있습니다.
        period (datetime.timedelta, optional): 반환된 데이터의 시간 간격. 기본값은 1분입니다. 30초 이상의 값을 30초간격으로 지정할 수 있습니다.
        source (str, optional): 데이터를 검색할 API. 'ebest' 또는 'kis'를 지정할 수 있습니다. 기본값은 'kis'입니다.
        adjusted (bool): 수정주가 여부. 기본값은 True.
        ascending (bool): 오름차순 여부. 기본값은 True.
        exchange (Union[str, DataExchange]): 거래소. 기본값은 KRX. (cf. NXT의 경우 해당되지 않는 종목은 Empty DataFrame이 반환됩니다.)

    Returns:
        dict[str, pd.DataFrame]: 주식 코드를 키로 하고, 해당 주식의 일일 OHLCV 데이터가 포함된 pandas DataFrame을 값으로 하는 딕셔너리.
        각 DataFrame에는 변환된 'time' 열이 포함되어 있으며, 이는 조회된 데이터의 시간을 나타냅니다. 'time' 열은 DataFrame의 인덱스로 설정되고 오름차순으로 정렬됩니다.

        DataFrame의 열은 다음과 같습니다:

        - open (int): 시가
        - high (int): 고가
        - low (int): 저가
        - close (int): 종가
        - volume (int): 누적거래량
        - sign (str): 대비부호 (1:상한가 2:상승, 3:보합 4:하한가, 5:하락)
        - change (str): 전일 대비 가격 변화
        - diff (float): 전일 대비 등락율
        - chdegree (float): 체결강도
        - mdvolume (int): 매도체결수량
        - msvolume (int): 매수체결수량
        - revolume (int): 순매수체결량
        - mdchecnt (int): 매도체결건수
        - mschecnt (int): 매수체결건수
        - rechecnt (int): 순체결건수
        - cvolume (int): 체결량
        - mdchecnttm (int): 시간별매도체결건수
        - mschecnttm (int): 시간별매수체결건수
        - totofferrem (int): 매도잔량
        - totbidrem (int): 매수잔량
        - mdvolumetm (int): 시간별매도체결량
        - msvolumetm (int): 시간별매수체결량

    Raises:
        requests.exceptions.RequestException: PYQQQ API로부터 데이터를 검색하는 과정에서 오류가 발생한 경우.

    Examples:
        >>> result = get_all_day_data(datetime.date(2024, 4, 26), ["005930", "319640"], datetime.timedelta(minutes=1))
        >>> print(result["069500"])
                            open   high    low  close   volume sign  change  diff  \
        time
        2024-04-26 09:00:00  77800  77900  77400  77600  1629535    2    1300  1.70
        2024-04-26 09:01:00  77500  77700  77300  77600  2155263    2    1300  1.70
        2024-04-26 09:02:00  77600  77700  77400  77500  2600420    2    1200  1.57
        2024-04-26 09:03:00  77500  77500  77200  77500  3033307    2    1200  1.57
        2024-04-26 09:04:00  77400  77600  77400  77500  3268502    2    1200  1.57
    """
    assert isinstance(date, datetime.date), "date must be a datetime.date object"
    assert type(date) is datetime.date, "date must be a datetime.date object"
    assert isinstance(codes, list) or isinstance(codes, str), "codes must be a list of strings or single code"

    if isinstance(codes, list):
        assert all(isinstance(code, str) for code in codes), "codes must be a list of strings"
    assert len(codes) > 0, "codes must not be empty"
    assert len(codes) <= 20, "codes must not exceed 20"

    if period is not None:
        assert period >= datetime.timedelta(seconds=30), "period must be at least 30 seconds"
        assert period.total_seconds() % 30 == 0, "period must be a multiple of 30 seconds"

    tz = pytz.timezone("Asia/Seoul")
    target_codes = codes if isinstance(codes, list) else [codes]

    exchange = DataExchange.validate(exchange)
    if exchange == DataExchange.UN:
        raise ValueError("UN 거래소는 지원되지 않습니다.")
    elif exchange == DataExchange.NXT or source == "kis":
        url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/minutes/{date}"
    else:
        url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/half-minutes/{date}"

    r = send_request(
        "GET",
        url,
        params={
            "codes": ",".join(target_codes) if target_codes else None,
            "brokerage": source,
            "adjusted": "true" if adjusted else "false",
            "current_date": datetime.date.today(),
            "exchange": exchange.value,
        },
    )

    if r.status_code != 200 and r.status_code != 201:
        logger.error(f"Failed to get day data: {r.text}")
        r.raise_for_status()

    result = {}
    for code in target_codes:
        result[code] = pd.DataFrame()

    entries = r.json()
    cols = entries["cols"]
    if len(cols) == 0:
        return result

    time_index = cols.index("time")
    multirows = entries["rows"]

    for code in multirows.keys():
        rows = multirows[code]
        for row in rows:
            time = row[time_index].replace("Z", "+00:00")
            time = datetime.datetime.fromisoformat(time).astimezone(tz).replace(tzinfo=None)
            row[time_index] = time

        rows.reverse()

        df = pd.DataFrame(rows, columns=cols)

        if source == "kis":
            df = resample_kis_data(df, period)
        else:
            df = resample_ebest_data(df, period)

        df.sort_index(ascending=ascending, inplace=True)

        result[code] = df

    if isinstance(codes, str):
        return result[codes]
    else:
        return result


def resample_ebest_data(df, period):
    if period is not None and period.total_seconds() != 30:
        df["time"] = df["time"] - datetime.timedelta(seconds=30)
        df.set_index("time", inplace=True)

        minutes = period.total_seconds() / 60

        op_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "sign": "last",
            "change": "last",
            "diff": "last",
            "chdegree": "last",
            "mdvolume": "sum",
            "msvolume": "sum",
            "revolume": "sum",
            "mdchecnt": "sum",
            "mschecnt": "sum",
            "rechecnt": "sum",
            "cvolume": "sum",
            "mdchecnttm": "sum",
            "mschecnttm": "sum",
            "totofferrem": "last",
            "totbidrem": "last",
            "mdvolumetm": "sum",
            "msvolumetm": "sum",
        }

        df = df.resample(f"{minutes}min").apply(op_dict)
        df.dropna(inplace=True)
        df.reset_index(inplace=True)

    dtypes = df.dtypes

    for k in [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "change",
        "totofferrem",
        "totbidrem",
    ]:
        dtypes[k] = np.dtype("int64")

    dtypes["diff"] = np.dtype("float64")
    dtypes["chdegree"] = np.dtype("float64")

    df = df.astype(dtypes)
    df.set_index("time", inplace=True)

    return df


def resample_kis_data(df, period):
    if period is not None and period.total_seconds() != 60:
        df.set_index("time", inplace=True)
        minutes = period.total_seconds() // 60

        op_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "value": "sum",
            "cum_volume": "sum",
            "cum_value": "sum",
        }

        df = df.resample(f"{minutes}min").apply(op_dict)
        df.dropna(inplace=True)
        df.reset_index(inplace=True)

    dtypes = df.dtypes

    for k in [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "value",
        "cum_volume",
        "cum_value",
    ]:
        dtypes[k] = np.dtype("int64")

    df = df.astype(dtypes)
    df = df[["time", "open", "high", "low", "close", "volume", "value", "cum_volume", "cum_value"]]
    df.set_index("time", inplace=True)

    return df


def get_orderbook(code: str, time: datetime.datetime) -> Dict:
    """
    주식 종목의 주문 호가 정보를 반환합니다.

    Args:
        code (str): 종목 코드
        time (datetime.datetime): 조회할 시간

    Returns:
        dict: 호가 정보가 포함된 사전.
            - total_bid_volume (int): 총 매수 잔량.
            - total_ask_volume (int): 총 매도 잔량.
            - ask_price (int): 1차 매도 호가 가격.
            - ask_volume (int): 1차 매도 호가 잔량.
            - bid_price (int): 1차 매수 호가 가격.
            - bid_volume (int): 1차 매수 호가 잔량.
            - time (datetime.datetime): 현지 기준 호가 정보 조회 시간.
            - bids (list): 매수 호가 목록 (각 항목은 price와 volume을 포함하는 dict).
            - asks (list): 매도 호가 목록 (각 항목은 price과 volume을 포함하는 dict).
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/orderbook/minutes/{code}/{time.date()}/{time.strftime('%H%M')}"
    r = send_request("GET", url)

    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

    data = r.json()
    data.pop("code")
    data["time"] = datetime.datetime.fromisoformat(data["time"]).astimezone(pytz.timezone("Asia/Seoul")).replace(tzinfo=None)

    return data
