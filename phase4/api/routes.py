"""
API Routes for The Closer
This module contains route definitions and can be imported by app.py
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'phase1'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'phase3'))

from phase4.database import Database
from phase4.auth import AuthManager, AuthenticationError
from phase1.input_loader import InputLoader
from phase1.email_generator import EmailGenerator
from phase1.email_sender import EmailSender
from phase1.config import Config

# Initialize routers
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])
contacts_router = APIRouter(prefix="/api/contacts", tags=["Contacts"])
emails_router = APIRouter(prefix="/api/emails", tags=["Emails"])
logs_router = APIRouter(prefix="/api/logs", tags=["Logs"])
stats_router = APIRouter(prefix="/api/stats", tags=["Statistics"])
analytics_router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Initialize components
db = Database()
auth_manager = AuthManager(db)
config = Config()

# Security
security = HTTPBearer()


# Dependency: Get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token."""
    token = credentials.credentials
    user = auth_manager.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# Authentication routes
@auth_router.post("/register")
async def register(username: str, password: str, email: Optional[str] = None):
    """Register a new user."""
    try:
        result = auth_manager.register_user(username, password, email)
        return {"success": True, "data": result}
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/login")
async def login(username: str, password: str):
    """Authenticate user and return access token."""
    result = auth_manager.authenticate_user(username, password)
    
    if not result:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    return {"success": True, "data": result}


# Contact routes
@contacts_router.get("/")
async def get_contacts(
    status: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all contacts, optionally filtered by status."""
    contacts = db.get_all_contacts(status=status, limit=limit)
    return {"success": True, "data": contacts}


@contacts_router.get("/{contact_id}")
async def get_contact(contact_id: int, current_user: dict = Depends(get_current_user)):
    """Get a specific contact by ID."""
    contact = db.get_contact(contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {"success": True, "data": contact}


@contacts_router.post("/")
async def create_contact(contact: dict, current_user: dict = Depends(get_current_user)):
    """Create a new contact."""
    try:
        contact_id = db.add_contact(contact)
        contact['id'] = contact_id
        return {"success": True, "data": contact}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@contacts_router.put("/{contact_id}")
async def update_contact(
    contact_id: int,
    updates: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update a contact."""
    success = db.update_contact(contact_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {"success": True, "message": "Contact updated successfully"}


@contacts_router.delete("/{contact_id}")
async def delete_contact(contact_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a contact."""
    success = db.delete_contact(contact_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {"success": True, "message": "Contact deleted successfully"}


@contacts_router.get("/{contact_id}/logs")
async def get_contact_logs(contact_id: int, current_user: dict = Depends(get_current_user)):
    """Get all log entries for a specific contact."""
    logs = db.get_contact_logs(contact_id)
    return {"success": True, "data": logs}


# Email routes
@emails_router.post("/generate")
async def generate_email(
    contact: dict,
    template: str = "default",
    use_llm: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Generate an email for a contact."""
    try:
        generator = EmailGenerator(template=template)
        email = generator.generate_email(contact)
        
        # Validate email
        is_valid, error_msg = generator.validate_email(email)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get word count
        email['word_count'] = generator.get_word_count(email)
        
        # Quality scoring
        from phase3.quality_scorer import QualityScorer
        scorer = QualityScorer()
        quality_score = scorer.score_email(email)
        email['quality_score'] = quality_score
        
        # Spam check
        from phase3.spam_checker import SpamChecker
        spam_checker = SpamChecker()
        spam_risk = spam_checker.check_spam_risk(email)
        email['spam_risk'] = spam_risk
        
        return {"success": True, "data": email}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@emails_router.post("/send")
async def send_email(
    contact: dict,
    email: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send an email to a contact."""
    try:
        sender = EmailSender(config)
        sender.connect()
        
        success = sender.send_email(
            to=contact['recipient_email'],
            subject=email['subject'],
            body=email['body']
        )
        
        sender.disconnect()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send email")
        
        # Log the action
        contact_record = db.get_contact_by_email(contact['recipient_email'])
        contact_id = contact_record['id'] if contact_record else None
        
        log_entry = {
            'contact_id': contact_id,
            'subject': email['subject'],
            'status': 'sent',
            'word_count': email.get('word_count', 0),
            'template_used': email.get('template_used', 'default'),
            'quality_score': email.get('quality_score', {}).get('overall'),
            'spam_risk': email.get('spam_risk', {}).get('risk_level')
        }
        
        db.add_log_entry(log_entry)
        
        return {"success": True, "message": "Email sent successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Log routes
@logs_router.get("/")
async def get_logs(
    contact_id: Optional[int] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get outreach log entries."""
    logs = db.get_logs(contact_id=contact_id, limit=limit)
    return {"success": True, "data": logs}


# Statistics routes
@stats_router.get("/")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """Get overall statistics."""
    stats = db.get_statistics()
    return {"success": True, "data": stats}


@stats_router.get("/overview")
async def get_overview(current_user: dict = Depends(get_current_user)):
    """Get overview statistics."""
    from phase4.analytics import AnalyticsDashboard
    analytics = AnalyticsDashboard(db)
    overview = analytics.get_overview_stats()
    return {"success": True, "data": overview}


# Analytics routes
@analytics_router.get("/time-series")
async def get_time_series(days: int = 30, current_user: dict = Depends(get_current_user)):
    """Get time series data for analytics."""
    from phase4.analytics import AnalyticsDashboard
    analytics = AnalyticsDashboard(db)
    data = analytics.get_time_series_data(days)
    return {"success": True, "data": data.to_dict() if hasattr(data, 'to_dict') else {}}


@analytics_router.get("/detailed")
async def get_detailed_metrics(current_user: dict = Depends(get_current_user)):
    """Get detailed analytics metrics."""
    from phase4.analytics import AnalyticsDashboard
    analytics = AnalyticsDashboard(db)
    metrics = analytics.get_detailed_metrics()
    return {"success": True, "data": metrics}


# Export all routers
def get_routers():
    """Return all API routers."""
    return [
        auth_router,
        contacts_router,
        emails_router,
        logs_router,
        stats_router,
        analytics_router
    ]
