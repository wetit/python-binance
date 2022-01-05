from flask import Flask,request
from flask_restful import Api,Resource
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.client import Client



app=Flask(__name__)
api=Api(app)


client = Client("QZnNV8z2rEjhyu3Eq47NVZWmSRNCcJ7eej8xeDa4CEHxLGH2DBifj9IWF9XM9Rtj", "8Fnk1S8A8LaS2hGI1iz0Jqkieq3brIpuiyS7TaKVdDsGt0rD5xciJJ4FworHNXXJ")


config = {
  "amount": 15,
  "marginType": "ISOLATED",
  "leverage": 2
}



# class openTrade(Resource):
#     def get(self):
#         return {'status':'success'}


# api.add_resource(openTrade,"/trade")


@app.route("/open-trade-future",methods=['POST'])
def openTradeFuture():
  if request.method=="POST":
      data=request.form

      # set margin type
      # marginStatus=client.futures_change_margin_type(symbol="BTCUSDT",marginType="CROSSED")

      # set leverage
      leverageStatus=client.futures_change_leverage(symbol=data["symbol"],leverage=config["leverage"])

      # execute order

      # return config["leverage"]
      return {"status":"success","LeverageStatus":leverageStatus}




if __name__ == "__main__":
    app.run(debug=True,port=80)