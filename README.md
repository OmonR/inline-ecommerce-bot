# Aiogram E-commerce Bot

This is a feature-rich Telegram bot designed for e-commerce, with an emphasis on an **interactive inline catalogue**. The catalogue improves user experience by offering a more dynamic and faster alternative to traditional inline buttons and Telegram web apps.

## Key Features:
- **Interactive Inline Catalogue**: A faster, more engaging shopping experience.
- **Order Management**: Users and admins can easily manage orders, cancel them, and leave comments.
- **Cryptobot Integration**: Currently supports payments via Cryptobot (soon to be replaced with a more mainstream option).
- **Admin Panel**: Manage products and orders with functions to add, delete, or list all orders.

## Prerequisites

- **Python 3.8+** must be installed on your system. You can download Python [here](https://www.python.org/downloads/).
- **Telegram Bot Token**: You will need to create a bot via [BotFather](https://core.telegram.org/bots#botfather) on Telegram and obtain a token.

## Project Initialization

1. Clone the Repository
```
git clone https://github.com/OmonR/inline-ecommerce-bot.git
```
2. Move to the project folder 
```
cd inline-ecommerce-bot
```
3. Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
4. Install the required dependencies
```
pip install -r requirements.txt
```
5. Create a file named .env in the project root directory to store your environment variables.
```
API_TOKEN=1234567890:AABcDe0fg0H0IG0K0L_M0nOPqRstUVwxyZ0 #fill it with real data
API_CRYPTO_TOKEN=234567:AABcDe0fg0H0IG0K0LmnopQQrst0U13
ADMIN_ID=1234567890

MIN_ORDER_PRICE=1000.0
ADDRESSES=Москва. Казакова 3А, Санкт-Петербург. Невский проспект 1
```
6. Run bot.py
```bash
python bot.py```
