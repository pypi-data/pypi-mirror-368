import os
import tempfile
from pacificpy.core.settings import Settings


def test_settings_defaults():
    # Test that settings have correct default values.
    settings = Settings()
    
    # Check default values
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.debug is False
    assert settings.secret_key == "pacificpy-secret-key-for-development-only"
    assert settings.session_backend == "memory"
    assert settings.templates_dir == "templates"
    assert settings.openapi_url == "/openapi.json"


def test_settings_from_env():
    # Test that settings can be loaded from environment variables.
    # Set environment variables
    os.environ["PACIFICPY_HOST"] = "0.0.0.0"
    os.environ["PACIFICPY_PORT"] = "9000"
    os.environ["PACIFICPY_DEBUG"] = "True"
    os.environ["PACIFICPY_SECRET_KEY"] = "test-secret-key"
    os.environ["PACIFICPY_SESSION_BACKEND"] = "redis"
    os.environ["PACIFICPY_TEMPLATES_DIR"] = "custom_templates"
    os.environ["PACIFICPY_OPENAPI_URL"] = "/custom-openapi.json"
    
    # Create settings from environment
    settings = Settings.from_env()
    
    # Check values from environment
    assert settings.host == "0.0.0.0"
    assert settings.port == 9000
    assert settings.debug is True
    assert settings.secret_key == "test-secret-key"
    assert settings.session_backend == "redis"
    assert settings.templates_dir == "custom_templates"
    assert settings.openapi_url == "/custom-openapi.json"
    
    # Clean up environment variables
    del os.environ["PACIFICPY_HOST"]
    del os.environ["PACIFICPY_PORT"]
    del os.environ["PACIFICPY_DEBUG"]
    del os.environ["PACIFICPY_SECRET_KEY"]
    del os.environ["PACIFICPY_SESSION_BACKEND"]
    del os.environ["PACIFICPY_TEMPLATES_DIR"]
    del os.environ["PACIFICPY_OPENAPI_URL"]


def test_settings_from_env_file():
    # Test that settings can be loaded from a .env file.
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
        f.write("PACIFICPY_HOST=192.168.1.1\n")
        f.write("PACIFICPY_PORT=7000\n")
        f.write("PACIFICPY_DEBUG=True\n")
        f.write("PACIFICPY_SECRET_KEY=file-secret-key\n")
        f.write("PACIFICPY_SESSION_BACKEND=database\n")
        f.write("PACIFICPY_TEMPLATES_DIR=file_templates\n")
        f.write("PACIFICPY_OPENAPI_URL=/file-openapi.json\n")
        env_file = f.name
    
    # Create settings from .env file
    settings = Settings.from_env(env_file)
    
    # Check values from .env file
    assert settings.host == "192.168.1.1"
    assert settings.port == 7000
    assert settings.debug is True
    assert settings.secret_key == "file-secret-key"
    assert settings.session_backend == "database"
    assert settings.templates_dir == "file_templates"
    assert settings.openapi_url == "/file-openapi.json"
    
    # Clean up
    os.unlink(env_file)


def test_settings_from_toml():
    # Test that settings can be loaded from a TOML file.
    # Create a temporary TOML file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as f:
        f.write("[tool.pacificpy]\n")
        f.write('host = "10.0.0.1"\n')
        f.write("port = 6000\n")
        f.write("debug = true\n")
        f.write('secret_key = "toml-secret-key"\n')
        f.write('session_backend = "memcached"\n')
        f.write('templates_dir = "toml_templates"\n')
        f.write('openapi_url = "/toml-openapi.json"\n')
        toml_file = f.name
    
    # Create settings from TOML file
    settings = Settings.from_toml(toml_file)
    
    # Check values from TOML file
    assert settings.host == "10.0.0.1"
    assert settings.port == 6000
    assert settings.debug is True
    assert settings.secret_key == "toml-secret-key"
    assert settings.session_backend == "memcached"
    assert settings.templates_dir == "toml_templates"
    assert settings.openapi_url == "/toml-openapi.json"
    
    # Clean up
    os.unlink(toml_file)