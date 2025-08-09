from datetime import datetime


def normalize_datetime_params(params: dict) -> dict:
    """
    將字典中的 'from' 與 'to' 日期字串標準化為 datetime 物件。

    支援格式包括：
    - 'YYYY-MM-DD'
    - 'YYYY-MM-DD HH:MM:SS'
    並會自動將 'to' 日期補上當日最後一秒（23:59:59），以利涵蓋整日資料區間。

    Args:
        params (dict): 包含 'from' 和 'to' 欄位的查詢參數字典，可為 datetime 或字串格式。

    Returns:
        dict: 處理後的參數字典，'from' 與 'to' 欄位皆為 datetime 物件。

    Normalize 'from' and 'to' datetime parameters in a dictionary.

    Supports the following formats:
    - 'YYYY-MM-DD'
    - 'YYYY-MM-DD HH:MM:SS'
    Automatically appends 23:59:59 to the 'to' date to ensure full-day coverage.

    Args:
        params (dict): Dictionary containing 'from' and 'to' keys. Values can be strings or datetime objects.

    Returns:
        dict: Dictionary with 'from' and 'to' fields converted to datetime objects.
    """
    def parse(val, is_to=False):
        if isinstance(val, str):
            try:
                dt = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.strptime(val, "%Y-%m-%d")
                if is_to:
                    dt = dt.replace(hour=23, minute=59, second=59)
                else:
                    dt = dt.replace(hour=0, minute=0, second=0)
            return dt
        return val

    params["from"] = parse(params.get("from"), is_to=False)
    params["to"] = parse(params.get("to"), is_to=True)
    return params
