"""
ResiliNER / SafeSlope-NER - Comms & Bot Package
Member 6: Communications & Bot Developer
"""

from app.comms.vernacular import get_text, get_ivr_script, SUPPORTED_LANGUAGES
from app.comms.classifier import classify_field_photo, classifier
from app.comms.cap_engine import CAPAlert, cap_registry
from app.comms.twilio_client import comms_client
from app.comms.queue_service import queue_service
from app.comms.bot_engine import bot_engine
from app.comms.dispatcher import alert_dispatcher
from app.comms.event_stream import broadcaster
