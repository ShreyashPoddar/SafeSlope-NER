import os
import sys
import asyncio
import traceback

os.environ["TESTING"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))

def run_tests():
    passed = 0
    failed = 0
    errors = []

    print("======================================================================")
    print("SafeSlope-NER Member 6 Test Suite: Vernacular, CV, CAP, Bot & API")
    print("======================================================================\n")

    # 1. Test Vernacular
    from tests import test_vernacular
    v_tests = [
        test_vernacular.test_supported_languages_coverage,
        test_vernacular.test_translation_keys_across_all_languages,
        test_vernacular.test_universal_visual_icons,
        test_vernacular.test_ivr_scripts,
    ]
    for t in v_tests:
        try:
            t()
            passed += 1
            print(f"  [PASS] vernacular::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] vernacular::{t.__name__}: {e}")

    # 2. Test Classifier
    from tests import test_classifier
    c_tests = [
        test_classifier.test_hazard_classes,
        test_classifier.test_sample_media_classification,
    ]
    for t in c_tests:
        try:
            t()
            passed += 1
            print(f"  [PASS] classifier::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] classifier::{t.__name__}: {e}")

    # 3. Test CAP Engine
    from tests import test_cap_engine
    cap_tests = [
        test_cap_engine.test_cap_alert_creation_and_fields,
        test_cap_engine.test_cap_xml_validity,
        test_cap_engine.test_cap_registry_lifecycle,
    ]
    for t in cap_tests:
        try:
            t()
            passed += 1
            print(f"  [PASS] cap_engine::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] cap_engine::{t.__name__}: {e}")

    # 4. Test Bot Engine (Async)
    from tests import test_bot_engine
    bot_tests = [
        test_bot_engine.test_bot_initial_menu,
        test_bot_engine.test_bot_language_switch,
        test_bot_engine.test_bot_reporting_flow_with_photo_and_location,
        test_bot_engine.test_bot_sos_shortcut,
    ]
    for t in bot_tests:
        try:
            asyncio.run(t())
            passed += 1
            print(f"  [PASS] bot_engine::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] bot_engine::{t.__name__}: {e}")

    # 5. Test API endpoints
    from tests import test_comms_api
    api_tests = [
        test_comms_api.test_root_and_demo_endpoints,
        test_comms_api.test_whatsapp_webhook_twiml,
        test_comms_api.test_verification_queue_workflow,
        test_comms_api.test_cap_alert_endpoints,
        test_comms_api.test_broadcast_trigger,
    ]
    for t in api_tests:
        try:
            t()
            passed += 1
            print(f"  [PASS] comms_api::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] comms_api::{t.__name__}: {e}")

    # 6. Test Telegram Bot Ingestion & Assessment Flow
    from tests import test_telegram_workflow
    tg_tests = [
        test_telegram_workflow.test_telegram_direct_photo_reporting_flow,
    ]
    for t in tg_tests:
        try:
            t()
            passed += 1
            print(f"  [PASS] telegram_workflow::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] telegram_workflow::{t.__name__}: {e}")

    # 7. Test Geospatial Live Feed & Corridor Layers (RFC 7946 GeoJSON)
    from tests import test_geospatial_feed
    geo_tests = [
        test_geospatial_feed.test_geospatial_geojson_endpoint_rfc7946,
        test_geospatial_feed.test_geospatial_geojson_filtering,
        test_geospatial_feed.test_geospatial_corridor_zones,
        test_geospatial_feed.test_geospatial_summary_feed,
    ]
    for t in geo_tests:
        try:
            t()
            passed += 1
            print(f"  [PASS] geospatial_feed::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] geospatial_feed::{t.__name__}: {e}")

    # 8. Test Landslide Algorithm Thresholds & Area Notification Infrastructure
    from tests import test_threshold_and_notifications
    thresh_tests = [
        test_threshold_and_notifications.test_threshold_settings_defaults_and_updates,
        test_threshold_and_notifications.test_determine_risk_level,
        test_threshold_and_notifications.test_area_directory_subscribers,
        test_threshold_and_notifications.test_multi_channel_broadcast_cascade,
        test_threshold_and_notifications.test_api_thresholds_endpoints,
        test_threshold_and_notifications.test_api_subscribers_endpoints,
        test_threshold_and_notifications.test_api_broadcast_trigger_with_notification_settings,
        test_threshold_and_notifications.test_api_algorithm_landslide_risk_ingestion,
    ]
    for t in thresh_tests:
        try:
            t()
            passed += 1
            print(f"  [PASS] threshold_notifications::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] threshold_notifications::{t.__name__}: {e}")

    # 9. Test Dynamic Geotechnical & Spatial Calculations & Live Demo Messaging
    from tests import test_risk_calculations
    calc_tests = [
        test_risk_calculations.test_factor_of_safety_physics,
        test_risk_calculations.test_failure_probability_and_evacuation_window,
        test_risk_calculations.test_spatial_isolation_calculation_no_hardcoding,
        test_risk_calculations.test_complete_risk_profile_generation,
        test_risk_calculations.test_algorithm_ingestion_api_endpoint,
        test_risk_calculations.test_live_demo_status_and_message_endpoints,
    ]
    for t in calc_tests:
        try:
            t()
            passed += 1
            print(f"  [PASS] dynamic_risk_calculations::{t.__name__}")
        except Exception as e:
            failed += 1
            errors.append((t.__name__, traceback.format_exc()))
            print(f"  [FAIL] dynamic_risk_calculations::{t.__name__}: {e}")


    print("\n----------------------------------------------------------------------")
    print(f"Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
    print("----------------------------------------------------------------------")

    if failed > 0:
        print("\nFailures:")
        for name, tb in errors:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
    else:
        print(f"\nALL {passed} TESTS PASSED SUCCESSFULLY! (100% Success Rate)")
        sys.exit(0)

if __name__ == "__main__":
    run_tests()
