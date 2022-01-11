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



config = {
    "amount": 15,
    "marginType": "CROSSED",
    "leverage": 2,
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
    print('precisedQuantity:'+str(precisedQuantity))
    print('precisedDownward:'+str(downward(precisedQuantity)))
            
    # quantity=precisedQuantity
    if precisedQuantity > 0:
        quantity = round(precisedQuantity) * config["leverage"]
        print('Margin:'+str(quantity))
    else:
        quantity = downward(precisedQuantity)
        print(quantity)

    
    if data["positionSide"] == "LONG" and data["side"] == "BUY":
        try:
            client.futures_create_order(symbol = data["symbol"], side = data["side"],positionSide="SHORT", type = 'MARKET', quantity = quantity)
            client.futures_create_order(symbol = data["symbol"], side = data["side"],positionSide=data["positionSide"], type = 'MARKET', quantity = quantity)
        except BinanceAPIException as e:
            print(str(e))
    elif data["positionSide"] == "SHORT" and data["side"] == "SELL":
        try:
            client.futures_create_order(symbol = data["symbol"], side = data["side"],positionSide="LONG", type = 'MARKET', quantity = quantity)
            client.futures_create_order(symbol = data["symbol"], side = data["side"],positionSide=data["positionSide"], type = 'MARKET', quantity = quantity)
        except BinanceAPIException as e:
            print(str(e))
    
    
   
    return {"symbol" : data["symbol"],"Margin": quantity}
    
    


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
