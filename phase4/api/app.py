from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
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

# Initialize FastAPI app
app = FastAPI(
    title="The Closer API",
    description="REST API for cold email automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


# Authentication endpoints
@app.post("/api/auth/register")
async def register(username: str, password: str, email: Optional[str] = None):
    """Register a new user."""
    try:
        result = auth_manager.register_user(username, password, email)
        return {"success": True, "data": result}
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def login(username: str, password: str):
    """Authenticate user and return access token."""
    result = auth_manager.authenticate_user(username, password)
    
    if not result:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    return {"success": True, "data": result}


# Contact endpoints
@app.get("/api/contacts")
async def get_contacts(
    status: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all contacts, optionally filtered by status."""
    contacts = db.get_all_contacts(status=status, limit=limit)
    return {"success": True, "data": contacts}


@app.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: int, current_user: dict = Depends(get_current_user)):
    """Get a specific contact by ID."""
    contact = db.get_contact(contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {"success": True, "data": contact}


@app.post("/api/contacts")
async def create_contact(contact: dict, current_user: dict = Depends(get_current_user)):
    """Create a new contact."""
    try:
        contact_id = db.add_contact(contact)
        contact['id'] = contact_id
        return {"success": True, "data": contact}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/contacts/{contact_id}")
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


@app.delete("/api/contacts/{contact_id}")
async def delete_contact(contact_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a contact."""
    success = db.delete_contact(contact_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {"success": True, "message": "Contact deleted successfully"}


# Email generation endpoints
@app.post("/api/generate")
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


@app.post("/api/send")
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
        contact_id = db.get_contact_by_email(contact['recipient_email'])
        if contact_id:
            contact_id = contact_id['id']
        
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


# Log endpoints
@app.get("/api/logs")
async def get_logs(
    contact_id: Optional[int] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get outreach log entries."""
    logs = db.get_logs(contact_id=contact_id, limit=limit)
    return {"success": True, "data": logs}


@app.get("/api/contacts/{contact_id}/logs")
async def get_contact_logs(
    contact_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get all log entries for a specific contact."""
    logs = db.get_contact_logs(contact_id)
    return {"success": True, "data": logs}


# Statistics endpoints
@app.get("/api/stats")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """Get overall statistics."""
    stats = db.get_statistics()
    return {"success": True, "data": stats}


@app.get("/api/stats/overview")
async def get_overview(current_user: dict = Depends(get_current_user)):
    """Get overview statistics."""
    from phase4.analytics import AnalyticsDashboard
    analytics = AnalyticsDashboard(db)
    overview = analytics.get_overview_stats()
    return {"success": True, "data": overview}


# Analytics endpoints
@app.get("/api/analytics/time-series")
async def get_time_series(days: int = 30, current_user: dict = Depends(get_current_user)):
    """Get time series data for analytics."""
    from phase4.analytics import AnalyticsDashboard
    analytics = AnalyticsDashboard(db)
    data = analytics.get_time_series_data(days)
    return {"success": True, "data": data.to_dict() if hasattr(data, 'to_dict') else {}}


@app.get("/api/analytics/detailed")
async def get_detailed_metrics(current_user: dict = Depends(get_current_user)):
    """Get detailed analytics metrics."""
    from phase4.analytics import AnalyticsDashboard
    analytics = AnalyticsDashboard(db)
    metrics = analytics.get_detailed_metrics()
    return {"success": True, "data": metrics}


# File upload endpoints
@app.post("/api/upload/contacts")
async def upload_contacts(
    file: str,
    current_user: dict = Depends(get_current_user)
):
    """Upload contacts from JSON or CSV file."""
    try:
        loader = InputLoader()
        
        if file.endswith('.json'):
            contacts = loader.load_from_json(file)
        elif file.endswith('.csv'):
            contacts = loader.load_from_csv(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Add contacts to database
        added_contacts = []
        for contact in contacts:
            try:
                contact_id = db.add_contact(contact)
                contact['id'] = contact_id
                added_contacts.append(contact)
            except Exception:
                # Skip duplicate contacts
                pass
        
        return {
            "success": True,
            "message": f"Uploaded {len(added_contacts)} contacts",
            "data": added_contacts
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Export endpoints
@app.get("/api/export/contacts")
async def export_contacts(current_user: dict = Depends(get_current_user)):
    """Export all contacts to CSV."""
    output_path = "contacts_export.csv"
    success = db.export_contacts_to_csv(output_path)
    
    if not success:
        raise HTTPException(status_code=500, detail="Export failed")
    
    return {"success": True, "message": "Contacts exported successfully", "file": output_path}


@app.get("/api/export/logs")
async def export_logs(current_user: dict = Depends(get_current_user)):
    """Export all logs to CSV."""
    output_path = "logs_export.csv"
    success = db.export_logs_to_csv(output_path)
    
    if not success:
        raise HTTPException(status_code=500, detail="Export failed")
    
    return {"success": True, "message": "Logs exported successfully", "file": output_path}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
