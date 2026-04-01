import logging
import aiohttp
from config import CONFIG

logger = logging.getLogger(__name__)

class OAuthService:
    def __init__(self):
        # oauth_validation: false means use mock, true means validate real tokens
        self.use_mock = not CONFIG.get('mock_services', {}).get('oauth_validation', False)
        
        if self.use_mock:
            logger.warning("OAuth validation is disabled - using mock responses")
    
    async def verify_google_token(self, token: str) -> dict:
        if self.use_mock:
            logger.debug("Returning mock Google OAuth response")
            return {
                "email": "mock.google@example.com",
                "name": "Mock Google User",
                "picture": "https://via.placeholder.com/150",
                "sub": "mock_google_123"
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={token}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Google OAuth token verified for: {data.get('email')}")
                        return {
                            "email": data.get("email"),
                            "name": data.get("name"),
                            "picture": data.get("picture"),
                            "sub": data.get("sub")
                        }
                    else:
                        logger.error(f"Google OAuth verification failed. Status: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error during Google OAuth verification: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error during Google OAuth verification: {e}", exc_info=True)
            return None
    
    async def verify_apple_token(self, token: str) -> dict:
        if self.use_mock:
            logger.debug("Returning mock Apple OAuth response")
            return {
                "email": "mock.apple@example.com",
                "name": "Mock Apple User",
                "sub": "mock_apple_123"
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                token_info = {
                    "id_token": token,
                    "client_id": CONFIG['api']['oauth']['apple']['client_id'],
                    "client_secret": CONFIG['api']['oauth']['apple']['client_secret']
                }
                
                async with session.post(
                    "https://appleid.apple.com/auth/token",
                    data=token_info
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        import base64
                        import json
                        
                        payload = data['id_token'].split('.')[1]
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = json.loads(base64.b64decode(payload))
                        
                        email = decoded.get("email")
                        logger.info(f"Apple OAuth token verified for: {email}")
                        
                        return {
                            "email": email,
                            "name": f"{decoded.get('name', {}).get('firstName', '')} {decoded.get('name', {}).get('lastName', '')}".strip(),
                            "sub": decoded.get("sub")
                        }
                    else:
                        logger.error(f"Apple OAuth verification failed. Status: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error during Apple OAuth verification: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error during Apple OAuth verification: {e}", exc_info=True)
            return None

oauth_service = OAuthService()
