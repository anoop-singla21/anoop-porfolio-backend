# main.py
from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import smtplib
import ssl
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

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
async def send_mail(
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    # Your existing email sending code here
    try:
        sender_email = os.getenv("EMAIL_USER")
        sender_pass = os.getenv("EMAIL_PASS")
        receiver_mail = "anoopsingla21@gmail.com"
        
        msg = EmailMessage()
        msg["Subject"] = f"New Message: {subject}"
        msg["From"] = email
        msg["To"] = receiver_mail
        msg.set_content(f"From: {name} <{email}>\n\n{message}")
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_pass)
            server.send_message(msg)
        
        return {"detail": "Successfully sent message"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error sending mail")

# Add this for Render deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)