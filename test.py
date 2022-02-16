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
import decimal 


app = Flask(__name__)
api = Api(app)


client = Client("QZnNV8z2rEjhyu3Eq47NVZWmSRNCcJ7eej8xeDa4CEHxLGH2DBifj9IWF9XM9Rtj", "8Fnk1S8A8LaS2hGI1iz0Jqkieq3brIpuiyS7TaKVdDsGt0rD5xciJJ4FworHNXXJ")



config = {
    "amount": 15,
    "marginType": "CROSSED",
    "leverage": 2,
    "type": "MARKET",
    "takeProfitPercent": 0.07,
    "callbackRate": 0.5,
    "percentForTralingStop":0.04,
    "stopMarketPercent":0.10,
    "phase":"BUY"
}

@app.route("/change-phase", methods=['POST'])
def phase():
    data = json.loads(request.data)
    old_phase=config["phase"]
    config["phase"] = data["phase"]
    return {"result": config,"old_phase":old_phase}




# fire orer and set take profit market
def fireOrder(symbol,side,type,quantity):
    try:
        if side == "BUY":
            client.futures_create_order(symbol = symbol, side = side,positionSide="LONG", type = type, quantity = quantity)
        else:
            client.futures_create_order(symbol = symbol, side = side,positionSide="SHORT", type = type, quantity = quantity)
    except BinanceAPIException as e:
        print(str(e))
        
        

def setTrailingStop(symbol,quantity,entryPrice,side):
    if side == "BUY":
        activationPrice = entryPrice+(entryPrice*config["percentForTralingStop"])/(config["leverage"])
        client.futures_create_order(symbol = symbol, side = "SELL",positionSide="LONG",activationPrice=activationPrice,callbackRate=config["callbackRate"], type = "TRAILING_STOP_MARKET", quantity = quantity)  
    elif side == "SELL":
        activationPrice = entryPrice-(entryPrice*config["percentForTralingStop"])/(config["leverage"])
        client.futures_create_order(symbol = symbol, side = "BUY",positionSide="SHORT",activationPrice=activationPrice,callbackRate=config["callbackRate"], type = "TRAILING_STOP_MARKET", quantity = quantity)
    
    
    


def maximumDecimalPlace(symbol):
    info = client.get_symbol_info(symbol)
    temp = info["filters"][0]["tickSize"]
    result = abs(decimal.Decimal(temp.rstrip('0')).as_tuple().exponent)
        
    return result
    

def setStopMarket(symbol,entryPrice,side):
    if side == "BUY":
        positionSide = "LONG"
        stopPrice = entryPrice-(entryPrice*config["stopMarketPercent"])/(config["leverage"])
        orderSide = "SELL"
    elif side == "SELL":
        positionSide = "SHORT"
        stopPrice = entryPrice+(entryPrice*config["stopMarketPercent"])/(config["leverage"])
        orderSide = "BUY"
    
    try:
        client.futures_create_order(
            closePosition=True,
            placeType="position",
            positionSide=positionSide,
            quantity=0,
            side=orderSide,
            stopPrice=round(stopPrice,maximumDecimalPlace(symbol=symbol)),
            symbol=symbol,
            timeInForce="GTE_GTC",
            type="STOP_MARKET",
            workingType="MARK_PRICE"  
        )
    except BinanceAPIException as e:
        print("ERROR_STOP_MARKET: "+str(e))
        

def cancelOrder(symbol):
    client.futures_cancel_all_open_orders(symbol=symbol)
    
        

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
def checkPhase():
    data=json.loads(request.data)
    if data["side"] == config["phase"]:
        openTradeFuture(data=data)
        return {"status":"execute success"}
    else:
        return {"message":"Invalid phase"}

def openTradeFuture(data):
    # data = json.loads(request.data)
    print(str(data))
    
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
            cancelOrder(symbol=data["symbol"])
            fireOrder(symbol = data["symbol"], side = side, type = 'MARKET', quantity = quantity)
            setTrailingStop(symbol = data["symbol"], quantity = quantity,entryPrice=float(symbolPrice["price"]), side = side)
            setStopMarket(symbol = data["symbol"],entryPrice=float(symbolPrice["price"]),side = side)
            client.futures_create_order(symbol = data["symbol"], side = side,positionSide="SHORT", type = 'MARKET', quantity = quantity)
        except BinanceAPIException as e:
            print(str(e))
    elif side == "SELL":
        try:
            cancelOrder(symbol=data["symbol"])
            fireOrder(symbol = data["symbol"], side = side,type = 'MARKET', quantity = quantity)
            setTrailingStop(symbol = data["symbol"], quantity = quantity,entryPrice=float(symbolPrice["price"]), side = side)
            setStopMarket(symbol = data["symbol"],entryPrice=float(symbolPrice["price"]),side = side)
            client.futures_create_order(symbol = data["symbol"], side = side,positionSide="LONG", type = 'MARKET', quantity = quantity)  
        except BinanceAPIException as e:
            print(str(e))
    
   
    return {"symbol" : data["symbol"],"Margin": quantity}
    
    


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
