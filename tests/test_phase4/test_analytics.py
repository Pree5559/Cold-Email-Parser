import pytest
import os
import sys
import tempfile
import pandas as pd

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'phase4'))

from phase4.database import Database
from phase4.analytics import AnalyticsDashboard


@pytest.fixture
def temp_db():
    """Create a temporary database with test data."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = Database(db_path)
    
    # Add test contacts
    for i in range(10):
        contact = {
            'recipient_email': f'contact{i}@example.com',
            'recipient_name': f'Contact {i}',
            'company': f'Company {i % 3}',  # 3 companies
            'role': 'Developer',
            'candidate_name': 'Candidate',
            'candidate_background': 'Python developer'
        }
        db.add_contact(contact)
    
    # Add test logs
    contacts = db.get_all_contacts()
    for i, contact in enumerate(contacts):
        status = 'sent' if i < 6 else ('skipped' if i < 8 else 'failed')
        log_entry = {
            'contact_id': contact['id'],
            'subject': f'Subject {i}',
            'status': status,
            'word_count': 80 + i * 5,
            'template_used': ['default', 'direct', 'story'][i % 3],
            'quality_score': 70 + i * 2,
            'spam_risk': 'low' if i < 7 else 'medium'
        }
        db.add_log_entry(log_entry)
    
    yield db
    
    db.close()
    os.unlink(db_path)


@pytest.fixture
def analytics(temp_db):
    """Create an analytics dashboard for testing."""
    return AnalyticsDashboard(temp_db)


class TestAnalyticsDashboard:
    """Test analytics dashboard operations."""
    
    def test_get_overview_stats(self, analytics):
        """Test getting overview statistics."""
        stats = analytics.get_overview_stats()
        
        assert 'total_contacts' in stats
        assert 'total_emails_sent' in stats
        assert 'success_rate' in stats
        assert 'average_quality_score' in stats
        assert stats['total_contacts'] == 10
    
    def test_get_time_series_data(self, analytics):
        """Test getting time series data."""
        df = analytics.get_time_series_data(days=30)
        
        assert isinstance(df, pd.DataFrame)
        # Should have data since we added logs
        assert not df.empty or len(df.columns) > 0
    
    def test_create_time_series_chart(self, analytics):
        """Test creating time series chart."""
        fig = analytics.create_time_series_chart(days=30)
        
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_create_status_pie_chart(self, analytics):
        """Test creating status pie chart."""
        fig = analytics.create_status_pie_chart()
        
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_create_quality_score_chart(self, analytics):
        """Test creating quality score histogram."""
        fig = analytics.create_quality_score_chart()
        
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_create_company_chart(self, analytics):
        """Test creating company bar chart."""
        fig = analytics.create_company_chart(top_n=5)
        
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_create_template_performance_chart(self, analytics):
        """Test creating template performance chart."""
        fig = analytics.create_template_performance_chart()
        
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_create_word_count_chart(self, analytics):
        """Test creating word count vs quality scatter plot."""
        fig = analytics.create_word_count_chart()
        
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_get_detailed_metrics(self, analytics):
        """Test getting detailed metrics."""
        metrics = analytics.get_detailed_metrics()
        
        assert 'total_emails' in metrics
        assert 'average_word_count' in metrics
        assert 'average_quality_score' in metrics
        assert metrics['total_emails'] == 10
    
    def test_export_analytics_report(self, analytics, tmp_path):
        """Test exporting analytics report."""
        output_path = str(tmp_path / "analytics_export.csv")
        success = analytics.export_analytics_report(output_path)
        
        assert success is True
        assert os.path.exists(output_path)
