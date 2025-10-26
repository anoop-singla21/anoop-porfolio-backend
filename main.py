from fastapi import FastAPI, Form, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator
import smtplib
import ssl
import os
import logging
from email.message import EmailMessage
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request validation
class ContactForm(BaseModel):
    name: str
    email: str
    subject: str
    message: str

    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

    @field_validator('subject')
    def subject_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Subject cannot be empty')
        return v.strip()

    @field_validator('message')
    def message_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters long')
        return v.strip()

# Security
security = HTTPBearer()

app = FastAPI(
    title="Portfolio Contact API",
    description="API for handling contact form submissions",
    version="1.0.0"
)

# Improved CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com",  # Replace with your actual domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # More restrictive than "*"
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting storage (in production, use Redis)
from datetime import datetime, timedelta
from collections import defaultdict

request_times = defaultdict(list)

def rate_limit(max_requests: int = 5, time_window: int = 3600):  # 5 requests per hour
    def decorator(ip: str):
        now = datetime.now()
        # Clean old requests
        request_times[ip] = [t for t in request_times[ip] if now - t < timedelta(seconds=time_window)]
        
        if len(request_times[ip]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        request_times[ip].append(now)
        return True
    return decorator

def get_client_ip(request):
    return request.client.host

# Email configuration
def get_email_config():
    sender_email = os.getenv("EMAIL_USER")
    sender_pass = os.getenv("EMAIL_PASS")
    
    if not sender_email or not sender_pass:
        logger.error("Email credentials not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email service not configured properly"
        )
    
    return sender_email, sender_pass

def create_email_message(name: str, email: str, subject: str, message: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Portfolio Contact: {subject}"
    msg["From"] = f"{name} <{email}>"
    msg["To"] = "anoopsingla21@gmail.com"
    msg["Reply-To"] = email
    
    # HTML email with better formatting
    html_content = f"""
    <html>
        <body>
            <h2>New Contact Form Submission</h2>
            <p><strong>From:</strong> {name} ({email})</p>
            <p><strong>Subject:</strong> {subject}</p>
            <hr>
            <p><strong>Message:</strong></p>
            <p>{message.replace(chr(10), '<br>')}</p>
            <hr>
            <p><small>Sent from your portfolio contact form</small></p>
        </body>
    </html>
    """
    
    msg.set_content(f"""
    From: {name} <{email}>
    Subject: {subject}
    
    Message:
    {message}
    """)
    
    msg.add_alternative(html_content, subtype='html')
    return msg

@app.get("/")
async def root():
    return {
        "message": "Portfolio Contact API is running",
        "version": "1.0.0",
        "endpoints": {
            "contact": "/send-mail (POST)"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/send-mail")
async def send_mail(
    name: str = Form(..., min_length=2, max_length=100),
    email: str = Form(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    subject: str = Form(..., min_length=1, max_length=200),
    message: str = Form(..., min_length=10, max_length=2000),
):
    """
    Send email from contact form with improved validation and error handling
    """
    try:
        # Validate input using Pydantic model
        contact_data = ContactForm(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Get email configuration
        sender_email, sender_pass = get_email_config()
        
        # Create email message
        msg = create_email_message(
            name=contact_data.name,
            email=contact_data.email,
            subject=contact_data.subject,
            message=contact_data.message
        )
        
        # Send email
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_pass)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully from {email}")
        
        return {
            "success": True,
            "detail": "Message sent successfully",
            "message_id": f"{datetime.now().timestamp()}"
        }
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email service configuration error"
        )
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "detail": exc.detail},
    )

@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "detail": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )