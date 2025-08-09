import MetaTrader5 as mt5
from datetime import datetime
from mas.module.time_helper import normalize_datetime_params
from mas.connection.connection import ConnectionManager


class AccountManager:
    def __init__(self, connection: ConnectionManager):
        """
        初始化 AccountManager 實例，並注入連線管理器。

        Args:
            connection (ConnectionManager): 來自 mas.connection.connection 模組的連線管理器，用於處理與後端服務的連線。

        Initialize an instance of AccountManager with a connection manager.

        Args:
            connection (ConnectionManager): Connection manager from mas.connection.connection,
                                            used to handle connections to backend services.
        """
        self.connection = connection

    def init_mt5(self):
        """
        初始化 MetaTrader 5 (MT5) 交易終端。

        Args:
            無

        Returns:
            無。若初始化失敗，將拋出 RuntimeError 異常。

        Initialize the MetaTrader 5 (MT5) trading terminal.

        Args:
            None

        Returns:
            None. Raises RuntimeError if initialization fails.
        """

        if not mt5.initialize():
            raise RuntimeError("無法初始化 MT5，請確認終端啟動")

    def get_account_info(self) -> dict:
        """
        查詢 MT5 帳戶基本資訊。

        Args:
            無

        Returns:
            dict: 成功時回傳包含帳戶資訊dict，欄位包含 login、balance、equity、margin、leverage 等。
                  若查詢失敗，則回傳 {"error": "查詢帳戶資訊失敗"}。

        Retrieve basic account information from MT5.

        Args:
            None

        Returns:
            dict: If successful, returns a dictionary containing account details such as login, balance,
                  equity, margin, leverage, etc. If retrieval fails, returns {"error": "Failed to retrieve account info"}.
        """

        self.init_mt5()

        info = mt5.account_info()
        if info is None:
            return {"error": "查詢帳戶資訊失敗"}

        return {
            "login": info.login,
            "trade_mode": info.trade_mode,
            "leverage": info.leverage,
            "limit_orders": info.limit_orders,
            "margin_so_mode": info.margin_so_mode,
            "trade_allowed": info.trade_allowed,
            "trade_expert": info.trade_expert,
            "margin_mode": info.margin_mode,
            "currency_digits": info.currency_digits,
            "fifo_close": info.fifo_close,
            "balance": info.balance,
            "credit": info.credit,
            "profit": info.profit,
            "equity": info.equity,
            "margin": info.margin,
            "margin_free": info.margin_free,
            "margin_level": info.margin_level,
            "margin_so_call": info.margin_so_call,
            "margin_so_so": info.margin_so_so,
            "margin_initial": info.margin_initial,
            "margin_maintenance": info.margin_maintenance,
            "assets": info.assets,
            "liabilities": info.liabilities,
            "commission_blocked": info.commission_blocked,
            "name": info.name,
            "server": info.server,
            "currency": info.currency,
            "company": info.company
        }

    def get_positions(self, params: dict = {}) -> list:
        """
        查詢目前持倉部位（Position），可依據商品、群組或持倉單號過濾查詢。

        Args:
            params (dict): 查詢參數，可包含以下欄位：
                - symbol (str): 非必填，指定商品代碼。
                - group (str): 非必填，指定商品群組。
                - ticket (int): 非必填，指定持倉單號（優先順序低於 symbol 與 group）。

        Returns:
            list[dict]: 每筆為完整的部位資訊，若無資料則回傳空列表。

        Retrieve current open positions, with optional filters by symbol, group, or ticket.

        Args:
            params (dict): Query parameters. Supported keys:
                - symbol (str): Optional. Specify instrument symbol.
                - group (str): Optional. Filter by symbol group.
                - ticket (int): Optional. Specify position ticket (lower priority than symbol or group).

        Returns:
            list[dict]: Each item represents a full position record. Returns an empty list if no data is found.
        """
        symbol = params.get("symbol", "")
        group = params.get("group", "")
        ticket = params.get("ticket", "")

        if not symbol == "":
            symbol = self.connection.find_symbol(symbol)
        if not group == "":
            group = self.connection.find_symbol(group)
            
        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        elif group:
            positions = mt5.positions_get(group=group)
        elif ticket:
            positions = mt5.positions_get(ticket=ticket)
        else:
            positions = mt5.positions_get()

        if positions is None:
            return []

        result = []
        for p in positions:
            result.append({
                "ticket": p.ticket,
                "symbol": p.symbol,
                "type": p.type,
                "magic": p.magic,
                "identifier": p.identifier,
                "reason": p.reason,
                "volume": p.volume,
                "price_open": p.price_open,
                "sl": p.sl,
                "tp": p.tp,
                "price_current": p.price_current,
                "swap": p.swap,
                "profit": p.profit,
                "comment": p.comment,
                "external_id": p.external_id,
                "time": datetime.fromtimestamp(p.time),
                "time_msc": p.time_msc,
                "time_update": datetime.fromtimestamp(p.time_update),
                "time_update_msc": p.time_update_msc
            })

        return result

    def get_order_history(self, params: dict = {}) -> list:
        """
        查詢歷史成交紀錄（Deal History）。

        Args:
            params (dict): 查詢參數，可包含以下欄位：
                - symbol (str): 非必填，指定商品代碼。
                - from (datetime | str): 非必填，起始時間，預設為 2000-01-01。
                - to (datetime | str): 非必填，結束時間，預設為現在時間。
                - ticket (int): 非必填，指定某張訂單的成交紀錄。
                - position (int): 非必填，指定某張部位的成交紀錄。

        Returns:
            list[dict]: 每筆為完整的成交紀錄。若查無資料則回傳空列表。

        Retrieve historical deal records (Deal History) from MT5.

        Args:
            params (dict): Query parameters. Supported keys:
                - symbol (str): Optional. Specify instrument symbol.
                - from (datetime | str): Optional. Start datetime (default is 2000-01-01).
                - to (datetime | str): Optional. End datetime (default is current time).
                - ticket (int): Optional. Specify a ticket to filter by order.
                - position (int): Optional. Specify a position ID to filter by deal.

        Returns:
            list[dict]: Each item is a full deal record. Returns an empty list if no data is found.
        """
        if params.get("from") != None and params.get("from") != None: 
            params = normalize_datetime_params(params)
        date_from = params.get("from", datetime(2000, 1, 1,0,0,1))
        date_to = params.get("to", datetime.now())
        symbol = params.get("symbol")
        ticket = params.get("ticket")
        position = params.get("position")
        if ticket != None:
            deals = mt5.history_deals_get(
                ticket=ticket,
            )
        elif position != None:
            deals = mt5.history_deals_get(
                position=position,
            )
        else:
            if symbol != None:
                print("have")
                real_symbol = self.connection.find_symbol(symbol)
                deals = mt5.history_deals_get(
                    date_from,
                    date_to,
                    group=real_symbol,
                    # ticket=ticket,
                    # position=position,
                )
            else:
                deals = mt5.history_deals_get(
                    date_from,
                    date_to,
                )

        if deals is None:
            return []

        result = []
        for d in deals:
            result.append({
                "ticket": d.ticket,
                "order": d.order,
                "position_id": d.position_id,
                "symbol": d.symbol,
                "type": d.type,
                "entry": d.entry,
                "reason": d.reason,
                "volume": d.volume,
                "price": d.price,
                "commission": d.commission,
                "swap": d.swap,
                "fee": d.fee,
                "profit": d.profit,
                "comment": d.comment,
                "external_id": d.external_id,
                "time": datetime.fromtimestamp(d.time),
                "time_msc": d.time_msc
            })

        return result
