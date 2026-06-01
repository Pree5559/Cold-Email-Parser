import pytest
import os
import sys
import tempfile
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'phase4'))

from phase4.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = Database(db_path)
    yield db
    
    db.close()
    os.unlink(db_path)


class TestDatabase:
    """Test database operations."""
    
    def test_database_initialization(self, temp_db):
        """Test that database initializes correctly."""
        assert temp_db.conn is not None
        assert temp_db.db_path.endswith('.db')
    
    def test_add_contact(self, temp_db):
        """Test adding a contact."""
        contact = {
            'recipient_email': 'test@example.com',
            'recipient_name': 'Test User',
            'company': 'Test Company',
            'role': 'Test Role',
            'candidate_name': 'Candidate',
            'candidate_background': 'Python developer',
            'portfolio_url': 'https://github.com/test'
        }
        
        contact_id = temp_db.add_contact(contact)
        assert contact_id > 0
        
        retrieved = temp_db.get_contact(contact_id)
        assert retrieved is not None
        assert retrieved['recipient_email'] == 'test@example.com'
    
    def test_get_contact_by_email(self, temp_db):
        """Test retrieving contact by email."""
        contact = {
            'recipient_email': 'email@example.com',
            'recipient_name': 'Email User',
            'company': 'Email Co',
            'role': 'Developer',
            'candidate_name': 'Dev',
            'candidate_background': 'Backend dev'
        }
        
        temp_db.add_contact(contact)
        
        retrieved = temp_db.get_contact_by_email('email@example.com')
        assert retrieved is not None
        assert retrieved['company'] == 'Email Co'
    
    def test_get_all_contacts(self, temp_db):
        """Test retrieving all contacts."""
        for i in range(3):
            contact = {
                'recipient_email': f'user{i}@example.com',
                'recipient_name': f'User {i}',
                'company': f'Company {i}',
                'role': 'Role',
                'candidate_name': 'Candidate',
                'candidate_background': 'Background'
            }
            temp_db.add_contact(contact)
        
        contacts = temp_db.get_all_contacts()
        assert len(contacts) == 3
    
    def test_update_contact(self, temp_db):
        """Test updating a contact."""
        contact = {
            'recipient_email': 'update@example.com',
            'recipient_name': 'Original Name',
            'company': 'Original Co',
            'role': 'Role',
            'candidate_name': 'Candidate',
            'candidate_background': 'Background'
        }
        
        contact_id = temp_db.add_contact(contact)
        
        success = temp_db.update_contact(contact_id, {'recipient_name': 'Updated Name'})
        assert success is True
        
        updated = temp_db.get_contact(contact_id)
        assert updated['recipient_name'] == 'Updated Name'
    
    def test_update_contact_status(self, temp_db):
        """Test updating contact status."""
        contact = {
            'recipient_email': 'status@example.com',
            'recipient_name': 'Status User',
            'company': 'Status Co',
            'role': 'Role',
            'candidate_name': 'Candidate',
            'candidate_background': 'Background'
        }
        
        contact_id = temp_db.add_contact(contact)
        
        success = temp_db.update_contact_status(contact_id, 'contacted')
        assert success is True
        
        updated = temp_db.get_contact(contact_id)
        assert updated['status'] == 'contacted'
    
    def test_delete_contact(self, temp_db):
        """Test deleting a contact."""
        contact = {
            'recipient_email': 'delete@example.com',
            'recipient_name': 'Delete User',
            'company': 'Delete Co',
            'role': 'Role',
            'candidate_name': 'Candidate',
            'candidate_background': 'Background'
        }
        
        contact_id = temp_db.add_contact(contact)
        
        success = temp_db.delete_contact(contact_id)
        assert success is True
        
        deleted = temp_db.get_contact(contact_id)
        assert deleted is None
    
    def test_add_log_entry(self, temp_db):
        """Test adding a log entry."""
        contact = {
            'recipient_email': 'log@example.com',
            'recipient_name': 'Log User',
            'company': 'Log Co',
            'role': 'Role',
            'candidate_name': 'Candidate',
            'candidate_background': 'Background'
        }
        
        contact_id = temp_db.add_contact(contact)
        
        log_entry = {
            'contact_id': contact_id,
            'subject': 'Test Subject',
            'status': 'sent',
            'word_count': 100,
            'template_used': 'default'
        }
        
        log_id = temp_db.add_log_entry(log_entry)
        assert log_id > 0
    
    def test_get_logs(self, temp_db):
        """Test retrieving log entries."""
        contact = {
            'recipient_email': 'logs@example.com',
            'recipient_name': 'Logs User',
            'company': 'Logs Co',
            'role': 'Role',
            'candidate_name': 'Candidate',
            'candidate_background': 'Background'
        }
        
        contact_id = temp_db.add_contact(contact)
        
        for i in range(3):
            log_entry = {
                'contact_id': contact_id,
                'subject': f'Subject {i}',
                'status': 'sent',
                'word_count': 100
            }
            temp_db.add_log_entry(log_entry)
        
        logs = temp_db.get_logs()
        assert len(logs) == 3
    
    def test_get_statistics(self, temp_db):
        """Test getting statistics."""
        # Add some test data
        for i in range(5):
            contact = {
                'recipient_email': f'stat{i}@example.com',
                'recipient_name': f'Stat {i}',
                'company': f'Stat Co {i}',
                'role': 'Role',
                'candidate_name': 'Candidate',
                'candidate_background': 'Background'
            }
            contact_id = temp_db.add_contact(contact)
            
            log_entry = {
                'contact_id': contact_id,
                'subject': 'Subject',
                'status': 'sent' if i < 3 else 'skipped',
                'word_count': 100
            }
            temp_db.add_log_entry(log_entry)
        
        stats = temp_db.get_statistics()
        assert stats['total_contacts'] == 5
        assert stats['total_logs'] == 5
        assert stats['logs_by_status']['sent'] == 3
        assert stats['logs_by_status']['skipped'] == 2
    
    def test_user_operations(self, temp_db):
        """Test user authentication operations."""
        username = 'testuser'
        password_hash = 'hashed_password'
        
        user_id = temp_db.add_user(username, password_hash, 'test@example.com')
        assert user_id > 0
        
        user = temp_db.get_user(username)
        assert user is not None
        assert user['username'] == username
        assert user['email'] == 'test@example.com'
    
    def test_duplicate_user(self, temp_db):
        """Test that duplicate usernames are rejected."""
        username = 'duplicate'
        temp_db.add_user(username, 'hash1', 'email1@example.com')
        
        with pytest.raises(ValueError):
            temp_db.add_user(username, 'hash2', 'email2@example.com')
