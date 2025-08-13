from typing import Dict, Any, Optional
from confluent_kafka import Consumer
from dagster import ConfigurableResource, get_dagster_logger
from pydantic import Field, validator
from enum import Enum
import re
import os


class SecurityProtocol(str, Enum):
    """Kafka security protocol options."""
    PLAINTEXT = "PLAINTEXT"
    SSL = "SSL"
    SASL_PLAINTEXT = "SASL_PLAINTEXT"
    SASL_SSL = "SASL_SSL"


class SaslMechanism(str, Enum):
    """SASL authentication mechanisms."""
    PLAIN = "PLAIN"
    SCRAM_SHA_256 = "SCRAM-SHA-256"
    SCRAM_SHA_512 = "SCRAM-SHA-512"
    GSSAPI = "GSSAPI"
    OAUTHBEARER = "OAUTHBEARER"


class KafkaResource(ConfigurableResource):
    """
    Resource for connecting to Kafka cluster with comprehensive security support.
    
    Supports both insecure local development and production security configurations
    including SASL authentication and SSL/TLS encryption.
    """

    # Core Configuration
    bootstrap_servers: str = Field(
        description="Kafka bootstrap servers (e.g., 'localhost:9092' or 'broker1:9092,broker2:9092')"
    )

    # Security Configuration
    security_protocol: SecurityProtocol = Field(
        default=SecurityProtocol.PLAINTEXT,
        description="Security protocol for Kafka connections. Use SASL_SSL for production."
    )

    # SASL Authentication
    sasl_mechanism: Optional[SaslMechanism] = Field(
        default=None,
        description="SASL mechanism for authentication. Required when using SASL protocols."
    )

    sasl_username: Optional[str] = Field(
        default=None,
        description="SASL username for authentication. Required for PLAIN and SCRAM mechanisms."
    )

    sasl_password: Optional[str] = Field(
        default=None,
        description="SASL password for authentication. Required for PLAIN and SCRAM mechanisms."
    )

    # SSL/TLS Configuration
    ssl_ca_location: Optional[str] = Field(
        default=None,
        description="Path to CA certificate file for SSL certificate verification."
    )

    ssl_certificate_location: Optional[str] = Field(
        default=None,
        description="Path to client certificate file for SSL client authentication."
    )

    ssl_key_location: Optional[str] = Field(
        default=None,
        description="Path to client private key file for SSL client authentication."
    )

    ssl_key_password: Optional[str] = Field(
        default=None,
        description="Password for client private key file."
    )

    ssl_check_hostname: bool = Field(
        default=True,
        description="Whether to verify SSL certificate hostname. Set to False for self-signed certificates."
    )

    # Advanced Configuration
    session_timeout_ms: int = Field(
        default=10000,
        description="Session timeout in milliseconds for consumer group coordination."
    )

    enable_auto_commit: bool = Field(
        default=True,
        description="Whether to automatically commit consumer offsets."
    )

    auto_offset_reset: str = Field(
        default="earliest",
        description="What to do when there is no initial offset ('earliest', 'latest', 'none')."
    )

    additional_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional Kafka configuration parameters as key-value pairs."
    )

    @validator('bootstrap_servers')
    def validate_bootstrap_servers(cls, v):
        """Validate bootstrap_servers format and prevent injection."""
        if not v:
            raise ValueError("bootstrap_servers cannot be empty")
        
        # Allow only valid hostname:port format
        if not re.match(r'^[a-zA-Z0-9.-]+(:[0-9]+)?(,[a-zA-Z0-9.-]+(:[0-9]+)?)*$', v):
            raise ValueError("Invalid bootstrap_servers format. Use 'host:port' or 'host1:port1,host2:port2'")
        
        return v

    @validator('additional_config')
    def validate_additional_config(cls, v):
        """Validate additional configuration to prevent injection attacks."""
        if not v:
            return v
        
        validated_config = {}
        
        for key, value in v.items():
            # Validate configuration key format
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9._-]*$', key):
                raise ValueError(f"Invalid configuration key format: '{key}'. Keys must start with a letter and contain only alphanumeric characters, dots, underscores, and hyphens.")
            
            # Validate configuration value
            validated_value = cls._validate_config_value(key, value)
            validated_config[key] = validated_value
        
        return validated_config

    @staticmethod
    def _validate_config_value(key: str, value: Any) -> str:
        """Validate and sanitize configuration values to prevent injection attacks."""
        # Convert to string for validation
        str_value = str(value)
        
        # Security validations
        security_issues = []
        
        # 1. Check for command injection patterns
        command_patterns = [
            r'[;&|`$()]',  # Command separators and execution
            r'rm\s+-rf',   # Dangerous commands
            r'wget|curl',  # Network commands
            r'>\s*/dev/',  # File redirections
            r'sudo|su\s',  # Privilege escalation
        ]
        
        for pattern in command_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                security_issues.append(f"Potentially dangerous command pattern detected")
        
        # 2. Check for SQL injection patterns
        sql_patterns = [
            r"';\s*(drop|delete|update|insert|alter|create)",
            r"--\s*$",
            r"union\s+select",
            r"or\s+1\s*=\s*1",
            r"'\s*or\s*'.*?'\s*=\s*'"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                security_issues.append(f"Potentially dangerous SQL-like pattern detected")
        
        # 3. Check for path traversal
        if '../' in str_value or '..\\' in str_value:
            security_issues.append("Path traversal pattern detected")
        
        # 4. Check for script injection
        script_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'on\w+\s*=',  # HTML event handlers
            r'<.*?onerror.*?>',
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                security_issues.append(f"Script injection pattern detected")
        
        # 5. Check for null byte injection
        if '\x00' in str_value:
            security_issues.append("Null byte injection detected")
        
        # 6. Length validation (prevent DoS via large configs)
        if len(str_value) > 2000:  # Reasonable limit for Kafka configs
            security_issues.append(f"Configuration value too long: {len(str_value)} characters (max: 2000)")
        
        # If security issues found, raise error
        if security_issues:
            raise ValueError(f"Invalid configuration value for '{key}': {'; '.join(security_issues)}")
        
        # Additional sanitization for specific config types
        if key in ['client.id', 'group.id', 'consumer.group.id']:
            # Allow only alphanumeric, hyphens, underscores, dots
            sanitized = re.sub(r'[^a-zA-Z0-9\-_.]', '', str_value)
            if sanitized != str_value:
                raise ValueError(f"Configuration '{key}' contains invalid characters. Allowed: alphanumeric, -, _, .")
            str_value = sanitized
        
        # For file paths, validate they're reasonable (don't check existence for placeholder paths)
        if key.endswith('.location'):
            if str_value.startswith('/path/to/'):
                # This is a placeholder path, allow it
                pass
            elif os.path.isabs(str_value):
                # This is an absolute path, validate it's not trying to access sensitive areas
                forbidden_paths = ['/etc/', '/root/', '/home/', '/usr/bin/', '/bin/', '/sbin/']
                if any(str_value.startswith(path) for path in forbidden_paths):
                    raise ValueError(f"File path '{str_value}' for config '{key}' points to a restricted directory")
        
        return str_value

    def get_consumer(self, group_id: str) -> Consumer:
        """
        Create a Kafka consumer with security configuration.

        Args:
            group_id: Consumer group ID for this consumer

        Returns:
            Configured Kafka Consumer instance

        Raises:
            ValueError: If security configuration is invalid
        """
        logger = get_dagster_logger()

        # Start with basic configuration
        config = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': self.auto_offset_reset,
            'session.timeout.ms': self.session_timeout_ms,
            'enable.auto.commit': self.enable_auto_commit,
        }

        # Add security configuration
        config['security.protocol'] = self.security_protocol.value

        # Configure SASL if needed
        if self.security_protocol in [SecurityProtocol.SASL_PLAINTEXT, SecurityProtocol.SASL_SSL]:
            if not self.sasl_mechanism:
                raise ValueError("sasl_mechanism is required when using SASL security protocols")

            config['sasl.mechanism'] = self.sasl_mechanism.value

            # Configure SASL credentials for PLAIN and SCRAM mechanisms
            if self.sasl_mechanism in [SaslMechanism.PLAIN, SaslMechanism.SCRAM_SHA_256, SaslMechanism.SCRAM_SHA_512]:
                if not self.sasl_username or not self.sasl_password:
                    raise ValueError("sasl_username and sasl_password are required for PLAIN and SCRAM mechanisms")

                config['sasl.username'] = self.sasl_username
                config['sasl.password'] = self.sasl_password

            logger.info(f"Configured SASL authentication with mechanism: {self.sasl_mechanism.value}")

        # Configure SSL if needed
        if self.security_protocol in [SecurityProtocol.SSL, SecurityProtocol.SASL_SSL]:
            if self.ssl_ca_location:
                config['ssl.ca.location'] = self.ssl_ca_location

            if self.ssl_certificate_location:
                config['ssl.certificate.location'] = self.ssl_certificate_location

            if self.ssl_key_location:
                config['ssl.key.location'] = self.ssl_key_location

                if self.ssl_key_password:
                    config['ssl.key.password'] = self.ssl_key_password

            config['ssl.check.hostname'] = self.ssl_check_hostname

            logger.info("Configured SSL/TLS encryption")

        # Add any additional configuration (now validated)
        if self.additional_config:
            config.update(self.additional_config)
            logger.info(f"Applied additional config: {list(self.additional_config.keys())}")

        logger.info(f"Creating Kafka consumer with security protocol: {self.security_protocol.value}")

        try:
            return Consumer(config)
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            raise

    def get_producer_config(self) -> Dict[str, Any]:
        """
        Get producer configuration with the same security settings.

        Returns:
            Dictionary of Kafka producer configuration
        """
        logger = get_dagster_logger()

        config = {
            'bootstrap.servers': self.bootstrap_servers,
            'security.protocol': self.security_protocol.value,
        }

        # Add SASL configuration for producer
        if self.security_protocol in [SecurityProtocol.SASL_PLAINTEXT, SecurityProtocol.SASL_SSL]:
            if not self.sasl_mechanism:
                raise ValueError("sasl_mechanism is required when using SASL security protocols")

            config['sasl.mechanism'] = self.sasl_mechanism.value

            if self.sasl_mechanism in [SaslMechanism.PLAIN, SaslMechanism.SCRAM_SHA_256, SaslMechanism.SCRAM_SHA_512]:
                if not self.sasl_username or not self.sasl_password:
                    raise ValueError("sasl_username and sasl_password are required for PLAIN and SCRAM mechanisms")

                config['sasl.username'] = self.sasl_username
                config['sasl.password'] = self.sasl_password

        # Add SSL configuration for producer
        if self.security_protocol in [SecurityProtocol.SSL, SecurityProtocol.SASL_SSL]:
            if self.ssl_ca_location:
                config['ssl.ca.location'] = self.ssl_ca_location

            if self.ssl_certificate_location:
                config['ssl.certificate.location'] = self.ssl_certificate_location

            if self.ssl_key_location:
                config['ssl.key.location'] = self.ssl_key_location

                if self.ssl_key_password:
                    config['ssl.key.password'] = self.ssl_key_password

            config['ssl.check.hostname'] = self.ssl_check_hostname

        # Add any additional configuration (now validated)
        if self.additional_config:
            config.update(self.additional_config)

        logger.info(f"Generated producer config with security protocol: {self.security_protocol.value}")
        return config

    def validate_security_config(self) -> bool:
        """
        Validate the security configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Check SASL configuration
        if self.security_protocol in [SecurityProtocol.SASL_PLAINTEXT, SecurityProtocol.SASL_SSL]:
            if not self.sasl_mechanism:
                raise ValueError("sasl_mechanism is required when using SASL security protocols")

            if self.sasl_mechanism in [SaslMechanism.PLAIN, SaslMechanism.SCRAM_SHA_256, SaslMechanism.SCRAM_SHA_512]:
                if not self.sasl_username or not self.sasl_password:
                    raise ValueError("sasl_username and sasl_password are required for PLAIN and SCRAM mechanisms")

        # Check SSL configuration
        if self.security_protocol in [SecurityProtocol.SSL, SecurityProtocol.SASL_SSL]:
            # SSL CA is highly recommended for production
            if not self.ssl_ca_location:
                logger = get_dagster_logger()
                logger.warning("ssl_ca_location not set - SSL certificate verification may fail in production")

        return True