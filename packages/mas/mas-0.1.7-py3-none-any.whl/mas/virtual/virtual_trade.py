from mas.receive.receive_manage import ReceiveManager
from mas.lang.i18n_strings import get_text, VirtualTradeText


class VirtualTradeManager:
    def __init__(self, receiver: ReceiveManager):
        """
        初始化 VirtualTradeManager，建立內部狀態以模擬掛單與成交流程。

        此建構子將初始化：
        - `order_id_counter`：模擬掛單用的自增編號。
        - `current_bar`：紀錄每個商品的當前 K 線資訊。
        - `pending_orders`：掛單列表，以 symbol 為索引。
        - `receiver`：推播成交與掛單狀態的接收端模組。

        Args:
            receiver (ReceiveManager): 用於推播虛擬交易事件的接收器。

        Initialize the VirtualTradeManager with internal state for simulating order handling.

        This constructor will initialize:
        - `order_id_counter`: Counter used for virtual order ID tracking.
        - `current_bar`: Stores current K-bar per symbol for decision-making.
        - `pending_orders`: Dictionary of simulated pending orders grouped by symbol.
        - `receiver`: Instance for reporting order status and execution events.

        Args:
            receiver (ReceiveManager): Receiver instance for order-related callbacks.
        """
        self.order_id_counter = 0
        self.current_bar = {}
        self.pending_orders = {}
        self.receiver = receiver

    def data_reset(self):
        """
        重置模擬交易內部資料，包括當前 K 線資訊與掛單清單。

        此方法常用於回測資料初始化或重啟模擬交易流程，會清空：
        - `current_bar`：每個商品的最新 K 線。
        - `pending_orders`：尚未成交的虛擬掛單。

        Returns:
            None

        Reset internal virtual trade data, including current K-bar and pending orders.

        This method is typically used during backtest initialization or before re-running a simulation. It clears:
        - `current_bar`: Latest K-bar per symbol.
        - `pending_orders`: All unfilled simulated orders.

        Returns:
            None
        """
        self.current_bar = {}
        self.pending_orders = {}

    def send_order(self, params: dict) -> str:
        """
        模擬送出一筆虛擬訂單，根據當前 K 棒時間掛入待處理佇列。

        此方法會：
        - 檢查商品代碼與當前 K 棒是否存在
        - 自動產生模擬訂單 ID（BT 開頭）
        - 將訂單加入 `pending_orders` 以待下根 K 棒判斷是否成交
        - 推播掛單成功訊息至 `receiver`

        Args:
            params (dict): 下單參數，需包含：
                - symbol (str): 商品代碼（必填）
                - 其他欄位將保留於 `params` 中待處理

        Returns:
            str: 虛擬訂單編號（格式為 BT{編號}），若 symbol 缺失則回傳空字串。

        Simulate sending a virtual order. The order is queued for evaluation at the next K-bar.

        This method:
        - Validates the symbol and current K-bar availability
        - Generates a virtual order ID with "BT" prefix
        - Appends order to the `pending_orders` queue for execution
        - Triggers order status update via `receiver`

        Args:
            params (dict): Order parameters, must include:
                - symbol (str): Instrument symbol (required)
                - Other fields will be stored for later evaluation

        Returns:
            str: The generated virtual order ID (e.g., "BT1"). Returns empty string if symbol is missing.
        """
        self.order_id_counter += 1
        order_id = f"BT{self.order_id_counter}"

        symbol = params.get("symbol")
        if not symbol:
            print(get_text(VirtualTradeText.MISSING_SYMBOL))
            return ""

        bar = self.current_bar.get(symbol)
        if bar is None or bar.empty:
            print(get_text(VirtualTradeText.NO_CURRENT_BAR))
            return order_id

        self.pending_orders.setdefault(symbol, []).append({
            "order_id": order_id,
            "params": params,
            "requested_bar_time": bar["time"]
        })

        self.receiver.on_order_status(order_id, {
            "status": 10009,
            "retcode": 10009,
            "message": "Request accepted, wait for next bar",
            "request": params
        })

        return order_id

    def set_current_bar(self, symbol: str, bar: dict):
        """
        設定指定商品的當前 K 棒資料，並依據時間邏輯判斷是否有掛單應成交。

        若有掛單的 `requested_bar_time` 早於目前 `bar["time"]`，則視為成交：
        - 使用當前 K 棒的開盤價（`open`）作為成交價
        - 推播成交結果至 `receiver.on_order_execution`
        - 未滿足條件的掛單會保留至下一根 K 棒再處理

        Args:
            symbol (str): 商品代碼。
            bar (dict): 當前 K 棒資料，需包含欄位 "time" 與 "open"。

        Returns:
            None

        Update the current K-bar for a given symbol and evaluate pending orders.

        If any order's `requested_bar_time` is earlier than the new bar's time,
        it is considered executed using the bar's opening price.

        Executed orders are:
        - Marked as filled
        - Reported to `receiver.on_order_execution`

        Remaining orders are retained for the next evaluation.

        Args:
            symbol (str): Instrument symbol.
            bar (dict): Current K-bar data. Must include keys "time" and "open".

        Returns:
            None
        """
        self.current_bar[symbol] = bar
        orders = self.pending_orders.get(symbol, [])

        if not orders:
            return

        remaining = []
        for order in orders:
            if order["requested_bar_time"] < bar["time"]:
                execution_data = {
                    "price": bar["open"],
                    "volume": order["params"]["volume"],
                    "symbol": symbol,
                    "time": bar["time"],
                    "type": order["params"]["order_type"]
                }
                self.receiver.on_order_execution(
                    order["order_id"], execution_data)
            else:
                remaining.append(order)

        self.pending_orders[symbol] = remaining

    def modify_order(self, params: dict) -> bool:
        """
        修改指定虛擬訂單的參數（如 price, sl, tp），並推播修改狀態。

        該方法會遍歷 `pending_orders`，根據 order_id 尋找對應的掛單，若找到：
        - 更新其 `params` 中的 price、sl、tp（若存在）
        - 推播修改狀態訊息至 receiver

        若找不到對應掛單，則會列印錯誤訊息。

        Args:
            params (dict): 修改參數，需包含：
                - order_id (str): 虛擬訂單 ID（必填）
                - price / sl / tp（可選）：欲修改的價格、停損或停利

        Returns:
            bool: 是否成功修改訂單，成功為 True，否則為 False。

        Modify a pending virtual order's parameters such as price, sl, or tp.

        This method searches for the order in the `pending_orders` queue by order_id.
        If found:
        - Updates the parameters in-place
        - Sends status update to the receiver

        If not found, prints error message.

        Args:
            params (dict): Modification parameters. Must include:
                - order_id (str): Virtual order ID (required)
                - price / sl / tp (optional): New values for price, stop loss, or take profit

        Returns:
            bool: True if the order was successfully modified, False otherwise.
        """
        order_id = params.get("order_id")
        if not order_id:
            print(get_text(VirtualTradeText.MODIFY_MISSING_ORDER_ID))
            return False

        found = False

        for symbol, orders in self.pending_orders.items():
            for order in orders:
                if order["order_id"] == order_id:
                    orig_params = order["params"]
                    for key in ["price", "sl", "tp"]:
                        if key in params:
                            orig_params[key] = params[key]

                    self.receiver.on_order_status(order_id, {
                        "status": 10010,
                        "retcode": 10010,
                        "message": f"Order modified for {order_id}",
                        "request": orig_params
                    })

                    found = True
                    break
            if found:
                break

        if not found:
            print(get_text(VirtualTradeText.ORDER_ID_NOT_FOUND, order_id=order_id))
            return False

        return True

    def cancel_order(self, params: dict) -> bool:
        """
        取消指定的虛擬掛單（pending order），並推播取消狀態。

        此方法會根據 symbol 與 order_id 查找對應的掛單，若成功移除：
        - 發出取消成功訊息與狀態通知（retcode = 10011）

        若查無此掛單，則回傳 False 並列印錯誤訊息。

        Args:
            params (dict): 取消參數，需包含：
                - symbol (str): 商品代碼（必填）
                - order_id (str): 虛擬訂單 ID（必填）

        Returns:
            bool: 若成功取消掛單則回傳 True，否則回傳 False。

        Cancel a pending virtual order identified by symbol and order_id.

        If the order exists in `pending_orders`, it is removed and a cancel status message
        is broadcasted to the receiver with retcode = 10011.

        If the order is not found, returns False and prints an error message.

        Args:
            params (dict): Cancellation parameters. Must include:
                - symbol (str): Symbol of the order (required)
                - order_id (str): Virtual order ID to cancel (required)

        Returns:
            bool: True if the order was successfully cancelled, False otherwise.
        """

        symbol = params.get("symbol")
        order_id = params.get("order_id")

        if not symbol or not order_id:
            print(get_text(VirtualTradeText.CANCEL_MISSING_PARAMS))
            return False

        orders = self.pending_orders.get(symbol, [])
        before_count = len(orders)

        self.pending_orders[symbol] = [
            o for o in orders if o["order_id"] != order_id
        ]
        after_count = len(self.pending_orders[symbol])

        if after_count < before_count:
            print(get_text(VirtualTradeText.CANCEL_SUCCESS, order_id=order_id))
            self.receiver.on_order_status(order_id, {
                "status": 10011,
                "retcode": 10011,
                "message": f"Order {order_id} cancelled",
                "request": params
            })
            return True
        else:
            print(get_text(VirtualTradeText.CANCEL_NOT_FOUND, order_id=order_id))
            return False
