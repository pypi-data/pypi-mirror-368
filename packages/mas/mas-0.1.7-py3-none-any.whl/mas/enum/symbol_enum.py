class SymbolSettingEnum:
    """
    儲存每個交易商品（symbol）的點差費用與數值精度設定，供回測與交易系統引用。

    This class stores spread fee and decimal precision settings for each trading symbol,
    used for backtesting or trading logic.

    Attributes:
        _settings (dict): 商品代碼對應的費用設定與精度設定，如 fee（點差）與 decimal_nub（價格刻度因子）。
    """
    _settings = {
        "AUDUSD": {"fee": 2.0, "decimal_nub": 10000},
        "EURUSD": {"fee": 1.5, "decimal_nub": 10000},
        "USDJPY": {"fee": 1.8, "decimal_nub": 100},
        "GBPUSD": {"fee": 2.5, "decimal_nub": 10000},
        "NZDUSD": {"fee": 2.5, "decimal_nub": 10000},
        "USDCAD": {"fee": 2.5, "decimal_nub": 10000},
        "EURJPY": {"fee": 3.0, "decimal_nub": 100},
        "GBPJPY": {"fee": 4.0, "decimal_nub": 100},
        "AUDJPY": {"fee": 3.0, "decimal_nub": 100},
        "NZDJPY": {"fee": 3.5, "decimal_nub": 100},
        "CADJPY": {"fee": 3.5, "decimal_nub": 100},
        "EURAUD": {"fee": 3.5, "decimal_nub": 10000},
        "EURNZD": {"fee": 4.5, "decimal_nub": 10000},
        "EURCAD": {"fee": 3.5, "decimal_nub": 10000},
        "GBPAUD": {"fee": 4.0, "decimal_nub": 10000},
        "GBPNZD": {"fee": 5.0, "decimal_nub": 10000},
        "GBPCAD": {"fee": 4.0, "decimal_nub": 10000},
        "AUDNZD": {"fee": 3.5, "decimal_nub": 10000},
        "NZDCAD": {"fee": 4.0, "decimal_nub": 10000},
        "XAUUSD": {"fee": 50.0, "decimal_nub": 100},
        "AUDCAD": {"fee": 3.0, "decimal_nub": 10000},
        "EURGBP": {"fee": 2.5, "decimal_nub": 10000}
    }

    @classmethod
    def get_setting(cls, code: str) -> dict:
        """
        根據商品代碼取得對應的費用與精度設定，若查無則回傳預設值。

        Args:
            code (str): 商品代碼（如 "EURUSD", "XAUUSD"）。

        Returns:
            dict: 對應的設定資料，包含：
                - fee (float): 該商品的點差費用。
                - decimal_nub (int): 該商品的價格刻度因子。
              若查無資料，則回傳 {"fee": 0.0, "decimal_nub": 10000}。

        Retrieve the fee and decimal precision settings for a given symbol.
        If the symbol is not found, a default setting will be returned.

        Args:
            code (str): Symbol code (e.g., "EURUSD", "XAUUSD").

        Returns:
            dict: A settings dictionary including:
                - fee (float): Spread fee for the symbol.
                - decimal_nub (int): Decimal scaling factor.
              If not found, returns {"fee": 0.0, "decimal_nub": 10000}.
        """
        return cls._settings.get(code, {"fee": 0.0, "decimal_nub": 10000})
