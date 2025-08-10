from typing import Any
from datetime import datetime
import httpx
from mcp.server.fastmcp import FastMCP
import pandas as pd
from pydantic import BaseModel, Field
import base64
import hmac
import json
import os
import time
from math import ceil
from urllib.parse import urlparse
import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

# Initialize FastMCP server
mcp = FastMCP("etana-trade-mcp")

config = json.load(open("/app/data/config.json"))

PRIVATE_API_KEY = config["trader"]["api_key_private"]
KEY_ID = config["trader"]["api_key_id"]
HOST = config["trader"]["host"]
REQUEST = config["trader"]["rest_request"]
PARAMS = config["trader"]["request_params"]
nonce = 0
session = {}

def numberToBytes(number):
    return number.to_bytes((ceil((number.bit_length() + 1) / 8)), "big")


def numberFromBytes(bytes):
    return int.from_bytes(bytes, byteorder="big")


def numberFromBase64(base64string):
    return numberFromBytes(base64.decodebytes(base64string.encode()))

def sign_request(method: str, url, params={}, headers={}, body=""):
    global session
    nonce = time.time_ns()
    if "id" not in session.keys():
        attempt = requests.post(HOST + "/api/v1/login/attempt", json={
            "api_key_id": KEY_ID
        }).json()

        session.update({
            "id": attempt["session_id"],
            "base": numberFromBase64(attempt["dh_base"]),
            "modulus": numberFromBase64(attempt["dh_modulus"]),
            "secret": numberFromBytes(os.urandom(512)),
        })
        print("Successfully started login attempt")

        digest = SHA256.new()
        digest.update(base64.decodebytes(attempt["challenge"].encode()))

        rsa = pkcs1_15.new(RSA.importKey(base64.decodebytes(PRIVATE_API_KEY.encode())))
        dh_public_key = pow(session["base"], session["secret"], session["modulus"])

        confirmation_body = {
            "session_id": session["id"],
            "signature": base64.encodebytes(rsa.sign(digest)).decode().replace("\n", ""),
            "dh_key": base64.encodebytes(numberToBytes(dh_public_key)).decode().replace("\n", "")
        }
        confirmation = requests.post(HOST + "/api/v1/login/confirm", json=confirmation_body).json()
        print("Successfully confirmed a session login")

        dh_server_public_key = numberFromBase64(confirmation["dh_key"])
        dh_common_secret = pow(dh_server_public_key, session["secret"], session["modulus"])
        session.update({
            "common_secret": dh_common_secret,
            "common_secret_bytes": numberToBytes(dh_common_secret),
            "server_public_key": dh_server_public_key
        })

    serialized_body = json.dumps(body) if isinstance(body, dict) else str(body)

    sorted_param_keys = sorted(params.keys())

    payload = method.upper() + \
              urlparse(url).path.lower() + \
              "&".join([key.lower() + "=" + params[key] for key in sorted_param_keys]) + \
              "X-Deltix-Nonce=" + str(nonce) + \
              "&X-Deltix-Session-Id=" + str(session["id"]) + \
              serialized_body

    print(payload)
    HMAC = hmac.new(session["common_secret_bytes"], payload.encode(), "sha384")
    digest = HMAC.digest()
    signature = base64.encodebytes(digest).decode().replace("\n", "")
    return (signature, nonce, serialized_body)


def request(method: str, url, params={}, headers={}, body=""):
    global session
    signature, nonce, serialized_body = sign_request(method, url, params, headers, body)
    headers.update({
        "X-Deltix-Signature": signature,
        "X-Deltix-Nonce": str(nonce),
        "X-Deltix-Session-Id": session["id"],
        "Content-Type": "application/json"
    })
    
    try:
        ret = requests.request(method, url, params=params, headers=headers, data=serialized_body)
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    return ret


@mcp.tool()
async def get_trading_accounts() -> str:
    """Get all trading accounts from the Etana trading system
    Args:
        None
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    REQUEST = str(f"/api/v1/accounts")
    RPARAMS = {}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        accounts = get.json()
        print(get.json())
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in accounts:
        return(accounts['status_code'])

    accounts_new = []
    for i in range(len(accounts)):
        data_dict = {  
            "currency":accounts[i]['currency_id'],
            "balance":float(accounts[i]['balance']),
            "available_for_trading":float(accounts[i]['available_for_trading']),
            "available_for_withdrawal":float(accounts[i]['available_for_withdrawal']),
            "status":accounts[i]['status'] }
        accounts_new.append(data_dict)  

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(accounts_new)

    #For Openwebui formatting
    table = "Currency | Balance | Available for Trading | Available for Withdraw | Status" + '\n' + "| :--- | :--- | :--- | :---  | :---" + '\n'

    for index, row in df.iterrows():
        table = table + str(f"{row['currency']} | {row['balance']:,.2f} | {row['available_for_trading']:,.2f} | {row['available_for_withdrawal']:,.2f} | {row['status']}") + '\n'
    
    answer = str(f"Here's your current account information from the Etana Trading system" + '\n' + table)
    return answer

@mcp.tool()
async def get_order_book(security_symbol: str = Field(default="none",description="trading symbol of the secrity that you want to buy or sell. Examples would be BTC for Bitcoin, ETH for Ethereum as crypto currencies and USD for US Dollar, EUR for Euro for European Union currency as Fiat currencies. Use uppercase characters only."),
                         trading_pair : str = Field(default="none",description="trading pair symbol that you want to buy or sell. Examples would be BTCUSD, ETHUSD for crypto trades and EURUSD, GBPUSD for Fiat trades. Use uppercase characters only. ")
    ) -> str:
    """Get the order book to buy and sell crypto or fiat currencies from the Etana trading system. Accepts security symbol like BTC for bitcoin or EUR for European Union from the Etana trading system. 2 arguments are available. 
    You do not have to provide values for both, but must provide a value for at least one argument.
    Example of using the first argument - User question: Can I get the order book for bitcoin? : buy_security_symbol would be BTC
    Example of using the second argument - User question: Can I get the order book for buy BTC with USD? or Can I get the order book for BTCUSD? : trading_pair would be BTCUSD
    
    Args:
        security_symbol: trading symbol of the security that you want to buy or sell. Examples would be BTC for Bitcoin, ETH for Ethereum as crypto currencies and USD for US Dollar, EUR for European Union currency as Fiat currencies. Use uppercase characters only.
        trading_pair : trading pair symbol that you want to buy or sell. Examples would be BTCUSD, ETHUSD for crypto trades and EURUSD, GBPUSD for Fiat trades. Use uppercase characters only.
    """    
    global nonce 
    nonce = 0
    global session
    session = {}
    err_msg  = str(f"trading pair could not be obtained by the our large language model. Please ask for securities that can be traded.")
    
    if security_symbol != "none":
        security_id = str(f"{security_symbol}USD")
    elif trading_pair != "none":
        security_id = str(f"{trading_pair}")
    else:
        security_id = str(f"EtanaAI could not figure out the trading pair")
       

    REQUEST = str(f"/api/v1/books/{security_id}")
    RPARAMS = {"limit_asks":"5","limit_bids":"5"}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        order_book = get.json()
        print(get.json())
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in order_book:
        return(order_book['status_code']+ ' ' + err_msg)

    order_book_new = []
    for i in range(len(order_book)):
        milliseconds_string = order_book[i]['timestamp']
        milliseconds = int(milliseconds_string)
        seconds = milliseconds / 1000
        dt = datetime.utcfromtimestamp(seconds)  
        dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")
        for j in range(len(order_book[i]['entries'])):
            data_dict = {   
                "trading_pair":order_book[i]['security_id'],
                "price":float(order_book[i]['entries'][j]['price']),
                "quantity":float(order_book[i]['entries'][j]['quantity']),
                "exchange":order_book[i]['entries'][j]['exchange_id']}
            order_book_new.append(data_dict)  

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(order_book_new)

    #For Openwebui formatting
    table = "Trading Pair | Price | Quantity | Exchange" + '\n' + "| :--- | :--- | :---  | :---" + '\n'

    for index, row in df.iterrows():
        table = table + str(f"{row['trading_pair']} | {row['price']:,} | {row['quantity']:,} | {row['exchange']}") + '\n'
    
    answer = str(f"Here's your the order book for {security_id} as of {dt_string} from the Etana Trading system" + '\n' + table)   
    return answer

@mcp.tool()
async def get_order_history(start_time: str = Field(description="The start time of the order history list")) -> str:
    """Get a historical list of orders from the Etana trading system
    Args:
        start_time: The start time of the order history list. If user does not specify, set to 0 as default

    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    REQUEST = str(f"/api/v1/orders/history")
    RPARAMS = {"startTime":start_time}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        order_history = get.json()
        print(get.json())
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in order_history:
        return(order_history['status_code'])

    order_history_new = []
    for i in range(len(order_history)):
        milliseconds_string = order_history[i]['timestamp']
        milliseconds = int(milliseconds_string)
        seconds = milliseconds / 1000
        dt = datetime.utcfromtimestamp(seconds)
        dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")
        data_dict = {  
            "datetime":dt_string,
            "security":order_history[i]['security_id'],
            "status":order_history[i]['status'],
            "type":order_history[i]['type'],
            "side":order_history[i]['side'],
            "quantity":float(order_history[i]['quantity']),
            "average_price":float(order_history[i]['average_price'])
         }
        order_history_new.append(data_dict)  

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(order_history_new)

    #For Openwebui formatting
    table = "Date | Security | Status | Type | Side | Quantity | Average Price" + '\n' + "| :--- | :--- | :--- | :---  | :--- | :---  | :---" + '\n'

    for index, row in df.iterrows():
        table = table + str(f"{row['datetime']} | {row['security']} | {row['status']} | {row['type']} | {row['side']} | {row['quantity']:,.2f} | {row['average_price']:,.2f} ") + '\n'
    
    answer = str(f"Here's your historical list of orders " + '\n' + table)
    return answer

@mcp.tool()
async def create_and_execute_order(security_symbol: str = Field(default="none",description="trading symbol of the secrity that you want to buy or sell. Examples would be BTC for Bitcoin, ETH for Ethereum as crypto currencies and USD for US Dollar, EUR for Euro for European Union currency as Fiat currencies. Use uppercase characters only."),
                       trading_pair : str = Field(default="none",description="trading pair symbol that you want to buy or sell. Examples would be BTCUSD, ETHUSD for crypto trades and EURUSD, GBPUSD for Fiat trades. Use uppercase characters only."),
                       side: str = Field(description="side of the order. The value can be buy or sell"),
                       quantity: str = Field(description="amount to buy or sell"),
                       )-> str:
    """To trade on the Etana trading system, you must create and execute an order on a trading pair from the order book. You must decide to use the
    security symbol that you want to buy or sell or use the trading pair you want to buy or sell. Do not use both arguements, use either security_symbol
    or trading_pair.

    Example of using the first argument - User question: I want to buy 5 bitcoin? : security_symbol = BTC, side = buy, and quantity = 5
    Example of using the second argument - User question: I want to buy 5 BTC with USD? or I want to buy 5 BTCUSD? : trading_pair = BTCUSD, side = buy, and quantity = 5

    Args:
        security_symbol: trading symbol of the security that you want to buy or sell. Examples would be BTC for Bitcoin, ETH for Ethereum as crypto currencies and USD for US Dollar, EUR for European Union currency as Fiat currencies. Use uppercase characters only.
        trading_pair : trading pair symbol that you want to buy or sell. Examples would be BTCUSD, ETHUSD for crypto trades and EURUSD, GBPUSD for Fiat trades. Use uppercase characters only.
        side: side of the order. The value can be buy or sell
        quantity: amount to buy or sell
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    err_msg  = str(f"trading pair could not be obtained by the our large language model. Please ask for securities that can be traded.")
    
    if security_symbol != "none":
        security_id = str(f"{security_symbol}USD")
    elif trading_pair != "none":
        security_id = str(f"{trading_pair}")
    else:
        security_id = str(f"EtanaAI could not figure out the trading pair")
       

    REQUEST = str(f"/api/v1/orders")
    RBODY = {"security_id":str(f"{security_id}"),
                 "type":"market",        #Can add limit orders later
                 "side":str(f"{side}"),
                 "time_in_force":"ioc",  #Immediate or Cancel
                 "quantity":str(f"{quantity}"),
                 "destination":"SSOR",   #Defaulting SSOR, can add destinations later
                 "source":"AIUI"}

    try:
        post = request("POST", HOST + REQUEST, body=RBODY)
        create_order = post.json()
        print(post.json())
    except requests.JSONDecodeError:
        print(post.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in create_order:
        return(create_order['status_code'])

    milliseconds_string = create_order['receipt_time']
    milliseconds = int(milliseconds_string)
    seconds = milliseconds / 1000
    dt = datetime.utcfromtimestamp(seconds)
    receipt_time_string = dt.strftime("%Y-%m-%d %H:%M:%S")

    answer = str(f"Your {create_order['side']} order of {create_order['quantity']} {create_order['security_id']} was created at {receipt_time_string}. You can ask about your order history if you would like to see it." )
    return answer

@mcp.tool()
async def get_trading_securities() -> str:
    """Get all securities the from the Etana trading system
    Args:
        None
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    REQUEST = str(f"/api/v1/securities")
    RPARAMS = {}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        securities = get.json()
        print(get.json())
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in accounts:
        return(securities['status_code'])

    securities_new = []
    destinations = ""
    for i in range(len(securities)):
        for j in range(len(securities[i]["available_destinations"])):
            destinations = destinations + securities[i]["available_destinations"][j] + " "
    
        data_dict = {  
            "name":securities[i]['name'],
            "type":securities[i]['type'],
            "destinations":destinations
        }
        securities_new.append(data_dict)  

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(securities_new)

    #For Openwebui formatting
    table = "Trading Pair, Type, Destinations" + '\n' + "| :---  | :--- | :--- " + '\n'
    for index, row in df.iterrows():
        table = table + str(f"{row['name']} | {row['type']} | {row['destinations']}") + '\n'
    
    answer = str(f"The Etana Trading system supports the following trading pairs " + '\n' + table)
    return answer


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

