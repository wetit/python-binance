from flask import Flask, request
from flask_restful import Api, Resource
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.client import Client
from binance.helpers import round_step_size
from datetime import datetime
from binance.exceptions import BinanceAPIException
import os
import json
import math
import mysql.connector

app = Flask(__name__)
api = Api(app)


client = Client("QZnNV8z2rEjhyu3Eq47NVZWmSRNCcJ7eej8xeDa4CEHxLGH2DBifj9IWF9XM9Rtj", "8Fnk1S8A8LaS2hGI1iz0Jqkieq3brIpuiyS7TaKVdDsGt0rD5xciJJ4FworHNXXJ")



config = {
    "amount": 15,
    "marginType": "CROSSED",
    "leverage": 2,
    "type": "MARKET",
    "takeProfitPercent": 0.07,
    "callbackRate": 1,
    "percentForTralingStop":0.03,
}

@app.route("/test", methods=['GET'])
def connect():
    mydb = mysql.connector.connect(
    host="us-cdbr-east-05.cleardb.net",
    user="b5a353e80bc919",
    password="419690e3",
    database="heroku_8669fd8463fbb6"
    )
    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM config")

    myresult = mycursor.fetchone()

    print(myresult)
    return 'success'



# fire orer and set take profit market
def fireOrder(symbol,side,type,quantity):
    try:
        if side == "BUY":
            client.futures_create_order(symbol = symbol, side = side,positionSide="LONG", type = type, quantity = quantity)
            # client.futures_create_order(symbol = symbol, side = side,positionSide="LONG", type = "TAKE_PROFIT_MARKET",stopPrice = price + (price*config["takeProfitPercent"]))
        else:
            client.futures_create_order(symbol = symbol, side = side,positionSide="SHORT", type = type, quantity = quantity)
            # client.futures_create_order(symbol = symbol, side = side,positionSide="SHORT", type = "TAKE_PROFIT_MARKET",stopPrice = price - (price*config["takeProfitPercent"]))
    except BinanceAPIException as e:
        print(str(e))
        
        

def setTrailingStop(symbol,quantity,entryPrice,side):
    if side == "BUY":
        activationPrice = entryPrice+(entryPrice*config["percentForTralingStop"])/(config["leverage"])
        client.futures_create_order(symbol = symbol, side = "SELL",positionSide="LONG",activationPrice=activationPrice,callbackRate=1, type = "TRAILING_STOP_MARKET", quantity = quantity)  
    elif side == "SELL":
        activationPrice = entryPrice-(entryPrice*config["percentForTralingStop"])/(config["leverage"])
        client.futures_create_order(symbol = symbol, side = "BUY",positionSide="SHORT",activationPrice=activationPrice,callbackRate=1, type = "TRAILING_STOP_MARKET", quantity = quantity)
    
    print('activation_price: '+ str(activationPrice))
    
        

@app.route("/", methods=['GET'])
def test():
    time=datetime.fromtimestamp(int("1641723878511")/1000)
    return {"message": time}

def downward(value):
    round(value) 
    i = 0
    cnum = value
    while (cnum != 0 and cnum < 1):
        cnum *= 10;
        i = i+1;
    return (cnum * 1) / math.pow(10, i)


@app.route("/open-trade-future", methods=['POST'])
def openTradeFuture():
    data = json.loads(request.data)

    # set margin type
    try:
        client.futures_change_margin_type(symbol=data["symbol"],marginType=config["marginType"])
    except BinanceAPIException as e:
        print(str(e))

    # set leverage
    leverage=client.futures_change_leverage(symbol=data["symbol"], leverage=config["leverage"])
    print(leverage)
    
    # current price
    symbolPrice = client.get_symbol_ticker(symbol=data["symbol"])

 
    precisedQuantity= config["amount"]/float(symbolPrice["price"])

            
    # quantity=precisedQuantity
    if precisedQuantity > 0:
        quantity = round(precisedQuantity) * config["leverage"]
        print('Margin:'+str(quantity))
    else:
        quantity = downward(precisedQuantity)
        print(quantity)

    side = data["side"].upper()
    
    if side == "BUY":
        try:
            fireOrder(symbol = data["symbol"], side = side, type = 'MARKET', quantity = quantity)
            setTrailingStop(symbol = data["symbol"], quantity = quantity,entryPrice=float(symbolPrice["price"]), side = side)
            client.futures_create_order(symbol = data["symbol"], side = side,positionSide="SHORT", type = 'MARKET', quantity = quantity)
        except BinanceAPIException as e:
            print(str(e))
    elif side == "SELL":
        try:
            fireOrder(symbol = data["symbol"], side = side,type = 'MARKET', quantity = quantity)
            setTrailingStop(symbol = data["symbol"], quantity = quantity,entryPrice=float(symbolPrice["price"]), side = side)
            client.futures_create_order(symbol = data["symbol"], side = side,positionSide="LONG", type = 'MARKET', quantity = quantity)  
        except BinanceAPIException as e:
            print(str(e))
    
    # if side == "SELL":
    #     try:
    #         fireOrder(symbol = data["symbol"], side = side,type = 'MARKET', quantity = quantity)
    #         setTrailingStop(symbol = data["symbol"], quantity = quantity,entryPrice=float(symbolPrice["price"]), side = side)
    #         client.futures_create_order(symbol = data["symbol"], side = side,positionSide="LONG", type = 'MARKET', quantity = quantity)  
    #     except BinanceAPIException as e:
    #         print(str(e))
    
   
    return {"symbol" : data["symbol"],"Margin": quantity}
    
    


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
