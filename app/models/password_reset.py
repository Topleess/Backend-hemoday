import secrets
from datetime import datetime, timedelta, timezone # <--- 1. Добавили timezone

from tortoise import fields
from tortoise.models import Model


class PasswordResetToken(Model):
    """
    Password reset token model
    Tokens expire after 1 hour
    """
    
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reset_tokens", on_delete=fields.CASCADE)
    token = fields.CharField(max_length=64, unique=True, index=True)
    expires_at = fields.DatetimeField()
    used = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "password_reset_tokens"
    
    @classmethod
    def generate_token(cls) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    async def create_token(cls, user_id: str) -> "PasswordResetToken":
        """Create a new password reset token for a user"""
        token = cls.generate_token()
        
        # 2. ИСПОЛЬЗУЕМ ВРЕМЯ С ЧАСОВЫМ ПОЯСОМ (Aware)
        # datetime.now(timezone.utc) вместо datetime.utcnow()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        return await cls.create(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        # 3. ТЕКУЩЕЕ ВРЕМЯ ТОЖЕ БЕРЕМ С ЧАСОВЫМ ПОЯСОМ
        now = datetime.now(timezone.utc)
        
        # Защита: если вдруг база вернула время без зоны, добавляем её принудительно
        expires_at_check = self.expires_at
        if expires_at_check.tzinfo is None:
            expires_at_check = expires_at_check.replace(tzinfo=timezone.utc)
            
        return now > expires_at_check
    
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)"""
        return not self.used and not self.is_expired()