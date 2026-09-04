"""
SafeSlope-NER / ResiliNER - WhatsApp Connection Quick Diagnostic
Member 6: Communications & Bot Developer

Run this script to verify WhatsApp credentials and send a live test message to your phone:
    python test_whatsapp_connection.py +919876543210
"""

import sys
from test_twilio_connection import test_connection

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_whatsapp_connection.py <phone-number> [--meta | --twilio]")
        print("Example: python test_whatsapp_connection.py +919436122880")
        sys.exit(1)

    provider_arg = None
    if len(sys.argv) > 2:
        if "--meta" in sys.argv:
            provider_arg = "META"
        elif "--twilio" in sys.argv:
            provider_arg = "TWILIO"

    test_connection(sys.argv[1], forced_provider=provider_arg)
