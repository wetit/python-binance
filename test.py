from flask import Flask, request
from flask_restful import Api, Resource
from requests.models import Response
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.client import Client
import os
import json
import math

app = Flask(__name__)
api = Api(app)


client = Client("QZnNV8z2rEjhyu3Eq47NVZWmSRNCcJ7eej8xeDa4CEHxLGH2DBifj9IWF9XM9Rtj", "8Fnk1S8A8LaS2hGI1iz0Jqkieq3brIpuiyS7TaKVdDsGt0rD5xciJJ4FworHNXXJ")


config = {
    "amount": 10,
    "marginType": "ISOLATED",
    "leverage": 1,
    "type": "MARKET"
}


@app.route("/", methods=['GET'])
def test():
    return {"message": "test"}



@app.route("/open-trade-future", methods=['POST'])
def openTradeFuture():
    # if request.method=="POST":
    data = json.loads(request.data)

    # set margin type
    # marginStatus=client.futures_change_margin_type(symbol="BTCUSDT",marginType="CROSSED")

    # set leverage
    client.futures_change_leverage(symbol=data["symbol"], leverage=config["leverage"])

    # current price
    symbolPrice = client.get_symbol_ticker(symbol=data["symbol"])
    # print(symbolPrice)

    # precision
    symbol_info = client.get_symbol_info(data["symbol"])
    step_size = 0.0
    for f in symbol_info['filters']:
        if f['filterType'] == 'LOT_SIZE':
            step_size = float(f['stepSize'])
            precision = int(round(-math.log(step_size, 10), 0))
            quantity = float(round(config["amount"]/float(symbolPrice["price"]), precision))

    #amount
    amount = quantity
    print(amount)
    print(data["symbol"])
    

    # execute order
    # executedOrder=client.futures_create_order(symbol=data["symbol"],side=data["side"],type=config["type"],quantity=amount)
    
    
    return {
        "status": "success",
        # "executedOrder":client.futures_coin_position_information()
    }


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
