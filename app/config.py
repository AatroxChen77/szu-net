from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # User Credentials
    SRUN_USERNAME: str
    SRUN_PASSWORD: str
    
    # Network Config
    SRUN_AC_ID: str = '12'
    SRUN_ENC: str = 'srun_bx1'
    SRUN_N: str = '200'
    SRUN_TYPE: str = '1'
    
    # Paths
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
    
    @property
    def JS_FILE_PATH(self) -> Path:
        return self.PROJECT_ROOT / "encryption" / "srun_base64.js"

    # API Endpoints
    GET_CHALLENGE_API: str = "https://net.szu.edu.cn/cgi-bin/get_challenge"
    SRUN_PORTAL_API: str = "https://net.szu.edu.cn/cgi-bin/srun_portal"
    
    # Request Headers
    USER_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36'

    # App Config
    RETRY_INTERVAL: int = 300  # seconds
    MAX_RETRIES: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
