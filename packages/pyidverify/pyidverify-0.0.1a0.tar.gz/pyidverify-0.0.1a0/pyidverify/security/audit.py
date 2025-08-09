"""
Security Audit and Tamper-Evident Logging

Provides comprehensive audit trail capabilities with tamper-evident logging,
secure event tracking, compliance reporting, and forensic analysis support.
Implements NIST SP 800-92 guidelines for security log management.

Features:
- Tamper-evident logging with cryptographic integrity
- Real-time security event monitoring
- Compliance reporting for GDPR, HIPAA, PCI DSS, SOX
- Forensic analysis support with detailed event correlation
- Secure log storage with encryption at rest
- Automatic log rotation and archival

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import json
import time
import uuid
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path
import logging
import hashlib
import hmac
import gzip
import os

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from .exceptions import SecurityError, AuditError, ComplianceError
from .constants import SecurityLevel, ComplianceFramework
from .encryption import SecureEncryption, secure_random

# Configure logging
logger = logging.getLogger('pyidverify.security.audit')


class AuditEvent:
    """
    Represents a single audit event with all required metadata.
    """
    
    def __init__(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        security_level: SecurityLevel = SecurityLevel.STANDARD
    ):
        """
        Create new audit event.
        
        Args:
            event_type: Type of event (authentication, access, error, etc.)
            event_data: Event-specific data
            user_id: User identifier (if applicable)
            session_id: Session identifier (if applicable)  
            source_ip: Source IP address
            user_agent: User agent string
            security_level: Security level for this event
        """
        self.event_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)
        self.event_type = event_type
        self.event_data = event_data
        self.user_id = user_id
        self.session_id = session_id
        self.source_ip = source_ip
        self.user_agent = user_agent
        self.security_level = security_level
        
        # Additional metadata
        self.process_id = os.getpid()
        self.thread_id = threading.get_ident()
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
        
        # Compliance flags
        self.gdpr_relevant = False
        self.hipaa_relevant = False
        self.pci_relevant = False
        self.sox_relevant = False
        
        # Set compliance flags based on event type
        self._set_compliance_flags()
    
    def _set_compliance_flags(self) -> None:
        """Set compliance relevance flags based on event type and data."""
        event_type_lower = self.event_type.lower()
        event_data_str = str(self.event_data).lower()
        
        # GDPR: Personal data processing events
        if any(keyword in event_type_lower or keyword in event_data_str 
               for keyword in ['personal', 'pii', 'data_processing', 'consent', 'privacy']):
            self.gdpr_relevant = True
        
        # HIPAA: Health information events
        if any(keyword in event_type_lower or keyword in event_data_str 
               for keyword in ['health', 'medical', 'phi', 'patient']):
            self.hipaa_relevant = True
        
        # PCI DSS: Payment card events
        if any(keyword in event_type_lower or keyword in event_data_str 
               for keyword in ['payment', 'card', 'transaction', 'cardholder']):
            self.pci_relevant = True
        
        # SOX: Financial reporting events
        if any(keyword in event_type_lower or keyword in event_data_str 
               for keyword in ['financial', 'accounting', 'report', 'audit']):
            self.sox_relevant = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert audit event to dictionary.
        
        Returns:
            Dictionary representation of audit event
        """
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'event_data': self.event_data,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'source_ip': self.source_ip,
            'user_agent': self.user_agent,
            'security_level': self.security_level.name,
            'process_id': self.process_id,
            'thread_id': self.thread_id,
            'hostname': self.hostname,
            'compliance': {
                'gdpr_relevant': self.gdpr_relevant,
                'hipaa_relevant': self.hipaa_relevant,
                'pci_relevant': self.pci_relevant,
                'sox_relevant': self.sox_relevant
            }
        }
    
    def to_json(self) -> str:
        """
        Convert audit event to JSON string.
        
        Returns:
            JSON representation of audit event
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """
        Create audit event from dictionary.
        
        Args:
            data: Dictionary containing event data
            
        Returns:
            AuditEvent instance
        """
        event = cls(
            event_type=data['event_type'],
            event_data=data['event_data'],
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            source_ip=data.get('source_ip'),
            user_agent=data.get('user_agent'),
            security_level=SecurityLevel[data.get('security_level', 'STANDARD')]
        )
        
        # Override generated values with stored ones
        event.event_id = data['event_id']
        event.timestamp = datetime.fromisoformat(data['timestamp'])
        event.process_id = data.get('process_id', os.getpid())
        event.thread_id = data.get('thread_id', threading.get_ident())
        event.hostname = data.get('hostname', 'unknown')
        
        # Set compliance flags
        compliance = data.get('compliance', {})
        event.gdpr_relevant = compliance.get('gdpr_relevant', False)
        event.hipaa_relevant = compliance.get('hipaa_relevant', False)
        event.pci_relevant = compliance.get('pci_relevant', False)
        event.sox_relevant = compliance.get('sox_relevant', False)
        
        return event


class TamperEvidenceChain:
    """
    Maintains tamper-evident chain of audit events using cryptographic hashing.
    """
    
    def __init__(self, private_key: Optional[bytes] = None):
        """
        Initialize tamper evidence chain.
        
        Args:
            private_key: Optional Ed25519 private key for signing (generated if not provided)
        """
        self._events = []
        self._chain_hash = b'\x00' * 32  # Initial hash
        self._sequence_number = 0
        
        # Initialize signing key
        if CRYPTOGRAPHY_AVAILABLE:
            if private_key is not None:
                self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
            else:
                self._private_key = ed25519.Ed25519PrivateKey.generate()
            self._public_key = self._private_key.public_key()
        else:
            self._private_key = None
            self._public_key = None
            logger.warning("Cryptography not available - using HMAC instead of Ed25519")
            self._signing_key = secure_random.bytes(32)
    
    def add_event(self, event: AuditEvent) -> Dict[str, Any]:
        """
        Add event to tamper-evident chain.
        
        Args:
            event: Audit event to add
            
        Returns:
            Chain metadata for the event
        """
        self._sequence_number += 1
        
        # Create event record with chain metadata
        event_record = {
            'sequence': self._sequence_number,
            'previous_hash': self._chain_hash.hex(),
            'event': event.to_dict(),
            'timestamp_added': datetime.now(timezone.utc).isoformat()
        }
        
        # Calculate event hash
        event_bytes = json.dumps(event_record, sort_keys=True).encode('utf-8')
        event_hash = hashlib.sha256(event_bytes).digest()
        
        # Sign the event hash
        if CRYPTOGRAPHY_AVAILABLE and self._private_key:
            signature = self._private_key.sign(event_hash)
        else:
            # Fallback to HMAC
            signature = hmac.new(
                self._signing_key,
                event_hash,
                hashlib.sha256
            ).digest()
        
        # Add signature to record
        event_record['signature'] = signature.hex()
        event_record['event_hash'] = event_hash.hex()
        
        # Update chain hash
        self._chain_hash = hashlib.sha256(
            self._chain_hash + event_hash + signature
        ).digest()
        
        # Store event
        self._events.append(event_record)
        
        return {
            'sequence': self._sequence_number,
            'event_hash': event_hash.hex(),
            'chain_hash': self._chain_hash.hex(),
            'signature': signature.hex()
        }
    
    def verify_chain(self) -> Dict[str, Any]:
        """
        Verify integrity of entire audit chain.
        
        Returns:
            Verification results
        """
        if not self._events:
            return {
                'valid': True,
                'total_events': 0,
                'corrupted_events': [],
                'chain_breaks': []
            }
        
        corrupted_events = []
        chain_breaks = []
        current_hash = b'\x00' * 32
        
        for i, record in enumerate(self._events):
            try:
                # Verify previous hash matches
                if bytes.fromhex(record['previous_hash']) != current_hash:
                    chain_breaks.append({
                        'sequence': record['sequence'],
                        'expected_hash': current_hash.hex(),
                        'actual_hash': record['previous_hash']
                    })
                
                # Recalculate event hash
                event_record_copy = dict(record)
                del event_record_copy['signature']
                del event_record_copy['event_hash']
                
                event_bytes = json.dumps(event_record_copy, sort_keys=True).encode('utf-8')
                calculated_hash = hashlib.sha256(event_bytes).digest()
                
                stored_hash = bytes.fromhex(record['event_hash'])
                if calculated_hash != stored_hash:
                    corrupted_events.append({
                        'sequence': record['sequence'],
                        'calculated_hash': calculated_hash.hex(),
                        'stored_hash': record['event_hash']
                    })
                
                # Verify signature
                signature = bytes.fromhex(record['signature'])
                if CRYPTOGRAPHY_AVAILABLE and self._public_key:
                    try:
                        self._public_key.verify(signature, calculated_hash)
                    except Exception:
                        corrupted_events.append({
                            'sequence': record['sequence'],
                            'error': 'Invalid signature'
                        })
                else:
                    # Verify HMAC
                    expected_signature = hmac.new(
                        self._signing_key,
                        calculated_hash,
                        hashlib.sha256
                    ).digest()
                    if signature != expected_signature:
                        corrupted_events.append({
                            'sequence': record['sequence'],
                            'error': 'Invalid HMAC signature'
                        })
                
                # Update current hash for next iteration
                current_hash = hashlib.sha256(
                    current_hash + calculated_hash + signature
                ).digest()
                
            except Exception as e:
                corrupted_events.append({
                    'sequence': record.get('sequence', i),
                    'error': f'Verification error: {e}'
                })
        
        return {
            'valid': len(corrupted_events) == 0 and len(chain_breaks) == 0,
            'total_events': len(self._events),
            'corrupted_events': corrupted_events,
            'chain_breaks': chain_breaks,
            'final_hash': current_hash.hex()
        }
    
    def get_public_key(self) -> Optional[bytes]:
        """
        Get public key for signature verification.
        
        Returns:
            Public key bytes (if available)
        """
        if CRYPTOGRAPHY_AVAILABLE and self._public_key:
            return self._public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        return None
    
    def export_chain(self) -> List[Dict[str, Any]]:
        """
        Export entire audit chain.
        
        Returns:
            List of all events in chain
        """
        return self._events.copy()


class SecureAuditLogger:
    """
    High-security audit logger with tamper-evident storage and compliance reporting.
    """
    
    def __init__(
        self,
        log_directory: Union[str, Path],
        security_level: SecurityLevel = SecurityLevel.MAXIMUM,
        encryption_key: Optional[bytes] = None,
        max_log_size: int = 100 * 1024 * 1024,  # 100MB
        retention_days: int = 2555  # 7 years for compliance
    ):
        """
        Initialize secure audit logger.
        
        Args:
            log_directory: Directory to store audit logs
            security_level: Security level for audit operations
            encryption_key: Optional encryption key for log files
            max_log_size: Maximum size per log file in bytes
            retention_days: Log retention period in days
        """
        self.log_directory = Path(log_directory)
        self.security_level = security_level
        self.max_log_size = max_log_size
        self.retention_days = retention_days
        
        # Create log directory
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self.encryption = SecureEncryption(
            security_level=security_level
        ) if encryption_key is None else SecureEncryption(
            security_level=security_level,
            master_key=encryption_key
        )
        
        # Initialize tamper evidence chain
        self.chain = TamperEvidenceChain()
        
        # Current log file tracking
        self.current_log_file = None
        self.current_log_size = 0
        
        # Event handlers
        self.event_handlers: List[Callable[[AuditEvent], None]] = []
        
        # Statistics tracking
        self.stats = {
            'events_logged': 0,
            'files_created': 0,
            'compliance_events': {
                'gdpr': 0,
                'hipaa': 0,
                'pci': 0,
                'sox': 0
            }
        }
        
        # Initialize current log file
        self._rotate_log_file()
        
        logger.info(f"SecureAuditLogger initialized with {security_level.name} security")
    
    def log_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Log security audit event.
        
        Args:
            event_type: Type of event
            event_data: Event-specific data
            user_id: User identifier
            session_id: Session identifier
            source_ip: Source IP address
            user_agent: User agent string
            
        Returns:
            Event ID
        """
        # Create audit event
        event = AuditEvent(
            event_type=event_type,
            event_data=event_data,
            user_id=user_id,
            session_id=session_id,
            source_ip=source_ip,
            user_agent=user_agent,
            security_level=self.security_level
        )
        
        try:
            # Add to tamper-evident chain
            chain_metadata = self.chain.add_event(event)
            
            # Prepare log entry
            log_entry = {
                'event': event.to_dict(),
                'chain': chain_metadata,
                'logged_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Encrypt log entry
            encrypted_entry = self.encryption.encrypt(json.dumps(log_entry))
            
            # Write to log file
            self._write_log_entry(encrypted_entry)
            
            # Update statistics
            self.stats['events_logged'] += 1
            if event.gdpr_relevant:
                self.stats['compliance_events']['gdpr'] += 1
            if event.hipaa_relevant:
                self.stats['compliance_events']['hipaa'] += 1
            if event.pci_relevant:
                self.stats['compliance_events']['pci'] += 1
            if event.sox_relevant:
                self.stats['compliance_events']['sox'] += 1
            
            # Notify event handlers
            for handler in self.event_handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
            
            return event.event_id
            
        except Exception as e:
            raise AuditError(
                f"Failed to log audit event: {e}",
                event_type=event_type,
                operation="log_event"
            )
    
    def _write_log_entry(self, encrypted_entry: bytes) -> None:
        """Write encrypted log entry to current log file."""
        entry_size = len(encrypted_entry)
        
        # Check if we need to rotate log file
        if self.current_log_size + entry_size > self.max_log_size:
            self._rotate_log_file()
        
        # Write entry with size prefix
        with open(self.current_log_file, 'ab') as f:
            # Write entry size as 4-byte big-endian integer
            f.write(entry_size.to_bytes(4, 'big'))
            # Write encrypted entry
            f.write(encrypted_entry)
        
        self.current_log_size += entry_size + 4
    
    def _rotate_log_file(self) -> None:
        """Create new log file and compress old one if needed."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        
        # Compress old log file
        if self.current_log_file and self.current_log_file.exists():
            compressed_path = self.current_log_file.with_suffix('.log.gz')
            with open(self.current_log_file, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove uncompressed file
            self.current_log_file.unlink()
        
        # Create new log file
        self.current_log_file = self.log_directory / f'audit_{timestamp}.log'
        self.current_log_size = 0
        self.stats['files_created'] += 1
        
        logger.info(f"Rotated to new log file: {self.current_log_file.name}")
    
    def add_event_handler(self, handler: Callable[[AuditEvent], None]) -> None:
        """
        Add event handler for real-time audit event processing.
        
        Args:
            handler: Function to call for each audit event
        """
        self.event_handlers.append(handler)
    
    def remove_event_handler(self, handler: Callable[[AuditEvent], None]) -> None:
        """
        Remove event handler.
        
        Args:
            handler: Handler function to remove
        """
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
    
    def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report for specified framework and date range.
        
        Args:
            framework: Compliance framework to report on
            start_date: Start date for report (defaults to 30 days ago)
            end_date: End date for report (defaults to now)
            
        Returns:
            Compliance report
        """
        if start_date is None:
            start_date = datetime.now(timezone.utc).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
        
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        
        # Read and analyze log files
        relevant_events = []
        
        for log_file in self.log_directory.glob('audit_*.log*'):
            try:
                events = self._read_log_file(log_file)
                for event in events:
                    event_time = datetime.fromisoformat(event['event']['timestamp'])
                    if start_date <= event_time <= end_date:
                        if self._is_relevant_for_framework(event['event'], framework):
                            relevant_events.append(event)
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
        
        # Generate report based on framework
        if framework == ComplianceFramework.GDPR:
            return self._generate_gdpr_report(relevant_events, start_date, end_date)
        elif framework == ComplianceFramework.HIPAA:
            return self._generate_hipaa_report(relevant_events, start_date, end_date)
        elif framework == ComplianceFramework.PCI_DSS:
            return self._generate_pci_report(relevant_events, start_date, end_date)
        elif framework == ComplianceFramework.SOX:
            return self._generate_sox_report(relevant_events, start_date, end_date)
        else:
            raise ComplianceError(
                f"Unsupported compliance framework: {framework}",
                framework=framework.value
            )
    
    def _read_log_file(self, log_file: Path) -> List[Dict[str, Any]]:
        """Read and decrypt log file entries."""
        events = []
        
        if log_file.suffix == '.gz':
            open_func = gzip.open
        else:
            open_func = open
        
        with open_func(log_file, 'rb') as f:
            while True:
                # Read entry size
                size_bytes = f.read(4)
                if not size_bytes:
                    break
                
                entry_size = int.from_bytes(size_bytes, 'big')
                
                # Read encrypted entry
                encrypted_entry = f.read(entry_size)
                if len(encrypted_entry) != entry_size:
                    break
                
                try:
                    # Decrypt entry
                    decrypted_entry = self.encryption.decrypt(encrypted_entry)
                    event_data = json.loads(decrypted_entry.decode('utf-8'))
                    events.append(event_data)
                except Exception as e:
                    logger.error(f"Failed to decrypt log entry: {e}")
        
        return events
    
    def _is_relevant_for_framework(
        self,
        event: Dict[str, Any],
        framework: ComplianceFramework
    ) -> bool:
        """Check if event is relevant for compliance framework."""
        compliance = event.get('compliance', {})
        
        if framework == ComplianceFramework.GDPR:
            return compliance.get('gdpr_relevant', False)
        elif framework == ComplianceFramework.HIPAA:
            return compliance.get('hipaa_relevant', False)
        elif framework == ComplianceFramework.PCI_DSS:
            return compliance.get('pci_relevant', False)
        elif framework == ComplianceFramework.SOX:
            return compliance.get('sox_relevant', False)
        
        return False
    
    def _generate_gdpr_report(
        self,
        events: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate GDPR compliance report."""
        return {
            'framework': 'GDPR',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': len(events),
                'data_processing_events': len([e for e in events if 'processing' in e['event']['event_type'].lower()]),
                'consent_events': len([e for e in events if 'consent' in e['event']['event_type'].lower()]),
                'access_requests': len([e for e in events if 'access_request' in e['event']['event_type'].lower()]),
                'deletion_requests': len([e for e in events if 'deletion' in e['event']['event_type'].lower()])
            },
            'events': events
        }
    
    def _generate_hipaa_report(
        self,
        events: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate HIPAA compliance report."""
        return {
            'framework': 'HIPAA',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': len(events),
                'phi_access_events': len([e for e in events if 'phi' in str(e['event']['event_data']).lower()]),
                'authentication_events': len([e for e in events if 'auth' in e['event']['event_type'].lower()]),
                'audit_events': len([e for e in events if 'audit' in e['event']['event_type'].lower()])
            },
            'events': events
        }
    
    def _generate_pci_report(
        self,
        events: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate PCI DSS compliance report."""
        return {
            'framework': 'PCI DSS',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': len(events),
                'payment_events': len([e for e in events if 'payment' in e['event']['event_type'].lower()]),
                'card_data_events': len([e for e in events if 'card' in str(e['event']['event_data']).lower()]),
                'security_events': len([e for e in events if 'security' in e['event']['event_type'].lower()])
            },
            'events': events
        }
    
    def _generate_sox_report(
        self,
        events: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate SOX compliance report."""
        return {
            'framework': 'SOX',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': len(events),
                'financial_events': len([e for e in events if 'financial' in e['event']['event_type'].lower()]),
                'audit_events': len([e for e in events if 'audit' in e['event']['event_type'].lower()]),
                'access_control_events': len([e for e in events if 'access' in e['event']['event_type'].lower()])
            },
            'events': events
        }
    
    def verify_audit_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of audit logs and tamper-evident chain.
        
        Returns:
            Integrity verification results
        """
        chain_verification = self.chain.verify_chain()
        
        # Additional file-level verification
        log_files = list(self.log_directory.glob('audit_*.log*'))
        file_verification = {
            'total_files': len(log_files),
            'readable_files': 0,
            'corrupted_files': []
        }
        
        for log_file in log_files:
            try:
                events = self._read_log_file(log_file)
                if events:
                    file_verification['readable_files'] += 1
            except Exception as e:
                file_verification['corrupted_files'].append({
                    'file': log_file.name,
                    'error': str(e)
                })
        
        return {
            'chain_integrity': chain_verification,
            'file_integrity': file_verification,
            'statistics': self.stats,
            'overall_status': (
                'VALID' if chain_verification['valid'] and 
                len(file_verification['corrupted_files']) == 0 
                else 'CORRUPTED'
            )
        }
    
    def cleanup_old_logs(self) -> Dict[str, Any]:
        """
        Clean up logs older than retention period.
        
        Returns:
            Cleanup results
        """
        cutoff_date = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=self.retention_days)
        
        deleted_files = []
        errors = []
        
        for log_file in self.log_directory.glob('audit_*.log*'):
            try:
                # Extract date from filename
                filename = log_file.stem
                if filename.endswith('.log'):
                    filename = filename[:-4]  # Remove .log suffix
                
                date_part = filename.split('_')[1]  # Get date part after 'audit_'
                file_date = datetime.strptime(date_part[:8], '%Y%m%d').replace(tzinfo=timezone.utc)
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_files.append(log_file.name)
                    
            except Exception as e:
                errors.append({
                    'file': log_file.name,
                    'error': str(e)
                })
        
        return {
            'cutoff_date': cutoff_date.isoformat(),
            'deleted_files': deleted_files,
            'errors': errors,
            'total_deleted': len(deleted_files)
        }
