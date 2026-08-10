import requests
from flask import current_app, flash
from ..models import Purchase
from ..extensions import db



# def verify_transaction(reference:dict) -> str|bool|None:
    
      
def initialize_transaction(email, amount, callback_url, metadata):
    PAYSTACK_API_TEST_PKEY = current_app.config['PAYSTACK_API_TEST_PKEY']
    PAYSTACK_API_TEST_SKEY = current_app.config['PAYSTACK_API_TEST_SKEY']
    header = {
      "Authorization": f"Bearer {PAYSTACK_API_TEST_SKEY}",
      "Content-Type": "application/json",
        }

    url = "https://api.paystack.co/transaction/initialize"
    response = requests.post(url,
                             headers=header,
                             json={"email": email, 
                                   "amount": amount, 
                                   "metadata": metadata,
                                   "callback_url" : callback_url
                                   }

                             )
    try:
      return response.json()['data']['authorization_url'] 
    except KeyError:
      flash("There was an issue rendering the payment page please try again later")
      return False


def verify_transaction(reference):
    PAYSTACK_API_TEST_SKEY = current_app.config["PAYSTACK_API_TEST_SKEY"]
    response = requests.get(
      f"https://api.paystack.co/transaction/verify/{reference}",
      headers={"Authorization": f"Bearer {PAYSTACK_API_TEST_SKEY}"}
      )
    try:
      return response.json()
    except requests.exceptions.JSONDecodeError:
      return False



def record_purchase(student_id, video_id, amount, reference, db_object):
    existing = Purchase.query.filter_by(student_id=student_id, video_id=video_id).first()
    if existing:
        return "OK", 200
    new_purchase = Purchase(
                       student_id=student_id,
                       video_id=video_id,
                       amount_paid=amount,
                       paystack_reference=reference
                   )
    db_object.session.add(new_purchase)
    db_object.session.commit()
    return "OK", 200
   