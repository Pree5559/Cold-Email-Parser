import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json


class Database:
    """SQLite database manager for contacts and outreach logs."""
    
    def __init__(self, db_path: str = "cold_email_bot.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dictionary-like access
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_email TEXT UNIQUE NOT NULL,
                recipient_name TEXT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                personalization_note TEXT,
                candidate_name TEXT NOT NULL,
                candidate_background TEXT NOT NULL,
                portfolio_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contacted_at TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Outreach logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subject TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                word_count INTEGER,
                template_used TEXT,
                quality_score INTEGER,
                spam_risk TEXT,
                FOREIGN KEY (contact_id) REFERENCES contacts(id)
            )
        """)
        
        # Users table (for authentication)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_contacts_email 
            ON contacts(recipient_email)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_logs_contact_id 
            ON outreach_logs(contact_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
            ON outreach_logs(timestamp)
        """)
        
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    # Contact CRUD Operations
    
    def add_contact(self, contact: Dict) -> int:
        """Add a new contact to the database.
        
        Args:
            contact: Dictionary containing contact information
            
        Returns:
            ID of the inserted contact
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO contacts (
                    recipient_email, recipient_name, company, role,
                    personalization_note, candidate_name, candidate_background,
                    portfolio_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact['recipient_email'],
                contact.get('recipient_name', ''),
                contact['company'],
                contact['role'],
                contact.get('personalization_note', ''),
                contact['candidate_name'],
                contact['candidate_background'],
                contact.get('portfolio_url', '')
            ))
            
            self.conn.commit()
            return cursor.lastrowid
        
        except sqlite3.IntegrityError:
            # Contact with this email already exists
            existing = self.get_contact_by_email(contact['recipient_email'])
            if existing:
                return existing['id']
            raise
    
    def get_contact(self, contact_id: int) -> Optional[Dict]:
        """Get a contact by ID.
        
        Args:
            contact_id: ID of the contact
            
        Returns:
            Contact dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_contact_by_email(self, email: str) -> Optional[Dict]:
        """Get a contact by email address.
        
        Args:
            email: Email address of the contact
            
        Returns:
            Contact dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE recipient_email = ?", (email,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_contacts(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get all contacts, optionally filtered by status.
        
        Args:
            status: Filter by status (pending, contacted, skipped, etc.)
            limit: Maximum number of contacts to return
            
        Returns:
            List of contact dictionaries
        """
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM contacts 
                WHERE status = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT * FROM contacts 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_contact(self, contact_id: int, updates: Dict) -> bool:
        """Update a contact's information.
        
        Args:
            contact_id: ID of the contact to update
            updates: Dictionary of fields to update
            
        Returns:
            True if update was successful
        """
        cursor = self.conn.cursor()
        
        # Build dynamic UPDATE query
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [contact_id]
        
        cursor.execute(f"""
            UPDATE contacts 
            SET {set_clause} 
            WHERE id = ?
        """, values)
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_contact_status(self, contact_id: int, status: str) -> bool:
        """Update a contact's status.
        
        Args:
            contact_id: ID of the contact
            status: New status (pending, contacted, skipped, etc.)
            
        Returns:
            True if update was successful
        """
        return self.update_contact(contact_id, {'status': status, 'last_contacted_at': datetime.now().isoformat()})
    
    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact from the database.
        
        Args:
            contact_id: ID of the contact to delete
            
        Returns:
            True if deletion was successful
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Outreach Log Operations
    
    def add_log_entry(self, log_entry: Dict) -> int:
        """Add a new outreach log entry.
        
        Args:
            log_entry: Dictionary containing log information
            
        Returns:
            ID of the inserted log entry
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO outreach_logs (
                contact_id, timestamp, subject, status, error_message,
                word_count, template_used, quality_score, spam_risk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_entry.get('contact_id'),
            log_entry.get('timestamp', datetime.now().isoformat()),
            log_entry.get('subject', ''),
            log_entry['status'],
            log_entry.get('error_message', ''),
            log_entry.get('word_count', 0),
            log_entry.get('template_used', 'default'),
            log_entry.get('quality_score'),
            log_entry.get('spam_risk')
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_logs(self, contact_id: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """Get outreach log entries.
        
        Args:
            contact_id: Filter by contact ID (optional)
            limit: Maximum number of entries to return
            
        Returns:
            List of log entry dictionaries
        """
        cursor = self.conn.cursor()
        
        if contact_id:
            cursor.execute("""
                SELECT * FROM outreach_logs 
                WHERE contact_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (contact_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM outreach_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_contact_logs(self, contact_id: int) -> List[Dict]:
        """Get all log entries for a specific contact.
        
        Args:
            contact_id: ID of the contact
            
        Returns:
            List of log entry dictionaries
        """
        return self.get_logs(contact_id=contact_id)
    
    # Statistics and Analytics
    
    def get_statistics(self) -> Dict:
        """Get overall statistics.
        
        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()
        
        # Total contacts
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        total_contacts = cursor.fetchone()['count']
        
        # Contacts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM contacts 
            GROUP BY status
        """)
        contacts_by_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Total logs
        cursor.execute("SELECT COUNT(*) as count FROM outreach_logs")
        total_logs = cursor.fetchone()['count']
        
        # Logs by status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM outreach_logs 
            GROUP BY status
        """)
        logs_by_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Average quality score
        cursor.execute("""
            SELECT AVG(quality_score) as avg_score 
            FROM outreach_logs 
            WHERE quality_score IS NOT NULL
        """)
        avg_quality = cursor.fetchone()['avg_score'] or 0
        
        # Success rate
        sent_count = logs_by_status.get('sent', 0)
        success_rate = (sent_count / total_logs * 100) if total_logs > 0 else 0
        
        return {
            'total_contacts': total_contacts,
            'contacts_by_status': contacts_by_status,
            'total_logs': total_logs,
            'logs_by_status': logs_by_status,
            'average_quality_score': round(avg_quality, 2),
            'success_rate': round(success_rate, 2)
        }
    
    # User Authentication Operations
    
    def add_user(self, username: str, password_hash: str, email: Optional[str] = None) -> int:
        """Add a new user.
        
        Args:
            username: Username
            password_hash: Hashed password
            email: Email address (optional)
            
        Returns:
            ID of the inserted user
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            """, (username, password_hash, email))
            
            self.conn.commit()
            return cursor.lastrowid
        
        except sqlite3.IntegrityError:
            raise ValueError(f"Username '{username}' already exists")
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get a user by username.
        
        Args:
            username: Username
            
        Returns:
            User dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def update_user_login(self, username: str) -> bool:
        """Update user's last login timestamp.
        
        Args:
            username: Username
            
        Returns:
            True if update was successful
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET last_login = ? 
            WHERE username = ?
        """, (datetime.now().isoformat(), username))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Database Maintenance
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database.
        
        Args:
            backup_path: Path for the backup file
            
        Returns:
            True if backup was successful
        """
        try:
            # Close current connection
            self.close()
            
            # Copy database file
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # Reconnect
            self._connect()
            
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            self._connect()
            return False
    
    def export_contacts_to_csv(self, output_path: str) -> bool:
        """Export all contacts to CSV file.
        
        Args:
            output_path: Path for the CSV file
            
        Returns:
            True if export was successful
        """
        try:
            import csv
            
            contacts = self.get_all_contacts(limit=10000)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if contacts:
                    writer = csv.DictWriter(f, fieldnames=contacts[0].keys())
                    writer.writeheader()
                    writer.writerows(contacts)
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def export_logs_to_csv(self, output_path: str) -> bool:
        """Export all logs to CSV file.
        
        Args:
            output_path: Path for the CSV file
            
        Returns:
            True if export was successful
        """
        try:
            import csv
            
            logs = self.get_logs(limit=10000)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if logs:
                    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                    writer.writeheader()
                    writer.writerows(logs)
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
