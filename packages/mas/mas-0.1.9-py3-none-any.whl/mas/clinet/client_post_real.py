import pandas as pd
import requests
from numpy import generic
import io
from mas.lang.i18n_strings import ClientText, get_text
URL = "http://127.0.0.1:8800"


class ClientPostReal:
    def __init__(self, path='.'):
        """
        初始化報表管理器，設定預設的輸出路徑。

        Args:
            path (str): 輸出檔案的根目錄，預設為當前目錄 '.'。

        Returns:
            無

        Initialize the report manager and set the default output path.

        Args:
            path (str): Root output directory for generated files. Default is current directory '.'.

        Returns:
            None
        """
        self.path = path

    def json_safe(self, d: dict):
        """
        將 dict 中的特殊物件（如 pandas.Timestamp、numpy 類型）轉換為可序列化為 JSON 的安全格式。

        Args:
            d (dict): 原始字典資料，可能包含不可直接序列化的物件。

        Returns:
            dict: 已轉換為可 JSON 序列化的字典。

        Convert special objects in a dictionary (e.g., pandas.Timestamp, numpy types)
        into JSON-safe formats.

        Args:
            d (dict): Input dictionary that may contain non-JSON-serializable objects.

        Returns:
            dict: A new dictionary with all values converted to JSON-serializable types.
        """

        for k, v in d.items():
            if isinstance(v, pd.Timestamp):
                d[k] = v.isoformat()
            elif isinstance(v, generic):  # numpy int/float
                d[k] = v.item()
        return d

    def check_server(self):
        """
        嘗試連線伺服器進行狀態檢查，若發生例外則顯示錯誤訊息並回傳 False。

        Args:
            無

        Returns:
            bool: 若伺服器連線成功則不回傳值（預設為 None）；
                  若連線失敗則印出錯誤提示並回傳 False。

        Attempt to connect to the server for a status check.
        If an exception occurs, display error messages and return False.

        Args:
            None

        Returns:
            bool: Returns None if the server is reachable;
                  returns False if the connection fails and error messages are shown.
        """
        try:
            requests.post(f"{URL}/check_server")
        except Exception as e:
            print(get_text(ClientText.SERVER_ERROR))
            print(get_text(ClientText.DOWNLOAD_HINT))
            return False

    def set_data(self, symbol, data: pd.DataFrame):
        """
        傳送指定商品的歷史資料至伺服器後端，以供回測引擎使用。

        Args:
            symbol (str): 商品代碼，例如 "EURUSD"、"AAPL"。
            data (pd.DataFrame): 歷史資料，將透過 DataFrame.to_json() 序列化後上傳。

        Returns:
            無

        Send historical price data for the given symbol to the backend server for backtesting use.

        Args:
            symbol (str): Trading symbol, e.g., "EURUSD", "AAPL".
            data (pd.DataFrame): Historical price data to be serialized via DataFrame.to_json() and sent via POST request.

        Returns:
            None
        """
        requests.post(f"{URL}/backtest/set_data", json={
            "data": data.to_json(),
            "symbol": symbol
        })

    def data_is_end(self):
        """
        通知伺服器端資料傳輸已完成，準備進行回測後續流程。

        Args:
            無

        Returns:
            無

        Notify the backend server that all data has been transmitted,
        and signal readiness for subsequent backtest processing.

        Args:
            None

        Returns:
            None
        """
        requests.post(f"{URL}/backtest/data_is_end")

    def record_reset(self):
        """
        通知伺服器端重置交易紀錄與持倉資訊，清除先前記錄的回測資料。

        Args:
            無

        Returns:
            無

        Notify the backend server to reset recorded trades and position data,
        clearing previously stored backtest information.

        Args:
            None

        Returns:
            None
        """
        requests.post(f"{URL}/backtest/record_reset")

    def record_trade(self, data):
        """
        將單筆交易資料轉換為 JSON 安全格式後，傳送至伺服器端儲存。

        Args:
            data (dict): 單筆交易資料，需包含如 "symbol"、"price"、"volume"、"type"、"time" 等欄位。

        Returns:
            無

        Convert a trade record into JSON-safe format and send it to the backend server for recording.

        Args:
            data (dict): A single trade record. Should include fields like "symbol", "price", "volume", "type", and "time".

        Returns:
            None
        """
        data = self.json_safe(data)
        requests.post(f"{URL}/backtest/record_trade", json={
            "data": data,
        })

    def gen_trade_report(self):
        """
        請求伺服器產出交易圖表報表（含進出場訊號），並根據伺服器回應顯示提示訊息與回傳結果。

        Args:
            無

        Returns:
            dict | None: 若成功則回傳報表結果資料（dict），並印出成功訊息；
                         若失敗則印出錯誤訊息並回傳 None。

        Send a request to the backend server to generate a trade chart report (with entry/exit signals),
        handle the server response, print user-friendly messages, and return the result.

        Args:
            None

        Returns:
            dict | None: Returns report data (dict) if successful and prints a success message;
                         otherwise prints an error message and returns None.
        """
        res = requests.post(f"{URL}/backtest/gen_trade_report", json={
            "path": self.path
        })

        if res.status_code == 200:
            result = res.json()
            print(get_text(ClientText.TRADE_SUCCESS))
            return result
        else:
            error_info = res.json()  # 這裡要用 json() 而不是 content
            print(get_text(ClientText.UNKNOWN_ERROR,
                msg=error_info.get("message", "Unknown error. Please try again.")))
            return None

    def gen_kpi_report(self):
        res = requests.post(f"{URL}/backtest/gen_kpi_report", json={
            "path": self.path
        })
        if res.status_code == 200:
            result = res.json()
            print(get_text(ClientText.KPI_SUCCESS))
            return result
        else:
            error_info = res.json()  # 這裡要用 json() 而不是 content
            print(get_text(ClientText.UNKNOWN_ERROR,
                msg=error_info.get("message", "Unknown error. Please try again.")))
            return None

    def gen_data_report(self):
        """
        請求伺服器產出策略績效報表（KPI 報表），並根據回應印出提示訊息與回傳結果。

        Args:
            無

        Returns:
            dict | None: 若成功則回傳 KPI 報表資料（dict），並印出成功訊息；
                         若失敗則印出錯誤訊息並回傳 None。

        Send a request to the backend server to generate a strategy KPI performance report,
        handle the server response, print user-friendly messages, and return the result.

        Args:
            None

        Returns:
            dict | None: Returns report data (dict) if successful and prints a success message;
                         otherwise prints an error message and returns None.
        """
        res = requests.post(f"{URL}/backtest/gen_data_report", json={
            "path": self.path
        })
        if res.status_code == 200:
            result = res.json()
            print(get_text(ClientText.DATA_SUCCESS))
            if "data_source" in result.get("data"):
                result["data"]["data_source"] = pd.read_json(
                    io.StringIO(result["data"]["data_source"]), encoding='utf-8')

            return result
        else:
            error_info = res.json()  # 這裡要用 json() 而不是 content
            print(get_text(ClientText.UNKNOWN_ERROR,
                msg=error_info.get("message", "Unknown error. Please try again.")))
            return None

    def set_spread_fee(self, data):
        """
        傳送商品的點差費用設定至伺服器端，用於回測損益計算。

        Args:
            data (dict): 點差費用設定資料，需包含以下欄位：
                - symbol (str): 商品代碼。
                - spread_fee (float): 該商品的點差費用。

        Returns:
            無

        Send spread fee configuration for a specific symbol to the backend server
        for use in PnL calculation during backtesting.

        Args:
            data (dict): Spread fee configuration. Must include:
                - symbol (str): Trading symbol.
                - spread_fee (float): Spread fee value for the symbol.

        Returns:
            None
        """
        requests.post(f"{URL}/backtest/set_spread_fee", json={
            "data": data
        })
