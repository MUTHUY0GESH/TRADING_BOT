# 🔥 Binance Futures Trading Bot

A complete CLI-based trading bot for **Binance Futures Testnet**, developed in Python.  
Built as part of the **Junior Python Developer - Crypto Trading Bot** application.

---

## ✅ Features

- Connects to Binance Futures Testnet
- Place **Market**, **Limit**, and **Stop-Limit** Orders
- View Account Info (balance, PnL, open positions)
- Get Real-Time Prices
- Cancel Orders & Check Order Status
- CLI-based menu system
- Full error handling and logging to file

---

## 📦 Setup Instructions

### 1. Clone & Navigate
```bash
git clone https://github.com/MUTHUYOGESH/TRADING_BOT.git
cd TRADING_BOT

### 2. INSTALL REQUIREMENTS

pip install -r requirements.txt

### 3. ADD YOUR API CREDENTIALS

BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret

https://testnet.binancefuture.com/en/futures/BTCUSDT  ### USE THIS LINK AND LOGIN SCROLL DOWN THERE IS OPTIONS LIKE 'POSITION' 'OPEN ORDER' MOVE RIGHT SIDE - THERE WILL BE API MANAGEMENT AND COPY THE SECRET KEY AND API KEY AND PASTE IN TO THE .env file 

### 4 . RUN THE BOT

python trading_bot.py

### 5. SAMPLE OUTPUT

Welcome to Binance Futures Trading Bot!
✅ Successfully connected to Binance Futures Testnet!

1. View Account Information
2. Get Current Price
3. Place Market Order
...

Enter your choice (1-9): 3

--- Place Market Order ---
Enter symbol (e.g., BTCUSDT): BTCUSDT
Enter side (BUY/SELL): BUY
Enter quantity: 0.01

✅ Market order placed successfully!
Order ID: 5272361185

### 6. logs

Logs are saved in trading_bot.log, including:

# Connection status
# Order executions
# API errors
# User inputs & validation
