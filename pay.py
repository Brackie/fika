import datetime
import base64
from flask import current_app
import requests
import json
from requests.auth import HTTPBasicAuth

def get_access_token():
    consumer_key = "P9viP4n9XTz96cW6RH5ALoNIchidf4Cg"
    consumer_secret = "GDVm1AjD09bkq4PU"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return r.json()["access_token"]

class mpesa:
    # def __init__(self, num, Amount):
    #     # self.stk_url=str(''),
    #     self.token_url='https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
    #     self.num= num
    #     self.Amount=Amount.strip()
    #     self.datentime=str(self.date[0])
    
    @classmethod
    def make_stk_push(cls, access_token, num, Amount, booking):
        Amount = str(Amount)
        num = str(num)
        
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = { "Authorization": "Bearer %s" % access_token }
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((str(174379)+passkey+date).encode('utf-8')).decode('utf-8')
        call_back_url = "https://{}.ngrok.io/webhook/{}".format(current_app.config['NGROK_ID'], booking)
        
        data={ 
                "BusinessShortCode": "174379",
                "Password": password,
                "Timestamp": date,
                "TransactionType":"CustomerPayBillOnline",
                "Amount":Amount,
                "PartyA":num,
                "PartyB":"174379",
                "PhoneNumber":num,
                "CallBackURL": call_back_url,
                "AccountReference":"test",
                "TransactionDesc":"test"
            }
        # coded =self.bs64(174379,'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919',self.datentime)
        # print(data["Password"])
        # print(self.datentime)
        # print(self.Amount)
        # print(data["Amount"])
        # print(self.num)

        # requests.post(api_url, json = request, headers=headers)
        response = requests.post(api_url, json = data, headers=headers)
        print(response.json())
        return response.json()
