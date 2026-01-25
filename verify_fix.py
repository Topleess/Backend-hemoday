import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Add app to path
sys.path.append(os.getcwd())

# Mock missing dependencies
sys.modules["fastapi_mail"] = MagicMock()

from app.services.sync import SyncService
from app.api.v1.auth import request_password_reset
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.api.v1.schemas import PasswordResetRequest
import app.core.mail

async def test_sync_deduplication():
    print("Testing Sync Deduplication...")
    # Mock models to avoid DB connection
    with patch("app.services.sync.SYNC_MODELS") as mock_models:
        # User/Family mock
        family_id = "test-family-id"
        
        # We want to catch what keys are in 'changes'
        # We need to mock the models so they don't crash when accessed
        mock_model = MagicMock()
        mock_model._meta.fields_map = {}
        mock_model._meta.db = MagicMock()
        # Mocking the async call to .all()
        # In the code: records = await query.all()
        # query is model.filter(...) or model.all()
        
        future = asyncio.Future()
        future.set_result([])
        
        mock_model.filter.return_value.all.return_value = future
        mock_model.all.return_value.all.return_value = future
        
        # Make all models return this mock
        mock_models.get.return_value = mock_model
        
        try:
            result = await SyncService.pull_changes(family_id)
            keys = list(result['changes'].keys())
            print(f"Keys in changes: {keys}")
            
            if len(keys) != len(set(keys)):
                print("FAIL: Duplicate keys found in sync response!")
            else:
                print("SUCCESS: No duplicate keys in sync response.")
                
            expected_tables = [
                "transfusions", "analyses", "analysis_items", 
                "analysis_templates", "analysis_template_items",
                "reminders",
                "component_types", "chelator_types"
            ]
            
            for t in expected_tables:
                if t not in keys:
                    print(f"WARNING: Expected table {t} missing from keys.")
            
            if len(keys) == len(expected_tables):
                 print(f"SUCCESS: Count matches expected ({len(expected_tables)}).")

        except Exception as e:
            print(f"Error during sync test: {e}")
            import traceback
            traceback.print_exc()

async def test_email_reset():
    print("\nTesting Email Reset...")
    
    # Mock dependencies
    # We explicitly patch the symbols where they are imported in the target file
    with patch("app.api.v1.auth.User") as MockUser, \
         patch("app.api.v1.auth.PasswordResetToken") as MockToken, \
         patch("app.core.mail.send_reset_email") as mock_send_email:
             
        # Setup User mock
        user = MagicMock()
        user.id = "user-id"
        user.email = "test@example.com"
        user.deleted_at = None
        
        # Mock DB async calls
        future_user = asyncio.Future()
        future_user.set_result(user)
        MockUser.filter.return_value.first.return_value = future_user
        
        # Setup Token mock
        token_obj = MagicMock()
        token_obj.token = "secure-token"
        
        future_token = asyncio.Future()
        future_token.set_result(token_obj)
        MockToken.create_token.return_value = future_token
        
        # Mock send_email async
        future_email = asyncio.Future()
        future_email.set_result(None)
        mock_send_email.return_value = future_email
        
        # Call function
        req = PasswordResetRequest(email="test@example.com")
        try:
            await request_password_reset(req)
            
            # Verify
            if mock_send_email.called:
                args = mock_send_email.call_args[0]
                print(f"SUCCESS: send_reset_email called with: {args}")
                if args[0] == "test@example.com" and args[1] == "secure-token":
                    print("Args match expected values.")
                else:
                    print("FAIL: Args do not match.")
            else:
                print("FAIL: send_reset_email NOT called.")
        except Exception as e:
            print(f"Error during email test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # We need to install requirements first? 
    # Attempt to run without full app context, relying on mocks.
    # pydantic might be needed.
    try:
        asyncio.run(test_sync_deduplication())
        asyncio.run(test_email_reset())
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run in environment with dependencies installed.")
