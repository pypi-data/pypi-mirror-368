from mas.clinet.client_post_real import ClientPostReal


class ClientPost():
    """
    封裝後端 API 傳輸邏輯，用於資料交換與報表產出。

    A wrapper class that communicates with the backend server (ClientPostReal),
    providing methods to send data, reset state, record trades, and generate reports.
    """
    def __init__(self, path='.'):
        """
        初始化 ClientPost 實例，指定輸出路徑與底層實作。

        Initialize ClientPost instance with output path and backend handler.

        Args:
            path (str): 輸出路徑，預設為當前資料夾。
        """
        self.path = path
        self.client = ClientPostReal(self.path)

    def check_server(self):
        """
        檢查後端伺服器是否正常運作。

        Check if the backend server is alive.

        Returns:
            bool: True 表示正常；False 表示無法連線。
        """
        return self.client.check_server()

    def set_data(self, symbol, data):
        """
        傳送歷史 Bar 資料至後端，供回測模組使用。

        Upload historical bar data to the backend for backtest simulation.

        Args:
            symbol (str): 商品代碼。
            data (pd.DataFrame): 含時間與價格欄位的資料。
        """
        return self.client.set_data(symbol, data)

    def data_is_end(self):
        """
        通知後端歷史資料已送完，可開始分析。

        Notify backend that all historical data has been sent.
        """
        return self.client.data_is_end()

    def record_reset(self):
        """
        重置交易紀錄與部位狀態。

        Reset recorded trades and positions.
        """
        return self.client.record_reset()

    def record_trade(self, data):
        """
        傳送單筆交易紀錄至後端。

        Record a single trade to the backend.

        Args:
            data (dict): 含 symbol、price、volume、time 等欄位的交易資料。
        """
        return self.client.record_trade(data)

    def gen_trade_report(self):
        """
        產出圖形化交易報表（進出場點、K 線圖）。

        Generate an HTML report with trade entry/exit points and candlestick chart.

        Returns:
            dict: 報表產出狀態。
        """
        return self.client.gen_trade_report()

    def gen_kpi_report(self):
        """
        產出績效指標報表（勝率、回撤等），並自動儲存。

        Generate KPI HTML report including win rate, drawdown, etc.

        Returns:
            dict: 報表產出狀態。
        """
        return self.client.gen_kpi_report()

    def gen_data_report(self):
        """
        回傳完整的績效資料字典（KPI、報酬曲線、統計值等）。

        Return full performance data dictionary including KPIs and return curve.

        Returns:
            dict: 報表資料。
        """
        return self.client.gen_data_report()

    def set_spread_fee(self, data):
        """
        傳送商品點差與費用設定至後端模組。

        Set spread fee configuration for a specific symbol.

        Args:
            data (dict): 包含 symbol 與 spread_fee 結構。
        """
        return self.client.set_spread_fee(data)
