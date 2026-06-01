import json
import csv
import re
from typing import List, Dict, Optional


class ValidationError(Exception):
    """Custom exception for validation errors with detailed messages."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error for field '{field}': {message}")


class InputLoader:
    """Load and validate contact data for cold emails."""
    
    # Validation rules
    VALIDATION_RULES = {
        "recipient_email": {"required": True, "type": str, "format": "email"},
        "company": {"required": True, "type": str, "min_length": 1},
        "role": {"required": True, "type": str, "min_length": 1},
        "candidate_name": {"required": True, "type": str, "min_length": 1},
        "candidate_background": {"required": True, "type": str, "min_length": 10},
        "portfolio_url": {"required": False, "type": str, "format": "url"},
    }
    
    # Field name mapping for different CSV column names
    FIELD_MAPPING = {
        "email": "recipient_email",
        "recipient": "recipient_name",
        "name": "recipient_name",
        "organization": "company",
        "org": "company",
        "position": "role",
        "job_title": "role",
        "title": "role",
        "my_name": "candidate_name",
        "applicant_name": "candidate_name",
        "background": "candidate_background",
        "my_background": "candidate_background",
        "portfolio": "portfolio_url",
        "link": "portfolio_url",
        "note": "personalization_note",
        "personalization": "personalization_note",
    }
    
    # Hardcoded sample contacts for MVP demo
    SAMPLE_CONTACTS = [
        {
            "recipient_name": "Priya Sharma",
            "recipient_email": "priya@example.com",
            "company": "Acme AI",
            "role": "Backend Engineering Intern",
            "personalization_note": "Company recently launched an AI workflow automation product",
            "candidate_name": "Your Name",
            "candidate_background": "Python developer interested in automation and AI agents",
            "portfolio_url": "https://github.com/yourname"
        },
        {
            "recipient_name": "Alex Johnson",
            "recipient_email": "alex@techstart.io",
            "company": "TechStart",
            "role": "Full Stack Developer",
            "personalization_note": "Recently raised Series B funding for their developer tools platform",
            "candidate_name": "Your Name",
            "candidate_background": "Full-stack developer with experience in React and Python",
            "portfolio_url": "https://github.com/yourname"
        },
        {
            "recipient_name": "Sarah Chen",
            "recipient_email": "sarah@innovate.co",
            "company": "Innovate Co",
            "role": "Software Engineer",
            "personalization_note": "Building next-gen productivity tools for remote teams",
            "candidate_name": "Your Name",
            "candidate_background": "Software engineer passionate about building tools that help people work better",
            "portfolio_url": "https://github.com/yourname"
        },
        {
            "recipient_name": "Michael Brown",
            "recipient_email": "michael@datalytics.com",
            "company": "DataLytics",
            "role": "Data Engineering Intern",
            "personalization_note": "Leading provider of real-time analytics solutions",
            "candidate_name": "Your Name",
            "candidate_background": "Data engineering student with experience in Python and SQL",
            "portfolio_url": "https://github.com/yourname"
        },
        {
            "recipient_name": "Emily Davis",
            "recipient_email": "emily@cloudscale.io",
            "company": "CloudScale",
            "role": "DevOps Engineer",
            "personalization_note": "Expanding their cloud infrastructure team to support growing customer base",
            "candidate_name": "Your Name",
            "candidate_background": "DevOps enthusiast with experience in AWS and containerization",
            "portfolio_url": "https://github.com/yourname"
        }
    ]
    
    def __init__(self):
        """Initialize the input loader."""
        self.contacts: List[Dict] = []
    
    def load_contacts(self, input_source: Optional[str] = None) -> List[Dict]:
        """Load contacts from specified source or use hardcoded data."""
        if input_source is None:
            return self.load_hardcoded_contacts()
        
        if input_source.endswith('.json'):
            return self.load_from_json(input_source)
        elif input_source.endswith('.csv'):
            return self.load_from_csv(input_source)
        else:
            raise ValueError(f"Unsupported input format: {input_source}. Use .json or .csv")
    
    def load_hardcoded_contacts(self) -> List[Dict]:
        """Load hardcoded sample contacts."""
        self.contacts = [self.validate_record(record) for record in self.SAMPLE_CONTACTS]
        return self.contacts
    
    def load_from_json(self, filepath: str) -> List[Dict]:
        """Load contacts from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValidationError("root", "JSON file must contain a list of contact objects")
            
            self.contacts = [self.validate_record(record) for record in data]
            print(f"Loaded {len(self.contacts)} contacts from {filepath}")
            return self.contacts
        
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise ValidationError("json", f"Invalid JSON format: {e}")
    
    def load_from_csv(self, filepath: str) -> List[Dict]:
        """Load contacts from CSV file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Map column names to standard field names
            normalized_rows = [self.normalize_field_names(row) for row in rows]
            
            self.contacts = [self.validate_record(row) for row in normalized_rows]
            print(f"Loaded {len(self.contacts)} contacts from {filepath}")
            return self.contacts
        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    def validate_record(self, record: Dict) -> Dict:
        """Validate a contact record with enhanced validation rules."""
        validated = {}
        errors = []
        
        # Validate each field according to rules
        for field, rules in self.VALIDATION_RULES.items():
            value = record.get(field)
            
            # Check if required
            if rules.get("required", False):
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"Field '{field}' is required")
                    continue
            
            # Skip validation if field is not required and not present
            if value is None or (isinstance(value, str) and not value.strip()):
                validated[field] = ""
                continue
            
            # Type validation
            if "type" in rules and not isinstance(value, rules["type"]):
                errors.append(f"Field '{field}' must be of type {rules['type'].__name__}")
                continue
            
            # Min length validation
            if "min_length" in rules and isinstance(value, str) and len(value) < rules["min_length"]:
                errors.append(f"Field '{field}' must be at least {rules['min_length']} characters")
                continue
            
            # Format validation
            if "format" in rules:
                if rules["format"] == "email" and not self._validate_email(value):
                    errors.append(f"Field '{field}' must be a valid email address")
                elif rules["format"] == "url" and not self._validate_url(value):
                    errors.append(f"Field '{field}' must be a valid URL")
            
            validated[field] = value
        
        # Copy optional fields not in validation rules
        optional_fields = ["recipient_name", "personalization_note"]
        for field in optional_fields:
            validated[field] = record.get(field, "")
        
        # Raise error if validation failed
        if errors:
            raise ValidationError("record", "; ".join(errors))
        
        # Normalize data
        validated = self.normalize_record(validated)
        
        return validated
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format using regex."""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None
    
    def normalize_record(self, record: Dict) -> Dict:
        """Normalize a contact record (trim whitespace, handle empty strings)."""
        normalized = {}
        
        for key, value in record.items():
            if isinstance(value, str):
                normalized[key] = value.strip() if value.strip() else ""
            else:
                normalized[key] = value
        
        return normalized
    
    def normalize_field_names(self, record: Dict) -> Dict:
        """Map non-standard field names to standard field names."""
        normalized = {}
        
        for key, value in record.items():
            # Convert to lowercase and strip whitespace
            normalized_key = key.strip().lower()
            
            # Map to standard field name if mapping exists
            if normalized_key in self.FIELD_MAPPING:
                normalized[self.FIELD_MAPPING[normalized_key]] = value
            else:
                normalized[key] = value
        
        return normalized
