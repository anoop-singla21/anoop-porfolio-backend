# main.py
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_USER = os.getenv("EMAIL_USER")
SMTP_PASS = os.getenv("EMAIL_PASS")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "anoopsingla21@gmail.com"
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully")
        return True
    except Exception as e:
        print("❌ Failed to send email:", str(e))
        return False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anoop-singla21.github.io"],  # Fixed: removed /anoop-portfolio
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
        subject_email = f"Email from website from {name} : {subject}"
        # Fixed: Use single quotes inside f-string
        body = f"Email from website from {name} : email {email}: {message}  ip_address:{request.client.host} user_agent:{request.headers.get('User-Agent')}"
        
        success = send_email(subject_email, body)
        
        if success:
            return {"detail": "Successfully sent message"}
        else:
            raise HTTPException(status_code=500, detail="Error sending mail")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error sending mail")
