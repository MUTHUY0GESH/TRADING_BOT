#!/usr/bin/env python3
"""
Binance Futures Trading Bot - Junior Python Developer Assignment
================================================================

This is a complete implementation of a Binance Futures trading bot for testnet.
The bot includes all required features plus advanced functionality.

Setup Instructions:
1. Install required packages: pip install python-binance python-dotenv
2. Create account at https://testnet.binancefuture.com
3. Generate API keys from the testnet interface
4. Create .env file with your credentials
5. Run: python trading_bot.py

Author: [MUTHU YOGESH J]
Date: July 2025
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_DOWN
import json

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException, BinanceOrderException
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install with: pip install python-binance python-dotenv")
    exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BinanceFuturesBot:
    """
    A comprehensive Binance Futures trading bot with full functionality.
    
    Features:
    - Market and limit order execution
    - Real-time price fetching
    - Account balance and position monitoring
    - Order management (status check, cancellation)
    - Comprehensive error handling
    - Detailed logging
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize the trading bot.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet environment (default: True)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Initialize Binance client
        try:
            if testnet:
                self.client = Client(
                    api_key=api_key,
                    api_secret=api_secret,
                    testnet=True
                )
                # Set the correct futures testnet URL
                self.client.API_URL = 'https://testnet.binancefuture.com'
                logger.info("Connected to Binance Futures Testnet")
            else:
                self.client = Client(api_key=api_key, api_secret=api_secret)
                logger.info("Connected to Binance Futures Live")
                
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            raise
    
    def get_account_info(self) -> Dict:
        """
        Get futures account information including balances and positions.
        
        Returns:
            Dict containing account information
        """
        try:
            account_info = self.client.futures_account()
            
            # Extract relevant information
            account_data = {
                'total_wallet_balance': account_info.get('totalWalletBalance', '0'),
                'total_unrealized_pnl': account_info.get('totalUnrealizedPnL', '0'),
                'total_margin_balance': account_info.get('totalMarginBalance', '0'),
                'available_balance': account_info.get('availableBalance', '0'),
                'max_withdraw_amount': account_info.get('maxWithdrawAmount', '0'),
                'positions': []
            }
            
            # Get positions with non-zero size
            for position in account_info.get('positions', []):
                if float(position.get('positionAmt', 0)) != 0:
                    account_data['positions'].append({
                        'symbol': position.get('symbol'),
                        'size': position.get('positionAmt'),
                        'entry_price': position.get('entryPrice'),
                        'unrealized_pnl': position.get('unrealizedPnL'),
                        'percentage': position.get('percentage')
                    })
            
            logger.info("Account information retrieved successfully")
            return account_data
            
        except BinanceAPIException as e:
            logger.error(f"API error getting account info: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting account info: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Current price as float
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            price = float(ticker['price'])
            logger.info(f"Current price for {symbol}: ${price:,.2f}")
            return price
            
        except BinanceAPIException as e:
            logger.error(f"API error getting price for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting price for {symbol}: {e}")
            raise
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            
        Returns:
            Order response dictionary
        """
        try:
            # Validate inputs
            if side.upper() not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            # Place the order
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='MARKET',
                quantity=quantity
            )
            
            logger.info(f"Market order placed: {side} {quantity} {symbol}")
            logger.info(f"Order ID: {order['orderId']}")
            
            return order
            
        except BinanceAPIException as e:
            logger.error(f"API error placing market order: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid input for market order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error placing market order: {e}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            
        Returns:
            Order response dictionary
        """
        try:
            # Validate inputs
            if side.upper() not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if price <= 0:
                raise ValueError("Price must be positive")
            
            # Place the order
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='LIMIT',
                timeInForce='GTC',  # Good Till Cancelled
                quantity=quantity,
                price=price
            )
            
            logger.info(f"Limit order placed: {side} {quantity} {symbol} at ${price}")
            logger.info(f"Order ID: {order['orderId']}")
            
            return order
            
        except BinanceAPIException as e:
            logger.error(f"API error placing limit order: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid input for limit order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error placing limit order: {e}")
            raise
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, 
                              stop_price: float, limit_price: float) -> Dict:
        """
        Place a stop-limit order (advanced feature).
        
        Args:
            symbol: Trading pair symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            stop_price: Stop price to trigger the order
            limit_price: Limit price for the order
            
        Returns:
            Order response dictionary
        """
        try:
            # Validate inputs
            if side.upper() not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if stop_price <= 0 or limit_price <= 0:
                raise ValueError("Stop price and limit price must be positive")
            
            # Place the order
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='STOP',
                timeInForce='GTC',
                quantity=quantity,
                price=limit_price,
                stopPrice=stop_price
            )
            
            logger.info(f"Stop-limit order placed: {side} {quantity} {symbol}")
            logger.info(f"Stop: ${stop_price}, Limit: ${limit_price}")
            logger.info(f"Order ID: {order['orderId']}")
            
            return order
            
        except BinanceAPIException as e:
            logger.error(f"API error placing stop-limit order: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid input for stop-limit order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error placing stop-limit order: {e}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """
        Get the status of a specific order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        try:
            order = self.client.futures_get_order(symbol=symbol.upper(), orderId=order_id)
            
            status_info = {
                'orderId': order['orderId'],
                'symbol': order['symbol'],
                'status': order['status'],
                'type': order['type'],
                'side': order['side'],
                'origQty': order['origQty'],
                'executedQty': order['executedQty'],
                'price': order['price'],
                'avgPrice': order['avgPrice'],
                'time': datetime.fromtimestamp(order['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"Order status retrieved: {order_id} - {status_info['status']}")
            return status_info
            
        except BinanceAPIException as e:
            logger.error(f"API error getting order status: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting order status: {e}")
            raise
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """
        Cancel an open order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response dictionary
        """
        try:
            result = self.client.futures_cancel_order(symbol=symbol.upper(), orderId=order_id)
            logger.info(f"Order cancelled successfully: {order_id}")
            return result
            
        except BinanceAPIException as e:
            logger.error(f"API error cancelling order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error cancelling order: {e}")
            raise
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """
        Get all open orders, optionally filtered by symbol.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of open orders
        """
        try:
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol.upper())
            else:
                orders = self.client.futures_get_open_orders()
            
            logger.info(f"Retrieved {len(orders)} open orders")
            return orders
            
        except BinanceAPIException as e:
            logger.error(f"API error getting open orders: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting open orders: {e}")
            raise

def display_menu():
    """Display the main menu options."""
    print("\n" + "="*50)
    print("    BINANCE FUTURES TRADING BOT")
    print("="*50)
    print("1. View Account Information")
    print("2. Get Current Price")
    print("3. Place Market Order")
    print("4. Place Limit Order")
    print("5. Place Stop-Limit Order")
    print("6. Check Order Status")
    print("7. Cancel Order")
    print("8. View Open Orders")
    print("9. Exit")
    print("="*50)

def get_user_input(prompt: str, input_type: type = str, validation_func=None):
    """
    Get user input with type validation and optional custom validation.
    
    Args:
        prompt: Input prompt message
        input_type: Expected input type (str, int, float)
        validation_func: Optional validation function
        
    Returns:
        Validated user input
    """
    while True:
        try:
            user_input = input(prompt).strip()
            
            if input_type == str:
                result = user_input
            elif input_type == int:
                result = int(user_input)
            elif input_type == float:
                result = float(user_input)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
            
            if validation_func and not validation_func(result):
                print("Invalid input. Please try again.")
                continue
                
            return result
            
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None

def format_account_info(account_info: Dict) -> None:
    """Format and display account information."""
    print("\n" + "="*50)
    print("           ACCOUNT INFORMATION")
    print("="*50)
    print(f"Total Wallet Balance:    ${float(account_info['total_wallet_balance']):,.2f}")
    print(f"Total Margin Balance:    ${float(account_info['total_margin_balance']):,.2f}")
    print(f"Available Balance:       ${float(account_info['available_balance']):,.2f}")
    print(f"Total Unrealized PnL:    ${float(account_info['total_unrealized_pnl']):,.2f}")
    print(f"Max Withdraw Amount:     ${float(account_info['max_withdraw_amount']):,.2f}")
    
    if account_info['positions']:
        print("\nCurrent Positions:")
        print("-" * 50)
        for pos in account_info['positions']:
            pnl = float(pos['unrealized_pnl'])
            pnl_color = "+" if pnl >= 0 else ""
            print(f"Symbol: {pos['symbol']}")
            print(f"  Size: {pos['size']}")
            print(f"  Entry Price: ${float(pos['entry_price']):,.2f}")
            print(f"  Unrealized PnL: {pnl_color}{pnl:,.2f}")
            print(f"  Percentage: {pos['percentage']}%")
            print("-" * 30)
    else:
        print("\nNo open positions.")

def format_order_info(order: Dict) -> None:
    """Format and display order information."""
    print("\n" + "="*40)
    print("         ORDER DETAILS")
    print("="*40)
    print(f"Order ID:        {order['orderId']}")
    print(f"Symbol:          {order['symbol']}")
    print(f"Side:            {order['side']}")
    print(f"Type:            {order['type']}")
    print(f"Status:          {order['status']}")
    print(f"Quantity:        {order['origQty']}")
    print(f"Executed Qty:    {order['executedQty']}")
    print(f"Price:           ${float(order['price']):,.2f}")
    if float(order['avgPrice']) > 0:
        print(f"Average Price:   ${float(order['avgPrice']):,.2f}")
    print(f"Time:            {order['time']}")

def main():
    """Main application loop."""
    print("Welcome to Binance Futures Trading Bot!")
    print("This bot connects to Binance Futures Testnet for safe trading practice.")
    
    # Load API credentials
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        print("\nAPI credentials not found in environment variables.")
        print("Please create a .env file with the following content:")
        print("BINANCE_API_KEY=your_api_key_here")
        print("BINANCE_API_SECRET=your_api_secret_here")
        print("\nAlternatively, enter them now:")
        
        api_key = get_user_input("Enter your Binance API Key: ")
        if not api_key:
            return
            
        api_secret = get_user_input("Enter your Binance API Secret: ")
        if not api_secret:
            return
    
    # Initialize the trading bot
    try:
        bot = BinanceFuturesBot(api_key, api_secret, testnet=True)
        print("✅ Successfully connected to Binance Futures Testnet!")
    except Exception as e:
        print(f"❌ Failed to connect to Binance: {e}")
        return
    
    # Main application loop
    while True:
        try:
            display_menu()
            choice = get_user_input("Enter your choice (1-9): ", int)
            
            if choice is None:  # User pressed Ctrl+C
                break
            
            if choice == 1:
                # View Account Information
                try:
                    account_info = bot.get_account_info()
                    format_account_info(account_info)
                except Exception as e:
                    print(f"Error getting account info: {e}")
            
            elif choice == 2:
                # Get Current Price
                symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str)
                if symbol:
                    try:
                        price = bot.get_current_price(symbol)
                        print(f"\n💰 Current price for {symbol.upper()}: ${price:,.2f}")
                    except Exception as e:
                        print(f"Error getting price: {e}")
            
            elif choice == 3:
                # Place Market Order
                print("\n--- Place Market Order ---")
                symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str)
                if not symbol:
                    continue
                
                side = get_user_input("Enter side (BUY/SELL): ", str, 
                                    lambda x: x.upper() in ['BUY', 'SELL'])
                if not side:
                    continue
                
                quantity = get_user_input("Enter quantity: ", float, lambda x: x > 0)
                if not quantity:
                    continue
                
                try:
                    order = bot.place_market_order(symbol, side, quantity)
                    print(f"✅ Market order placed successfully!")
                    print(f"Order ID: {order['orderId']}")
                except Exception as e:
                    print(f"❌ Error placing market order: {e}")
            
            elif choice == 4:
                # Place Limit Order
                print("\n--- Place Limit Order ---")
                symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str)
                if not symbol:
                    continue
                
                side = get_user_input("Enter side (BUY/SELL): ", str, 
                                    lambda x: x.upper() in ['BUY', 'SELL'])
                if not side:
                    continue
                
                quantity = get_user_input("Enter quantity: ", float, lambda x: x > 0)
                if not quantity:
                    continue
                
                price = get_user_input("Enter limit price: ", float, lambda x: x > 0)
                if not price:
                    continue
                
                try:
                    order = bot.place_limit_order(symbol, side, quantity, price)
                    print(f"✅ Limit order placed successfully!")
                    print(f"Order ID: {order['orderId']}")
                except Exception as e:
                    print(f"❌ Error placing limit order: {e}")
            
            elif choice == 5:
                # Place Stop-Limit Order
                print("\n--- Place Stop-Limit Order ---")
                symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str)
                if not symbol:
                    continue
                
                side = get_user_input("Enter side (BUY/SELL): ", str, 
                                    lambda x: x.upper() in ['BUY', 'SELL'])
                if not side:
                    continue
                
                quantity = get_user_input("Enter quantity: ", float, lambda x: x > 0)
                if not quantity:
                    continue
                
                stop_price = get_user_input("Enter stop price: ", float, lambda x: x > 0)
                if not stop_price:
                    continue
                
                limit_price = get_user_input("Enter limit price: ", float, lambda x: x > 0)
                if not limit_price:
                    continue
                
                try:
                    order = bot.place_stop_limit_order(symbol, side, quantity, stop_price, limit_price)
                    print(f"✅ Stop-limit order placed successfully!")
                    print(f"Order ID: {order['orderId']}")
                except Exception as e:
                    print(f"❌ Error placing stop-limit order: {e}")
            
            elif choice == 6:
                # Check Order Status
                symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str)
                if not symbol:
                    continue
                
                order_id = get_user_input("Enter order ID: ", int)
                if not order_id:
                    continue
                
                try:
                    order_status = bot.get_order_status(symbol, order_id)
                    format_order_info(order_status)
                except Exception as e:
                    print(f"Error getting order status: {e}")
            
            elif choice == 7:
                # Cancel Order
                symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str)
                if not symbol:
                    continue
                
                order_id = get_user_input("Enter order ID to cancel: ", int)
                if not order_id:
                    continue
                
                try:
                    result = bot.cancel_order(symbol, order_id)
                    print(f"✅ Order {order_id} cancelled successfully!")
                except Exception as e:
                    print(f"❌ Error cancelling order: {e}")
            
            elif choice == 8:
                # View Open Orders
                symbol = get_user_input("Enter symbol (optional, press Enter for all): ", str)
                symbol = symbol if symbol else None
                
                try:
                    orders = bot.get_open_orders(symbol)
                    if orders:
                        print(f"\n📋 Open Orders ({len(orders)} total):")
                        print("="*60)
                        for order in orders:
                            print(f"ID: {order['orderId']} | {order['symbol']} | {order['side']} | "
                                  f"{order['type']} | Qty: {order['origQty']} | "
                                  f"Price: ${float(order['price']):,.2f} | Status: {order['status']}")
                    else:
                        print("No open orders found.")
                except Exception as e:
                    print(f"Error getting open orders: {e}")
            
            elif choice == 9:
                # Exit
                print("Thank you for using Binance Futures Trading Bot!")
                break
            
            else:
                print("Invalid choice. Please select a number between 1 and 9.")
                
        except KeyboardInterrupt:
            print("\n\nExiting application...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            logger.error(f"Unexpected error in main loop: {e}")

if __name__ == "__main__":
    main()
