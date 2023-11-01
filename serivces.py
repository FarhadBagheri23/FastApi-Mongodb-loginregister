from passlib.hash import pbkdf2_sha256
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
from datetime import datetime, timedelta
import random
from smtplib import SMTP
from email.message import EmailMessage
from email.mime.text import MIMEText


mongo_url = "mongodb://localhost:27017/"
mongo_client = AsyncIOMotorClient(mongo_url)
database = mongo_client['Users']
collection = database['users']
otp_collection = database['otp_holder']
otp_collection.create_index('expireAt', expireAfterSeconds= 120)


JWT_KEY = "da69c0cb87a302386b4b5bc4a1b08357e14c7e5b011d92dc0f792c6ae0120b96"


"""
 Run below code one time to have unique email and 
 username in the database.

# collection.create_index('username', unique = True)
# collection.create_index('email', unique = True)
"""

def hash_password(password : str) -> str : 
    """
    Hashing the password for saving in the
    database.
    """
    hashed_password = pbkdf2_sha256.hash(password)
    return hashed_password

def verify_password(password : str, hashed_password : str) -> bool:
    """
    Function for check the if the entered
    password is correct or not.
    """
    hashedpassword = hash_password(password)
    verify_password = pbkdf2_sha256.verify(password, hashedpassword)
    return verify_password


def generate_token(username) -> str:
    """
    Function for generate token for user.
    """

    payload = {
        'user':username,
        'expiry': datetime.utcnow().timestamp()
    }

    token = jwt.encode(payload, key=JWT_KEY, algorithm="HS256")
    access_token = {
        'token':token
    }

    return access_token

def decode_token(token: str) -> dict:
    """
    Function for decoding the token.
    """
    decoded_token = jwt.decode(token , key= JWT_KEY, algorithms=['HS256', ])
    return decoded_token


def generate_otp() -> int:
    """
    Function that produce an
    One Time Password
    """
    otp = random.randint(0,1000000)
    return otp

def send_verifyemail(reciever: str, message : str):
    """
    Function that send verify email
    for the existed user.
    Notice that for sender_password you 
    must go to app password on your gmail
    security and create your own password
    """
    
    sender = "SENDER GMAIL!"
    sender_password = "YOUR GMAIL APP PASSWORD"
    server = SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, sender_password)
    server.sendmail(sender, reciever,str(message))



    
    
    
    
