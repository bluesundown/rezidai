import logging
import aiohttp
from config import CONFIG

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.from_email = CONFIG.get('email', {}).get('from_email', 'noreply@realtyai.com')
        self.from_name = CONFIG.get('email', {}).get('from_name', 'RealtyAI')
        self.sendgrid_api_key = CONFIG.get('email', {}).get('sendgrid_api_key', '')
    
    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        return await self._send_email(
            to_email,
            user_name,
            "Welcome to RealtyAI!",
            f"Hi {user_name},<br><br>Welcome to RealtyAI, your AI-powered real estate listing platform.<br><br>Get started by creating your first listing!<br><br>Best regards,<br>The RealtyAI Team"
        )
    
    async def send_password_reset_email(self, to_email: str, reset_link: str) -> bool:
        return await self._send_email(
            to_email,
            "Password Reset Request",
            "Reset Your Password",
            f"Click the link below to reset your password:<br><br><a href='{reset_link}'>{reset_link}</a><br><br>This link expires in 24 hours.<br><br>Best regards,<br>The RealtyAI Team"
        )
    
    async def send_email_verification(self, to_email: str, verification_link: str) -> bool:
        return await self._send_email(
            to_email,
            "Verify Your Email",
            "Email Verification",
            f"Please verify your email address by clicking the link below:<br><br><a href='{verification_link}'>{verification_link}</a><br><br>Best regards,<br>The RealtyAI Team"
        )
    
    async def _send_email(self, to_email: str, user_name: str, subject: str, body: str) -> bool:
        # Check if SendGrid is configured
        if not self.sendgrid_api_key or self.sendgrid_api_key.startswith('your_'):
            logger.warning(f"SendGrid not configured. Email not sent to: {to_email}")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                form = aiohttp.FormData()
                form.add_field('from', f'{self.from_name} <{self.from_email}>')
                form.add_field('to', to_email)
                form.add_field('subject', subject)
                form.add_field('html', body)
                
                async with session.post(
                    'https://api.sendgrid.com/v3/mail/send',
                    data=form,
                    headers={'Authorization': f'Bearer {self.sendgrid_api_key}'}
                ) as response:
                    if response.status == 202:
                        logger.info(f"Email sent successfully to: {to_email}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send email to {to_email}. Status: {response.status}, Error: {error_text}")
                        return False
        except aiohttp.ClientError as e:
            logger.error(f"Network error sending email to {to_email}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}", exc_info=True)
            return False

email_service = EmailService()
