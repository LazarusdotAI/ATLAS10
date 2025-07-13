"""
A.T.L.A.S. Security Manager
Comprehensive security hardening, authentication, and authorization
"""

import asyncio
import logging
import hashlib
import secrets
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import pyotp
import qrcode
from io import BytesIO

logger = logging.getLogger(__name__)

class UserRole(Enum):
    ADMIN = "admin"
    TRADER = "trader"
    ANALYST = "analyst"
    VIEWER = "viewer"
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"

class Permission(Enum):
    # Trading permissions
    EXECUTE_TRADES = "execute_trades"
    VIEW_PORTFOLIO = "view_portfolio"
    MODIFY_ORDERS = "modify_orders"
    
    # Analysis permissions
    VIEW_ANALYTICS = "view_analytics"
    GENERATE_REPORTS = "generate_reports"
    ACCESS_MARKET_DATA = "access_market_data"
    
    # Administrative permissions
    MANAGE_USERS = "manage_users"
    SYSTEM_CONFIGURATION = "system_configuration"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    
    # Compliance permissions
    KYC_VERIFICATION = "kyc_verification"
    AML_INVESTIGATION = "aml_investigation"
    COMPLIANCE_REPORTING = "compliance_reporting"

@dataclass
class SecurityEvent:
    id: str
    event_type: str
    severity: str
    user_id: Optional[str]
    ip_address: str
    timestamp: datetime
    description: str
    details: Dict[str, Any]
    resolved: bool = False

@dataclass
class AuthenticationResult:
    success: bool
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    requires_2fa: bool = False

class PasswordValidator:
    """Password strength validation"""
    
    def __init__(self):
        self.min_length = 12
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special and not re.search(f'[{re.escape(self.special_chars)}]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            errors.append("Password cannot contain repeated characters")
        
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            errors.append("Password cannot contain sequential numbers")
        
        return len(errors) == 0, errors

class TwoFactorAuth:
    """Two-factor authentication management"""
    
    def __init__(self):
        self.issuer_name = "A.T.L.A.S. Trading System"
    
    def generate_secret(self, user_id: str) -> str:
        """Generate TOTP secret for user"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user_id: str, secret: str) -> bytes:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name=self.issuer_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

class JWTManager:
    """JWT token management"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=30)
    
    def create_access_token(self, user_id: str, roles: List[str], 
                          permissions: List[str]) -> Tuple[str, datetime]:
        """Create JWT access token"""
        expires_at = datetime.utcnow() + self.access_token_expire
        
        payload = {
            "sub": user_id,
            "roles": roles,
            "permissions": permissions,
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, expires_at
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expires_at = datetime.utcnow() + self.refresh_token_expire
        
        payload = {
            "sub": user_id,
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

class RBACManager:
    """Role-Based Access Control manager"""
    
    def __init__(self):
        self.role_permissions = {
            UserRole.ADMIN: [
                Permission.EXECUTE_TRADES,
                Permission.VIEW_PORTFOLIO,
                Permission.MODIFY_ORDERS,
                Permission.VIEW_ANALYTICS,
                Permission.GENERATE_REPORTS,
                Permission.ACCESS_MARKET_DATA,
                Permission.MANAGE_USERS,
                Permission.SYSTEM_CONFIGURATION,
                Permission.VIEW_AUDIT_LOGS,
                Permission.KYC_VERIFICATION,
                Permission.AML_INVESTIGATION,
                Permission.COMPLIANCE_REPORTING
            ],
            UserRole.TRADER: [
                Permission.EXECUTE_TRADES,
                Permission.VIEW_PORTFOLIO,
                Permission.MODIFY_ORDERS,
                Permission.VIEW_ANALYTICS,
                Permission.ACCESS_MARKET_DATA
            ],
            UserRole.ANALYST: [
                Permission.VIEW_PORTFOLIO,
                Permission.VIEW_ANALYTICS,
                Permission.GENERATE_REPORTS,
                Permission.ACCESS_MARKET_DATA
            ],
            UserRole.VIEWER: [
                Permission.VIEW_PORTFOLIO,
                Permission.VIEW_ANALYTICS,
                Permission.ACCESS_MARKET_DATA
            ],
            UserRole.COMPLIANCE_OFFICER: [
                Permission.VIEW_AUDIT_LOGS,
                Permission.KYC_VERIFICATION,
                Permission.AML_INVESTIGATION,
                Permission.COMPLIANCE_REPORTING,
                Permission.VIEW_ANALYTICS
            ],
            UserRole.RISK_MANAGER: [
                Permission.VIEW_PORTFOLIO,
                Permission.VIEW_ANALYTICS,
                Permission.GENERATE_REPORTS,
                Permission.ACCESS_MARKET_DATA,
                Permission.VIEW_AUDIT_LOGS
            ]
        }
    
    def get_permissions(self, roles: List[UserRole]) -> List[Permission]:
        """Get all permissions for given roles"""
        permissions = set()
        for role in roles:
            permissions.update(self.role_permissions.get(role, []))
        return list(permissions)
    
    def has_permission(self, user_roles: List[UserRole], 
                      required_permission: Permission) -> bool:
        """Check if user has required permission"""
        user_permissions = self.get_permissions(user_roles)
        return required_permission in user_permissions

class SecurityEventMonitor:
    """Security event monitoring and alerting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.events: List[SecurityEvent] = []
        
        # Threat detection thresholds
        self.failed_login_threshold = 5
        self.suspicious_ip_threshold = 10
        self.rate_limit_threshold = 100  # requests per minute
    
    async def log_security_event(self, event_type: str, severity: str,
                                user_id: Optional[str], ip_address: str,
                                description: str, details: Dict[str, Any]) -> str:
        """Log security event"""
        event_id = secrets.token_urlsafe(16)
        
        event = SecurityEvent(
            id=event_id,
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
            description=description,
            details=details
        )
        
        self.events.append(event)
        
        # Check for threat patterns
        await self._analyze_threat_patterns(event)
        
        self.logger.warning(f"🚨 Security Event: {description} (ID: {event_id})")
        return event_id
    
    async def _analyze_threat_patterns(self, event: SecurityEvent):
        """Analyze events for threat patterns"""
        if event.event_type == "failed_login":
            await self._check_brute_force_attack(event)
        elif event.event_type == "suspicious_activity":
            await self._check_anomalous_behavior(event)
        elif event.event_type == "rate_limit_exceeded":
            await self._check_dos_attack(event)
    
    async def _check_brute_force_attack(self, event: SecurityEvent):
        """Check for brute force login attempts"""
        recent_failures = [
            e for e in self.events
            if e.event_type == "failed_login"
            and e.ip_address == event.ip_address
            and e.timestamp > datetime.utcnow() - timedelta(minutes=15)
        ]
        
        if len(recent_failures) >= self.failed_login_threshold:
            await self.log_security_event(
                event_type="brute_force_detected",
                severity="critical",
                user_id=event.user_id,
                ip_address=event.ip_address,
                description=f"Brute force attack detected from {event.ip_address}",
                details={"failed_attempts": len(recent_failures)}
            )
    
    async def _check_anomalous_behavior(self, event: SecurityEvent):
        """Check for anomalous user behavior"""
        # Implement behavioral analysis
        pass
    
    async def _check_dos_attack(self, event: SecurityEvent):
        """Check for denial of service attacks"""
        # Implement DoS detection
        pass

class SecurityManager:
    """Main security manager coordinating all security functionality"""
    
    def __init__(self, jwt_secret: str):
        self.logger = logging.getLogger(__name__)
        self.password_validator = PasswordValidator()
        self.two_factor_auth = TwoFactorAuth()
        self.jwt_manager = JWTManager(jwt_secret)
        self.rbac_manager = RBACManager()
        self.security_monitor = SecurityEventMonitor()
        
        # Rate limiting
        self.rate_limits = {}
        self.rate_limit_window = timedelta(minutes=1)
        self.max_requests_per_window = 100
    
    async def authenticate_user(self, username: str, password: str,
                              totp_token: Optional[str] = None,
                              ip_address: str = "unknown") -> AuthenticationResult:
        """Authenticate user with optional 2FA"""
        try:
            # Get user from database (placeholder)
            user = await self._get_user_by_username(username)
            if not user:
                await self.security_monitor.log_security_event(
                    event_type="failed_login",
                    severity="warning",
                    user_id=None,
                    ip_address=ip_address,
                    description=f"Login attempt with invalid username: {username}",
                    details={"username": username}
                )
                return AuthenticationResult(
                    success=False,
                    error_message="Invalid credentials"
                )
            
            # Verify password
            if not self._verify_password(password, user["password_hash"]):
                await self.security_monitor.log_security_event(
                    event_type="failed_login",
                    severity="warning",
                    user_id=user["id"],
                    ip_address=ip_address,
                    description=f"Failed login attempt for user {username}",
                    details={"username": username}
                )
                return AuthenticationResult(
                    success=False,
                    error_message="Invalid credentials"
                )
            
            # Check if 2FA is enabled
            if user.get("totp_secret"):
                if not totp_token:
                    return AuthenticationResult(
                        success=False,
                        requires_2fa=True,
                        error_message="2FA token required"
                    )
                
                if not self.two_factor_auth.verify_totp(user["totp_secret"], totp_token):
                    await self.security_monitor.log_security_event(
                        event_type="failed_2fa",
                        severity="warning",
                        user_id=user["id"],
                        ip_address=ip_address,
                        description=f"Failed 2FA verification for user {username}",
                        details={"username": username}
                    )
                    return AuthenticationResult(
                        success=False,
                        error_message="Invalid 2FA token"
                    )
            
            # Generate tokens
            user_roles = [UserRole(role) for role in user.get("roles", ["trader"])]
            permissions = [perm.value for perm in self.rbac_manager.get_permissions(user_roles)]
            
            access_token, expires_at = self.jwt_manager.create_access_token(
                user["id"], [role.value for role in user_roles], permissions
            )
            refresh_token = self.jwt_manager.create_refresh_token(user["id"])
            
            # Log successful login
            await self.security_monitor.log_security_event(
                event_type="successful_login",
                severity="info",
                user_id=user["id"],
                ip_address=ip_address,
                description=f"Successful login for user {username}",
                details={"username": username, "roles": [role.value for role in user_roles]}
            )
            
            return AuthenticationResult(
                success=True,
                user_id=user["id"],
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return AuthenticationResult(
                success=False,
                error_message="Authentication service error"
            )
    
    async def authorize_action(self, token: str, required_permission: Permission) -> bool:
        """Authorize user action based on JWT token and required permission"""
        try:
            payload = self.jwt_manager.verify_token(token)
            if not payload:
                return False
            
            user_permissions = payload.get("permissions", [])
            return required_permission.value in user_permissions
            
        except Exception as e:
            self.logger.error(f"Authorization error: {e}")
            return False
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    async def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username (placeholder)"""
        # In production, query from database
        return {
            "id": "user123",
            "username": username,
            "password_hash": self._hash_password("SecurePassword123!"),
            "roles": ["trader"],
            "totp_secret": None
        }
    
    async def check_rate_limit(self, user_id: str, ip_address: str) -> bool:
        """Check if user/IP is within rate limits"""
        now = datetime.utcnow()
        key = f"{user_id}:{ip_address}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Remove old requests outside the window
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if now - timestamp < self.rate_limit_window
        ]
        
        # Check if within limit
        if len(self.rate_limits[key]) >= self.max_requests_per_window:
            await self.security_monitor.log_security_event(
                event_type="rate_limit_exceeded",
                severity="warning",
                user_id=user_id,
                ip_address=ip_address,
                description=f"Rate limit exceeded for user {user_id}",
                details={"requests_count": len(self.rate_limits[key])}
            )
            return False
        
        # Add current request
        self.rate_limits[key].append(now)
        return True
