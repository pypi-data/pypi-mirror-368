"""
Configuration module for LogSentinelAI
Centralizes all configuration constants and environment variable handling
"""

import os
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(dotenv_path="config")

# commons.py에서 로깅 설정 가져오기 (순환 참조 해결됨)
from .commons import setup_logger, LOG_LEVEL

logger = setup_logger(__name__, LOG_LEVEL)
logger.info("Loading configuration from .env file")


# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODELS = {
    "ollama": os.getenv("LLM_MODEL_OLLAMA", "qwen2.5-coder:3b"),
    "vllm": os.getenv("LLM_MODEL_VLLM", "Qwen/Qwen2.5-1.5B-Instruct"),
    "openai": os.getenv("LLM_MODEL_OPENAI", "gpt-4o-mini"),
    "gemini": os.getenv("LLM_MODEL_GEMINI", "gemini-1.5-pro")
}
LLM_API_HOSTS = {
    "ollama": os.getenv("LLM_API_HOST_OLLAMA", "http://127.0.0.1:11434/v1"),
    "vllm": os.getenv("LLM_API_HOST_VLLM", "http://127.0.0.1:5000/v1"),
    "openai": os.getenv("LLM_API_HOST_OPENAI", "https://api.openai.com/v1"),
    "gemini": os.getenv("LLM_API_HOST_GEMINI", "https://generativelanguage.googleapis.com/v1beta/openai/")
}
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.5"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))




# Logging Configuration - managed by commons.py
# LOG_LEVEL and LOG_FILE are imported from commons


# Common Analysis Configuration
RESPONSE_LANGUAGE = os.getenv("RESPONSE_LANGUAGE", "korean")
ANALYSIS_MODE = os.getenv("ANALYSIS_MODE", "batch")


# Log Paths Configuration - Simple defaults
LOG_PATHS = {
    "httpd_access": os.getenv("LOG_PATH_HTTPD_ACCESS", "sample-logs/access-10k.log"),
    "httpd_server": os.getenv("LOG_PATH_HTTPD_SERVER", "sample-logs/apache-10k.log"),
    "linux_system": os.getenv("LOG_PATH_LINUX_SYSTEM", "sample-logs/linux-2k.log"),
    "general_log": os.getenv("LOG_PATH_GENERAL_LOG", "sample-logs/general.log")
}


# Real-time Monitoring Configuration
REALTIME_CONFIG = {
    "polling_interval": int(os.getenv("REALTIME_POLLING_INTERVAL", "5")),
    "max_lines_per_batch": int(os.getenv("REALTIME_MAX_LINES_PER_BATCH", "50")),
    "buffer_time": int(os.getenv("REALTIME_BUFFER_TIME", "2")),
    "only_sampling_mode": os.getenv("REALTIME_ONLY_SAMPLING_MODE", "false").lower() == "true",
    "sampling_threshold": int(os.getenv("REALTIME_SAMPLING_THRESHOLD", "100"))
}


# Default Remote SSH Configuration
DEFAULT_REMOTE_SSH_CONFIG = {
    "mode": os.getenv("REMOTE_LOG_MODE", "local"),
    "host": os.getenv("REMOTE_SSH_HOST", ""),
    "port": int(os.getenv("REMOTE_SSH_PORT", "22")),
    "user": os.getenv("REMOTE_SSH_USER", ""),
    "key_path": os.getenv("REMOTE_SSH_KEY_PATH", ""),
    "password": os.getenv("REMOTE_SSH_PASSWORD", ""),
    "timeout": int(os.getenv("REMOTE_SSH_TIMEOUT", "10"))
}


# Default Chunk Sizes
LOG_CHUNK_SIZES = {
    "httpd_access": int(os.getenv("CHUNK_SIZE_HTTPD_ACCESS", "10")),
    "httpd_server": int(os.getenv("CHUNK_SIZE_HTTPD_SERVER", "10")),
    "linux_system": int(os.getenv("CHUNK_SIZE_LINUX_SYSTEM", "10")),
    "general_log": int(os.getenv("CHUNK_SIZE_GENERAL_LOG", "10"))
}


# GeoIP Configuration
GEOIP_CONFIG = {
    "enabled": os.getenv("GEOIP_ENABLED", "true").lower() == "true",
    "database_path": os.getenv("GEOIP_DATABASE_PATH", "~/.logsentinelai/GeoLite2-City.mmdb"),
    "fallback_country": os.getenv("GEOIP_FALLBACK_COUNTRY", "Unknown"),
    "cache_size": int(os.getenv("GEOIP_CACHE_SIZE", "1000")),
    "include_private_ips": os.getenv("GEOIP_INCLUDE_PRIVATE_IPS", "false").lower() == "true"
}


# Elasticsearch Configuration
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER", "elastic")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "changeme")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "logsentinelai-analysis")

def get_analysis_config(log_type, chunk_size=None, analysis_mode=None, 
                       remote_mode=None, ssh_config=None, remote_log_path=None):
    """
    Get analysis configuration for specific log type
    
    Args:
        log_type: Log type ("httpd_access", "httpd_server", "linux_system")
        chunk_size: Override chunk size (optional)
        analysis_mode: Override analysis mode (optional) - "batch" or "realtime"
        remote_mode: Override remote mode (optional) - "local" or "ssh" 
        ssh_config: Custom SSH configuration dict (optional)
        remote_log_path: Custom remote log path (optional)
    
    Returns:
        dict: Configuration containing log_path, chunk_size, response_language, analysis_mode, ssh_config
    """
    logger.info(f"Getting analysis configuration for log_type: {log_type}")
    
    mode = analysis_mode if analysis_mode is not None else ANALYSIS_MODE
    access_mode = remote_mode if remote_mode is not None else DEFAULT_REMOTE_SSH_CONFIG["mode"]
    
    logger.debug(f"Configuration parameters - mode: {mode}, access_mode: {access_mode}")
    
    # Get log path - use simple LOG_PATHS for all cases
    if access_mode == "ssh":
        log_path = remote_log_path or LOG_PATHS.get(log_type, "")
        logger.info(f"SSH mode: using log path: {log_path}")
    else:
        log_path = LOG_PATHS.get(log_type, "")
        logger.info(f"Local mode: using log path: {log_path}")
    
    # SSH configuration
    if access_mode == "ssh":
        final_ssh_config = {**DEFAULT_REMOTE_SSH_CONFIG, **(ssh_config or {}), "mode": "ssh"}
        logger.info(f"SSH configuration prepared: {final_ssh_config}")
    else:
        final_ssh_config = {"mode": "local"}
        logger.debug("Local mode configuration prepared")
    
    final_chunk_size = chunk_size if chunk_size is not None else LOG_CHUNK_SIZES.get(log_type, 3)
    logger.info(f"Final configuration - chunk_size: {final_chunk_size}, response_language: {RESPONSE_LANGUAGE}")
    
    config = {
        "log_path": log_path,
        "chunk_size": final_chunk_size,
        "response_language": RESPONSE_LANGUAGE,
        "analysis_mode": mode,
        "access_mode": access_mode,
        "ssh_config": final_ssh_config,
        "realtime_config": REALTIME_CONFIG if mode == "realtime" else None
    }
    
    logger.info("Analysis configuration prepared successfully")
    return config