# fika
To remember before using:

## Git
if you don't have a git installation visit https://git-scm.com/downloads and choose a setup for your OS

https://git-scm.com/docs/gittutorial offers a basic tutorial for using git after installation

## Python

Visit https://www.python.org/downloads/release/python-380/ to get the latest release

After installation move to the fika app directory in a terminal and run

> pip install -r requiremnts.txt

### Runing flask

OS Dependent

## Daraja

https://medium.com/the-andela-way/demystifying-the-m-pesa-api-lipa-na-m-pesa-online-payment-a22d68a42d5e

Reffer to the above site to learn how to get the access token for use

The access token expires every hour so you need to renew it before use

Update the config variable in app.py with your new access token 

## Ngrok

https://ngrok.com/download

If you don't have ngrok install download it from the above site

Once installed open the folder containing the ngrok executable in a terminal and run

> ngrok http 5000

to start a ngrok session

copy the ID in the provided url http://{ID}.ngrok.io and update the ngrok_id 
variable in config in app.py

## Mail

In the config in app.py, change the email and password to match your own

Visit https://myaccount.google.com/lesssecureapps and allow less secure apps to access your email
