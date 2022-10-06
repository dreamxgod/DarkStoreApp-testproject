from app.models import *
from app.imports import *
from app.secrets import *

class YTDPerformance(BaseModel):
    performance: Decimal

class YTDPoint(BaseModel):
    amount: Decimal
    date: datetime.date

class YTDMinMax(BaseModel):
    min: YTDPoint
    max: YTDPoint

def finnhub_client() -> finnhub.Client:
    return finnhub.Client(api_key=yourAPIkey)   

def get_ytd_borders() -> tuple[int, int]:
    year_start_timestamp = round(dt.datetime(dt.date.today().year, 1, 1).timestamp())
    current_timestamp = round(dt.datetime.now().timestamp())
    return year_start_timestamp, current_timestamp

def profile_performance(client: finnhub.Client, profile: list[Profile]) -> Generator[Decimal, None, None]:
    ytd_borders = get_ytd_borders()
    for value in profile:
        data = client.crypto_candles(f"BINANCE:{value.name}USDT", "D", *ytd_borders)
        if data["s"] == "no_data":
            yield 0
            continue
        yield value.amount * Decimal(data["c"][-1]) - value.amount * Decimal(data["c"][0])

def get_currency_values(
    client: finnhub.Client, name: str, ytd_borders: tuple[int, int]) -> Iterable[Decimal]:
    data = client.crypto_candles(f"BINANCE:{name}USDT", "D", *ytd_borders)
    if data["s"] == "no_data":
        return [Decimal(0)]
    return map(lambda x: Decimal(x), data["c"])

def get_profile_min_max(
    values: Iterable[Iterable[Decimal]],
) -> tuple[tuple[Decimal, int], tuple[Decimal, int]]:
    min_value = None
    max_value = None
    for index, daily_values in enumerate(zip_longest(*values, fillvalue=Decimal(0))):
        daily_value = sum(daily_values)
        if max_value is None or daily_value > max_value[0]:
            max_value = daily_value, index
        if min_value is None or daily_value < min_value[0]:
            min_value = daily_value, index
    return min_value, max_value