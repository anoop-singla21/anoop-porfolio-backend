# main.py
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.responses import JSONResponse
import resend

# Initialize Resend
resend.api_key = os.getenv("RESEND_API_KEY")

def create_html_body(name: str, email: str, subject: str, message: str, ip: str, user_agent: str) -> str:
    """Create HTML email body"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .message {{ background: #f1f3f4; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .technical {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 14px; }}
            .label {{ font-weight: bold; color: #555; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📧 New Portfolio Contact Form Submission</h2>
            </div>
            
            <div>
                <h3>Contact Information</h3>
                <p><span class="label">Name:</span> {name}</p>
                <p><span class="label">Email:</span> <a href="mailto:{email}">{email}</a></p>
                <p><span class="label">Subject:</span> {subject}</p>
            </div>
            
            <div class="message">
                <h3>Message</h3>
                <p>{message.replace(chr(10), '<br>')}</p>
            </div>
            
            <div class="technical">
                <h4>Technical Details</h4>
                <p><span class="label">IP Address:</span> {ip}</p>
                <p><span class="label">User Agent:</span> {user_agent}</p>
                <p><span class="label">Sent via:</span> Portfolio Contact Form</p>
            </div>
        </div>
    </body>
    </html>
    """

def send_email_resend(name: str, email: str, subject: str, message: str, ip: str, user_agent: str) -> bool:
    """Send email using Resend"""
    try:
        html_body = create_html_body(name, email, subject, message, ip, user_agent)
        
        # Create plain text version as fallback
        plain_text = f"""
        New Portfolio Contact Form Submission
        
        Contact Information:
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message}
        
        Technical Details:
        IP Address: {ip}
        User Agent: {user_agent}
        """
        
        r = resend.Emails.send({
            "from": "Portfolio <onboarding@resend.dev>",
            "to": ["anoopsingla71@gmail.com"],
            "subject": f"Portfolio Contact: {subject}",
            "html": html_body,
            "text": plain_text,
            "reply_to": email
        })
        
        print("✅ Email sent successfully via Resend")
        return True
        
    except Exception as e:
        print("❌ Failed to send email via Resend:", str(e))
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
        success = send_email_resend(
            name=name,
            email=email,
            subject=subject,
            message=message,
            ip=request.client.host,
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
        
        if success:
            return {"detail": "Successfully sent message"}
        else:
            return JSONResponse(
                status_code=500,
                content={"detail": "Error sending mail"}
            )
            
    except Exception as e:
        print("Unexpected error:", e)
        return JSONResponse(
            status_code=500,
            content={"detail": "Error sending mail"}
        )
