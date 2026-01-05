import time
import re
import json
import requests
import execjs
from loguru import logger
from typing import Tuple, Dict, Any

from app.config import settings
from app.utils import get_local_ip,is_internet_connected
from encryption.srun_md5 import get_md5
from encryption.srun_sha1 import get_sha1
from encryption.srun_xencode import get_xencode

class SZUNetworkClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': settings.USER_AGENT})
        # Lazy loading of JS context: only initialize if needed (Teaching Zone)
        if settings.NETWORK_ZONE == 'teaching':
            self._init_js_context()
        
    def _init_js_context(self):
        """Initialize PyExecJS context with the encryption script."""
        if not settings.JS_FILE_PATH.exists():
            raise FileNotFoundError(f"JS encryption file not found at: {settings.JS_FILE_PATH}")
            
        logger.info(f"Loading JS encryption logic from {settings.JS_FILE_PATH}")
        with open(settings.JS_FILE_PATH, 'r', encoding='utf-8') as f:
            js_code = f.read()
        self.ctx = execjs.compile(js_code)

    def _get_token(self, ip: str) -> str:
        """Retrieve the challenge token from the server."""
        timestamp = int(time.time() * 1000)
        params = {
            "callback": f"jQuery112404953340710317169_{timestamp}",
            "username": settings.SRUN_USERNAME,
            "ip": ip,
            "_": timestamp,
        }
        
        logger.debug(f"Requesting challenge token for IP: {ip}")
        try:
            resp = self.session.get(settings.GET_CHALLENGE_API, params=params, timeout=10)
            resp.raise_for_status()
            # Extract token using regex
            match = re.search(r'"challenge":"(.*?)"', resp.text)
            if not match:
                raise ValueError("Failed to extract challenge token from response")
            token = match.group(1)
            logger.debug(f"Got token: {token}")
            return token
        except Exception as e:
            logger.error(f"Error getting token: {e}")
            raise

    def _get_info_str(self, ip: str) -> str:
        """Construct the info JSON string required for encryption."""
        info = {
            "username": settings.SRUN_USERNAME,
            "password": settings.SRUN_PASSWORD,
            "ip": ip,
            "acid": settings.SRUN_AC_ID,
            "enc_ver": settings.SRUN_ENC
        }
        # Mimic the original script's JSON formatting (single quotes to double quotes, no spaces)
        # Note: Standard json.dumps might add spaces, so we use the original regex method to be safe
        # or just json.dumps(info, separators=(',', ':')) which removes spaces.
        # However, the original script used regex on str(dict), which is risky but specific.
        # Let's use standard JSON but ensure no spaces.
        return json.dumps(info, separators=(',', ':'))

    def _get_chksum(self, token: str, hmd5: str, ip: str, info_str: str) -> str:
        """Calculate the checksum."""
        chkstr = f"{token}{settings.SRUN_USERNAME}"
        chkstr += f"{token}{hmd5}"
        chkstr += f"{token}{settings.SRUN_AC_ID}"
        chkstr += f"{token}{ip}"
        chkstr += f"{token}{settings.SRUN_N}"
        chkstr += f"{token}{settings.SRUN_TYPE}"
        chkstr += f"{token}{info_str}"
        return chkstr

    def _encrypt_payload(self, ip: str, token: str) -> Tuple[str, str, str]:
        """Perform the complex encryption logic."""
        info_str = self._get_info_str(ip)
        
        # 1. Encode info using custom XEncode and Base64 (via JS)
        xencoded = get_xencode(info_str, token)
        encoded_info = "{SRBX1}" + self.ctx.call('_encode', xencoded)
        
        # 2. MD5 hash of password
        hmd5 = get_md5(settings.SRUN_PASSWORD, token)
        
        # 3. SHA1 checksum
        chkstr = self._get_chksum(token, hmd5, ip, encoded_info)
        chksum = get_sha1(chkstr)
        
        return encoded_info, hmd5, chksum
        
    def _login_teaching(self) -> bool:
        """Execute the full login flow for Teaching Zone (SRUN)."""
        try:
            ip = get_local_ip()
            logger.info(f"Starting login process for IP: {ip} / User: {settings.SRUN_USERNAME}")
            
            token = self._get_token(ip)
            encoded_info, hmd5, chksum = self._encrypt_payload(ip, token)
            
            timestamp = int(time.time() * 1000)
            params = {
                'callback': f'jQuery11240645308969735664_{timestamp}',
                'action': 'login',
                'username': settings.SRUN_USERNAME,
                'password': '{MD5}' + hmd5,
                'ac_id': settings.SRUN_AC_ID,
                'ip': ip,
                'chksum': chksum,
                'info': encoded_info,
                'n': settings.SRUN_N,
                'type': settings.SRUN_TYPE,
                'os': 'windows+10',
                'name': 'windows',
                'double_stack': '0',
                '_': timestamp
            }
            
            logger.debug("Sending login request...")
            resp = self.session.get(settings.SRUN_PORTAL_API, params=params, timeout=10)
            resp.raise_for_status()
            
            # Parse response
            if '"suc_msg":"' in resp.text:
                msg = re.search(r'"suc_msg":"(.*?)"', resp.text).group(1)
                logger.success(f"Login Successful! Server response: {msg}")
                return True
            else:
                # Try to capture error message
                error_msg = "Unknown error"
                if '"error_msg":"' in resp.text:
                    error_msg = re.search(r'"error_msg":"(.*?)"', resp.text).group(1)
                logger.error(f"Login Failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.exception(f"An unexpected error occurred during login: {e}")
            return False

    def _login_dorm(self) -> bool:
        """Execute the login flow for Dorm Zone (Dr.COM)."""
        try:
            ip = get_local_ip()
            logger.info(f"Starting Dorm Zone login process for IP: {ip} / User: {settings.SRUN_USERNAME}")
            
            timestamp = int(time.time() * 1000)
            params = {
                'callback': 'dr1003',
                'login_method': '1',
                'user_account': f',0,{settings.SRUN_USERNAME}',
                'user_password': settings.SRUN_PASSWORD,
                'wlan_user_ip': ip,
                'jsVersion': '4.1.3'
            }
            
            # Dorm zone URL
            url = "http://172.30.255.42:801/eportal/portal/login"
            
            logger.debug("Sending Dorm Zone login request...")
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            
            # Handle potential encoding issues (Dr.COM might return GBK/GB2312)
            resp.encoding = 'utf-8'  # Try forcing utf-8 first, or rely on apparent_encoding if needed

            # Strict success validation
            # Captive portals often return 200 OK even on failure, so we must check the body.
            if '"result":1' in resp.text or '"msg":"成功"' in resp.text or "已在线" in resp.text:
                logger.success(f"Dorm Zone Login Successful!")
                return True
            else:
                # Try to capture error message
                error_msg = "Unknown error"
                if '"msg":"' in resp.text:
                    match = re.search(r'"msg":"(.*?)"', resp.text)
                    if match:
                        error_msg = match.group(1)
                
                logger.error(f"Dorm Zone Login Failed: {error_msg}")
                logger.debug(f"Full response: {resp.text}")
                return False
                
        except Exception as e:
            logger.exception(f"An unexpected error occurred during Dorm Zone login: {e}")
            return False

    def login(self) -> bool:
        """
        Dispatch login to the appropriate strategy based on configuration.
        """
        if settings.NETWORK_ZONE == 'dorm':
            logger.info("Executing Dorm Zone Login Strategy")
            return self._login_dorm()
        else:
            logger.info("Executing Teaching Zone Login Strategy")
            return self._login_teaching()

    def keep_alive(self):
        """
        Daemon mode: Check network status periodically and relogin if disconnected.
        """
        logger.info(f"Starting Keep-Alive Daemon (Interval: {settings.RETRY_INTERVAL}s)")
        
        while True:
            try:
                # 1. 先做体检：网络通吗？
                if is_internet_connected():
                    # 网络正常，只打印个 debug 日志（平时看不见，清爽）
                    logger.debug("✅ Network check passed (Status: 204/200). Sleeping...")
                else:
                    # 2. 网络断了！触发登录
                    logger.warning("⚠️ Network disconnected or captive portal detected! Initiating login...")
                    self.login()
                    
            except Exception as e:
                logger.error(f"Unexpected error in daemon loop: {e}")
            
            # 3. 休息
            time.sleep(settings.RETRY_INTERVAL)
