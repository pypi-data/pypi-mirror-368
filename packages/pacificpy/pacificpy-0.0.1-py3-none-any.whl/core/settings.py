from typing import Optional
import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """
    Application settings with smart defaults following Convention over Configuration.
    """
    
    # Server settings
    host: str = field(default="127.0.0.1", metadata={"description": "Host to bind to"})
    port: int = field(default=8000, metadata={"description": "Port to bind to"})
    debug: bool = field(default=False, metadata={"description": "Debug mode"})
    
    # Security settings
    secret_key: str = field(
        default="pacificpy-secret-key-for-development-only",
        metadata={"description": "Secret key for cryptographic signing"}
    )
    
    # Session settings
    session_backend: str = field(
        default="memory",
        metadata={"description": "Session backend (memory, redis, etc.)"}
    )
    
    # Template settings
    templates_dir: str = field(
        default="templates",
        metadata={"description": "Directory for templates"}
    )
    
    # OpenAPI settings
    openapi_url: Optional[str] = field(
        default="/openapi.json",
        metadata={"description": "OpenAPI schema URL"}
    )
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Settings":
        """
        Create settings from environment variables.
        
        Args:
            env_file: Path to .env file (optional)
            
        Returns:
            Settings instance with values from environment
        """
        # Load environment variables from file if provided
        if env_file:
            cls._load_env_file(env_file)
        
        # Create settings instance with environment values
        return cls(
            host=os.getenv("PACIFICPY_HOST", "127.0.0.1"),
            port=int(os.getenv("PACIFICPY_PORT", 8000)),
            debug=os.getenv("PACIFICPY_DEBUG", "False").lower() == "true",
            secret_key=os.getenv(
                "PACIFICPY_SECRET_KEY", 
                "pacificpy-secret-key-for-development-only"
            ),
            session_backend=os.getenv("PACIFICPY_SESSION_BACKEND", "memory"),
            templates_dir=os.getenv("PACIFICPY_TEMPLATES_DIR", "templates"),
            openapi_url=os.getenv("PACIFICPY_OPENAPI_URL", "/openapi.json")
        )
    
    @classmethod
    def from_toml(cls, toml_file: str) -> "Settings":
        """
        Create settings from TOML file (pyproject.toml or pacificpy.toml).
        
        Args:
            toml_file: Path to TOML file
            
        Returns:
            Settings instance with values from TOML file
        """
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib  # Python < 3.11
            except ImportError:
                raise ImportError(
                    "tomli is required to read TOML files. "
                    "Install it with 'pip install tomli'"
                )
        
        # Read the TOML file
        with open(toml_file, "rb") as f:
            data = tomllib.load(f)
        
        # Extract settings from TOML data
        pacificpy_config = data.get("tool", {}).get("pacificpy", {})
        
        # Create settings instance with TOML values
        return cls(
            host=pacificpy_config.get("host", "127.0.0.1"),
            port=pacificpy_config.get("port", 8000),
            debug=pacificpy_config.get("debug", False),
            secret_key=pacificpy_config.get(
                "secret_key", 
                "pacificpy-secret-key-for-development-only"
            ),
            session_backend=pacificpy_config.get("session_backend", "memory"),
            templates_dir=pacificpy_config.get("templates_dir", "templates"),
            openapi_url=pacificpy_config.get("openapi_url", "/openapi.json")
        )
    
    @staticmethod
    def _load_env_file(env_file: str) -> None:
        """
        Load environment variables from a .env file.
        
        Args:
            env_file: Path to .env file
        """
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        os.environ[key] = value
        except FileNotFoundError:
            pass