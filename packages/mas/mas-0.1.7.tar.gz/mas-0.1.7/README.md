# MAS Trading Library

[![PyPI version](https://img.shields.io/pypi/v/mas.svg)](https://pypi.org/project/mas/)
[![License](https://img.shields.io/github/license/yourname/mas-trading-lib.svg)](LICENSE)

> **PyPI Package Name:** `mas`
<!-- > **GitHub Repository:** `mas-trading-lib` -->

`mas` is a **Python trading library** built specifically for **MetaTrader 5 (MT5)** to quickly build, backtest, and deploy fully automated trading strategies.
It supports **real-time and historical market data access, order execution, strategy backtesting, static KPI reports, and dynamic trade visualization**, and can be integrated with **WinForm GUI desktop applications**.

This library is ideal for **Forex trading, Gold (XAUUSD), Indices, Stocks, and Cryptocurrencies**, offering a complete workflow for **quantitative traders, financial engineers, and automated strategy developers**. With the built-in **AI Trading Assistant**, even non-programmers can easily generate strategies and backtest reports.

---

## 📈 Key Features

* **MetaTrader 5 Python API Integration**: Fast access to MT5 real-time and historical market data.
* **Cross-Market Support**: Works for Forex, Gold, Indices, and Cryptocurrencies.
* **Full Automated Trading Workflow**: From data → strategy → backtest → KPI report → live deployment.
* **AI Strategy Generator**: Lowers the barrier to entry for automated trading by generating strategies quickly.
* **Dynamic Trading Visualization**: Displays trade signals, equity curves, and position changes in real-time.
* **KPI & Risk Reports**: Includes Sharpe Ratio, Profit Factor, Win Rate, Maximum Drawdown, and more.
* **Desktop App Integration**: Supports WinForm GUI for user-friendly desktop applications.
* **Highly Modular**: Designed for scalable quantitative trading systems and financial data analysis.

> 📌 **SEO Keywords**: MetaTrader5 Python Library, MT5 API, Automated Trading, Quantitative Trading, Backtesting, KPI Report, Forex Trading Bot, Algorithmic Trading SDK, AI Trading Assistant, MAS Trading Library, Python Quant Framework.

---

## 📦 Installation

### 1️⃣ Register an Account (Required)

Before installing and using `mas`, you must register on the official website to activate API and backtesting features.

🔗 [Register on the Official Website](https://mas.mindaismart.com/authentication/sign-up)

### 2️⃣ Install the Python Package

```bash
pip install mas
```

### 3️⃣ Install the MAS Data Analysis & Backtest Tool

This project requires the **MAS Backtest Tool** to generate complete KPI reports and dynamic analytics.

📥 [Download MAS Backtest Tool](https://mindaismart.com/product_lib)

After installation, ensure the tool is running and log in with your registered account. `mas` will then be able to connect and generate reports properly.

---

## 🚀 Quick Start

```python
import mas

class MASStrategy(mas):
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

        self.index += 1
        if is_end:
            data = self.generate_data_report()
            data_source = data.get("data")
            print(data_source)
            self.generate_kpi_report()
            self.generate_trade_chart()

def main():
    try:
        toggle = True
        mas_c = MASStrategy(toggle)
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

## 🌐 Online Documentation

📖 [View Full Documentation](https://doc.mindaismart.com/)

![Online Documentation Preview](https://github.com/ma2750335/mas-img/blob/main/lib/lib_1.jpg?raw=true)

---

## 📊 Report Previews

### Full Data Report

![Full Data Report Example](https://github.com/ma2750335/mas-img/blob/main/lib/lib_4.jpg?raw=true)

### KPI Report

![KPI Report Example](https://github.com/ma2750335/mas-img/blob/main/lib/lib_5.jpg?raw=true)

### Trade Signal Visualization

![Trade Signal Example](https://github.com/ma2750335/mas-img/blob/main/lib/lib_8.jpg?raw=true)

> 📌 **Note**: These images are for demonstration purposes only. Actual reports will be generated based on your strategies and backtest data.

---

## 🌍 Official Website & AI Trading Assistant

🔗 [Mas Intelligent Technology Official Website](https://mindaismart.com/)
🤖 [Use AI Trading Assistant (No Coding Required)](https://mindaismart.com/product_ai)

### AI Trading Workflow Previews

#### Input Your Strategy Ideas

![Input Strategy Ideas](https://github.com/ma2750335/mas-img/blob/main/ai/ai_1.jpg?raw=true)

#### Strategy Example Assistance

![Strategy Example Assistance](https://github.com/ma2750335/mas-img/blob/main/ai/ai_2.jpg?raw=true)

#### Confirm and Refine Logic

![Confirm and Refine Logic](https://github.com/ma2750335/mas-img/blob/main/ai/ai_3.jpg?raw=true)

#### Perform Data Analysis & Generate Reports

![Data Analysis & Reports](https://github.com/ma2750335/mas-img/blob/main/ai/ai_4.jpg?raw=true)

---

## 📚 Resources

* [Official Website](https://mindaismart.com/)
* [Official Website Registration](https://mas.mindaismart.com/authentication/sign-up)
* [Documentation](https://doc.mindaismart.com/)
* [Download MAS Backtest Tool](https://mindaismart.com/product_lib)
<!-- * [GitHub](https://github.com/ma2750335/mas-trading-lib) -->
* [PyPI](https://pypi.org/project/mas/)

---

## 📄 License

[API-License](https://mindaismart.com/terms_api)
