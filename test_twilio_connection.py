"""
SafeSlope-NER / ResiliNER - Live WhatsApp & Twilio Connection Diagnostic Tool
Member 6: Communications & Bot Developer

Run this script to verify your WhatsApp credentials and send a live test message to your phone:
    python test_twilio_connection.py +919876543210
Or:
    python test_whatsapp_connection.py +919876543210
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv

# Hot-reload environment variables
load_dotenv(override=True)

from app.comms.twilio_client import (
    comms_client,
    get_meta_credentials,
    get_twilio_credentials,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
)


def test_connection(recipient_phone: str, forced_provider: str = None):
    print("=" * 70)
    print("SafeSlope-NER: WhatsApp Gateway Multi-Provider Live Diagnostic")
    print("=" * 70)

    meta_token, meta_phone_id, meta_verify = get_meta_credentials()
    tw_sid, tw_token, tw_from, tw_sms = get_twilio_credentials()

    print(f"1. Meta WhatsApp Cloud API:")
    print(f"   Token Configured       : {'[YES] ' + meta_token[:12] + '...' if meta_token else '[NO] Not configured'}")
    print(f"   Phone Number ID        : {meta_phone_id if meta_phone_id else '[NO] Not configured'}")
    print(f"   Verify Token           : {meta_verify}")
    print(f"   Meta Live Status       : {'🟢 LIVE ACTIVE' if comms_client.is_meta_live else '⚪ Inactive / Incomplete'}")

    print(f"\n2. Twilio WhatsApp & SMS:")
    print(f"   Account SID            : {tw_sid[:10] + '...' if tw_sid else '[NO] Not configured'}")
    print(f"   Auth Token             : {'*' * 10 if tw_token else '[NO] Not configured'}")
    print(f"   From WhatsApp Number   : {tw_from}")
    print(f"   Twilio Live Status     : {'🟢 LIVE ACTIVE' if comms_client.is_twilio_live else '⚪ Inactive / Incomplete'}")

    active_provider = forced_provider.upper() if forced_provider else comms_client.active_provider
    print(f"\n3. Dispatch Configuration:")
    print(f"   Target Recipient       : {recipient_phone}")
    print(f"   Active Outbound Engine : {active_provider}")
    print("-" * 70)

    if not comms_client.is_live and not forced_provider:
        print("[!] NOTICE: Neither Meta WhatsApp nor Twilio live credentials found in .env.")
        print("    Running in ZERO-CRASH LOCAL SIMULATION MODE.")
        print("    Outbound messages are queued to in-memory history and demo consoles.")
        print("    To send real messages:")
        print("      Option A (Meta Cloud API): add META_WHATSAPP_TOKEN and META_WHATSAPP_PHONE_ID to .env")
        print("      Option B (Twilio): add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to .env")
        print("-" * 70)

    from app.comms.twilio_client import normalize_phone_number
    _, normalized_e164, _ = normalize_phone_number(recipient_phone)

    from app.services.risk_calculator import calculate_complete_risk_profile
    calc = calculate_complete_risk_profile(zone_name="Champhai - Serchhip Corridor (NH-54)")
    iso = calc["isolation_metrics"]

    test_message = (
        "🚨 *SafeSlope-NER Dynamic Geotechnical Alert*\n"
        "Authority: District Disaster Management Authority (DDMA)\n"
        f"Corridor: {calc['zone_name']}\n"
        f"Factor of Safety: {calc['factor_of_safety']:.2f} ({'CRITICAL SHEAR FAILURE' if calc['is_physics_failure'] else 'UNSTABLE SLOPE'})\n"
        f"Evacuation Window: {calc['evacuation_window_hours']} hrs | Impact Radius: {calc['impact_radius_km']} km\n"
        f"Population at Risk: {iso['affected_population']:,} citizens across {iso['isolated_villages']} villages\n"
        f"Road Blockage: {iso['facilities_cut_off'][0]}\n"
        f"Designated Detour: {iso['designated_bypass']}\n"
        f"Gateway: {active_provider} | Dynamic Geotechnical Physics Engine"
    )

    print(f"Dispatching dynamic geotechnical alert to {normalized_e164} via {active_provider}...")
    res = comms_client.send_whatsapp(
        to_phone=normalized_e164,
        body=test_message,
        send_via_api=True,
        preferred_provider=forced_provider,
    )

    print("\nResult:")
    for k, v in res.items():
        if k == "response":
            continue
        print(f"  {k:18}: {v}")
    print("=" * 70)
    return res


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_twilio_connection.py <phone-number> [--meta | --twilio]")
        print("Examples:")
        print("  python test_twilio_connection.py +919436122880")
        print("  python test_twilio_connection.py +919436122880 --meta")
        print("  python test_twilio_connection.py +919436122880 --twilio")
        sys.exit(1)

    phone = sys.argv[1]
    provider_arg = None
    if len(sys.argv) > 2:
        if "--meta" in sys.argv:
            provider_arg = "META"
        elif "--twilio" in sys.argv:
            provider_arg = "TWILIO"

    test_connection(phone, forced_provider=provider_arg)
