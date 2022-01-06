from flask import Flask,request
from flask_restful import Api,Resource
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.client import Client
import os
import json


app=Flask(__name__)
api=Api(app)


client = Client("QZnNV8z2rEjhyu3Eq47NVZWmSRNCcJ7eej8xeDa4CEHxLGH2DBifj9IWF9XM9Rtj", "8Fnk1S8A8LaS2hGI1iz0Jqkieq3brIpuiyS7TaKVdDsGt0rD5xciJJ4FworHNXXJ")


config = {
  "amount": 15,
  "marginType": "ISOLATED",
  "leverage": 4,
  "type" : "MARKET"
}



# class openTrade(Resource):
#     def get(self):
#         return {'status':'success'}


# api.add_resource(openTrade,"/trade")

@app.route("/",methods=['GET'])
def test():
  return {"message":"test"}


@app.route("/open-trade-future",methods=['POST'])
def openTradeFuture():
  # if request.method=="POST":
      data=json.loads(request.data)
     
      # set margin type
      # marginStatus=client.futures_change_margin_type(symbol="BTCUSDT",marginType="CROSSED")

      
      # set leverage
      leverageStatus=client.futures_change_leverage(symbol=data["symbol"],leverage=config["leverage"])

      #current price
      symbolPrice=client.get_symbol_ticker(symbol=data["symbol"])
      print(symbolPrice)

      #calculate amount
      amount= config["amount"]/float(symbolPrice["price"])
      print(amount)

      # execute order
      # executedOrder=client.futures_create_order(symbol=data["symbol"],side=data["side"],type=config["type"],quantity=amount)

      # return config["leverage"]
      return {"status":"success"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port,debug=True)