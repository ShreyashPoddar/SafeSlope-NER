"""
ResiliNER / SafeSlope-NER - Multilingual & Vernacular Adaptation Engine
Member 6: Communications & Bot Developer

Supports 6 primary North East regional languages:
1. Assamese (as) - অসমীয়া
2. Khasi (kha) - Ka Ktien Khasi
3. Mizo (lus) - Mizo ṭawng
4. Manipuri (mni) - ꯃꯩꯇꯩꯂꯣꯟ (Meiteilon)
5. Bengali (bn) - বাংলা
6. English (en) - English

Includes universal visual icons / emoji cues for non-literate accessibility
and audio/IVR script templates for voice-based workflows.
"""

from typing import Any, Dict, Optional

# Supported Language Metadata
SUPPORTED_LANGUAGES = {
    "en": {"code": "en", "name": "English", "native": "English", "flag": "🌐"},
    "as": {"code": "as", "name": "Assamese", "native": "অসমীয়া", "flag": "🇮🇳"},
    "kha": {"code": "kha", "name": "Khasi", "native": "Ka Ktien Khasi", "flag": "⛰️"},
    "lus": {"code": "lus", "name": "Mizo", "native": "Mizo ṭawng", "flag": "🌄"},
    "mni": {"code": "mni", "name": "Manipuri", "native": "ꯃꯩꯇꯩꯂꯣꯟ", "flag": "🌿"},
    "bn": {"code": "bn", "name": "Bengali", "native": "বাংলা", "flag": "🌾"},
}

DEFAULT_LANGUAGE = "en"

# Universal Visual Accessibility Icons
ICONS = {
    "alert": "🚨",
    "warning": "⚠️",
    "rockfall": "🪨",
    "crack": "⚡",
    "landslide": "⛰️",
    "culvert": "🌊",
    "safe": "✅",
    "road": "🛣️",
    "shelter": "⛺",
    "evacuate": "🏃",
    "sos": "🆘",
    "phone": "📞",
    "location": "📍",
    "camera": "📸",
    "volunteer": "🤝",
    "deoc": "🏢",
    "clock": "⏱️",
    "pin": "📌",
}

# Vernacular Translation Dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # -------------------------------------------------------------
    # ENGLISH (en)
    # -------------------------------------------------------------
    "en": {
        "welcome_banner": (
            "🚨 *SafeSlope-NER / ResiliNER Citizen Emergency Network*\n"
            "District Disaster Management Authority (DDMA) & Aapda Mitra System\n"
            "Zero-barrier landslide early warning & community reporting."
        ),
        "menu_prompt": (
            "👋 Welcome to SafeSlope Emergency Assistant.\n\n"
            "Please select an option by replying with a number:\n"
            "1️⃣ 📸 *Report Slope Hazard* (Road Crack, Rockfall, Mudflow)\n"
            "2️⃣ ⛺ *Safe Evacuation Shelters & Routes*\n"
            "3️⃣ 🆘 *Emergency SOS / Call DEOC Control Room*\n"
            "4️⃣ 🌐 *Change Language / Bhasha Bodol*\n\n"
            "⚠️ _If you are in immediate life-threatening danger, call 112 / 1077 immediately._"
        ),
        "lang_select_prompt": (
            "🌐 *Choose your preferred language / ভাষা বাছক / Tawng thlang rawh:*\n\n"
            "1️⃣ English\n"
            "2️⃣ অসমীয়া (Assamese)\n"
            "3️⃣ Ka Ktien Khasi (Khasi)\n"
            "4️⃣ Mizo ṭawng (Mizo)\n"
            "5️⃣ ꯃꯩꯇꯩꯂꯣꯟ (Manipuri)\n"
            "6️⃣ বাংলা (Bengali)\n\n"
            "Reply with 1, 2, 3, 4, 5, or 6."
        ),
        "lang_updated": "✅ Preferred language set to *English*. How can we assist you today?",
        "report_step1_hazard": (
            "📸 *Report a Slope Hazard (Aapda Mitra & Citizen Feed)*\n\n"
            "What type of hazard did you spot? Reply with a number:\n"
            "1️⃣ ⚡ *Road Tension Crack* (Cracks on asphalt / slope edge)\n"
            "2️⃣ 🪨 *Surface Rockfall* (Fallen rocks, boulders on road)\n"
            "3️⃣ ⛰️ *Landslide Scar / Mudflow* (Active mud/debris sliding)\n"
            "4️⃣ 🌊 *Blocked Culvert / Water Surge* (Drainage failure)\n"
            "5️⃣ ❓ *Other Hazardous Movement*"
        ),
        "report_step2_photo": (
            "📸 *Attach a Photo / Media:*\n"
            "Please send or snap a clear photo of the hazard now.\n\n"
            "💡 _Our AI Computer Vision model will automatically analyze the threat level._\n"
            "_(You can also reply 'SKIP' if you don't have a photo.)_"
        ),
        "report_step3_location": (
            "📍 *Share Hazard Location:*\n"
            "Please share your current location pin via WhatsApp:\n"
            "👉 Tap the paperclip/plus icon 📎 ➡️ Location 📍 ➡️ 'Send your current location'\n\n"
            "_(Or reply with the road name / milestone, e.g., 'NH-54 km 34 near Serchhip')_"
        ),
        "report_confirm_title": "✅ *Hazard Report Submitted Successfully!*",
        "report_confirm_body": (
            "📋 *Incident Tracking ID:* `{tracking_id}`\n"
            "🏷️ *AI Classification:* {classification} ({confidence}% confidence)\n"
            "📍 *Location:* {location_str}\n"
            "⏱️ *Timestamp:* {timestamp}\n\n"
            "🛡️ *Human-in-the-Loop Notice:*\n"
            "Your report is now in the District Emergency Operations Center (DEOC) queue. "
            "Our response officers will verify the data before regional broadcast."
        ),
        "shelter_title": "⛺ *Designated Safe Evacuation Shelters & Bypass Routes*",
        "shelter_default": (
            "📍 *Zone: Champhai - Serchhip Corridor (NH-54)*\n\n"
            "1️⃣ 🏫 *Serchhip Community Hall Relief Camp*\n"
            "   Capacity: 450 persons | Medical Staff On Duty | 📍 GPS: 23.3102° N, 92.8524° E\n\n"
            "2️⃣ 🏟️ *Aizawl South Higher Secondary Shelter*\n"
            "   Capacity: 600 persons | Generator Power & Clean Water | 📍 GPS: 23.7271° N, 92.7176° E\n\n"
            "🛣️ *Safe Travel Recommendation:*\n"
            "Avoid NH-54 slope section at km 42 due to high pore pressure readings. "
            "Use Eastern District Bypass Road B-7."
        ),
        "sos_prompt": (
            "🆘 *DISTRICT EMERGENCY OPERATION CENTER (DEOC) CONTACTS*\n\n"
            "📞 *Toll-Free Disaster Helpline:* 1077\n"
            "🚨 *State Emergency Operation Centre (SEOC):* 112\n"
            "🚒 *Fire & Rescue Operations:* 101\n"
            "🚑 *Emergency Medical Ambulance:* 108\n"
            "🤝 *Aapda Mitra Field Coordinator:* +91 94361 22880\n\n"
            "Control Room operators are active 24/7 on VHF Channel 4."
        ),
        "alert_broadcast_high": (
            "🚨 *RED ALERT: HIGH LANDSLIDE RISK DETECTED*\n"
            "Issued by SafeSlope-NER & District Disaster Management Authority\n\n"
            "📍 *Zone:* {zone_name}\n"
            "⚡ *Risk Level:* HIGH (Triggered by {trigger_source})\n"
            "⚠️ *Expected Threat:* Slope destabilization, active tension cracks & debris flow.\n"
            "🏘️ *Isolation Impact:* {isolation_summary}\n"
            "🛣️ *Recommended Action:* Evacuate downhill slopes immediately. Take designated {bypass_route}. Do not travel along slope cuts."
        ),
        "alert_broadcast_moderate": (
            "⚠️ *YELLOW ALERT: MODERATE LANDSLIDE ADVISORY*\n"
            "Issued by SafeSlope-NER Early Warning Network\n\n"
            "📍 *Zone:* {zone_name}\n"
            "🌧️ *Advisory:* Heavy precipitation & soil saturation observed.\n"
            "👀 Maintain vigil on culverts and road cracks. Report any movement using this WhatsApp bot."
        ),
    },

    # -------------------------------------------------------------
    # ASSAMESE (as) - অসমীয়া
    # -------------------------------------------------------------
    "as": {
        "welcome_banner": (
            "🚨 *SafeSlope-NER / ResiliNER নাগৰিক জৰুৰীকালীন সেৱা*\n"
            "জিলা দুৰ্যোগ ব্যৱস্থাপনা কৰ্তৃপক্ষ (DDMA) আৰু আপদা মিত্ৰ ব্যৱস্থা\n"
            "ভূমিস্খলনৰ আগতীয়া সতৰ্কবাণী আৰু সম্প্ৰদায়িক তথ্য প্ৰেৰণ।"
        ),
        "menu_prompt": (
            "👋 SafeSlope জৰুৰীকালীন সহায়কতালৈ স্বাগতম।\n\n"
            "অনুগ্ৰহ কৰি এটা বিকল্প বাছনি কৰিবলৈ নম্বৰ লিখি পঠিয়াওক:\n"
            "1️⃣ 📸 *পাহাৰৰ বিপদৰ প্ৰতিবেদন দিয়ক* (ৰাস্তাৰ ফাঁট, শিল খহি পৰা, মাটি খহনীয়া)\n"
            "2️⃣ ⛺ *সুৰক্ষিত আশ্ৰয়স্থল আৰু পথসমূহ*\n"
            "3️⃣ 🆘 *জৰুৰীকালীন SOS / DEOC কন্ট্ৰোল ৰূমত ফোন কৰক*\n"
            "4️⃣ 🌐 *ভাষা সলনি কৰক / Change Language*\n\n"
            "⚠️ _প্ৰাণৰ তাৎক্ষণিক বিপদ থাকিলে তৎক্ষণাৎ ১১২ / ১০৭৭ নম্বৰত ফোন কৰক।_"
        ),
        "lang_select_prompt": (
            "🌐 *আপোনাৰ পছন্দৰ ভাষা বাছনি কৰক:*\n\n"
            "1️⃣ English\n"
            "2️⃣ অসমীয়া (Assamese)\n"
            "3️⃣ Ka Ktien Khasi (Khasi)\n"
            "4️⃣ Mizo ṭawng (Mizo)\n"
            "5️⃣ ꯃꯩꯇꯩꯂꯣꯟ (Manipuri)\n"
            "6️⃣ বাংলা (Bengali)\n\n"
            "উত্তৰ হিচাপে ১, ২, ৩, ৪, ৫, বা ৬ পঠিয়াওক।"
        ),
        "lang_updated": "✅ ভাষা *অসমীয়া*লৈ নিৰ্ধাৰণ কৰা হ'ল। আমি আপোনাক কেনেকৈ সহায় কৰিব পাৰোঁ?",
        "report_step1_hazard": (
            "📸 *বিপদৰ তথ্য প্ৰেৰণ (আপদা মিত্ৰ আৰু নাগৰিক সেৱা)*\n\n"
            "আপুনি কি ধৰণৰ বিপদ দেখিছে? নম্বৰ লিখি পঠিয়াওক:\n"
            "1️⃣ ⚡ *ৰাস্তাৰ ফাঁট* (ডাঙৰ ফাঁট বা তললৈ বহি যোৱা)\n"
            "2️⃣ 🪨 *শিল খহি পৰা* (পাহাৰৰ পৰা শিল বাগৰি অহা)\n"
            "3️⃣ ⛰️ *ভূমিস্খলন / বোকা খহনীয়া* (সক্ৰিয় মাটি বাগৰি অহা)\n"
            "4️⃣ 🌊 *কালভাৰ্ট বন্ধ / পানী জমা হোৱা* (নলা বন্ধ হোৱা)\n"
            "5️⃣ ❓ *অন্যান্য বিপদজনক চলাচল*"
        ),
        "report_step2_photo": (
            "📸 *এখন ফটো পঠিয়াওক:*\n"
            "অনুগ্ৰহ কৰি বিপদজনক স্থানৰ এখন পৰিষ্কাৰ ফটো এতিয়া পঠিয়াওক।\n\n"
            "💡 _আমাৰ কম্পিউটাৰ ভিজন ব্যৱস্থাই নিজেই ফটোখন পৰীক্ষা কৰিব।_\n"
            "_(ফটো নাথাকিলে 'SKIP' বুলি লিখি পঠিয়াওক)_"
        ),
        "report_step3_location": (
            "📍 *স্থান শ্বেয়াৰ কৰক:*\n"
            "অনুগ্ৰহ কৰি WhatsApp ৰ জৰিয়তে আপোনাৰ বৰ্তমান স্থান পঠিয়াওক:\n"
            "👉 📎 চিহ্ন স্পৰ্শ কৰক ➡️ Location 📍 ➡️ 'Send your current location'\n\n"
            "_(অথবা ৰাস্তাৰ নাম/মাইলষ্টোন লিখি পঠিয়াওক, যেনে: 'NH-54 km 34')_"
        ),
        "report_confirm_title": "✅ *প্ৰতিবেদন সফলভাৱে জমা হ'ল!*",
        "report_confirm_body": (
            "📋 *ট্ৰেকিং নম্বৰ:* `{tracking_id}`\n"
            "🏷️ *AI শ্ৰেণীবিভাজন:* {classification} ({confidence}% সঠিকতা)\n"
            "📍 *স্থান:* {location_str}\n"
            "⏱️ *সময়:* {timestamp}\n\n"
            "🛡️ *প্ৰশাসনীয় তথ্য:*\n"
            "আপোনাৰ প্ৰতিবেদন জিলা দুৰ্যোগ নিয়ন্ত্ৰণ কক্ষত (DEOC) জমা হৈছে। বিষয়াসকলে সত্যাপন কৰাৰ পিছত ব্যৱস্থা গ্ৰহণ কৰা হ'ব।"
        ),
        "shelter_title": "⛺ *নিৰ্ধাৰিত সুৰক্ষিত আশ্ৰয় শিবিৰ আৰু সুৰক্ষিত পথ*",
        "shelter_default": (
            "📍 *এলেকা: চম্ফাই - চাৰ্চিপ কৰিডৰ (NH-54)*\n\n"
            "1️⃣ 🏫 *চাৰ্চিপ কমিউনিটি হল সাহায্য শিবিৰ*\n"
            "   ক্ষমতা: ৪৫০ জন | চিকিৎসা সেৱা মজুত আছে\n\n"
            "2️⃣ 🏟️ *আইজল দক্ষিণ উচ্চতৰ মাধ্যমিক আশ্ৰয়স্থল*\n"
            "   ক্ষমতা: ৬০০ জন | বিদ্যুৎ আৰু বিশুদ্ধ খোৱাপানীৰ সুবিধা\n\n"
            "🛣️ *সুৰক্ষিত যাত্ৰাৰ পৰামৰ্শ:*\n"
            "NH-54 ৰ ৪২ কিমি অংশ এৰাই চলক। পূব বাইপাছ ৰোড ব্যৱহাৰ কৰক।"
        ),
        "sos_prompt": (
            "🆘 *জিলা জৰুৰীকালীন নিয়ন্ত্ৰণ কক্ষ (DEOC) নম্বৰ*\n\n"
            "📞 *টোল-ফ্ৰী দুৰ্যোগ হেল্পলাইন:* ১০৭৭\n"
            "🚨 *ৰাজ্যিক নিয়ন্ত্ৰণ কক্ষ (SEOC):* ১১২\n"
            "🚒 *অগ্নিনিৰ্বাপক বাহিনী:* ১০১\n"
            "🚑 *এম্বুলেন্স সেৱা:* ১০৮\n"
            "🤝 *আপদা মিত্ৰ সমন্বয়ক:* +91 94361 22880\n\n"
            "নিয়ন্ত্ৰণ কক্ষ দিনে-ৰাতি ২৪ ঘণ্টাই সক্ৰিয়।"
        ),
        "alert_broadcast_high": (
            "🚨 *ৰঙা সতৰ্কবাণী: ভূমিস্খলনৰ গভীৰ আশংকা*\n"
            "SafeSlope-NER আৰু জিলা দুৰ্যোগ ব্যৱস্থাপনা কৰ্তৃপক্ষ দ্বাৰা জাৰি\n\n"
            "📍 *এলেকা:* {zone_name}\n"
            "⚡ *বিপদৰ মাত্ৰা:* উচ্চ (ট্ৰিগাৰ: {trigger_source})\n"
            "⚠️ *সম্ভাব্য ক্ষতি:* পাহাৰ খহা আৰু ৰাস্তাৰ ফাঁট বৃদ্ধি।\n"
            "🏘️ *বিচ্ছিন্নতা প্ৰভাৱ:* {isolation_summary}\n"
            "🛣️ *পৰামৰ্শ:* পাহাৰীয়া ঢালৰ পৰা তৎক্ষণাৎ আঁতৰি সুৰক্ষিত {bypass_route} ব্যৱহাৰ কৰক।"
        ),
        "alert_broadcast_moderate": (
            "⚠️ *হালধীয়া সতৰ্কবাণী: ভূমিস্খলনৰ সতৰ্কতা*\n"
            "📍 *এলেকা:* {zone_name}\n"
            "প্ৰচণ্ড বৰষুণৰ বাবে সতৰ্ক থাকক আৰু যিকোনো ফাঁট দেখিলে এই বটত জনাওক।"
        ),
    },

    # -------------------------------------------------------------
    # KHASI (kha) - Ka Ktien Khasi (Meghalaya)
    # -------------------------------------------------------------
    "kha": {
        "welcome_banner": (
            "🚨 *SafeSlope-NER / ResiliNER Ka Jingpyntip Jingma*\n"
            "District Disaster Management Authority (DDMA) bad Aapda Mitra\n"
            "Ka jingpyntip kloi halor ka jyllop bad ka twa khyndew."
        ),
        "menu_prompt": (
            "👋 Khublei! SafeSlope Jingiarap kyrkieh.\n\n"
            "Jied ia kawei na kine da kaba phah da u nombar:\n"
            "1️⃣ 📸 *Pyntip Jingma na ka Twa Khyndew* (Khyndew bthei, Maw twa)\n"
            "2️⃣ ⛺ *Ki Jakashong basa ba Shngain bad ki Lad Surok*\n"
            "3️⃣ 🆘 *Jingiarap Kyrkieh / Phone sha DEOC Control Room*\n"
            "4️⃣ 🌐 *Kylliang Ktien / Change Language*\n\n"
            "⚠️ _Lada don jingma ia ka jingim, phone kloi sha 112 / 1077._"
        ),
        "lang_select_prompt": (
            "🌐 *Jied ia ka Ktien ba kwah:*\n\n"
            "1️⃣ English\n"
            "2️⃣ অসমীয়া (Assamese)\n"
            "3️⃣ Ka Ktien Khasi (Khasi)\n"
            "4️⃣ Mizo ṭawng (Mizo)\n"
            "5️⃣ ꯃꯩꯇꯩꯂꯣꯟ (Manipuri)\n"
            "6️⃣ বাংলা (Bengali)\n\n"
            "Phah 1, 2, 3, 4, 5, lane 6."
        ),
        "lang_updated": "✅ Lah buh ia ka ktien sha ka *Khasi*. Kumno ngi lah ban iarap?",
        "report_step1_hazard": (
            "📸 *Phah Jingpyntip halor ka Jingma:*\n\n"
            "Kiei kiba phi iohi? Phah u nombar:\n"
            "1️⃣ ⚡ *Ka Surok ba pait / bthei*\n"
            "2️⃣ 🪨 *Ki Maw ba twa ha surok*\n"
            "3️⃣ ⛰️ *Ka Khyndew ba twa jur*\n"
            "4️⃣ 🌊 *Ka Mori ba sah khongpong bad duma um*\n"
            "5️⃣ ❓ *Kiwei de ki jingpait bad twa*"
        ),
        "report_step2_photo": (
            "📸 *Phah Dur:*\n"
            "Sngewbha phah ia ka dur ba shai mynta.\n"
            "_(Lada phim don dur, phah 'SKIP')_"
        ),
        "report_step3_location": (
            "📍 *Phah ia ka jaka:*\n"
            "Phah ia ka Location lyngba ka WhatsApp:\n"
            "👉 Pynkhih 📎 ➡️ Location 📍 ➡️ 'Send your current location'"
        ),
        "report_confirm_title": "✅ *Ka Jingpyntip ka lah poi bha!*",
        "report_confirm_body": (
            "📋 *Tracking ID:* `{tracking_id}`\n"
            "🏷️ *AI Classification:* {classification} ({confidence}%)\n"
            "📍 *Jaka:* {location_str}\n\n"
            "🛡️ Ka DEOC kan sa peit bniah shuwa ban pynbna paidbah."
        ),
        "shelter_title": "⛺ *Ki Jakashong Basa ba Shngain*",
        "shelter_default": (
            "1️⃣ 🏫 *Community Hall Relief Shelter*\n"
            "2️⃣ 🏟️ *Higher Secondary School Safe Camp*\n"
            "🛣️ Kiad na ki surok khap lum ba lah ban twa. Pyndonkam da ka bypass."
        ),
        "sos_prompt": (
            "🆘 *NOMBAR JINGIARAP KYRKIEH (DEOC)*\n\n"
            "📞 *Disaster Helpline:* 1077\n"
            "🚨 *Emergency Service:* 112\n"
            "🚑 *Ambulance:* 108\n"
            "🚒 *Ding (Fire):* 101"
        ),
        "alert_broadcast_high": (
            "🚨 *JINGMA BA JUR: KA TWA KHYNDEW!*\n"
            "📍 *Jaka:* {zone_name}\n"
            "⚡ *Risk Level:* HIGH\n"
            "⚠️ Kynriah kloi sha ki jaka ba shngain lyngba ka {bypass_route}."
        ),
        "alert_broadcast_moderate": (
            "⚠️ *JINGMA: SLOPING INSTABILITY*\n"
            "📍 *Jaka:* {zone_name}\n"
            "Peitngor bha halor ki maw ba lah ban twa na ki riat."
        ),
    },

    # -------------------------------------------------------------
    # MIZO (lus) - Mizo ṭawng (Mizoram)
    # -------------------------------------------------------------
    "lus": {
        "welcome_banner": (
            "🚨 *SafeSlope-NER / ResiliNER - Chhiatrup Vengtu Network*\n"
            "District Disaster Management Authority (DDMA) & Aapda Mitra\n"
            "Lirnghing, leimin leh kawngchhia hriattirna rang."
        ),
        "menu_prompt": (
            "👋 Chibai! SafeSlope Chhiatrup Vengtu ah kan lo lawm a che.\n\n"
            "Khawngaihin a hnuaia mi hi thlang rawh (A number chauh hi thawn rawh):\n"
            "1️⃣ 📸 *Leimin / Kawng Khi Report Rawh* (Kawng kak, Lung tla, Leimin)\n"
            "2️⃣ ⛺ *Bihrukna Him (Shelter) & Kawng Him Thlanna*\n"
            "3️⃣ 🆘 *Emergency SOS / DEOC Control Room Bia rawh*\n"
            "4️⃣ 🌐 *Ṭawng Thlakna / Change Language*\n\n"
            "⚠️ _Nunna atana hlauhawm a awm chuan 112 / 1077 ah call nghal rawh._"
        ),
        "lang_select_prompt": (
            "🌐 *I ṭawng hman duh thlang rawh:*\n\n"
            "1️⃣ English\n"
            "2️⃣ অসমীয়া (Assamese)\n"
            "3️⃣ Ka Ktien Khasi (Khasi)\n"
            "4️⃣ Mizo ṭawng (Mizo)\n"
            "5️⃣ ꯃꯩꯇꯩꯂꯣꯟ (Manipuri)\n"
            "6️⃣ বাংলা (Bengali)\n\n"
            "1, 2, 3, 4, 5, emaw 6 thawn rawh."
        ),
        "lang_updated": "✅ I ṭawng thlan chu *Mizo ṭawng* a ni e. Engtin nge kan puih theih ang che?",
        "report_step1_hazard": (
            "📸 *Hlauhawm Thleng Report Rawh (Aapda Mitra & Mipui Feed)*\n\n"
            "Eng ang hlauhawm nge i hmuh? A number chauh thawn rawh:\n"
            "1️⃣ ⚡ *Kawngpui Khi / Kak* (Tension Crack)\n"
            "2️⃣ 🪨 *Lung Tla / Lung Lum* (Rockfall)\n"
            "3️⃣ ⛰️ *Leimin / Chirh Tla* (Mudflow / Landslide)\n"
            "4️⃣ 🌊 *Tui Luankawr Ping / Tuilian* (Blocked Culvert)\n"
            "5️⃣ ❓ *Hlauhawm Dang*"
        ),
        "report_step2_photo": (
            "📸 *Thlalak Thawn Rawh:*\n"
            "Khawngaihin thil awmdan thlalak fiah tawk thawn rawh le.\n\n"
            "💡 _Kan AI Computer Vision model hian thlalak aṭangin a hlauhawm dan a chhut nghal ang._\n"
            "_(Thlalak i neih loh chuan 'SKIP' tiin chhang rawh)_"
        ),
        "report_step3_location": (
            "📍 *Hmun Awmna (Location) Thawn Rawh:*\n"
            "WhatsApp aṭangin i awmna location rawn share rawh le:\n"
            "👉 📎 icon hmet la ➡️ Location 📍 ➡️ 'Send your current location'\n\n"
            "_(A nih loh pawhin hmun hming/milepost ziak rawh, e.g. 'NH-54 km 34 Serchhip bul')_"
        ),
        "report_confirm_title": "✅ *Report Hlawhtling Takin A Lut E!*",
        "report_confirm_body": (
            "📋 *Tracking ID:* `{tracking_id}`\n"
            "🏷️ *AI Finfiahna:* {classification} ({confidence}% chiang)\n"
            "📍 *A Hmun:* {location_str}\n"
            "⏱️ *Huna:* {timestamp}\n\n"
            "🛡️ *DEOC Hriattirna:*\n"
            "I report hi DEOC Control Room ah a lut nghal a, official ten an finfiah hnuah midangte hriattirna chhuah a ni ang."
        ),
        "shelter_title": "⛺ *Chhiatrup Tawh Thut a Bihrukna Him & Kawng Him*",
        "shelter_default": (
            "📍 *Zone: Champhai - Serchhip Corridor (NH-54)*\n\n"
            "1️⃣ 🏫 *Serchhip Community Hall Relief Camp*\n"
            "   Mihring leng: 450 | Doctor leh Nurse an awm e | 📍 GPS: 23.3102° N, 92.8524° E\n\n"
            "2️⃣ 🏟️ *Aizawl South Higher Secondary Shelter*\n"
            "   Mihring leng: 600 | Generator leh tui thianghlim a awm | 📍 GPS: 23.7271° N, 92.7176° E\n\n"
            "🛣️ *Kawng Him Zawh Tur:*\n"
            "NH-54 km 42 leimin vanga kawng ping lakah inveng rawh. Chhimchhak Bypass B-7 zawh ang che."
        ),
        "sos_prompt": (
            "🆘 *DISTRICT EMERGENCY OPERATION CENTER (DEOC) BIAKPAWRNA*\n\n"
            "📞 *Chhiatrup Helpline (Toll-Free):* 1077\n"
            "🚨 *Police / Emergency SEOC:* 112\n"
            "🚒 *Mei Chhehlap (Fire):* 101\n"
            "🚑 *Ambulance (Damdawi In):* 108\n"
            "🤝 *Aapda Mitra Coordinator:* +91 94361 22880\n\n"
            "Control Room hi chhun leh zan 24/7 hawn a ni."
        ),
        "alert_broadcast_high": (
            "🚨 *RED ALERT: LEIMIN HLAUHAWM CHHUAH A NI*\n"
            "SafeSlope-NER leh District Disaster Management Authority hriattirna\n\n"
            "📍 *Zone:* {zone_name}\n"
            "⚡ *Hlauhawm San Lam:* HIGH ({trigger_source} aṭanga hmuh)\n"
            "⚠️ *Thil Thleng Thei:* Leimin thut thei, kawng pait leh lung lum.\n"
            "🏘️ *Khaw Tuam Bikin:* {isolation_summary}\n"
            "🛣️ *Tih Tur:* Khua leh in hniam aṭangin chhuak nghal rawh. {bypass_route} kawng zawh ang che."
        ),
        "alert_broadcast_moderate": (
            "⚠️ *YELLOW ALERT: LEIMIN HLAUHAWM HRIATTIRNA*\n"
            "Ruah a sur nasat avangin lei a dup hle. Kawngpui khi leh lung lum lakah fimkhur ang che."
        ),
    },

    # -------------------------------------------------------------
    # MANIPURI (mni) - ꯃꯩꯇꯩꯂꯣꯟ / Meiteilon
    # -------------------------------------------------------------
    "mni": {
        "welcome_banner": (
            "🚨 *SafeSlope-NER / ResiliNER - ꯈꯨꯗꯣꯡꯊꯤꯕ ꯊꯣꯛꯄꯗ ꯀꯟꯅꯕ ꯅꯦꯠꯋꯥꯔꯛ*\n"
            "District Disaster Management Authority (DDMA) & Aapda Mitra\n"
            "ꯆꯤꯡ ꯇꯨꯕ, ꯂꯝꯕꯤ ꯇꯦꯛꯄꯒꯤ ꯃꯃꯥꯡꯗ ꯈꯪꯍꯟꯕ ꯄꯥꯎ।"
        ),
        "menu_prompt": (
            "👋 SafeSlope Emergency Assistant ꯗ ꯇꯔꯥꯝꯅ ꯑꯣꯛꯆꯔꯤ।\n\n"
            "ꯃꯈꯥꯒꯤ ꯑꯣꯞꯁꯟꯁꯤꯡꯁꯤꯗꯒꯤ ꯅꯝꯕꯔ ꯊꯥꯕꯤꯌꯨ:\n"
            "1️⃣ 📸 *ꯈꯨꯗꯣꯡꯊꯤꯕ ꯊꯣꯛꯂꯛꯄ ꯔꯤꯄꯣꯔ꯭ꯠ ꯇꯧꯕꯤꯌꯨ* (ꯂꯝꯕꯤ ꯀꯥꯏꯕ, ꯅꯨꯡ ꯇꯥꯕ, ꯂꯩ ꯇꯨꯕ)\n"
            "2️⃣ ⛺ *ꯁꯦꯐ ꯁꯦꯜꯇꯔ ꯑꯃꯁꯨꯡ ꯁꯦꯐ ꯔꯨꯠꯁꯤꯡ*\n"
            "3️⃣ 🆘 *Emergency SOS / DEOC ꯀꯟꯠꯔꯣꯜ ꯔꯨꯃꯗ ꯀꯣꯜ ꯇꯧꯕ*\n"
            "4️⃣ 🌐 *ꯂꯣꯟ ꯍꯣꯡꯗꯣꯛꯄ / Change Language*\n\n"
            "⚠️ _ꯄꯨꯟꯁꯤꯒꯤ ꯑꯀꯟꯕ ꯈꯨꯗꯣꯡꯊꯤꯕ ꯑꯣꯏꯔꯕꯗꯤ ꯈꯨꯗꯛꯇ 112 / 1077 ꯗ ꯀꯣꯜ ꯇꯧꯕꯤꯌꯨ।_"
        ),
        "lang_select_prompt": (
            "🌐 *ꯅꯍꯥꯛꯅ ꯄꯥꯝꯕ ꯂꯣꯟ ꯈꯟꯕꯤꯌꯨ:*\n\n"
            "1️⃣ English\n"
            "2️⃣ অসমীয়া (Assamese)\n"
            "3️⃣ Ka Ktien Khasi (Khasi)\n"
            "4️⃣ Mizo ṭawng (Mizo)\n"
            "5️⃣ ꯃꯩꯇꯩꯂꯣꯟ (Manipuri)\n"
            "6️⃣ বাংলা (Bengali)\n\n"
            "1, 2, 3, 4, 5, ꯅꯠꯇ꯭ꯔꯒ 6 ꯊꯥꯕꯤꯌꯨ।"
        ),
        "lang_updated": "✅ ꯂꯣꯟ *ꯃꯩꯇꯩꯂꯣꯟ* ꯑꯣꯏꯅ ꯂꯦꯞꯂꯦ। ꯀꯔꯤ ꯃꯇꯦꯡ ꯄꯥꯡꯕ ꯌꯥꯒꯅꯤ?",
        "report_step1_hazard": (
            "📸 *ꯈꯨꯗꯣꯡꯊꯤꯕ ꯔꯤꯄꯣꯔ꯭ꯠ (Aapda Mitra & Citizen Feed)*\n\n"
            "ꯀꯔꯤ ꯃꯈꯜꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕ ꯎꯕꯤꯕꯒꯦ? ꯅꯝꯕꯔ ꯊꯥꯕꯤꯌꯨ:\n"
            "1️⃣ ⚡ *ꯂꯝꯕꯤ ꯀꯥꯏꯕ / ꯆꯦꯠꯄ* (Road Crack)\n"
            "2️⃣ 🪨 *ꯅꯨꯡ ꯇꯨꯕ / ꯅꯨꯡ ꯇꯥꯕ* (Rockfall)\n"
            "3️⃣ ⛰️ *ꯂꯩ ꯇꯨꯕ / ꯂꯩ ꯍꯨꯡꯕ* (Landslide)\n"
            "4️⃣ 🌊 *ꯗ꯭ꯔꯦꯟ ꯊꯤꯡꯕ / ꯏꯁꯤꯡ ꯏꯆꯥꯎ* (Blocked Culvert)\n"
            "5️⃣ ❓ *ꯑꯇꯣꯞꯄ ꯈꯨꯗꯣꯡꯊꯤꯕ*"
        ),
        "report_step2_photo": (
            "📸 *ꯐꯣꯇꯣ ꯊꯥꯕꯤꯌꯨ:*\n"
            "ꯆꯥꯅꯕꯤꯗꯨꯅ ꯍꯧꯖꯤꯛ ꯃꯌꯦꯛ ꯁꯦꯡꯕ ꯐꯣꯇꯣ ꯑꯃ ꯊꯥꯕꯤꯌꯨ।\n"
            "_(ꯐꯣꯇꯣ ꯂꯩꯇ꯭ꯔꯕꯗꯤ 'SKIP' ꯍꯥꯏꯅ ꯊꯥꯕꯤꯌꯨ)_"
        ),
        "report_step3_location": (
            "📍 *ꯂꯣꯀꯦꯁꯟ ꯄꯤꯕꯤꯌꯨ:*\n"
            "WhatsApp ꯒꯤ Location share ꯇꯧꯕꯤꯌꯨ:\n"
            "👉 📎 ꯅꯝꯕꯤꯌꯨ ➡️ Location 📍 ➡️ 'Send your current location'"
        ),
        "report_confirm_title": "✅ *ꯔꯤꯄꯣꯔ꯭ꯠ ꯃꯥꯌꯄꯥꯛꯅ ꯂꯧꯁꯤꯟꯈ꯭ꯔꯦ!*",
        "report_confirm_body": (
            "📋 *Tracking ID:* `{tracking_id}`\n"
            "🏷️ *AI ꯀ꯭ꯂꯥꯁꯤꯐꯤꯀꯦꯁꯟ:* {classification} ({confidence}%)\n"
            "📍 *ꯃꯐꯝ:* {location_str}\n\n"
            "🛡️ ꯗꯤꯁꯇ꯭ꯔꯤꯛ ꯀꯟꯠꯔꯣꯜ ꯔꯨꯃꯗ ꯌꯧꯈ꯭ꯔꯦ ꯑꯃꯁꯨꯡ ꯑꯣꯐꯤꯁꯥꯔꯁꯤꯡꯅ ꯌꯦꯡꯁꯤꯟꯒꯅꯤ।"
        ),
        "shelter_title": "⛺ *ꯁꯦꯐ ꯁꯦꯜꯇꯔ ꯑꯃꯁꯨꯡ ꯂꯝꯕꯤꯁꯤꯡ*",
        "shelter_default": (
            "1️⃣ 🏫 *Community Hall Relief Shelter*\n"
            "2️⃣ 🏟️ *Govt Higher Secondary Shelter Camp*\n"
            "🛣️ NH-54 ꯒꯤ ꯂꯩ ꯇꯨꯕ ꯃꯐꯝꯁꯤꯡ ꯊꯤꯡꯗꯨꯅ ꯕꯥꯏꯄꯥꯁ ꯂꯝꯕꯤ ꯁꯤꯖꯤꯟꯅꯕꯤꯌꯨ।"
        ),
        "sos_prompt": (
            "🆘 *DEOC EMERGENCY CONTACTS*\n\n"
            "📞 *Disaster Helpline:* 1077\n"
            "🚨 *Emergency Service:* 112\n"
            "🚑 *Ambulance:* 108\n"
            "🚒 *Fire Service:* 101"
        ),
        "alert_broadcast_high": (
            "🚨 *RED ALERT: ꯆꯤꯡ ꯇꯨꯕꯒꯤ ꯑꯀꯟꯕ ꯈꯨꯗꯣꯡꯊꯤꯕ!*\n"
            "📍 *Zone:* {zone_name}\n"
            "⚡ *Risk Level:* HIGH\n"
            "⚠️ ꯈꯨꯗꯛꯇ ꯁꯦꯐ ꯑꯣꯏꯕ ꯃꯐꯝꯗ ꯆꯠꯈꯤꯕꯤꯌꯨ ꯑꯃꯁꯨꯡ {bypass_route} ꯂꯝꯕꯤ ꯁꯤꯖꯤꯟꯅꯕꯤꯌꯨ।"
        ),
        "alert_broadcast_moderate": (
            "⚠️ *MODERATE LANDSLIDE ADVISORY*\n"
            "📍 *Zone:* {zone_name}\n"
            "ꯅꯣꯡ ꯀꯟꯅ ꯆꯨꯕꯅ ꯃꯔꯝ ꯑꯣꯏꯗꯨꯅ ꯂꯝꯕꯤꯗ ꯆꯠꯊꯣꯛ-ꯆꯠꯁꯤꯟ ꯇꯧꯕꯗ ꯆꯦꯛꯁꯤꯟꯕꯤꯌꯨ।"
        ),
    },

    # -------------------------------------------------------------
    # BENGALI (bn) - বাংলা
    # -------------------------------------------------------------
    "bn": {
        "welcome_banner": (
            "🚨 *SafeSlope-NER / ResiliNER নাগরিক জরুরি পরিষেবা*\n"
            "জেলা দুর্যোগ ব্যবস্থাপনা কর্তৃপক্ষ (DDMA) ও আপদা মিত্র নেটওয়ার্ক\n"
            "ভূমিধসের আগাম সতর্কতা এবং তাৎক্ষণিক মাঠপর্যায়ের তথ্য প্রদান।"
        ),
        "menu_prompt": (
            "👋 SafeSlope জরুরি সহায়তায় আপনাকে স্বাগত।\n\n"
            "অনুগ্রহ করে একটি বিকল্প নির্বাচন করতে নম্বর লিখে পাঠান:\n"
            "1️⃣ 📸 *পাহাড়ের বিপদের তথ্য দিন* (রাস্তায় ফাটল, পাথর ধস, মাটি ধস)\n"
            "2️⃣ ⛺ *নিরাপদ আশ্রয়কেন্দ্র ও সুরক্ষিত পথ*\n"
            "3️⃣ 🆘 *জরুরি SOS / জেলা DEOC কন্ট্রোল রুমে কল করুন*\n"
            "4️⃣ 🌐 *ভাষা পরিবর্তন করুন / Change Language*\n\n"
            "⚠️ _জীবনের সরাসরি ঝুঁকি থাকলে অবিলম্বে ১১২ / ১০৭৭ নম্বরে কল করুন।_"
        ),
        "lang_select_prompt": (
            "🌐 *আপনার পছন্দের ভাষা বেছে নিন:*\n\n"
            "1️⃣ English\n"
            "2️⃣ অসমীয়া (Assamese)\n"
            "3️⃣ Ka Ktien Khasi (Khasi)\n"
            "4️⃣ Mizo ṭawng (Mizo)\n"
            "5️⃣ ꯃꯩꯇꯩꯂꯣꯟ (Manipuri)\n"
            "6️⃣ বাংলা (Bengali)\n\n"
            "উত্তর হিসেবে ১, ২, ৩, ৪, ৫, বা ৬ পাঠান।"
        ),
        "lang_updated": "✅ ভাষা *বাংলা*য় সেট করা হয়েছে। কীভাবে আপনাকে সাহায্য করতে পারি?",
        "report_step1_hazard": (
            "📸 *বিপদের তথ্য প্রেরণ (আপদা মিত্র ও নাগরিক পরিষেবা)*\n\n"
            "আপনি কী ধরনের বিপদ দেখেছেন? নম্বর লিখে পাঠান:\n"
            "1️⃣ ⚡ *রাস্তায় ফাটল* (পিচে চওড়া ফাটল / দেবে যাওয়া)\n"
            "2️⃣ 🪨 *পাথর ধস* (পাহাড় থেকে পাথর গড়িয়ে পড়া)\n"
            "3️⃣ ⛰️ *ভূমিধস / কাদা ধস* (সক্রিয় মাটি নেমে আসা)\n"
            "4️⃣ 🌊 *কালভার্ট বন্ধ / জলমগ্নতা* (নিকাশি বন্ধ হওয়া)\n"
            "5️⃣ ❓ *অন্যান্য বিপদজনক পরিস্থিতি*"
        ),
        "report_step2_photo": (
            "📸 *একটি ছবি পাঠান:*\n"
            "অনুগ্রহ করে বিপদজনক স্থানের একটি পরিষ্কার ছবি তুলুন বা পাঠান।\n\n"
            "💡 _আমাদের AI কম্পিউটার ভিশন মডেল স্বয়ংক্রিয়ভাবে বিপদের মাত্রা যাচাই করবে।_\n"
            "_(ছবি না থাকলে 'SKIP' লিখে পাঠান)_"
        ),
        "report_step3_location": (
            "📍 *আপনার অবস্থান জানান:*\n"
            "অনুগ্রহ করে WhatsApp-এর মাধ্যমে আপনার বর্তমান লোকেশন পাঠান:\n"
            "👉 📎 চিহ্ন স্পর্শ করুন ➡️ Location 📍 ➡️ 'Send your current location'\n\n"
            "_(বা রাস্তার নাম/মাইলফলক লিখে পাঠান, যেমন: 'NH-54 km 34')_"
        ),
        "report_confirm_title": "✅ *রিপোর্ট সফলভাবে জমা হয়েছে!*",
        "report_confirm_body": (
            "📋 *ট্র্যাকিং আইডি:* `{tracking_id}`\n"
            "🏷️ *AI শ্রেণিবিন্যাস:* {classification} ({confidence}% নিশ্চিত)\n"
            "📍 *অবস্থান:* {location_str}\n"
            "⏱️ *সময়:* {timestamp}\n\n"
            "🛡️ *প্রশাসনিক তথ্য:*\n"
            "আপনার তথ্যটি জেলা দুর্যোগ কন্ট্রোল রুমে (DEOC) পাঠানো হয়েছে। অফিসারদের পর্যালোচনার পর সার্বজনীন পদক্ষেপ নেওয়া হবে।"
        ),
        "shelter_title": "⛺ *নির্ধারিত নিরাপদ আশ্রয় শিবির ও বিকল্প পথ*",
        "shelter_default": (
            "📍 *এলাকা: চম্পাই - সারছিপ করিডোর (NH-54)*\n\n"
            "1️⃣ 🏫 *সারছিপ কমিউনিটি হল ত্রাণ শিবির*\n"
            "   ধারণক্ষমতা: ৪৫০ জন | চিকিৎসা কর্মী উপস্থিত আছেন\n\n"
            "2️⃣ 🏟️ *আইজল সাউথ হায়ার সেকেন্ডারি স্কুল আশ্রয়কেন্দ্র*\n"
            "   ধারণক্ষমতা: ৬০০ জন | জেনারেটর ও পানীয় জলের ব্যবস্থা\n\n"
            "🛣️ *নিরাপদ যাত্রার পরামর্শ:*\n"
            "NH-54 এর ৪২ কিমি অংশ এড়িয়ে চলুন। পূর্ব বাইপাস রুট B-7 ব্যবহার করুন।"
        ),
        "sos_prompt": (
            "🆘 *জেলা দুর্যোগ ব্যবস্থাপনা কন্ট্রোল রুম (DEOC)*\n\n"
            "📞 *টোল-ফ্রি দুর্যোগ হেল্পলাইন:* ১০৭৭\n"
            "🚨 *জরুরি পরিষেবা (SEOC):* ১১২\n"
            "🚒 *দমকল বাহিনী (Fire):* ১০১\n"
            "🚑 *অ্যাম্বুলেন্স:* ১০৮\n"
            "🤝 *আপদা মিত্র সমন্বয়কারী:* +91 94361 22880\n\n"
            "কন্ট্রোল রুম ২৪ ঘণ্টা সচল রয়েছে।"
        ),
        "alert_broadcast_high": (
            "🚨 *রেড অ্যালার্ট: ভয়াবহ ভূমিধসের আশঙ্কা*\n"
            "SafeSlope-NER এবং জেলা দুর্যোগ ব্যবস্থাপনা কর্তৃপক্ষ দ্বারা প্রচারিত\n\n"
            "📍 *এলাকা:* {zone_name}\n"
            "⚡ *ঝুঁকির মাত্রা:* উচ্চ ({trigger_source} দ্বারা সনাক্ত)\n"
            "⚠️ *সম্ভাব্য বিপদ:* পাহাড় ধস, সক্রিয় ফাটল এবং যোগাযোগ বিচ্ছিন্নতা।\n"
            "🏘️ *বিচ্ছিন্নতার প্রভাব:* {isolation_summary}\n"
            "🛣️ *করণীয়:* অবিলম্বে ঝুঁকিপূর্ণ ঢাল ছেড়ে নিরাপদ স্থানে যান। {bypass_route} বিকল্প সড়ক ব্যবহার করুন।"
        ),
        "alert_broadcast_moderate": (
            "⚠️ *হলুদ সতর্কতা: মধ্যম স্তরের ভূমিধস সতর্কতা*\n"
            "📍 *এলাকা:* {zone_name}\n"
            "ভারী বৃষ্টির কারণে রাস্তাঘাটে চলাচলে সতর্ক থাকুন। যে কোনো ফাটল দেখলে এই নম্বরে রিপোর্ট করুন।"
        ),
    },
}

# IVR / Voice Prompt Script Templates (for Interactive Voice Response)
IVR_SCRIPTS: Dict[str, Dict[str, str]] = {
    "en": {
        "intro": "Welcome to SafeSlope Landslide Early Warning. Press 1 to report an active road crack or rockfall. Press 2 for safe evacuation shelters. Press 3 for emergency rescue.",
        "evac": "Emergency evacuation advisory. NH-54 is at risk. Please proceed to the designated eastern bypass shelter.",
        "sos": "Connecting to District Emergency Operation Center on helpline 1077.",
    },
    "lus": {
        "intro": "SafeSlope Chhiatrup Vengtu ah kan lo lawm a che. Leimin leh kawng kak report turin 1 hmet rawh. Bihrukna him zawng turin 2 hmet rawh. Emergency tan 3 hmet rawh.",
        "evac": "Fimkhur rawh le. NH-54 kawng a hlauhawm avangin Chhimchhak Bypass zawh ang che.",
        "sos": "DEOC Control Room 1077 ah kan thlunzawm mek a che.",
    },
    "as": {
        "intro": "SafeSlope জৰুৰীকালীন সেৱালৈ স্বাগতম। ৰাস্তাৰ ফাঁট বা শিল খহি পৰাৰ তথ্য দিবলৈ ১ টিপক। আশ্ৰয় শিবিৰৰ বাবে ২ টিপক। জৰুৰী সাহায্যৰ বাবে ৩ টিপক।",
        "evac": "সতৰ্কবাণী। NH-54 ৰ বিপদাশংকা আছে। সুৰক্ষিত পূব বাইপাছ পথ ব্যৱহাৰ কৰক।",
        "sos": "জিলা দুৰ্যোগ কন্ট্ৰোল ৰূম ১০৭৭ লৈ সংযোগ কৰা হৈছে।",
    },
}


def get_text(key: str, lang: str = "en", **kwargs: Any) -> str:
    """Retrieve a localized template string and format it with kwargs."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE])
    template = lang_dict.get(key)
    if not template:
        template = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, f"[{key}]")
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def get_ivr_script(key: str, lang: str = "en") -> str:
    """Retrieve IVR voice script in target language with English fallback."""
    ivr_dict = IVR_SCRIPTS.get(lang, IVR_SCRIPTS["en"])
    return ivr_dict.get(key, IVR_SCRIPTS["en"].get(key, ""))
