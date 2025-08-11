
from enum import Enum

DEFAULT_LANG = "en"


def switch_lang():
    """
    切換目前語系設定（中英文互換）。

    若當前語系為 'zh' 則切換為 'en'，反之亦然。

    Toggle the current language between Chinese (zh) and English (en).

    Returns:
        None
    """
    global DEFAULT_LANG
    DEFAULT_LANG = "zh-tw" if DEFAULT_LANG == "zh-tw" else "en"


def get_current_lang():
    """
    取得目前使用的語系設定。

    Returns:
        str: 語系字串，如 'zh' 或 'en'。

    Get the currently active language code.

    Returns:
        str: Language code string, such as 'zh' or 'en'.
    """
    return DEFAULT_LANG


class ClientText(Enum):
    SERVER_ERROR = "❌ Cannot connect to MAS server. Make sure the soft is running."
    DOWNLOAD_HINT = "Or visit mindaismart.com to download MAS Soft."
    TRADE_SUCCESS = "✅ Successfully generated trade report."
    KPI_SUCCESS = "✅ Successfully generated KPI report."
    DATA_SUCCESS = "✅ Successfully generated full report."
    UNKNOWN_ERROR = "❌ Error: {msg}"


class ConnectText(Enum):
    LOGIN_ERROR = "[Login Error] Login failed: {msg}"
    INIT_ERROR = "[Initialize Error] MT5 initialization failed: {msg}"
    SHUTDOWN_EXCEPTION = "⚠️ MT5 shutdown raised exception: {msg}"
    CONNECTION_NONE = "[Connection Check] MT5 is not connected"
    CONNECTION_OK = "[Connection Check] MT5 connection is active"
    SHUTDOWN_MSG = "[Shutdown] MT5 connection closed"
    REQUIRED_PARAM_MISSING = "{param} is a required parameter"


class HistoryText(Enum):
    MISSING_PARAMS = "[HistoryData] ❌ Missing 'symbol', 'from', or 'to'"
    UNSUPPORTED_MODE = "[HistoryData] ⚠️ Unsupported mode: '{mode}', fallback to 'all'"
    TICK_FAIL = "[HistoryData] ❌ Failed to retrieve tick data for: {symbol}"
    NO_DATA = "[MT5] ⚠️ No data for: {symbol} {start} ~ {end}"
    COPY_FAIL = "[MT5] ❌ Failed to fetch data: {msg}"


class MarketText(Enum):
    TICK_ALL_STOP = "❎ All Tick subscriptions stopped"
    BAR_ALL_STOP = "❎ All Bar subscriptions stopped"
    TICK_NO_SYMBOL = "❌ Tick subscription failed: missing symbol"
    TICK_ALREADY_SUBSCRIBED = "⚠️ {symbol} already subscribed for Tick. Ignored."
    TICK_SUBSCRIBED = "✅ Subscribed Tick: {symbol}, interval = {interval}ms"
    TICK_READ_ERROR = "❌ Tick read error: {msg}"
    TICK_UNSUB_NO_SYMBOL = "❌ Tick unsubscribe failed: missing symbol"
    TICK_UNSUB_NOT_EXIST = "⚠️ No valid subscription found: {symbol}"
    TICK_UNSUB_SUCCESS = "❎ Unsubscribed Tick: {symbol}"

    BAR_NO_SYMBOL = "❌ Bar subscription failed: missing symbol or timeframe"
    BAR_UNSUPPORTED_TF = "❌ Unsupported timeframe: {timeframe}"
    BAR_ALREADY_SUBSCRIBED = "⚠️ {key_name} already subscribed. Ignored."
    BAR_INIT_FAIL = "❌ MT5 initialize failed"
    BAR_SUB_ERROR = "❌ Bar subscription error: {msg}"
    BAR_SUBSCRIBED = "✅ Subscribed: {symbol} / {timeframe}"
    BAR_UNSUB_NO_SYMBOL = "❌ Bar unsubscribe failed: missing symbol or timeframe"
    BAR_UNSUB_NOT_EXIST = "⚠️ No valid subscription found: {key_name}"
    BAR_UNSUB_SUCCESS = "❎ Unsubscribed Bar: {key_name}"


class TradeText(Enum):
    MISSING_ORDER_PARAMS = "Missing required fields: symbol/order_type/volume"
    INIT_FAILED = "Initialization failed"
    NOT_LOGGED_IN = "MT5 not logged in"
    NO_TICK_INFO = "Cannot get tick info"
    UNSUPPORTED_ORDER_TYPE = "Unsupported order_type: {order_type}"
    ORDER_FAILED = "Order failed: {msg}"
    MODIFY_MISSING_PARAMS = "Please provide order_id and price"
    MODIFY_NO_RESPONSE = "No response, please check initialization/login"
    MODIFY_FAILED = "Modify failed: {msg}"
    MODIFY_SUCCESS = "Modify success: {msg}"
    CANCEL_MISSING_ORDER_ID = "Please provide order_id"
    CANCEL_NO_RESPONSE = "No response, check MT5 login/init"
    CANCEL_FAILED = "Cancel failed: {msg}"
    CANCEL_SUCCESS = "Successfully canceled order: {order_id}"
    EXCEPTION_ERROR = "Exception error: {error}"


class VirtualTradeText(Enum):
    MISSING_SYMBOL = "Missing 'symbol' parameter"
    NO_CURRENT_BAR = "No current K-bar, cannot record order time"
    MODIFY_MISSING_ORDER_ID = "Missing 'order_id', cannot modify order"
    ORDER_ID_NOT_FOUND = "Order not found: order_id={order_id}"
    CANCEL_MISSING_PARAMS = "Missing 'symbol' or 'order_id'"
    CANCEL_SUCCESS = "Successfully cancelled virtual order {order_id}"
    CANCEL_NOT_FOUND = "Cannot find virtual order {order_id}, cancel failed"

# 中英文訊息對照表，每種語言對應一組 Enum 的翻譯
# A dictionary mapping Enum message keys to translations in different languages
i18n_map = {
    "zh-tw": {
        ClientText.SERVER_ERROR: "❌ 無法連線到 mas 伺服器，請確認是否已開啟 soft。",
        ClientText.DOWNLOAD_HINT: "或者去 mindaismart.com 下載 mas soft",
        ClientText.TRADE_SUCCESS: "✅ 成功產生買賣點報表",
        ClientText.KPI_SUCCESS: "✅ 成功產生 KPI 報表",
        ClientText.DATA_SUCCESS: "✅ 成功產生完整報表",
        ClientText.UNKNOWN_ERROR: "❌ 錯誤：{msg}",

        ConnectText.LOGIN_ERROR: "[登入錯誤] 登入失敗：{msg}",
        ConnectText.INIT_ERROR: "[初始化錯誤] MT5初始化失敗：{msg}",
        ConnectText.SHUTDOWN_EXCEPTION: "⚠️ MT5 shutdown 發生例外：{msg}",
        ConnectText.CONNECTION_NONE: "[連線檢查] 尚未連線到MT5",
        ConnectText.CONNECTION_OK: "[連線檢查] MT5連線正常",
        ConnectText.SHUTDOWN_MSG: "[關閉] MT5已關閉",
        ConnectText.REQUIRED_PARAM_MISSING: "{param} 為必要參數",

        HistoryText.MISSING_PARAMS: "[歷史資料] ❌ 缺少 symbol、from 或 to 參數",
        HistoryText.UNSUPPORTED_MODE: "[歷史資料] ⚠️ 不支援的模式：'{mode}'，改為 'all'",
        HistoryText.TICK_FAIL: "[歷史資料] ❌ 無法取得 Tick 資料：{symbol}",
        HistoryText.NO_DATA: "[MT5] ⚠️ 無資料：{symbol} {start} ~ {end}",
        HistoryText.COPY_FAIL: "[MT5] ❌ 擷取資料失敗：{msg}",

        MarketText.TICK_ALL_STOP: "❎ 所有 Tick 訂閱已取消",
        MarketText.BAR_ALL_STOP: "❎ 所有 Bar 訂閱已取消",
        MarketText.TICK_NO_SYMBOL: "❌ 訂閱 Tick 失敗：缺少 symbol",
        MarketText.TICK_ALREADY_SUBSCRIBED: "⚠️ {symbol} 已訂閱 Tick，忽略重複訂閱。",
        MarketText.TICK_SUBSCRIBED: "✅ 成功訂閱 Tick：{symbol}，每 {interval}ms 檢查一次",
        MarketText.TICK_READ_ERROR: "❌ Tick 讀取錯誤：{msg}",
        MarketText.TICK_UNSUB_NO_SYMBOL: "❌ 取消訂閱 Tick 失敗：缺少 symbol",
        MarketText.TICK_UNSUB_NOT_EXIST: "⚠️ 無有效 Tick 訂閱：{symbol}",
        MarketText.TICK_UNSUB_SUCCESS: "❎ 成功取消訂閱 Tick：{symbol}",
        MarketText.BAR_NO_SYMBOL: "❌ 訂閱失敗：缺少 symbol 或 timeframe",
        MarketText.BAR_UNSUPPORTED_TF: "❌ 不支援的 timeframe：{timeframe}",
        MarketText.BAR_ALREADY_SUBSCRIBED: "⚠️ {key_name} 已訂閱，忽略重複訂閱",
        MarketText.BAR_INIT_FAIL: "❌ MT5 初始化失敗",
        MarketText.BAR_SUB_ERROR: "❌ Bar 訂閱錯誤：{msg}",
        MarketText.BAR_SUBSCRIBED: "✅ 已訂閱：{symbol} / {timeframe}",
        MarketText.BAR_UNSUB_NO_SYMBOL: "❌ 取消訂閱 Bar 失敗：缺少 symbol 或 timeframe",
        MarketText.BAR_UNSUB_NOT_EXIST: "⚠️ 無有效訂閱存在：{key_name}",
        MarketText.BAR_UNSUB_SUCCESS: "❎ 成功取消訂閱 Bar：{key_name}",

        TradeText.MISSING_ORDER_PARAMS: "❌ 缺少必要參數 symbol/order_type/volume",
        TradeText.INIT_FAILED: "❌ 初始化失敗",
        TradeText.NOT_LOGGED_IN: "❌ 尚未登入 MT5",
        TradeText.NO_TICK_INFO: "❌ 無法取得 Tick 資訊",
        TradeText.UNSUPPORTED_ORDER_TYPE: "❌ 不支援 order_type: {order_type}",
        TradeText.ORDER_FAILED: "❌ 下單失敗：{msg}",
        TradeText.MODIFY_MISSING_PARAMS: "❌ 請提供 order_id 與 price",
        TradeText.MODIFY_NO_RESPONSE: "❌ 回傳 None，請確認初始化或登入狀況",
        TradeText.MODIFY_FAILED: "❌ 修改失敗：{msg}",
        TradeText.MODIFY_SUCCESS: "✅ 修改成功：{msg}",
        TradeText.CANCEL_MISSING_ORDER_ID: "❌ 請提供 order_id",
        TradeText.CANCEL_NO_RESPONSE: "❌ 無回傳結果，請檢查初始化與登入狀態",
        TradeText.CANCEL_FAILED: "❌ 取消失敗：{msg}",
        TradeText.CANCEL_SUCCESS: "✅ 成功取消訂單：{order_id}",
        TradeText.EXCEPTION_ERROR: "❌ 例外錯誤: {error}",

        VirtualTradeText.MISSING_SYMBOL: "❌ 缺少 symbol 參數",
        VirtualTradeText.NO_CURRENT_BAR: "⚠️ 無目前 K 棒，無法記錄下單時間",
        VirtualTradeText.MODIFY_MISSING_ORDER_ID: "❌ 缺少 order_id，無法修改訂單",
        VirtualTradeText.ORDER_ID_NOT_FOUND: "❌ 找不到對應的掛單 order_id={order_id}",
        VirtualTradeText.CANCEL_MISSING_PARAMS: "❌ 缺少 symbol 或 order_id",
        VirtualTradeText.CANCEL_SUCCESS: "❎ 已取消模擬掛單 {order_id}",
        VirtualTradeText.CANCEL_NOT_FOUND: "⚠️ 找不到掛單 {order_id}，取消失敗"
    },
    "en": {
        ClientText.SERVER_ERROR: "❌ Cannot connect to MAS server. Make sure the soft is running.",
        ClientText.DOWNLOAD_HINT: "Or visit mindaismart.com to download MAS Soft.",
        ClientText.TRADE_SUCCESS: "✅ Successfully generated trade report.",
        ClientText.KPI_SUCCESS: "✅ Successfully generated KPI report.",
        ClientText.DATA_SUCCESS: "✅ Successfully generated full report.",
        ClientText.UNKNOWN_ERROR: "❌ Error: {msg}",

        ConnectText.LOGIN_ERROR: "[Login Error] Login failed: {msg}",
        ConnectText.INIT_ERROR: "[Initialize Error] MT5 initialization failed: {msg}",
        ConnectText.SHUTDOWN_EXCEPTION: "⚠️ MT5 shutdown raised exception: {msg}",
        ConnectText.CONNECTION_NONE: "[Connection Check] MT5 is not connected",
        ConnectText.CONNECTION_OK: "[Connection Check] MT5 connection is active",
        ConnectText.SHUTDOWN_MSG: "[Shutdown] MT5 connection closed",
        ConnectText.REQUIRED_PARAM_MISSING: "{param} is a required parameter",

        HistoryText.MISSING_PARAMS: "[HistoryData] ❌ Missing 'symbol', 'from', or 'to'",
        HistoryText.UNSUPPORTED_MODE: "[HistoryData] ⚠️ Unsupported mode: '{mode}', fallback to 'all'",
        HistoryText.TICK_FAIL: "[HistoryData] ❌ Failed to retrieve tick data for: {symbol}",
        HistoryText.NO_DATA: "[MT5] ⚠️ No data for: {symbol} {start} ~ {end}",
        HistoryText.COPY_FAIL: "[MT5] ❌ Failed to fetch data: {msg}",

        MarketText.TICK_ALL_STOP: "❎ All Tick subscriptions stopped",
        MarketText.BAR_ALL_STOP: "❎ All Bar subscriptions stopped",
        MarketText.TICK_NO_SYMBOL: "❌ Tick subscription failed: missing symbol",
        MarketText.TICK_ALREADY_SUBSCRIBED: "⚠️ {symbol} already subscribed for Tick. Ignored.",
        MarketText.TICK_SUBSCRIBED: "✅ Subscribed Tick: {symbol}, interval = {interval}ms",
        MarketText.TICK_READ_ERROR: "❌ Tick read error: {msg}",
        MarketText.TICK_UNSUB_NO_SYMBOL: "❌ Tick unsubscribe failed: missing symbol",
        MarketText.TICK_UNSUB_NOT_EXIST: "⚠️ No valid subscription found: {symbol}",
        MarketText.TICK_UNSUB_SUCCESS: "❎ Unsubscribed Tick: {symbol}",
        MarketText.BAR_NO_SYMBOL: "❌ Bar subscription failed: missing symbol or timeframe",
        MarketText.BAR_UNSUPPORTED_TF: "❌ Unsupported timeframe: {timeframe}",
        MarketText.BAR_ALREADY_SUBSCRIBED: "⚠️ {key_name} already subscribed. Ignored.",
        MarketText.BAR_INIT_FAIL: "❌ MT5 initialize failed",
        MarketText.BAR_SUB_ERROR: "❌ Bar subscription error: {msg}",
        MarketText.BAR_SUBSCRIBED: "✅ Subscribed: {symbol} / {timeframe}",
        MarketText.BAR_UNSUB_NO_SYMBOL: "❌ Bar unsubscribe failed: missing symbol or timeframe",
        MarketText.BAR_UNSUB_NOT_EXIST: "⚠️ No valid subscription found: {key_name}",
        MarketText.BAR_UNSUB_SUCCESS: "❎ Unsubscribed Bar: {key_name}",

        TradeText.MISSING_ORDER_PARAMS: "❌ Missing required fields: symbol/order_type/volume",
        TradeText.INIT_FAILED: "❌ Initialization failed",
        TradeText.NOT_LOGGED_IN: "❌ MT5 not logged in",
        TradeText.NO_TICK_INFO: "❌ Cannot get tick info",
        TradeText.UNSUPPORTED_ORDER_TYPE: "❌ Unsupported order_type: {order_type}",
        TradeText.ORDER_FAILED: "❌ Order failed: {msg}",
        TradeText.MODIFY_MISSING_PARAMS: "❌ Please provide order_id and price",
        TradeText.MODIFY_NO_RESPONSE: "❌ No response, please check initialization/login",
        TradeText.MODIFY_FAILED: "❌ Modify failed: {msg}",
        TradeText.MODIFY_SUCCESS: "✅ Modify success: {msg}",
        TradeText.CANCEL_MISSING_ORDER_ID: "❌ Please provide order_id",
        TradeText.CANCEL_NO_RESPONSE: "❌ No response, check MT5 login/init",
        TradeText.CANCEL_FAILED: "❌ Cancel failed: {msg}",
        TradeText.CANCEL_SUCCESS: "✅ Successfully canceled order: {order_id}",
        TradeText.EXCEPTION_ERROR: "❌ Exception error: {error}",

        VirtualTradeText.MISSING_SYMBOL: "❌ Missing 'symbol' parameter",
        VirtualTradeText.NO_CURRENT_BAR: "⚠️ No current K-bar, cannot record order time",
        VirtualTradeText.MODIFY_MISSING_ORDER_ID: "❌ Missing 'order_id', cannot modify order",
        VirtualTradeText.ORDER_ID_NOT_FOUND: "❌ Order not found: order_id={order_id}",
        VirtualTradeText.CANCEL_MISSING_PARAMS: "❌ Missing 'symbol' or 'order_id'",
        VirtualTradeText.CANCEL_SUCCESS: "❎ Successfully cancelled virtual order {order_id}",
        VirtualTradeText.CANCEL_NOT_FOUND: "⚠️ Cannot find virtual order {order_id}, cancel failed"
    }
}


def get_text(key: Enum, lang: str = None, **kwargs) -> str:
    """
    根據目前語系或指定語系，取得對應的多語系訊息，支援格式化參數（如 {msg}, {symbol} 等）。

    Args:
        key (Enum): Enum 成員，例如 ClientText.SERVER_ERROR。
        lang (str, optional): 語系代碼（預設使用目前語系），支援 'zh' 或 'en'。
        **kwargs: 可填入訊息模板中的動態變數。

    Returns:
        str: 對應語系的文字訊息，若翻譯不存在則回傳原始 Enum value。

    Retrieve a localized string based on the current or specified language.
    Supports dynamic string formatting via template variables (e.g., {msg}, {symbol}).

    Args:
        key (Enum): Enum member, such as ClientText.SERVER_ERROR.
        lang (str, optional): Language code, defaults to current language. Supports 'zh' or 'en'.
        **kwargs: Keyword arguments used to populate message templates.

    Returns:
        str: The localized message. Falls back to Enum's default value if translation not found.
    """
    if lang is None:
        lang = get_current_lang()  # ✅ 你的語系切換邏輯
    template = i18n_map.get(lang, {}).get(key, key.value)
    return template.format(**kwargs)  # ✅ 支援 {error}, {msg}, {order_id} 等變數

