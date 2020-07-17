# fika
To remember before using:

https://medium.com/the-andela-way/demystifying-the-m-pesa-api-lipa-na-m-pesa-online-payment-a22d68a42d5e

Reffer to the above site to learn how to get the access token for use

The access token expires every hour so you need to renew it before use

Update the config variable in app.py with your new access token 

https://ngrok.com/download

If you don't have ngrok install download it from the above site

Once installed open the folder containing the ngrok executable in a terminal and run

> ngrok http 5000

to start a ngrok session

copy the ID in the provided url http://{ID}.ngrok.io and update the ngrok_id 
variable in config in app.py
