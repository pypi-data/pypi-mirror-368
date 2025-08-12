from keycloak import KeycloakOpenID
from transpara import tlogging
from datetime import datetime, timedelta
import threading
from typing import Optional, Dict

logger = tlogging.get_logger(__name__)

class TAuthManager:
    """Background authentication manager for Keycloak machine-to-machine communication."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, server_url: str, realm: str, client_id: str, client_secret: str, verify_ssl: bool, timeout: int):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.keycloak = KeycloakOpenID(
            server_url=server_url,
            realm_name=realm,
            client_id=client_id,
            client_secret_key=client_secret,
            verify=verify_ssl,
            timeout=timeout
        )
        
        self.token_data: Optional[Dict] = None
        self.token_expires_at: Optional[datetime] = None
        self.token_lock = threading.Lock()
        self.refresh_thread: Optional[threading.Thread] = None
        self.stop_refresh = threading.Event()
        
        # Get initial token
        self._refresh_token()
        
        # Start background refresh thread
        self._start_refresh_thread()
    
    def _refresh_token(self) -> bool:
        """Refresh the authentication token."""
        try:
            logger.tdebug("Refreshing authentication token from Keycloak")
            token_response = self.keycloak.token(grant_type="client_credentials")
            
            with self.token_lock:
                self.token_data = token_response
                # Calculate expiration time with a buffer (refresh 30 seconds before expiry)
                expires_in = token_response.get('expires_in', 300)  # Default 5 minutes
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 30)
            
            logger.info("Successfully refreshed authentication token")
            return True
            
        except Exception as e:
            logger.terror(f"Failed to refresh authentication token: {e}")
            return False
    
    def _start_refresh_thread(self):
        """Start the background token refresh thread."""
        def refresh_loop():
            while not self.stop_refresh.is_set():
                try:
                    if self.token_expires_at and datetime.now() >= self.token_expires_at:
                        self._refresh_token()
                    
                    # Check every 30 seconds
                    self.stop_refresh.wait(30)
                    
                except Exception as e:
                    logger.terror(f"Error in token refresh loop: {e}")
                    self.stop_refresh.wait(30)
        
        self.refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.refresh_thread.start()
        logger.info("Started background token refresh thread")
    
    def get_token_header(self, force_refresh: bool = False) -> Optional[Dict[str, str]]:
        """Get the current authentication header with Bearer token."""
        if force_refresh or not self.token_data or (
            self.token_expires_at and datetime.now() >= self.token_expires_at
        ):
            if not self._refresh_token():
                return None
        
        with self.token_lock:
            if self.token_data and 'access_token' in self.token_data:
                return {"Authorization": f"Bearer {self.token_data['access_token']}"}
        
        return None
    
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """Get the current access token."""
        if force_refresh or not self.token_data or (
            self.token_expires_at and datetime.now() >= self.token_expires_at
        ):
            if not self._refresh_token():
                return None
        
        with self.token_lock:
            if self.token_data and 'access_token' in self.token_data:
                return self.token_data['access_token']
        
        return None
    
    def is_token_valid(self) -> bool:
        """Check if the current token is valid and not expired."""
        with self.token_lock:
            return (
                self.token_data is not None 
                and self.token_expires_at is not None 
                and datetime.now() < self.token_expires_at
            )
    
    def stop_background_refresh(self):
        """Stop the background token refresh thread."""
        if self.refresh_thread:
            self.stop_refresh.set()
            self.refresh_thread.join(timeout=5)
            logger.info("Stopped background token refresh thread")

# Global instance
#tauth_manager = TAuthManager()

if __name__ == "__main__":
    # tauth_manager = TAuthManager(
    #     server_url="https://tauth.borg-ci.transpara.com/",
    #     realm="transpara",
    #     client_id="tgraph",
    #     client_secret="",
    #     verify_ssl=False,
    #     timeout=30
    # )
    # print(tauth_manager.get_token_header()) 
    # print(tauth_manager.get_access_token())
    # print(tauth_manager.is_token_valid())

    reordered_lookup = "/System/INMATION/Demo OPC Node/Milo OPC UA/Demo/Dynamic/Int16"

    if reordered_lookup.startswith("/"):
        reordered_lookup = reordered_lookup[1:]

    print(reordered_lookup)