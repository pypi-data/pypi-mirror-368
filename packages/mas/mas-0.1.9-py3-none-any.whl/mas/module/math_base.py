from decimal import Decimal

def get_spread_fee_for_tick(df):
    """
    根據 Tick 資料計算點差費用與價格精度（decimal_nub），用於後續交易損益估算。

    將 ask - bid 的差值作為 spread，並計算加權後的平均 spread 作為 fee。
    同時計算標的價格的小數點精度，轉換為 decimal_nub（如 10000、100、1）。

    Args:
        df (pd.DataFrame): 必填，含有欄位 ['bid', 'ask', 'last'] 的 Tick 資料。

    Returns:
        dict: 回傳點差參數，包含：
            - decimal_nub (int): 精度倍率，根據 last 價格的小數位數計算。
            - fee (float): 計算後的平均點差費用。

    Estimate spread fee and price precision (decimal_nub) based on Tick data.

    Calculates the spread as (ask - bid), then derives a weighted average spread as the fee.
    Also determines the decimal precision from the 'last' price to get the corresponding multiplier.

    Args:
        df (pd.DataFrame): Required. Tick DataFrame with columns ['bid', 'ask', 'last'].

    Returns:
        dict: Spread fee configuration with:
            - decimal_nub (int): Decimal multiplier derived from the price precision.
            - fee (float): Estimated average spread fee.
    """
    df = df.copy()
    df = df[(df["ask"] >= df["bid"]) & df["bid"].notna() & df["ask"].notna()]
    df["spread"] = df["ask"] - df["bid"]

    if df.empty:
        raise ValueError("no spread data")

    fee = (df["spread"].mean() + 0.25 * df["spread"].std()) / 2
    price = df["last"].iloc[0]

    def get_decimal_nub(price: float) -> int:
        d = Decimal(str(price)).normalize()
        decimal_places = -d.as_tuple().exponent if d.as_tuple().exponent < 0 else 0
        if decimal_places > 4:
            return 100000
        if decimal_places == 4:
            return 10000
        elif decimal_places == 3:
            return 1000
        elif decimal_places == 2:
            return 100
        elif decimal_places == 1:
            return 10
        else:
            return 1

    return {
        "decimal_nub": get_decimal_nub(price),
        "fee": round(fee, 1)
    }

def get_spread_fee(df):
    """
    根據 Bar 資料計算點差費用與價格精度（decimal_nub），用於後續交易損益估算。

    此函式預期傳入資料中已包含 spread 欄位，會計算加權後的平均 spread 作為 fee，
    並依據 close 價格的小數位數估算 decimal_nub（精度倍率）。

    Args:
        df (pd.DataFrame): 必填，包含 'spread' 與 'close' 欄位的 Bar 資料。

    Returns:
        dict: 回傳點差參數，包含：
            - decimal_nub (int): 精度倍率，根據 close 價格的小數位數決定。
            - fee (float): 平均點差費用（加權後）。

    Estimate spread fee and price precision (decimal_nub) based on Bar (candlestick) data.

    Assumes the input DataFrame already contains a 'spread' column.
    Calculates the weighted average spread as the fee and determines decimal precision
    from the 'close' price to get the corresponding multiplier.

    Args:
        df (pd.DataFrame): Required. Bar data containing 'spread' and 'close' columns.

    Returns:
        dict: Spread fee configuration including:
            - decimal_nub (int): Decimal multiplier derived from the price precision.
            - fee (float): Estimated average spread fee.
    """
    fee = (df['spread'].mean() + 0.25 * df['spread'].std()) / 2
    price = df['close'].iloc[0]

    def get_decimal_nub(price: float) -> int:
        d = Decimal(str(price)).normalize()
        decimal_places = -d.as_tuple().exponent if d.as_tuple().exponent < 0 else 0
        if decimal_places > 4:
            return 100000
        if decimal_places == 4:
            return 10000
        elif decimal_places == 3:
            return 1000
        elif decimal_places == 2:
            return 100
        elif decimal_places == 1:
            return 10
        else:
            return 1

    return {
        "decimal_nub": get_decimal_nub(price),
        "fee": round(fee, 1)
    }
