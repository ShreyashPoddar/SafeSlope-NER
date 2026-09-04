"""
Unit tests for Member 6 Two-Way Conversational Bot Engine
Tests conversation state machine, multilingual switching, hazard reporting, and CV integration.
"""

from app.comms.bot_engine import bot_engine
from app.comms.sample_media import get_sample_base64


async def test_bot_initial_menu():
    """Verify greeting and initial menu options."""
    phone = "+919436100099"
    res = await bot_engine.process_incoming_message(from_phone=phone, body_text="Hi")

    assert "SafeSlope" in res["reply"]
    assert "1️⃣" in res["reply"]
    assert res["session_state"] == "MENU"


async def test_bot_language_switch():
    """Verify switching language to Mizo (lus) returns localized menu."""
    phone = "+919436100088"
    # Select language change option
    await bot_engine.process_incoming_message(from_phone=phone, body_text="4")
    # Choose Mizo (choice 4)
    res = await bot_engine.process_incoming_message(from_phone=phone, body_text="4")

    assert "Mizo ṭawng" in res["reply"] or "Chibai" in res["reply"] or "Leimin" in res["reply"]
    assert res["language"] == "lus"


async def test_bot_reporting_flow_with_photo_and_location():
    """Verify complete end-to-end inbound hazard reporting workflow."""
    phone = "+919436100077"
    # 1. Start report
    r1 = await bot_engine.process_incoming_message(from_phone=phone, body_text="1")
    assert "What type of hazard" in r1["reply"] or "Report a Slope Hazard" in r1["reply"]

    # 2. Choose Rockfall (choice 2)
    r2 = await bot_engine.process_incoming_message(from_phone=phone, body_text="2")
    assert "Attach a Photo" in r2["reply"] or "photo" in r2["reply"].lower()

    # 3. Attach rockfall photo via base64
    b64_img = get_sample_base64("rockfall")
    r3 = await bot_engine.process_incoming_message(
        from_phone=phone,
        body_text="Here is the picture",
        image_base64=b64_img,
    )
    assert "Location" in r3["reply"] or "📍" in r3["reply"]

    # 4. Share GPS Location pin
    r4 = await bot_engine.process_incoming_message(
        from_phone=phone,
        body_text="Current Location",
        lat=23.3150,
        lng=92.8540,
    )
    assert "Submitted Successfully" in r4["reply"] or "Tracking ID" in r4["reply"]
    assert "SLOPE-" in r4["reply"]
    assert "Surface Rockfall" in r4["reply"]
    assert "DEOC" in r4["reply"]


async def test_bot_sos_shortcut():
    """Verify instant SOS response with emergency helpline numbers."""
    phone = "+919436100066"
    res = await bot_engine.process_incoming_message(from_phone=phone, body_text="SOS")
    assert "1077" in res["reply"]
    assert "112" in res["reply"]
