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

app = Flask(__name__)
api = Api(app)


client = Client("QZnNV8z2rEjhyu3Eq47NVZWmSRNCcJ7eej8xeDa4CEHxLGH2DBifj9IWF9XM9Rtj", "8Fnk1S8A8LaS2hGI1iz0Jqkieq3brIpuiyS7TaKVdDsGt0rD5xciJJ4FworHNXXJ")

brul = "https://api.binance.com"
endPoint = "/api/v1/order"


config = {
    "amount": 10,
    "marginType": "ISOLATED",
    "leverage": 1,
    "type": "MARKET"
}


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
    return (math.floor(cnum) * 1) / math.pow(10, i)


@app.route("/open-trade-future", methods=['POST'])
def openTradeFuture():
    # if request.method=="POST":
    data = json.loads(request.data)

    # set margin type
    # marginStatus=client.futures_change_margin_type(symbol="BTCUSDT",marginType="CROSSED")

    # set leverage
    leverage=client.futures_change_leverage(symbol=data["symbol"], leverage=config["leverage"])
    print(leverage)
    
    # current price
    symbolPrice = client.get_symbol_ticker(symbol=data["symbol"])

    # calculate asset amount
    symbol_info = client.get_symbol_info(data["symbol"])
    step_size = 0.0
    for f in symbol_info['filters']:
        if f['filterType'] == 'LOT_SIZE':
            step_size = float(f['stepSize'])
            precision = int(round(-math.log(step_size, 10), 0))
            precisedQuantity =   float(round(config["amount"]/float(symbolPrice["price"]), precision)) 
            
    
    if precisedQuantity > 0:
        quantity = math.floor(precisedQuantity)
        print(quantity)
    else:
        quantity = downward(precisedQuantity)
        print(quantity)

    

    # execute order
    # if data["side"] == "BUY" and data["positionSide"] == "LONG":
        # order=client.futures_create_order(symbol = data["symbol"], side = "BUY",positionSide="LONG", type = 'MARKET', quantity = quantity)
        # client.futures_create_order(symbol = data["symbol"], side = "BUY",positionSide="LONG", type = 'MARKET', quantity = quantity)
    # elif data["side"] == "SELL" and data["positionSide"] == "SHORT":
        # client.futures_create_order(symbol = data["symbol"], side = "SELL",positionSide="LONG", type = 'MARKET', quantity = quantity)
        # order=client.futures_create_order(symbol = data["symbol"], side = "SELL",positionSide="SHORT", type = 'MARKET', quantity = quantity)
    # order=client.futures_create_order(symbol = data["symbol"], side = data["side"],type = 'MARKET', closePosition=True)
    
    order=client.futures_create_order(symbol = data["symbol"], side = data["side"],positionSide=data["positionSide"], type = 'MARKET', quantity = quantity)
    print(order)
    
   
    return {"result" : order}
    
    


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
