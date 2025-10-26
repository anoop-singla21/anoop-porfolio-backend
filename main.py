# main.py
from fastapi import FastAPI, Form, HTTPException, status,Request
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env
SMTP_USER = os.getenv("EMAIL_USER")
SMTP_PASS = os.getenv("EMAIL_PASS")
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
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
    except Exception as e:
        print("❌ Failed to send email:", str(e))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anoop-singla21.github.io/anoop-portfolio"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Portfolio API is running"}

@app.post("/send-mail")
async def send_mail(request:Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    # Your existing email sending code here
    try:
        subject_email = f"Email from website from {name} : {subject}"
        body = f"Email on websit from {name} : email {email}: {message}  ip_address:{request.client.host} user_agent:{request.headers.get("User-Agent")}"
        send_email(subject_email,body)
        return {"detail": "Successfully sent message"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error sending mail")

# Add this for Render deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
