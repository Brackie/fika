from flask import Flask,g, request, render_template, url_for,redirect,flash,jsonify,send_file, current_app
from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from flask_cors import CORS
from io import BytesIO
from werkzeug.security import check_password_hash
from peewee import *
from models import User, create_tables, Safari, Booking, Payment
from api2pdf import Api2Pdf
from pay import mpesa
from flask_mail import Mail, Message
from os.path import join
from datetime import datetime
from pprint import pprint as pp
import uuid

fika =Flask(__name__)
CORS(fika)
fika.secret_key ="1222564"
fika.config.from_mapping(
        ACCESS_TOKEN = "NEW ACCESS_TOKEN",
        MAIL_DEFAULT_SENDER = 'your email',
        MAIL_SERVER ='smtp.gmail.com',
        MAIL_PORT  = 465,
        MAIL_USERNAME  = 'your email',
        MAIL_PASSWORD  = 'your password',
        MAIL_USE_SSL  = True,
        NGROK_ID = "b3d80409f81a"
    )

a2p_client = Api2Pdf('2e70670c-add5-40e4-8fdc-8d6be87596ce')
mail = Mail(fika)

login_manager= LoginManager()
login_manager.init_app(fika)
login_manager.login_view='user_login'

@login_manager.user_loader
def load_user(userid):
    try:
        return User.get(int(userid))
    except DoesNotExist:
        return None

@fika.before_request
def before_request():
    g.user=current_user

def email_exist(email):
    """
    this method checks if simmillar email exists
    """
    mail = User.select().where(email == email)
    return mail

@fika.route('/', methods=["GET"])
def homepage():
   return render_template("index.html")

@fika.route('/lnm_hook/<booking_id>', methods=["POST"])
def webhook(booking_id):
    """
    Store information about the payment in the database
    """
    payment_data = request.get_json()
    print("~~~~~~~~~~~~~Received LNM hook~~~~~~~~~~~~~~~~~~")
    print(payment_data)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    '''
    if payment_data is not None:
        transaction_id = payment_data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
        amount = payment_data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        mobile_num = payment_data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']
        Payment.create_payment(transaction_id, booking_id, amount, mobile_num)
        q = (Booking.update({Booking.is_paid: True}).where(Booking.booking_id == booking_id))
        q.execute()
        send_email(booking_id, mobile_num, amount)
        return jsonify({"message": "success"})
    '''
    return jsonify({"message": "success"})


def send_email(booking_id, phone, price):
    booking = Booking.select(Booking, Safari).join(Safari).where(Booking.id == booking_id).objects()
    user = User.get(int(booking[0].booked_by_id.id))

    receipt = '''
    -------------------------------
    \t\tRECEIPT\t\t
    -------------------------------\n\n
    Item\t\t\tPrice
    ----\t\t\t-----\n
    Trip {} - {}\t{}\n
    ---------------------------------
    Total\t\t\t{}
    ---------------------------------\n
    Paid by: {} {}
    Tel: {}
    '''.format(booking[0].from_, booking[0].Destination, price, price, user.first_name, user.last_name, phone)

    file_name = "{}_{}.txt".format(datetime.now().strftime("%d%m%Y%H%M%S"), user.first_name)
    path = join("./static/receipt/", file_name)
    with open(path, "w+") as f:
        f.write(receipt)
        f.close()

    html = '''<p>
    <b>Hello {} {},</b><br><br>
    This is to confirm your payment of Ksh. {} for a bus trip from {} to {}.
    Find receipt attached.
    </p>'''.format(user.first_name, user.last_name, price, booking[0].from_, booking[0].Destination)
    
    msg = Message(
        "Fika Receipt of Payment", 
        recipients=[current_user.email]
    )
    msg.html = html
    with fika.open_resource(path) as fp:
        msg.attach(file_name, "text/plain", fp.read())

        
@fika.route('/search', methods=["GET"])
def search():
    """
    for any data thta is sent in a form but the method is get
    the data isn the request is found in the args
    ie: request.args["name]
    """
    # data = [request.args["from"],request.args["destination"], request.args['date']]  
    safaris =Safari.search_safari(request.args["destination"], request.args["from"])
    return render_template("buses.html", buses = safaris)
    

@fika.route('/register', methods=["POST","GET"])
def register():
    """
    with this view one can be able to register to the application
    """
    if request.method == 'POST': 
       
        data = [
                request.form['First_Name'],
                 request.form['Last_Name'], 
                 request.form['Email'], 
                 request.form['Password']
                ]

        for name in data:
            print(name)

        response =User.add_user(data[0], data[1], data[2], data[3])

        if response != "e":
            flash (f"welcome {request.form['Last_Name']}")
            return redirect(url_for('homepage'))
    return render_template('register.html')

@fika.route("/user-login", methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        form_data = [request.form['email'],request.form['password']]
        
        try:
            user=User.get(User.email==form_data[0])
        except DoesNotExist:
            return "user does not exists"
        else:
            if check_password_hash(user.password, form_data[1]):

                login_user(user)
                flash("You've been logged in ")
                return redirect(url_for("homepage"))
            else:
                flash(" Your email or password does not match !", "error")
    return render_template("login.html")


@fika.route("/logout")
@login_required
def logout():
    logout_user()
    flash("you have been looged out! come back soon")
    return redirect(url_for("homepage"))

    
@fika.route('/resp',methods=["GET"])
def resp():
    return render_template("resp.html")


@fika.route('/make_booking/<int:journey_id>', methods=["POST","GET"])
@login_required
def bookings(journey_id):
    if request.method=="POST":
        user =g.user._get_current_object()
        safari_id = journey_id

        add_booking= Booking.create_bk(safari_id, user)
        if add_booking:

            print (add_booking)
            return redirect(url_for("my_bookings"))
    return render_template("index.html")

# @fika.route('/cancel_booking', methods=["PUT"])
# def bookings():
#     if request.method!="PUT":
#         return render_template("error.html")
    
#     form_data =request.form["booking_id"]
#     user =request.token["token"]

#     add_booking= Bookings.cancel_booking(form_data, user)

#     bookings = Bookings.select(id, jounery_id).where(booked_by=user)
#     return render_template("bookings_made.html")


# @fika.route('/pay/<int:booking_id>', methods=["GET", "POST"])
# def pay(booking_id):
#     if request.method=="POST":
#         form_data = [request.form["phone_number"], request.form["amount"]]
        

#         booking = Booking.get(id=booking_id)
#         if not booking:
#             return "No booking with that id"
        
#         mpesa_response = mpesa.make_stk_push(form_data[0], form_data[1])
#         return mpesa_response["ResponseCode"]

#     return redirect(url_for('my_bookings'))

@fika.route('/add_safari', methods=["GET", "POST"])
@login_required
def add_safari():
    if request.method== "POST":
        # print(g.user.id)
        # user =User.get().where(id=g.user.id)
        # if user == False:
        #     return "Wewe you are not admin pole"
        
        # print(g.user.id)
        form_data = [
                    request.form['bus_number'],
                    request.form['from'],
                    request.form['Destination'],
                    request.form['Fare'],
                    request.form['depature_date']
                    ]
        user = current_user.id
        
        add_safari = Safari.create_safari(form_data[0],form_data[1],form_data[2],form_data[3],form_data[4],user)
        return redirect("all_safaris")

    return render_template("add_bus.html")


@fika.route('/all_safaris', methods=["GET"])
@login_required
def all_safaris():
    all_safaris =Safari.select().dicts()
    return render_template("all_safaris.html", buses =all_safaris )

# @fika.route('/all_payments', methods=["GET"])
# def all_payments():
#     all_payments =Payments.select(id, mpesa_ref, amount, paid_by)
#     if not all_payments:
#         return render_template("not_found.html")
#     return render_template("all_payments.html", data =all_safaris )


@fika.route('/all_bookings', methods=["GET"])
@login_required
def all_bookings():
    all_bookings = Booking.select().dicts()
    return render_template("all_bookings.html", data =all_bookings)


@fika.route('/my_bookings', methods=["GET"])
@login_required
def my_bookings():
    all_bookings = Booking.select().where(Booking.booked_by_id==current_user.id).dicts()
    return render_template("all_bookings.html", data =all_bookings)

# @fika.route('/load', methods=['GET'])
# def load():
#     url =url_for("download",id_=1)

#     api_response = a2p_client.HeadlessChrome.convert_from_html(url, inline_pdf=True, file_name='test.pdf')

#     print(api_response)
#     return "api_response['pdf']"

@fika.route('/payments', methods=["GET"])
@login_required
def all_payments():
    all_payments = None
    if current_user.is_admin:
        all_payments = Payment.select(Payment, Booking).join(Booking).objects()
    else:
        all_payments = Payment.select(Payment, Booking, User).join(Booking).join(User).where(User.id == current_user.id).objects()
    
    return render_template("all_payments.html", payments=all_payments)


@fika.route('/success', methods=['GET'])
def success():
    return render_template("success.html")


@fika.route('/get_phone/<booking_id>', methods=['POST', 'GET'])
@login_required
def get_phone(booking_id):
    if request.method == 'POST':
        print("----------------------")
        print(f"{booking_id}")
        print("----------------------")
        phone = request.form['phone']
        booking = Booking.select().where(Booking.id == booking_id).objects()
        safari = Safari.select().where(Safari.id == booking[0].safari_booked_id).objects()
        price = safari[0].Fare
        '''
        Do something with the phone number and price
        '''
        result = mpesa.make_stk_push(current_app.config["ACCESS_TOKEN"], phone, price, booking_id)
        if 'ResponseCode' in result and result['ResponseCode'] == '0':
            transaction_id = uuid.uuid4().hex
            print("--------------------------")
            print(f"{transaction_id}")
            print("--------------------------")
            Payment.create_payment(transaction_id, booking_id, price, phone)
            q = (Booking.update({Booking.is_paid: True}).where(Booking.id == booking_id))
            q.execute()
            send_email(booking_id, phone, price)
            return render_template("payment_status.html", success=True)
        else:
            return render_template("payment_status.html", success=False, booking_id=booking_id)
    
    return render_template("phone.html", booking_id=booking_id)


@fika.route("/download/<int:id_>", methods=["GET"])
def download(id_):
    id_ = id_
    ticket = Booking.select().where(Booking.id == id_).dicts()
    # safari =Safari.select().where(Safari.id == ticket.safari_booked_id).dicts()
    rendered= render_template('ticket.html', data=ticket) 
    api_response = a2p_client.HeadlessChrome.convert_from_html(rendered, inline_pdf=True, file_name='test.pdf')
    link =api_response.result['pdf']

    return link

if __name__ == "__main__":
    create_tables()
    admin= User.add_user("admin", "admin", "admin@gmail.com", "admin", is_admin=True)
    fika.run(debug = True)
