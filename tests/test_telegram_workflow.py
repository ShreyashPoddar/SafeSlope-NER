import os
import sys
import asyncio
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.comms.bot_engine import bot_engine
from app.comms.queue_service import queue_service


def test_telegram_direct_photo_reporting_flow():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    from app.comms.sample_media import get_sample_bytes
    dummy_photo_bytes = get_sample_bytes("rockfall")

    # Step 1: Citizen messages Telegram bot
    chat_id = 987654321
    res1 = loop.run_until_complete(
        bot_engine.process_incoming_message(
            from_phone="tg_987654321",
            body_text="/start",
            sender_name="Lalthan Mawia",
            sender_username="lalthan_m",
            channel="Telegram Bot",
            telegram_chat_id=chat_id,
        )
    )
    assert res1["session_state"] == "MENU"

    # Step 2: Citizen directly sends a photo with a caption
    res2 = loop.run_until_complete(
        bot_engine.process_incoming_message(
            from_phone="tg_987654321",
            body_text="Massive boulders fallen across the highway near Serchhip",
            media_bytes=dummy_photo_bytes,
            sender_name="Lalthan Mawia",
            sender_username="lalthan_m",
            channel="Telegram Bot",
            telegram_chat_id=chat_id,
        )
    )
    assert res2["session_state"] == "AWAITING_LOCATION"

    # Step 3: Citizen sends real GPS location pin
    res3 = loop.run_until_complete(
        bot_engine.process_incoming_message(
            from_phone="tg_987654321",
            body_text="GPS Location Pin",
            lat=23.3150,
            lng=92.8540,
            sender_name="Lalthan Mawia",
            sender_username="lalthan_m",
            channel="Telegram Bot",
            telegram_chat_id=chat_id,
        )
    )
    assert res3["session_state"] == "MENU"
    assert "report" in res3

    rep = res3["report"]
    assert rep["channel"] == "Telegram Bot"
    assert rep["sender_username"] == "lalthan_m"
    assert rep["sender_name"] == "Lalthan Mawia"
    assert rep["telegram_chat_id"] == chat_id
    assert rep["image_url"].startswith("/uploads/citizen_report_")
    assert rep["lat"] == 23.3150
    assert rep["lng"] == 92.8540
    assert rep["review_status"] == "PENDING_REVIEW"
    assert "cv_details" in rep

    # Step 4: DEOC Officer assesses report on localhost
    with patch("app.comms.telegram_bot.send_message") as mock_send_msg:
        assessed_rep = loop.run_until_complete(
            queue_service.review_report(
                report_id=rep["id"],
                action="APPROVE",
                officer_name="Officer Z. Ralte (DEOC Lead)",
                deoc_notes="Ground truth verified; clearing bulldozer dispatched",
                adjusted_severity="CRITICAL",
                assigned_unit="Serchhip PWD Clearance Squad #3",
                notify_citizen=True,
            )
        )
        assert assessed_rep["review_status"] == "VERIFIED_APPROVED"
        assert assessed_rep["verified"] is True
        assert assessed_rep["severity"] == "CRITICAL"
        assert assessed_rep["assigned_unit"] == "Serchhip PWD Clearance Squad #3"
        assert mock_send_msg.called

    loop.close()
    print("[PASS] test_telegram_direct_photo_reporting_flow")


if __name__ == "__main__":
    test_telegram_direct_photo_reporting_flow()
