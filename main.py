from http.client import HTTPException
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import smtplib, ssl, os
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.middleware(CORSMiddleware,
               allow_origins=["*"],
               allow_credentials=True,
               allow_methods=["*"],
               allow_headers=["*"],)
@app.post("/send-mail")
def send_mail(name:str = Form(...), email:str=Form(...),subject:str=Form(...),message:str=Form(...)):
    sender_email = os.getenv("EMAIL_USER")
    sender_pass = os.getenv("EMAIL_PASS")
    receiver_mail = "anoopsingla21@gmail.com"
    try:
        msg = EmailMessage()
        msg["Subject"] = f"New Message: {subject}"
        msg["From"] = email
        msg["To"] = receiver_mail
        msg.set_content(f"From: {name} < {email}>\n\n{message}")
        context =ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as server:
            server.login(sender_email,sender_pass)
            server.send_message(msg)
        return {"detail":"Successfully send message"}
    except Exception as e:
        raise HTTPException(status=500,detail="Error sending mail")