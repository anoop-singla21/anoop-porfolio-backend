# main.py
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_USER = os.getenv("EMAIL_USER")
SMTP_PASS = os.getenv("EMAIL_PASS")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # Changed to 465 for SSL

def send_email(subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "anoopsingla21@gmail.com"
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Use SMTP_SSL instead of regular SMTP
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        print("✅ Email sent successfully")
        return True
    except Exception as e:
        print("❌ Failed to send email:", str(e))
        return False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anoop-singla21.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Portfolio API is running"}

@app.post("/send-mail")
async def send_mail(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    try:
        subject_email = f"Portfolio Contact: {subject} from {name}"
        body = f"""
        New contact form submission:
        
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message}
        
        Technical Info:
        IP: {request.client.host}
        User Agent: {request.headers.get('User-Agent')}
        """
        
        success = send_email(subject_email, body)
        
        if success:
            return {"detail": "Successfully sent message"}
        else:
            raise HTTPException(status_code=500, detail="Error sending mail")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error sending mail")
