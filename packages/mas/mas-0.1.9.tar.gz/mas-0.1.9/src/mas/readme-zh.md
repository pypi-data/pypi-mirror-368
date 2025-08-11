# MAS Trading Library

[![PyPI version](https://img.shields.io/pypi/v/mas.svg)](https://pypi.org/project/mas/)
[![License](https://img.shields.io/github/license/yourname/mas-trading-lib.svg)](LICENSE)

> **PyPI Package Name:** `mas`
> **GitHub Repository:** `mas-trading-lib`

`mas` 是一款專為 **MetaTrader 5 (MT5)** 打造的 **Python 程式交易庫**，用於快速構建、回測與部署全自動化交易策略。
它支援 **即時市價/歷史資料存取、下單執行、策略回測、靜態 KPI 報表、動態買賣圖**，並可與 **WinForm GUI 桌面應用程式整合**。

這個套件特別適合 **外匯交易 (Forex)、黃金 (XAUUSD)、指數 (Index)、股票、加密貨幣 (Crypto)** 等市場，並針對 **量化交易者、金融工程師、自動化策略開發者** 提供完整工作流程，結合 **AI 交易助理**，即使沒有程式背景也能快速生成策略與回測報表。

---

## 📈 關鍵特點

* **MetaTrader 5 Python API 整合**：快速存取 MT5 平台的即時與歷史市場資料。
* **跨市場支援**：Forex、黃金、指數、加密貨幣皆可應用。
* **完整自動化交易流程**：資料 → 策略 → 回測 → KPI 報表 → 部署交易。
* **AI 策略生成器**：降低程式交易門檻，快速產生交易邏輯。
* **動態交易視覺化**：買賣點圖、資金曲線、持倉變化動態展示。
* **KPI & 風控報表**：Sharpe Ratio、Profit Factor、Win Rate、最大回撤等完整績效指標。
* **桌面應用整合**：支援 WinForm GUI，提供友好操作介面。
* **高擴充性**：模組化架構，適合量化交易系統與金融數據分析。

> 📌 **SEO 關鍵字**：MetaTrader5 Python Library, MT5 API, Automated Trading, Quantitative Trading, Backtesting, KPI Report, Forex Trading Bot, Algorithmic Trading SDK, AI Trading Assistant, MAS Trading Library, Python Quant Framework。

---

### 1️⃣ 註冊會員（必要步驟）

在安裝與使用 `mas` 之前，您必須先前往官方網站註冊帳號以啟用 API 與回測功能。

🔗 [前往官方網站註冊會員](https://mas.mindaismart.com/authentication/sign-up)

### 2️⃣ 安裝 Python 套件

```bash
pip install mas
```

### 3️⃣ 安裝 MAS 數據分析與回測軟體

此專案需要搭配 **MAS Backtest Tool** 才能產生完整的 KPI 報表與動態分析。

📥 [下載 MAS Backtest Tool](https://mindaismart/mas_soft)

安裝完成後，請確保該軟體已啟動，並使用註冊帳號登入，`mas` 才能正確連線並產生報表。

---
## 🌐 線上技術文件

📖 [查看完整技術文件](https://doc.mindaismart.com/)

![線上技術文件預覽](docs/images/doc.jpg)

---
## 🚀 快速開始

```python
import mas


class MAS_Client(mas):
    def __init__(self, toggle):
        super().__init__()
        self.index = 0
        self.hold = False
        self.ma = 0
        self.toggle = toggle
        self.order_id = None

    def receive_bars(self, symbol, data, is_end):
        single = self.index % self.ma

        if single == 0:
            if not self.hold:
                self.order_id = self.send_order({
                    "symbol": "EURUSD",
                    "order_type": "buy",
                    "volume": 0.1,
                    "backtest_toggle": self.toggle
                })
                self.hold = True
            else:
                self.send_order({
                    "symbol": "EURUSD",
                    "order_type": "sell",
                    "order_id": self.order_id,
                    "volume": 0.1,
                    "backtest_toggle": self.toggle
                })
                self.hold = False

        self.index = self.index+1
        if is_end:
            data = self.generate_data_report()
            data_source = data.get("data")
            print(data_source)
            self.generate_kpi_report()
            self.generate_trade_chart()


def main():
    try:
        toggle = True
        mas_c = MAS_Client(toggle)
        params = {
            "account": YOUR_ACCOUNT,
            "password": YOUR_PASSWORD,
            "server": YOUR_SERVER
        }

        mas_c.login(params)
        params = {
            "symbol": "EURUSD",
            "from": '2020-01-01',
            "to": '2024-12-31',
            "timeframe": "D1",
            "backtest_toggle": mas_c.toggle
        }
        mas_c.ma = 50
        df = mas_c.subscribe_bars(params)
    except Exception as e:
        return {
            'status': False,
            'error': str(e)
        }


if __name__ == "__main__":
    main()

```

---

## ✨ 功能特色

* ✅ **即時 & 歷史資料存取**（支援多種時間週期）
* ✅ **自動化下單 & 持倉管理**
* ✅ **策略回測引擎 & 績效指標**
* ✅ **靜態 KPI 報表（Sharpe Ratio, Profit Factor, Win Rate 等）**
* ✅ **動態交易視覺化（買賣點、資金曲線、持倉變化）**
* ✅ **WinForm GUI 整合，適合桌面應用**

---

## 📊 報表展示

### 完整資料數據

![完整資料數據範例](docs/images/soft_3.jpg)

### KPI 報表

![KPI報表範例](docs/images/report_1.jpg)

### 買賣訊號動態圖

![買賣訊號範例](docs/images/report_4.jpg)


> 📌 **提示**：這些圖片僅為展示，實際產出的報表會根據策略與回測資料動態生成。

---
## 🌍 官方網站 & AI 交易助理

🔗 [順星智能科技官方網站](https://mindaismart.com/)
### AI 交易助理
🤖 [使用 AI 交易助理（免寫程式快速生成策略）](https://mindaismart.com/product_ai)
### 輸入策略想法
![輸入策略想法](docs/images/ai_1.jpg)
### 策略範例輔助
![策略範例輔助](docs/images/ai_2.jpg)
### 補充與確認策略邏輯
![補充與確認策略邏輯](docs/images/ai_3.jpg)
### 進行數據分析&視覺化報表
![進行數據分析&視覺化報表](docs/images/ai_4.jpg)

---

## 📚 文件 & 資源

* [順星智能科技官方網站](https://mindaismart.com/)
* [註冊MAS專屬會員](https://mas.mindaismart.com/authentication/sign-up)
* [技術文件](https://doc.mindaismart.com/)
* [下載 MAS Backtest Tool](https://mindaismart/mas_soft)
* [GitHub](https://github.com/ma2750335/mas-trading-lib)
* [PyPI](https://pypi.org/project/mas/)
---

## 📄 授權

[API-License](docs/licenses/API-LICENSE)
