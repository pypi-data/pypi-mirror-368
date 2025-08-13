"""Security validation service for Error Explorer Python SDK."""

import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
from ..types import ErrorData, RequestData


@dataclass
class SecurityConfig:
    """Security validation configuration."""
    enforce_https: bool = True
    max_payload_size_mb: float = 1.0
    enable_xss_protection: bool = True
    sensitive_fields: List[str] = None
    allowed_hosts: Optional[List[str]] = None
    block_local_urls: bool = True
    
    def __post_init__(self):
        if self.sensitive_fields is None:
            self.sensitive_fields = [
                "password", "passwd", "pwd", "token", "secret", "key", "auth", 
                "authorization", "csrf", "session", "cookie", "api_key", 
                "access_token", "refresh_token", "private_key", "credit_card",
                "ssn", "social_security", "ccv", "cvv", "card_number"
            ]


class SecurityValidator:
    """
    Comprehensive security validation service.
    
    Features:
    - API URL validation with HTTPS enforcement
    - Project token validation
    - Payload size limits (1MB default)
    - Data sanitization removing sensitive information
    - XSS prevention with pattern filtering
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize security validator.
        
        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        
        # XSS patterns to detect and filter
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'expression\s*\(',
            r'url\s*\(',
            r'@import',
        ]
        
        self.compiled_xss_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                                    for pattern in self.xss_patterns]
    
    def validate_api_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate API URL for security requirements.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            parsed_url = urlparse(url)
            
            # Check HTTPS requirement
            if self.config.enforce_https and parsed_url.scheme != 'https':
                return False, "HTTPS required for API URL"
            
            # Check for valid scheme
            if parsed_url.scheme not in ['http', 'https']:
                return False, f"Invalid URL scheme: {parsed_url.scheme}"
            
            # Check for hostname
            if not parsed_url.hostname:
                return False, "Invalid URL: missing hostname"
            
            # Block local URLs if configured
            if self.config.block_local_urls:
                local_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
                if parsed_url.hostname in local_hosts:
                    return False, "Local URLs not allowed"
                
                # Check for private IP ranges
                if self._is_private_ip(parsed_url.hostname):
                    return False, "Private IP addresses not allowed"
            
            # Check allowed hosts
            if self.config.allowed_hosts:
                if parsed_url.hostname not in self.config.allowed_hosts:
                    return False, f"Host not in allowed list: {parsed_url.hostname}"
            
            return True, "URL is valid"
            
        except Exception as e:
            return False, f"URL validation error: {str(e)}"
    
    def validate_payload_size(self, error_data: ErrorData) -> Tuple[bool, str, float]:
        """
        Validate payload size against limits.
        
        Args:
            error_data: Error data to validate
            
        Returns:
            Tuple of (is_valid, reason, size_mb)
        """
        try:
            # Calculate payload size
            import json
            from ..client import ErrorExplorer
            
            dummy_client = ErrorExplorer.__new__(ErrorExplorer)
            data_dict = dummy_client._dataclass_to_dict(error_data)
            json_str = json.dumps(data_dict)
            size_bytes = len(json_str.encode('utf-8'))
            size_mb = size_bytes / (1024 * 1024)
            
            if size_mb > self.config.max_payload_size_mb:
                return False, f"Payload size ({size_mb:.2f}MB) exceeds limit ({self.config.max_payload_size_mb}MB)", size_mb
            
            return True, "Payload size is valid", size_mb
            
        except Exception as e:
            return False, f"Payload size validation error: {str(e)}", 0.0
    
    def sanitize_error_data(self, error_data: ErrorData) -> ErrorData:
        """
        Sanitize error data by removing sensitive information and XSS patterns.
        
        Args:
            error_data: Error data to sanitize
            
        Returns:
            Sanitized error data
        """
        # Create a copy to avoid modifying original
        import copy
        sanitized_data = copy.deepcopy(error_data)
        
        # Sanitize message and stack trace
        if sanitized_data.message:
            sanitized_data.message = self._sanitize_string(sanitized_data.message)
        
        if sanitized_data.stack_trace:
            sanitized_data.stack_trace = self._sanitize_string(sanitized_data.stack_trace)
        
        # Sanitize context
        if sanitized_data.context:
            sanitized_data.context = self._sanitize_dict(sanitized_data.context)
        
        # Sanitize request data
        if sanitized_data.request:
            sanitized_data.request = self._sanitize_request_data(sanitized_data.request)
        
        # Sanitize user data
        if sanitized_data.user and sanitized_data.user.extra:
            sanitized_data.user.extra = self._sanitize_dict(sanitized_data.user.extra)
        
        # Sanitize breadcrumbs
        if sanitized_data.breadcrumbs:
            for breadcrumb in sanitized_data.breadcrumbs:
                if breadcrumb.message:
                    breadcrumb.message = self._sanitize_string(breadcrumb.message)
                if breadcrumb.data:
                    breadcrumb.data = self._sanitize_dict(breadcrumb.data)
        
        return sanitized_data
    
    def _sanitize_request_data(self, request_data: RequestData) -> RequestData:
        """Sanitize request data."""
        import copy
        sanitized = copy.deepcopy(request_data)
        
        # Sanitize headers
        if sanitized.headers:
            sanitized.headers = self._sanitize_dict(sanitized.headers)
        
        # Sanitize query parameters
        if sanitized.query:
            sanitized.query = self._sanitize_dict(sanitized.query)
        
        # Sanitize body
        if isinstance(sanitized.body, dict):
            sanitized.body = self._sanitize_dict(sanitized.body)
        elif isinstance(sanitized.body, str):
            sanitized.body = self._sanitize_string(sanitized.body)
        
        # Sanitize URL parameters
        if sanitized.url:
            sanitized.url = self._sanitize_url_params(sanitized.url)
        
        return sanitized
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary by removing sensitive fields and XSS patterns."""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        
        for key, value in data.items():
            # Check if key is sensitive
            if self._is_sensitive_field(key):
                sanitized[key] = "[FILTERED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_dict(item) if isinstance(item, dict) 
                                else self._sanitize_string(str(item)) if isinstance(item, str)
                                else item for item in value]
            elif isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize string by removing XSS patterns and sensitive data."""
        if not isinstance(text, str):
            return text
        
        sanitized = text
        
        # Remove XSS patterns if enabled
        if self.config.enable_xss_protection:
            for pattern in self.compiled_xss_patterns:
                sanitized = pattern.sub('[XSS_FILTERED]', sanitized)
        
        # Limit string length to prevent excessive data
        max_length = 10000  # 10KB limit for individual strings
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... [TRUNCATED]"
        
        return sanitized
    
    def _sanitize_url_params(self, url: str) -> str:
        """Sanitize URL by removing sensitive parameters."""
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            
            parsed = urlparse(url)
            if parsed.query:
                params = parse_qs(parsed.query)
                
                # Filter sensitive parameters
                sanitized_params = {}
                for key, values in params.items():
                    if self._is_sensitive_field(key):
                        sanitized_params[key] = ['[FILTERED]']
                    else:
                        sanitized_params[key] = values
                
                # Reconstruct URL
                new_query = urlencode(sanitized_params, doseq=True)
                return urlunparse(parsed._replace(query=new_query))
            
            return url
            
        except Exception:
            return url  # Return original if sanitization fails
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if field name indicates sensitive data."""
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self.config.sensitive_fields)
    
    def _is_private_ip(self, hostname: str) -> bool:
        """Check if hostname is a private IP address."""
        try:
            import ipaddress
            ip = ipaddress.ip_address(hostname)
            return ip.is_private
        except ValueError:
            return False  # Not an IP address
    
    def validate_token_format(self, token: str) -> Tuple[bool, str]:
        """
        Validate project token format.
        
        Args:
            token: Token to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not token:
            return False, "Token is required"
        
        if len(token) < 8:
            return False, "Token too short (minimum 8 characters)"
        
        if len(token) > 256:
            return False, "Token too long (maximum 256 characters)"
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', token):
            return False, "Token contains invalid characters"
        
        return True, "Token format is valid"
    
    def get_security_report(self, error_data: ErrorData, api_url: str = "") -> Dict[str, Any]:
        """
        Generate a security validation report.
        
        Args:
            error_data: Error data to analyze
            api_url: API URL to validate
            
        Returns:
            Security validation report
        """
        report = {
            "validation_time": sys.version_info[:2],
            "checks": {},
            "recommendations": []
        }
        
        # URL validation
        if api_url:
            url_valid, url_reason = self.validate_api_url(api_url)
            report["checks"]["api_url"] = {
                "valid": url_valid,
                "reason": url_reason
            }
            if not url_valid:
                report["recommendations"].append(f"Fix API URL: {url_reason}")
        
        # Payload size validation
        size_valid, size_reason, size_mb = self.validate_payload_size(error_data)
        report["checks"]["payload_size"] = {
            "valid": size_valid,
            "reason": size_reason,
            "size_mb": size_mb
        }
        if not size_valid:
            report["recommendations"].append(f"Reduce payload size: {size_reason}")
        
        # Sensitive data detection
        sensitive_fields_found = self._detect_sensitive_fields(error_data)
        report["checks"]["sensitive_data"] = {
            "fields_found": sensitive_fields_found,
            "count": len(sensitive_fields_found)
        }
        if sensitive_fields_found:
            report["recommendations"].append(f"Found {len(sensitive_fields_found)} potentially sensitive fields that will be filtered")
        
        # XSS pattern detection
        if self.config.enable_xss_protection:
            xss_patterns_found = self._detect_xss_patterns(error_data)
            report["checks"]["xss_patterns"] = {
                "patterns_found": xss_patterns_found,
                "count": len(xss_patterns_found)
            }
            if xss_patterns_found:
                report["recommendations"].append(f"Found {len(xss_patterns_found)} potential XSS patterns that will be filtered")
        
        return report
    
    def _detect_sensitive_fields(self, error_data: ErrorData) -> List[str]:
        """Detect sensitive fields in error data."""
        sensitive_fields = []
        
        def check_dict(d: Dict[str, Any], prefix: str = ""):
            if not isinstance(d, dict):
                return
            
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if self._is_sensitive_field(key):
                    sensitive_fields.append(full_key)
                elif isinstance(value, dict):
                    check_dict(value, full_key)
        
        # Check various data sources
        if error_data.context:
            check_dict(error_data.context, "context")
        
        if error_data.request:
            if error_data.request.headers:
                check_dict(error_data.request.headers, "request.headers")
            if error_data.request.query:
                check_dict(error_data.request.query, "request.query")
            if isinstance(error_data.request.body, dict):
                check_dict(error_data.request.body, "request.body")
        
        if error_data.user and error_data.user.extra:
            check_dict(error_data.user.extra, "user.extra")
        
        return sensitive_fields
    
    def _detect_xss_patterns(self, error_data: ErrorData) -> List[str]:
        """Detect XSS patterns in error data."""
        patterns_found = []
        
        def check_string(text: str, source: str):
            if not isinstance(text, str):
                return
            
            for i, pattern in enumerate(self.compiled_xss_patterns):
                if pattern.search(text):
                    patterns_found.append(f"{source}: pattern_{i+1}")
        
        # Check various string fields
        if error_data.message:
            check_string(error_data.message, "message")
        
        if error_data.stack_trace:
            check_string(error_data.stack_trace, "stack_trace")
        
        # Check breadcrumbs
        if error_data.breadcrumbs:
            for i, bc in enumerate(error_data.breadcrumbs):
                if bc.message:
                    check_string(bc.message, f"breadcrumb_{i}.message")
        
        return patterns_found