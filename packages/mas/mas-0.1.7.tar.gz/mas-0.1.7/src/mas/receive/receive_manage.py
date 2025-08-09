from mas.clinet.client_post import ClientPost
from mas.enum.env_setting import env_type

class ReceiveManager:
    """
    管理所有接收事件的處理與轉發，作為策略模組與回測伺服器之間的橋樑。

    支援 Tick / Bar 資料推播、訂單狀態更新與成交回報的接收邏輯，
    並根據 backtest_toggle 判斷是否要將交易紀錄寫入伺服器（回測模式專用）。

    A centralized manager for receiving and dispatching market data, order status,
    and execution reports to the strategy module or backtest server.

    It acts as a bridge between strategy and server, and controls whether
    to persist order executions based on the `backtest_toggle` flag.
    """
    def __init__(self, clientpost: ClientPost, owner=None):
        """
        初始化接收器，綁定推播對象與回測狀態。

        Args:
            clientpost (ClientPost): 與回測伺服器互動的 ClientPost 實例。
            owner (object, optional): 策略或上層模組實例，負責實際接收資料。

        Returns:
            None

        Initialize the receiver with connection to the backend and owner delegate.

        Args:
            clientpost (ClientPost): ClientPost instance for backend reporting.
            owner (object, optional): Strategy or parent module to receive events.

        Returns:
            None
        """
        self.owner = owner
        self.clientpost = clientpost
        self.backtest_toggle = True

    def set_bakctest_toggle(self, val):
        """
        設定是否啟用回測模式。

        Args:
            val (bool): True 表示為回測模式，False 表示為即時模式。

        Returns:
            None

        Set the backtest mode switch.

        Args:
            val (bool): True for backtest mode; False for live trading mode.

        Returns:
            None
        """
        self.backtest_toggle = val

    def on_tick(self, symbol: str, data: dict, is_end=False):
        """
        接收 Tick 資料，並轉發至owner（如策略模組）。

        Args:
            symbol (str): 商品代碼。
            data (dict): Tick 資料。
            is_end (bool): 是否為最後一筆（回測推播結尾用）。

        Returns:
            None

        Handle incoming Tick data and dispatch to the owner if available.

        Args:
            symbol (str): Instrument symbol.
            data (dict): Tick data dictionary.
            is_end (bool): Whether this is the final record (used in backtest).

        Returns:
            None
        """
        if self.owner:
            self.owner.receive_ticks(symbol, data, is_end)

    def on_bar(self, symbol: str, data: dict, is_end=False):
        """
        接收 Bar（K 線）資料，並轉發至owner（如策略模組）。

        Args:
            symbol (str): 商品代碼。
            data (dict): Bar 資料。
            is_end (bool): 是否為最後一筆（回測推播結尾用）。

        Returns:
            None

        Handle incoming Bar data and dispatch to the owner if available.

        Args:
            symbol (str): Instrument symbol.
            data (dict): Bar data dictionary.
            is_end (bool): Whether this is the final record (used in backtest).

        Returns:
            None
        """
        if self.owner:
            self.owner.receive_bars(symbol, data, is_end)

    def on_order_status(self, order_id: str, status_data: dict):
        """
        接收訂單狀態更新，並轉發至owner（如策略模組）。

        Args:
            order_id (str): 訂單編號。
            status_data (dict): 訂單狀態內容。

        Returns:
            None

        Handle order status updates and forward to the strategy module.

        Args:
            order_id (str): Order identifier.
            status_data (dict): Status update content.

        Returns:
            None
        """
        if self.owner:
            self.owner.receive_order_status(order_id, status_data)

    def on_order_execution(self, order_id: str, execution_data: dict):
        """
        接收成交回報資訊，若為回測模式則同步記錄至伺服器。

        Args:
            order_id (str): 訂單編號。
            execution_data (dict): 成交資料。

        Returns:
            None

        Handle order execution reports.
        In backtest mode, also logs the trade via ClientPost.

        Args:
            order_id (str): Order identifier.
            execution_data (dict): Execution data payload.

        Returns:
            None
        """
        if self.backtest_toggle:
            if not env_type.exe.value:
                self.clientpost.record_trade(execution_data)
        if self.owner:
            self.owner.receive_order_execution(order_id, execution_data)
