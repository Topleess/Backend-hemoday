import asyncio
from unittest.mock import MagicMock
from app.services.sync import SyncService

async def test_filter_logic():
    # Mock data with internal fields and family_id
    data = {
        "id": "123",
        "volume": 200,
        "_status": "created",
        "_changed": "",
        "family_id": "family-uuid",
        "extra_garbage": "should be removed"
    }

    # Mock Model
    Model = MagicMock()
    # Mock fields_map to include volume but NOT family_id (mimicking the issue constraint, 
    # but allowing family relation if I mimic Foreign Key correctly? 
    # Actually I just need to check if 'family_id' key survives the filter.
    # The filter logic I wrote is:
    # valid_fields = model._meta.fields_map.keys()
    # data = {k: v for k, v in data.items() if k in valid_fields or k == 'id' or k == 'family_id'}
    
    Model._meta.fields_map = {
        "volume": "dummy"
        # family is usually here, but family_id is NOT in keys usually?
        # Tortoise FK creates 'family' in fields_map.
    }

    # We need to mock _create_or_update_record to NOT call DB but just return the processed data?
    # No, I want to test the logic INSIDE it.
    # But it calls await model.filter...
    # I can copy the function logic to this script or import it.
    
    # Let's just import the Service and mock the DB calls inside logic?
    # It's a static method.
    
    # Mock model.filter(...).first() -> None
    # Mock model.create(**data) -> Assertion
    
    future_none = asyncio.Future()
    future_none.set_result(None)
    Model.filter.return_value.first.return_value = future_none
    
    future_create = asyncio.Future()
    future_create.set_result(None)
    Model.create.return_value = future_create

    try:
        await SyncService._create_or_update_record(Model, data)
        print("Function executed successfully.")
    except Exception as e:
        print(f"Function failed: {e}")

    # Verify what create was called with
    call_args = Model.create.call_args
    if not call_args:
        print("Model.create was NOT called.")
        return

    saved_data = call_args[1] # kwargs
    # OR call_args.kwargs if named
    saved_data = call_args.kwargs

    print(f"Saved Data: {saved_data}")

    if "_status" in saved_data:
        print("FAIL: _status NOT filtered out")
    else:
        print("SUCCESS: _status filtered out")

    if "family_id" in saved_data:
        print("SUCCESS: family_id preserved")
    else:
        print("FAIL: family_id lost")

if __name__ == "__main__":
    asyncio.run(test_filter_logic())
