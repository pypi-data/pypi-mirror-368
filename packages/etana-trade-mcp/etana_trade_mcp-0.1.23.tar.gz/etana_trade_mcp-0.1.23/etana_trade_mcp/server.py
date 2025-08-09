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
async def get_trading_accounts(username: str = Field(description="username usually an email address")) -> str:
    """Get all trading accounts from the Etana trading system
    Args:
        username: user's name usually their email address
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
async def get_order_book(buy_security_symbol: str = Field(description="symbol of the secrity that you want to buy"),
                         sell_security_symbol: str = Field(description="symbol of the secrity that you want to sell")
    ) -> str:
    """Get the order book for buy and sell trading pairs from the Etana trading system
    Args:
        buy_security_symbol: symbol of the secrity that you want to buy
        sell_security_symbol: symbol of the secrity that you want to sell
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    security_id = str(f"{buy_security_symbol}{sell_security_symbol}")

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
        return(order_book['status_code'])

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
async def create_order(buy_security_symbol: str = Field(description="symbol of the secrity that you want to buy"),
                       sell_security_symbol: str = Field(description="symbol of the secrity that you want to sell"),
                       side: str = Field(description="side of the order. The value can be buy or sell"),
                       quantity: str = Field(description="amount to buy or sell"),
                       )-> str:
    """Get a historical list of orders from the Etana trading system
    Args:
        buy_security_symbol: symbol of the secrity that you want to buy
        sell_security_symbol: symbol of the secrity that you want to sell
        side: side of the order. The value can be buy or sell
        quantity: amount to buy or sell
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    security_id = str(f"{buy_security_symbol}{sell_security_symbol}")

    REQUEST = str(f"/api/v1/orders/history")
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

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

