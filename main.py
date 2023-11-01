from fastapi import FastAPI, HTTPException, status
from models import User, ShowUser, Login
from serivces import *
import datetime
from pydantic import EmailStr

app = FastAPI()

@app.get('/intro')
def intro():
    return {"message":"Hello world"}

@app.post('/Register')
async def Register(person : User):
    password = hash_password(person.password)
    user = {
            'first_name':person.first_name,
            'last_name':person.last_name,
            'email':person.email,
            'username':person.username,
            'password':password,
            'is_verified': False,
            'is_active':False
        }
    
    await collection.insert_one(user)
    return {'Message':"Registered Successfully !"}
    
@app.post('/Login')
async def login(user : Login):
    username = await collection.find_one({'username':user.username},{"_id":0})
    if username:
        if username['is_verified'] == False:
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Account has not verified yet !")
        if username['is_active'] == True:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Already logged in!")
        saved_password = username['password']
        if verify_password(user.password, saved_password):
            token = generate_token(username['username'])
            await collection.update_one({'username':user.username}, {"$set": {"is_active": True}})
            return token
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password!")   
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password!")
    

@app.post('/send_verify')
async def send_verify_code(email : str):
    find_email = await collection.find_one({'email':email})
    if find_email:
        if find_email['is_verified'] == True :
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Account has already Verified!')
        elif find_email['is_verified'] == False:
            message = generate_otp()
            find_verify_email = await otp_collection.find_one({'email':email})

            if find_verify_email:
                raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail = 'Verify code has already sent!')
            else:
                expire = datetime.datetime.utcnow()
                await otp_collection.insert_one({'email':email, 'otp_code':message ,'expireAt':expire})
                send_verifyemail(email, message)
                return {'Message':'Verify passcode has been senden to your email!'}
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Email not found !!")
    


@app.post('/verify_account')
async def verify_account(email: EmailStr, entered_otp : str):
    unverified_account = await otp_collection.find_one({'email':email})
    if unverified_account:
        saved_otp = unverified_account["otp_code"]
        if entered_otp == str(saved_otp):
            await collection.update_one({'email':email},{"$set": {'is_verified':True}})
            return {'message':'Account has been Verified succesfully!'}
        else:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f'{saved_otp}')
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail='Invalid Passcode!')
        
    
    