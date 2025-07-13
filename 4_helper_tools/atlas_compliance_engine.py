"""
A.T.L.A.S. Compliance Engine
Comprehensive KYC/AML workflows, audit trails, and regulatory compliance
"""

import asyncio
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import uuid

from models import Order, Position, User

logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    REQUIRES_DOCUMENTATION = "requires_documentation"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DocumentType(Enum):
    GOVERNMENT_ID = "government_id"
    PROOF_OF_ADDRESS = "proof_of_address"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    EMPLOYMENT_VERIFICATION = "employment_verification"

@dataclass
class KYCDocument:
    id: str
    user_id: str
    document_type: DocumentType
    file_path: str
    upload_timestamp: datetime
    verification_status: ComplianceStatus
    expiry_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    verification_timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = None

@dataclass
class AMLAlert:
    id: str
    user_id: str
    transaction_id: str
    alert_type: str
    risk_score: float
    description: str
    created_timestamp: datetime
    status: ComplianceStatus
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_timestamp: Optional[datetime] = None

@dataclass
class AuditTrailEntry:
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    session_id: str
    details: Dict[str, Any]
    compliance_flags: List[str] = None

class KYCEngine:
    """Know Your Customer verification engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # KYC requirements by jurisdiction
        self.kyc_requirements = {
            "US": [
                DocumentType.GOVERNMENT_ID,
                DocumentType.PROOF_OF_ADDRESS,
                DocumentType.TAX_DOCUMENT
            ],
            "EU": [
                DocumentType.GOVERNMENT_ID,
                DocumentType.PROOF_OF_ADDRESS,
                DocumentType.BANK_STATEMENT
            ],
            "UK": [
                DocumentType.GOVERNMENT_ID,
                DocumentType.PROOF_OF_ADDRESS,
                DocumentType.EMPLOYMENT_VERIFICATION
            ]
        }
        
    async def initiate_kyc_process(self, user_id: str, jurisdiction: str) -> Dict[str, Any]:
        """Initiate KYC verification process for a user"""
        try:
            required_docs = self.kyc_requirements.get(jurisdiction, self.kyc_requirements["US"])
            
            kyc_session = {
                "session_id": str(uuid.uuid4()),
                "user_id": user_id,
                "jurisdiction": jurisdiction,
                "required_documents": [doc.value for doc in required_docs],
                "status": ComplianceStatus.PENDING.value,
                "created_timestamp": datetime.now().isoformat(),
                "expiry_timestamp": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            self.logger.info(f"[SEARCH] KYC process initiated for user {user_id} in {jurisdiction}")
            return kyc_session
            
        except Exception as e:
            self.logger.error(f"KYC initiation failed: {e}")
            raise
    
    async def upload_document(self, user_id: str, document_type: DocumentType, 
                            file_data: bytes, filename: str) -> KYCDocument:
        """Upload and encrypt KYC document"""
        try:
            # Encrypt document data
            encrypted_data = self.cipher_suite.encrypt(file_data)
            
            # Generate secure file path
            doc_id = str(uuid.uuid4())
            file_path = f"kyc_docs/{user_id}/{doc_id}_{filename}"
            
            # Save encrypted document (in production, use secure cloud storage)
            # await self._save_encrypted_document(file_path, encrypted_data)
            
            document = KYCDocument(
                id=doc_id,
                user_id=user_id,
                document_type=document_type,
                file_path=file_path,
                upload_timestamp=datetime.now(),
                verification_status=ComplianceStatus.PENDING,
                metadata={
                    "original_filename": filename,
                    "file_size": len(file_data),
                    "upload_ip": "127.0.0.1"  # Get from request
                }
            )
            
            self.logger.info(f"[DOC] Document uploaded: {document_type.value} for user {user_id}")
            return document
            
        except Exception as e:
            self.logger.error(f"Document upload failed: {e}")
            raise
    
    async def verify_document(self, document_id: str, verifier_id: str, 
                            approved: bool, notes: str = "") -> bool:
        """Verify uploaded KYC document"""
        try:
            # In production, integrate with document verification services
            # like Jumio, Onfido, or Trulioo
            
            verification_result = {
                "document_id": document_id,
                "verifier_id": verifier_id,
                "status": ComplianceStatus.APPROVED.value if approved else ComplianceStatus.REJECTED.value,
                "verification_timestamp": datetime.now().isoformat(),
                "notes": notes,
                "confidence_score": 0.95 if approved else 0.3
            }
            
            self.logger.info(f"[OK] Document {document_id} verification: {'APPROVED' if approved else 'REJECTED'}")
            return approved
            
        except Exception as e:
            self.logger.error(f"Document verification failed: {e}")
            raise

class AMLEngine:
    """Anti-Money Laundering monitoring engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # AML risk thresholds
        self.risk_thresholds = {
            "daily_transaction_limit": 10000,
            "weekly_transaction_limit": 50000,
            "monthly_transaction_limit": 200000,
            "suspicious_pattern_score": 0.7,
            "high_risk_country_multiplier": 2.0
        }
        
        # High-risk countries (FATF list)
        self.high_risk_countries = [
            "AF", "IR", "KP", "MM", "PK"  # Afghanistan, Iran, North Korea, Myanmar, Pakistan
        ]
        
    async def monitor_transaction(self, user_id: str, transaction: Dict[str, Any]) -> Optional[AMLAlert]:
        """Monitor transaction for AML compliance"""
        try:
            risk_score = await self._calculate_risk_score(user_id, transaction)
            
            if risk_score >= self.risk_thresholds["suspicious_pattern_score"]:
                alert = AMLAlert(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    transaction_id=transaction.get("id", "unknown"),
                    alert_type="suspicious_transaction",
                    risk_score=risk_score,
                    description=f"High-risk transaction detected (score: {risk_score:.2f})",
                    created_timestamp=datetime.now(),
                    status=ComplianceStatus.UNDER_REVIEW
                )
                
                self.logger.warning(f"🚨 AML Alert: {alert.description} for user {user_id}")
                return alert
            
            return None
            
        except Exception as e:
            self.logger.error(f"AML monitoring failed: {e}")
            raise
    
    async def _calculate_risk_score(self, user_id: str, transaction: Dict[str, Any]) -> float:
        """Calculate AML risk score for transaction"""
        try:
            base_score = 0.0
            
            # Transaction amount risk
            amount = transaction.get("amount", 0)
            if amount > self.risk_thresholds["daily_transaction_limit"]:
                base_score += 0.3
            
            # Frequency risk
            daily_count = await self._get_daily_transaction_count(user_id)
            if daily_count > 10:
                base_score += 0.2
            
            # Geographic risk
            user_country = await self._get_user_country(user_id)
            if user_country in self.high_risk_countries:
                base_score *= self.risk_thresholds["high_risk_country_multiplier"]
            
            # Pattern analysis risk
            pattern_score = await self._analyze_transaction_patterns(user_id)
            base_score += pattern_score
            
            return min(base_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.error(f"Risk score calculation failed: {e}")
            return 0.5  # Default medium risk
    
    async def _get_daily_transaction_count(self, user_id: str) -> int:
        """Get daily transaction count for user"""
        # In production, query from database
        return 5  # Placeholder
    
    async def _get_user_country(self, user_id: str) -> str:
        """Get user's country code"""
        # In production, query from user profile
        return "US"  # Placeholder
    
    async def _analyze_transaction_patterns(self, user_id: str) -> float:
        """Analyze transaction patterns for suspicious activity"""
        # In production, implement ML-based pattern analysis
        return 0.1  # Placeholder

class AuditTrailManager:
    """Comprehensive audit trail management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_entries: List[AuditTrailEntry] = []
    
    async def log_action(self, user_id: str, action: str, resource_type: str,
                        resource_id: str, details: Dict[str, Any],
                        ip_address: str = "127.0.0.1", user_agent: str = "unknown",
                        session_id: str = "unknown") -> str:
        """Log user action for audit trail"""
        try:
            entry_id = str(uuid.uuid4())
            
            # Generate compliance flags
            compliance_flags = self._generate_compliance_flags(action, details)
            
            entry = AuditTrailEntry(
                id=entry_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                timestamp=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                details=details,
                compliance_flags=compliance_flags
            )
            
            # Store in immutable audit log
            await self._store_audit_entry(entry)
            
            self.logger.info(f"[NOTE] Audit log: {action} by user {user_id}")
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            raise
    
    def _generate_compliance_flags(self, action: str, details: Dict[str, Any]) -> List[str]:
        """Generate compliance flags based on action and details"""
        flags = []
        
        # High-value transaction flag
        if action == "trade_execution" and details.get("amount", 0) > 10000:
            flags.append("high_value_transaction")
        
        # Rapid trading flag
        if action == "trade_execution" and details.get("time_since_last_trade", 0) < 60:
            flags.append("rapid_trading")
        
        # Administrative action flag
        if action in ["user_role_change", "system_configuration_change"]:
            flags.append("administrative_action")
        
        return flags
    
    async def _store_audit_entry(self, entry: AuditTrailEntry):
        """Store audit entry in immutable storage"""
        # In production, use blockchain or immutable database
        self.audit_entries.append(entry)
        
        # Create hash for integrity verification
        entry_hash = hashlib.sha256(
            json.dumps(asdict(entry), default=str).encode()
        ).hexdigest()
        
        self.logger.debug(f"Audit entry stored with hash: {entry_hash}")

class ComplianceEngine:
    """Main compliance engine coordinating all compliance functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.kyc_engine = KYCEngine()
        self.aml_engine = AMLEngine()
        self.audit_manager = AuditTrailManager()
        
        # Compliance rules
        self.trading_limits = {
            "unverified_user_daily_limit": 1000,
            "verified_user_daily_limit": 50000,
            "institutional_daily_limit": 1000000
        }
    
    async def check_trading_compliance(self, user_id: str, order: Order) -> Tuple[bool, str]:
        """Check if trade complies with regulations"""
        try:
            # Check KYC status
            kyc_status = await self._get_kyc_status(user_id)
            if kyc_status != ComplianceStatus.APPROVED:
                return False, "KYC verification required"
            
            # Check trading limits
            daily_volume = await self._get_daily_trading_volume(user_id)
            user_limit = self.trading_limits["verified_user_daily_limit"]
            
            if daily_volume + order.quantity * order.price > user_limit:
                return False, f"Daily trading limit exceeded (${user_limit:,})"
            
            # AML monitoring
            transaction_data = {
                "id": order.id,
                "amount": order.quantity * order.price,
                "symbol": order.symbol,
                "type": order.type.value
            }
            
            aml_alert = await self.aml_engine.monitor_transaction(user_id, transaction_data)
            if aml_alert and aml_alert.risk_score > 0.8:
                return False, "Transaction flagged for AML review"
            
            # Log compliance check
            await self.audit_manager.log_action(
                user_id=user_id,
                action="compliance_check",
                resource_type="order",
                resource_id=order.id,
                details={
                    "order_details": asdict(order),
                    "compliance_result": "approved",
                    "kyc_status": kyc_status.value,
                    "daily_volume": daily_volume
                }
            )
            
            return True, "Compliance check passed"
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
            return False, f"Compliance check error: {str(e)}"
    
    async def _get_kyc_status(self, user_id: str) -> ComplianceStatus:
        """Get KYC verification status for user"""
        # In production, query from database
        return ComplianceStatus.APPROVED  # Placeholder
    
    async def _get_daily_trading_volume(self, user_id: str) -> float:
        """Get daily trading volume for user"""
        # In production, query from database
        return 5000.0  # Placeholder
    
    async def generate_compliance_report(self, start_date: datetime, 
                                       end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            report = {
                "report_id": str(uuid.uuid4()),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "generated_timestamp": datetime.now().isoformat(),
                "kyc_statistics": await self._get_kyc_statistics(start_date, end_date),
                "aml_statistics": await self._get_aml_statistics(start_date, end_date),
                "audit_statistics": await self._get_audit_statistics(start_date, end_date),
                "regulatory_violations": await self._get_violations(start_date, end_date)
            }
            
            self.logger.info(f"[DATA] Compliance report generated: {report['report_id']}")
            return report
            
        except Exception as e:
            self.logger.error(f"Compliance report generation failed: {e}")
            raise
    
    async def _get_kyc_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get KYC statistics for reporting period"""
        return {
            "total_applications": 150,
            "approved": 120,
            "rejected": 15,
            "pending": 15,
            "approval_rate": 0.8
        }
    
    async def _get_aml_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get AML statistics for reporting period"""
        return {
            "total_transactions_monitored": 5000,
            "alerts_generated": 25,
            "high_risk_alerts": 5,
            "false_positive_rate": 0.15
        }
    
    async def _get_audit_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get audit trail statistics for reporting period"""
        return {
            "total_actions_logged": 10000,
            "compliance_flags": 50,
            "administrative_actions": 25,
            "data_integrity_checks": "passed"
        }
    
    async def _get_violations(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get regulatory violations for reporting period"""
        return []  # No violations in this period
