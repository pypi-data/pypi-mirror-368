import MetaTrader5 as mt5
from mas.enum.env_setting import env_type
from mas.lang.i18n_strings import get_text, ConnectText


class ConnectionManager:
    def __init__(self):
        """
        初始化實例並設定連線狀態與商品代碼清單為預設值。

        Args:
            無

        Returns:
            無

        Initialize the instance and set default values for connection status and symbol list.

        Args:
            None

        Returns:
            None
        """
        self.is_connected = False
        self.all_code = None

    def is_not_platfrom(self):
        """
        判斷當前執行環境是否不是平台模式。

        Args:
            無

        Returns:
            bool: 若非平台模式則回傳 True，否則回傳 False。

        Determine whether the current execution environment is not in platform mode.

        Args:
            None

        Returns:
            bool: Returns True if not in platform mode; otherwise returns False.
        """
        return not env_type.platform.value

    def set_all_symbols(self, filter_tradeable=False):
        """
        從 MT5 載入所有商品代碼，並儲存至 self.all_code，可選擇只保留可交易商品。

        Args:
            filter_tradeable (bool): 是否只保留可交易的商品代碼，預設為 False。

        Returns:
            list[str]: 載入的商品代碼清單，若載入失敗則回傳空列表。

        Load all available symbol codes from MT5 and store them in self.all_code.
        Optionally filter to include only tradeable symbols.

        Args:
            filter_tradeable (bool): Whether to include only tradeable symbols. Default is False.

        Returns:
            list[str]: A list of loaded symbol names. Returns an empty list if loading fails.
        """
        all_symbols = mt5.symbols_get()
        if all_symbols is None:
            return []

        result = []
        for sym in all_symbols:
            if filter_tradeable and sym.trade_mode != mt5.SYMBOL_TRADE_MODE_FULL:
                continue
            result.append(sym.name)
        self.all_code = result

    def find_symbol(self, base_code: str):
        """
        根據輸入的簡化商品代碼，在已載入的商品清單中尋找最接近的完整商品代碼。

        Args:
            base_code (str): 基礎商品代碼字首（如 "USDJPY"）。

        Returns:
            str | None: 若找到匹配的完整商品代碼則回傳該字串，否則回傳 None。

        Find the best-matching full symbol code from the loaded symbol list using the given base code.

        Args:
            base_code (str): The base part of a symbol code (e.g., "USDJPY").

        Returns:
            str | None: Returns the best matching symbol string if found; otherwise returns None.
        """
        candidates = [code for code in self.all_code if code.startswith(base_code)]
        if not candidates:
            return None
        candidates.sort(key=lambda x: (len(x), x))
        return candidates[0]

    def login(self, params) -> bool:
        """
        嘗試登入 MT5 帳戶，並初始化連線與商品清單。登入失敗時會印出錯誤提示並拋出例外。

        Args:
            params (dict): 登入參數，需包含以下欄位：
                - account (int): MT5 帳戶號碼。
                - password (str): 密碼（可為空字串）。
                - server (str): 伺服器名稱。
                - timeout (int): 初始化逾時毫秒數，預設為 6000。

        Returns:
            bool: 登入成功則回傳 True，否則拋出例外。

        Attempt to log in to the MT5 account, initialize the connection, and load symbol list.
        If login fails, an error message will be printed and the exception will be raised.

        Args:
            params (dict): Login parameters. Must include:
                - account (int): MT5 account number.
                - password (str): Password string (can be empty).
                - server (str): Server name.
                - timeout (int): Connection timeout in milliseconds (default is 6000).

        Returns:
            bool: Returns True if login is successful; otherwise raises an exception.
        """
        account = params.get("account")
        password = params.get("password")
        server = params.get("server")
        timeout = int(params.get("timeout", 6000))

        try:
            if account == None:
                raise RuntimeError(
                        get_text(ConnectText.REQUIRED_PARAM_MISSING,param="account")
                    )
            account = int(account)
            if password == None:
                raise RuntimeError(
                        get_text(ConnectText.REQUIRED_PARAM_MISSING,param="password")
                    )
            if server == None:
                raise RuntimeError(
                        get_text(ConnectText.REQUIRED_PARAM_MISSING,param="server")
                    )
            
            if self.is_not_platfrom():
                if not mt5.initialize(login=account, password=password, server=server, timeout=timeout):
                    error_code, error_msg = mt5.last_error()
                    raise RuntimeError(
                        get_text(ConnectText.INIT_ERROR,msg=f"{error_code} - {error_msg}")
                    )
                self.set_all_symbols()
            self.is_connected = True
            return True

        except Exception as e:
            print(get_text(ConnectText.LOGIN_ERROR,msg=str(e)))
            raise e

        finally:
            if not self.is_connected and self.is_not_platfrom():
                try:
                    mt5.shutdown()
                except Exception as e:
                    print(get_text(ConnectText.SHUTDOWN_EXCEPTION,msg=str(e)))

    def initialize_mt5(self) -> bool:
        """
        初始化 MT5 並載入商品代碼清單（僅在非平台模式下執行）。

        Args:
            無

        Returns:
            bool: 若初始化成功則回傳 True；失敗則印出錯誤訊息並回傳 False。

        Initialize the MT5 terminal and load symbol list (only when not in platform mode).

        Args:
            None

        Returns:
            bool: Returns True if initialization is successful;
                  returns False and prints error message if it fails.
        """
        if self.is_not_platfrom():
            if not mt5.initialize():
                err = mt5.last_error()
                print(get_text(ConnectText.INIT_ERROR,msg=err))
                return False
            self.set_all_symbols()
        return True

    def shutdown_mt5(self) -> None:
        """
        關閉 MT5 連線並更新連線狀態（僅在非平台模式下執行），同時印出關閉提示訊息。

        Args:
            無

        Returns:
            無

        Shutdown the MT5 terminal and reset the connection status.
        This operation is performed only when not in platform mode. A shutdown message will be printed.

        Args:
            None

        Returns:
            None
        """
        if self.is_not_platfrom():
            mt5.shutdown()
        self.is_connected = False
        print(get_text(ConnectText.SHUTDOWN_MSG))

    def check_connection(self) -> bool:
        """
        檢查 MT5 是否已成功連線（僅在非平台模式下執行），並根據狀態印出提示訊息。

        Args:
            無

        Returns:
            bool: 若已連線則回傳 True，否則回傳 False 並印出錯誤提示。

        Check whether MT5 is connected (only in non-platform mode), and print status messages accordingly.

        Args:
            None

        Returns:
            bool: Returns True if connected; otherwise returns False and prints a warning message.
        """
        if self.is_not_platfrom():
            if not mt5.initialize():
                print("initialize() failed, error code =",mt5.last_error())
                quit()
            if not mt5.terminal_info():
                print(get_text(ConnectText.CONNECTION_NONE))
                return False
            print(get_text(ConnectText.CONNECTION_OK))
        return True

    def reconnect_mt5(self) -> bool:
        """
        重新連線 MT5：先關閉現有連線，再重新初始化 MT5。

        Args:
            無

        Returns:
            bool: 若重新連線成功則回傳 True，否則回傳 False。

        Reconnect to MT5 by first shutting down the current session and then reinitializing it.

        Args:
            None

        Returns:
            bool: Returns True if reconnection is successful; otherwise returns False.
        """
        self.shutdown_mt5()
        return self.initialize_mt5()
