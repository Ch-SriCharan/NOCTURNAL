import subprocess
import sys
import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()  # loads .env → OPENAI_API_KEY

app = Flask(__name__)
app.secret_key = "medfollow_ai_secret_2024"
CORS(app)  # allow the static SPA to call our API routes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSES_FILE = os.path.join(BASE_DIR, "responses.txt")


# ─────────────────────────────────────────────
#  Translation Dictionaries
# ─────────────────────────────────────────────

TRANSLATIONS = {
    "English": {
        # Patient Page
        "patient_title":        "Patient Details",
        "patient_sub":          "Enter your information to begin the care session",
        "patient_name_label":   "Patient Name",
        "patient_name_ph":      "e.g. Priya Sharma",
        "surgery_label":        "Surgery / Procedure Type",
        "surgery_optional":     "(optional)",
        "surgery_hint":         "This helps personalize your care recommendations.",
        "continue_btn":         "Continue →",
        "saving_btn":           "Saving…",
        "surgery_options": [
            ("", "— Not applicable / General care —"),
            ("Appendectomy", "Appendectomy"),
            ("Cardiac Surgery", "Cardiac Surgery"),
            ("Knee Replacement", "Knee Replacement"),
            ("Hip Replacement", "Hip Replacement"),
            ("Spinal Surgery", "Spinal Surgery"),
            ("Cholecystectomy", "Cholecystectomy (Gallbladder)"),
            ("Hernia Repair", "Hernia Repair"),
            ("Cataract Surgery", "Cataract Surgery"),
            ("Hysterectomy", "Hysterectomy"),
            ("Caesarean Section", "Caesarean Section (C-Section)"),
            ("Tonsillectomy", "Tonsillectomy"),
            ("Other", "Other"),
        ],
        # Service Page
        "service_title":        "Care Services",
        "service_sub":          "Choose the type of care you need today",
        "service_welcome":      "Welcome back — select your care type below",
        "regular_care":         "Regular Care",
        "regular_care_desc":    "General health consultation, symptom discussion, and medication guidance for routine follow-ups.",
        "regular_badge":        "Routine Follow-Up",
        "postop_care":          "Post-Op Care",
        "postop_care_desc":     "Specialized guidance for post-surgical recovery — wound care, vitals monitoring, and complication screening.",
        "postop_badge":         "Post-Surgery",
        "health_overview":      "Health Overview",
        "health_overview_desc": "Enter your vitals — temperature, blood pressure, heart rate, and more — for an AI health summary.",
        "health_badge":         "Vitals Analysis",
        "appointments":         "Appointments",
        "appointments_desc":    "Book a doctor consultation or follow-up visit at your preferred date and time.",
        "appt_badge":           "Schedule Visit",
        # Chat Page
        "chat_topbar_title":    "MedFollow AI Assistant",
        "ai_greeting":          "Hello, {name}! 👋 I'm your AI health assistant. Tell me about any symptoms or concerns you're experiencing today, and I'll provide personalized guidance. How can I help you?",
        "call_label":           "Follow-Up Call",
        "call_sub":             "Launch automated IVR check-in for {name}",
        "start_call_btn":       "📞 Start Call",
        "calling_btn":          "⏳ Calling…",
        "chat_placeholder":     "Describe your symptoms…",
        # Health Page
        "health_title":         "Health Overview",
        "health_sub":           "Enter your vitals for {name} — our AI will analyze them",
        "temp_label":           "Temperature",
        "temp_norm":            "Normal: 97–99°F",
        "bp_label":             "Blood Pressure",
        "bp_norm":              "Normal: 90–120/60–80 mmHg",
        "hr_label":             "Heart Rate",
        "hr_norm":              "Normal: 60–100 bpm",
        "sugar_label":          "Blood Sugar",
        "sugar_norm":           "Normal: 70–140 mg/dL",
        "spo2_label":           "Oxygen Level (SpO₂)",
        "spo2_norm":            "Normal: 95–100%",
        "analyze_btn":          "🔍 Analyze My Health",
        "analyzing_btn":        "⏳ Analyzing…",
        "ai_summary_title":     "AI Health Summary",
        "back_services":        "Back to Services",
        # Appointments Page
        "appt_title":           "Book Appointment",
        "appt_sub":             "Schedule a consultation for {name}",
        "doctor_label":         "Doctor / Specialist",
        "doctor_ph":            "— Select a doctor —",
        "date_label":           "Date",
        "time_label":           "Time",
        "time_ph":              "— Select —",
        "reason_label":         "Reason for Visit",
        "reason_ph":            "e.g. Post-op follow-up, fever since 3 days, blood pressure check…",
        "confirm_btn":          "📅 Confirm Appointment",
        "booking_btn":          "Booking…",
        "success_title":        "Appointment Confirmed!",
        "back_btn":             "← Back to Services",
        "upcoming_title":       "📋 Upcoming Appointments",
    },

    "Hindi": {
        # Patient Page
        "patient_title":        "रोगी विवरण",
        "patient_sub":          "देखभाल सत्र शुरू करने के लिए अपनी जानकारी दर्ज करें",
        "patient_name_label":   "रोगी का नाम",
        "patient_name_ph":      "उदा. प्रिया शर्मा",
        "surgery_label":        "ऑपरेशन / प्रक्रिया का प्रकार",
        "surgery_optional":     "(वैकल्पिक)",
        "surgery_hint":         "यह आपकी देखभाल सिफारिशों को व्यक्तिगत बनाने में मदद करता है।",
        "continue_btn":         "जारी रखें →",
        "saving_btn":           "सहेज रहे हैं…",
        "surgery_options": [
            ("", "— लागू नहीं / सामान्य देखभाल —"),
            ("Appendectomy", "अपेंडिक्टोमी"),
            ("Cardiac Surgery", "हृदय शल्य चिकित्सा"),
            ("Knee Replacement", "घुटना प्रतिस्थापन"),
            ("Hip Replacement", "कूल्हा प्रतिस्थापन"),
            ("Spinal Surgery", "रीढ़ की सर्जरी"),
            ("Cholecystectomy", "कोलेसिस्टेक्टोमी (पित्ताशय)"),
            ("Hernia Repair", "हर्निया मरम्मत"),
            ("Cataract Surgery", "मोतियाबिंद सर्जरी"),
            ("Hysterectomy", "गर्भाशय उच्छेदन"),
            ("Caesarean Section", "सिजेरियन सेक्शन"),
            ("Tonsillectomy", "टॉन्सिलेक्टोमी"),
            ("Other", "अन्य"),
        ],
        # Service Page
        "service_title":        "देखभाल सेवाएं",
        "service_sub":          "आज आपको किस प्रकार की देखभाल की आवश्यकता है चुनें",
        "service_welcome":      "वापस स्वागत है — नीचे अपना देखभाल प्रकार चुनें",
        "regular_care":         "नियमित देखभाल",
        "regular_care_desc":    "नियमित अनुवर्ती के लिए सामान्य स्वास्थ्य परामर्श, लक्षण चर्चा और दवा मार्गदर्शन।",
        "regular_badge":        "नियमित अनुवर्ती",
        "postop_care":          "ऑपरेशन के बाद देखभाल",
        "postop_care_desc":     "पोस्ट-सर्जिकल रिकवरी के लिए विशेष मार्गदर्शन — घाव की देखभाल, जीवन संकेत निगरानी।",
        "postop_badge":         "पश्चात की देखभाल",
        "health_overview":      "स्वास्थ्य अवलोकन",
        "health_overview_desc": "AI स्वास्थ्य सारांश के लिए अपने जीवन संकेत दर्ज करें — तापमान, रक्तचाप, हृदय गति आदि।",
        "health_badge":         "जीवन संकेत विश्लेषण",
        "appointments":         "नियुक्तियां",
        "appointments_desc":    "अपनी पसंदीदा तारीख और समय पर डॉक्टर से परामर्श बुक करें।",
        "appt_badge":           "परामर्श बुक करें",
        # Chat Page
        "chat_topbar_title":    "MedFollow AI सहायक",
        "ai_greeting":          "नमस्ते, {name}! 👋 मैं आपका AI स्वास्थ्य सहायक हूं। आज आपको जो भी लक्षण या समस्या हो रही है, मुझे बताएं और मैं व्यक्तिगत मार्गदर्शन प्रदान करूंगा। मैं आपकी कैसे सहायता कर सकता हूं?",
        "call_label":           "अनुवर्ती कॉल",
        "call_sub":             "{name} के लिए स्वचालित IVR चेक-इन शुरू करें",
        "start_call_btn":       "📞 कॉल शुरू करें",
        "calling_btn":          "⏳ कॉल हो रही है…",
        "chat_placeholder":     "अपने लक्षण बताएं…",
        # Health Page
        "health_title":         "स्वास्थ्य अवलोकन",
        "health_sub":           "{name} के जीवन संकेत दर्ज करें — हमारा AI उनका विश्लेषण करेगा",
        "temp_label":           "तापमान",
        "temp_norm":            "सामान्य: 97–99°F",
        "bp_label":             "रक्तचाप",
        "bp_norm":              "सामान्य: 90–120/60–80 mmHg",
        "hr_label":             "हृदय गति",
        "hr_norm":              "सामान्य: 60–100 bpm",
        "sugar_label":          "रक्त शर्करा",
        "sugar_norm":           "सामान्य: 70–140 mg/dL",
        "spo2_label":           "ऑक्सीजन स्तर (SpO₂)",
        "spo2_norm":            "सामान्य: 95–100%",
        "analyze_btn":          "🔍 मेरे स्वास्थ्य का विश्लेषण करें",
        "analyzing_btn":        "⏳ विश्लेषण हो रहा है…",
        "ai_summary_title":     "AI स्वास्थ्य सारांश",
        "back_services":        "सेवाओं पर वापस जाएं",
        # Appointments Page
        "appt_title":           "नियुक्ति बुक करें",
        "appt_sub":             "{name} के लिए परामर्श शेड्यूल करें",
        "doctor_label":         "डॉक्टर / विशेषज्ञ",
        "doctor_ph":            "— डॉक्टर चुनें —",
        "date_label":           "तारीख",
        "time_label":           "समय",
        "time_ph":              "— चुनें —",
        "reason_label":         "परामर्श का कारण",
        "reason_ph":            "उदा. ऑपरेशन के बाद अनुवर्ती, 3 दिनों से बुखार, रक्तचाप जांच…",
        "confirm_btn":          "📅 नियुक्ति की पुष्टि करें",
        "booking_btn":          "बुक हो रहा है…",
        "success_title":        "नियुक्ति की पुष्टि हो गई!",
        "back_btn":             "← सेवाओं पर वापस जाएं",
        "upcoming_title":       "📋 आगामी नियुक्तियां",
    },

    "Telugu": {
        # Patient Page
        "patient_title":        "రోగి వివరాలు",
        "patient_sub":          "సత్రం ప్రారంభించడానికి మీ సమాచారం నమోదు చేయండి",
        "patient_name_label":   "రోగి పేరు",
        "patient_name_ph":      "ఉదా. ప్రియా శర్మ",
        "surgery_label":        "శస్త్రచికిత్స / విధాన రకం",
        "surgery_optional":     "(ఐచ్ఛికం)",
        "surgery_hint":         "ఇది మీ సంరక్షణ సిఫారసులను వ్యక్తిగతీకరించడంలో సహాయపడుతుంది.",
        "continue_btn":         "కొనసాగించు →",
        "saving_btn":           "సేవ్ అవుతోంది…",
        "surgery_options": [
            ("", "— వర్తించదు / సాధారణ సంరక్షణ —"),
            ("Appendectomy", "అపెండెక్టమీ"),
            ("Cardiac Surgery", "హృదయ శస్త్రచికిత్స"),
            ("Knee Replacement", "మోకాలు పునఃస్థాపన"),
            ("Hip Replacement", "పిరుదు పునఃస్థాపన"),
            ("Spinal Surgery", "వెన్నెముక శస్త్రచికిత్స"),
            ("Cholecystectomy", "కొలెసిస్టెక్టమీ (పిత్తాశయం)"),
            ("Hernia Repair", "హెర్నియా మరమ్మతు"),
            ("Cataract Surgery", "కంటిపొర శస్త్రచికిత్స"),
            ("Hysterectomy", "గర్భాశయ తొలగింపు"),
            ("Caesarean Section", "సిజేరియన్ విభాగం"),
            ("Tonsillectomy", "టాన్సిల్ తొలగింపు"),
            ("Other", "ఇతర"),
        ],
        # Service Page
        "service_title":        "సంరక్షణ సేవలు",
        "service_sub":          "నేడు మీకు అవసరమైన సంరక్షణ రకాన్ని ఎంచుకోండి",
        "service_welcome":      "తిరిగి స్వాగతం — దిగువ మీ సంరక్షణ రకాన్ని ఎంచుకోండి",
        "regular_care":         "సాధారణ సంరక్షణ",
        "regular_care_desc":    "సాధారణ ఆరోగ్య సంప్రదింపు, లక్షణ చర్చ మరియు రొటీన్ ఫాలో-అప్‌ల కోసం మందుల మార్గదర్శకత్వం.",
        "regular_badge":        "రొటీన్ ఫాలో-అప్",
        "postop_care":          "శస్త్రచికిత్స అనంతర సంరక్షణ",
        "postop_care_desc":     "పోస్ట్-సర్జికల్ రికవరీ కోసం విశేష మార్గదర్శకత్వం — గాయం సంరక్షణ, వైటల్స్ పర్యవేక్షణ.",
        "postop_badge":         "శస్త్రచికిత్స అనంతరం",
        "health_overview":      "ఆరోగ్య అవలోకనం",
        "health_overview_desc": "AI ఆరోగ్య సారాంశం కోసం మీ వైటల్స్ నమోదు చేయండి — ఉష్ణోగ్రత, రక్తపోటు, హృదయ స్పందన మరియు ఇంకా.",
        "health_badge":         "వైటల్స్ విశ్లేషణ",
        "appointments":         "అపాయింట్‌మెంట్‌లు",
        "appointments_desc":    "మీకు నచ్చిన తేదీ మరియు సమయంలో డాక్టర్ పరామర్శ బుక్ చేసుకోండి.",
        "appt_badge":           "సందర్శన షెడ్యూల్",
        # Chat Page
        "chat_topbar_title":    "MedFollow AI సహాయకుడు",
        "ai_greeting":          "నమస్కారం, {name}! 👋 నేను మీ AI ఆరోగ్య సహాయకుడిని. నేడు మీకు అనుభవమవుతున్న లక్షణాలు లేదా ఆందోళనలను చెప్పండి, నేను మీకు వ్యక్తిగత మార్గదర్శకత్వం ఇస్తాను. నేను మీకు ఏ విధంగా సహాయపడగలను?",
        "call_label":           "ఫాలో-అప్ కాల్",
        "call_sub":             "{name} కోసం స్వయంచాలిత IVR చెక్-ఇన్ ప్రారంభించండి",
        "start_call_btn":       "📞 కాల్ ప్రారంభించు",
        "calling_btn":          "⏳ కాల్ అవుతోంది…",
        "chat_placeholder":     "మీ లక్షణాలు వివరించండి…",
        # Health Page
        "health_title":         "ఆరోగ్య అవలోకనం",
        "health_sub":           "{name} కోసం వైటల్స్ నమోదు చేయండి — మా AI వాటిని విశ్లేషిస్తుంది",
        "temp_label":           "ఉష్ణోగ్రత",
        "temp_norm":            "సాధారణ: 97–99°F",
        "bp_label":             "రక్తపోటు",
        "bp_norm":              "సాధారణ: 90–120/60–80 mmHg",
        "hr_label":             "హృదయ స్పందన",
        "hr_norm":              "సాధారణ: 60–100 bpm",
        "sugar_label":          "రక్తంలో చక్కెర",
        "sugar_norm":           "సాధారణ: 70–140 mg/dL",
        "spo2_label":           "ఆక్సిజన్ స్థాయి (SpO₂)",
        "spo2_norm":            "సాధారణ: 95–100%",
        "analyze_btn":          "🔍 నా ఆరోగ్యాన్ని విశ్లేషించు",
        "analyzing_btn":        "⏳ విశ్లేషిస్తోంది…",
        "ai_summary_title":     "AI ఆరోగ్య సారాంశం",
        "back_services":        "సేవలకు తిరిగి వెళ్ళు",
        # Appointments Page
        "appt_title":           "అపాయింట్‌మెంట్ బుక్ చేయండి",
        "appt_sub":             "{name} కోసం పరామర్శ షెడ్యూల్ చేయండి",
        "doctor_label":         "డాక్టర్ / నిపుణుడు",
        "doctor_ph":            "— డాక్టర్ ఎంచుకోండి —",
        "date_label":           "తేదీ",
        "time_label":           "సమయం",
        "time_ph":              "— ఎంచుకోండి —",
        "reason_label":         "సందర్శన కారణం",
        "reason_ph":            "ఉదా. శస్త్రచికిత్స అనంతర ఫాలో-అప్, 3 రోజులుగా జ్వరం, రక్తపోటు తనిఖీ…",
        "confirm_btn":          "📅 అపాయింట్‌మెంట్ నిర్ధారించు",
        "booking_btn":          "బుక్ అవుతోంది…",
        "success_title":        "అపాయింట్‌మెంట్ నిర్ధారించబడింది!",
        "back_btn":             "← సేవలకు తిరిగి వెళ్ళు",
        "upcoming_title":       "📋 రాబోయే అపాయింట్‌మెంట్‌లు",
    },
}


def get_t():
    """Return the translation dict for the current session language."""
    lang = session.get("language", "English")
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"])


# ─────────────────────────────────────────────
#  OpenAI GPT — Medical AI Chatbot
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are MedFollow AI, a compassionate and knowledgeable hospital patient follow-up assistant.

Your role:
- Help patients recovering from surgery or illness understand and manage their symptoms
- Provide clear, medically accurate, and comforting guidance
- Always remind patients to consult their doctor for serious concerns
- Never diagnose — only provide general health guidance and post-care support
- In emergencies, always recommend calling 108 (India) immediately

Tone: Warm, professional, reassuring — like a caring nurse
Format: Keep responses concise (3–5 sentences). Use plain language, no jargon.
Language: ALWAYS reply in the EXACT SAME LANGUAGE the patient writes in.
  - If they write in Hindi, reply fully in Hindi
  - If they write in Telugu, reply fully in Telugu
  - If they write in English, reply in English

Safety: Never suggest stopping prescribed medications. Always err on the side of caution."""


def ask_llm(message: str) -> str:
    """Call GPT-4o-mini with a hospital assistant system prompt.
    Falls back to keyword-based response if API key is missing or request fails.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            # Include patient context from session if available
            patient_name  = session.get("patient_name", "")
            surgery_type  = session.get("surgery_type", "")
            language      = session.get("language", "English")

            context_lines = []
            if patient_name:
                context_lines.append(f"Patient name: {patient_name}")
            if surgery_type:
                context_lines.append(f"Surgery/procedure: {surgery_type}")
            if language:
                context_lines.append(f"Preferred language: {language} (reply in this language)")

            system = SYSTEM_PROMPT
            if context_lines:
                system += "\n\nPatient context:\n" + "\n".join(context_lines)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system",  "content": system},
                    {"role": "user",    "content": message},
                ],
                max_tokens=300,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            # Log and fall through to keyword fallback
            print(f"[WARN] OpenAI API error: {e}")

    # ── Smart Conversational Fallback ─────────────────────────────────
    msg = message.lower().strip()
    name = session.get("patient_name", "")
    greeting_name = f", {name}" if name else ""

    # Greetings
    greetings = ["hi", "hello", "hey", "hii", "helo", "howdy", "namaste",
                 "नमस्ते", "నమస్కారం", "good morning", "good evening",
                 "good afternoon", "good night", "sup", "yo"]
    if any(msg == g or msg.startswith(g + " ") for g in greetings):
        return (
            f"Hello{greeting_name}! 👋 I'm MedFollow AI, your personal health assistant. "
            "I'm here to help you with any symptoms, recovery questions, or medication concerns. "
            "How are you feeling today? Please describe what's going on and I'll guide you."
        )

    # How are you
    if any(p in msg for p in ["how are you", "how r u", "are you ok", "kaise ho", "ela unnav"]):
        return (
            f"I'm doing great, thank you{greeting_name}! 😊 More importantly — how are YOU feeling? "
            "Tell me about any symptoms or concerns and I'll provide guidance right away."
        )

    # Who are you / what can you do
    if any(p in msg for p in ["who are you", "what are you", "what can you do",
                               "tell me about yourself", "aap kaun"]):
        return (
            "I'm MedFollow AI 🏥 — your hospital follow-up health assistant. I can help with:\n"
            "• Post-surgery recovery questions\n"
            "• Symptom assessment (fever, pain, swelling, etc.)\n"
            "• Medication and wound care guidance\n"
            "• Vital sign interpretation\n\n"
            "Just describe your symptoms and I'll give you personalised guidance!"
        )

    # Help / menu
    if any(p in msg for p in ["help", "options", "menu", "help me", "सहायता", "సహాయం"]):
        return (
            "Sure! Here's what you can ask me about:\n\n"
            "🌡️ Fever / Temperature\n"
            "💊 Pain or Discomfort\n"
            "💓 Blood Pressure / Heart Rate\n"
            "🩸 Blood Sugar / Diabetes\n"
            "😮‍💨 Breathing Difficulty\n"
            "🤢 Nausea / Dizziness\n"
            "🩹 Wound / Incision Care\n"
            "💤 Fatigue / Sleep Issues\n"
            "💉 Medication Questions\n\n"
            "Just type your symptom and I'll guide you!"
        )

    # Thank you
    if any(p in msg for p in ["thank", "thanks", "thank you", "ty", "dhanyavad",
                               "ధన్యవాదాలు", "धन्यवाद"]):
        return (
            f"You're very welcome{greeting_name}! 😊 "
            "If anything feels urgent, don't hesitate to call 108 or contact your doctor directly. "
            "Take good care and feel better soon!"
        )

    # OK / fine
    if msg in ["ok", "okay", "fine", "alright", "got it", "understood", "k", "sure"]:
        return (
            "Glad to hear that! 😊 Feel free to ask me anything else. "
            "If new symptoms appear or anything changes, just let me know."
        )

    # Fever
    if any(w in msg for w in ["fever", "temperature", "hot", "burning", "chills",
                               "बुखार", "तापमान", "జ్వరం", "ఉష్ణోగ్రత"]):
        return (
            "🌡️ A fever can be your body fighting infection. Here's what to do:\n\n"
            "• Stay well hydrated — drink water, ORS, or coconut water every hour\n"
            "• Rest completely; avoid physical exertion\n"
            "• Take paracetamol (as prescribed) to bring it down\n"
            "• Apply a cool damp cloth on your forehead\n\n"
            "⚠️ Call your doctor immediately if: temperature exceeds 103°F (39.4°C), "
            "fever lasts more than 48 hours, or is accompanied by severe headache or rash."
        )

    # Pain
    if any(w in msg for w in ["pain", "ache", "hurt", "sore", "cramp",
                               "दर्द", "నొప్పి"]):
        return (
            "💊 Pain management after surgery or illness:\n\n"
            "• Note the location and rate your pain (1 = mild, 10 = severe)\n"
            "• Take your prescribed pain medication on schedule, don't skip doses\n"
            "• Apply a warm compress for muscle aches, cold pack for swelling\n\n"
            "⚠️ Seek care immediately if: pain is sudden and severe (8–10/10), "
            "pain is spreading, or accompanied by fever or swelling."
        )

    # Breathing
    if any(w in msg for w in ["breathe", "breathing", "breath", "shortness",
                               "oxygen", "chest", "सांस", "ఊపిరి"]):
        return (
            "😮‍💨 Breathing difficulty needs immediate attention:\n\n"
            "• Sit upright — don't lie flat\n"
            "• Breathe in slowly through your nose, out through your mouth\n"
            "• Loosen any tight clothing around your chest\n\n"
            "🚨 Call 108 immediately if: SpO₂ drops below 94%, "
            "you feel chest tightness, or you cannot speak full sentences."
        )

    # Dizziness / Nausea
    if any(w in msg for w in ["dizzy", "dizziness", "faint", "nausea", "nauseous",
                               "vomit", "vomiting", "lightheaded", "चक्कर", "మైకం"]):
        return (
            "🤢 Dizziness or nausea is common after surgery or medication changes:\n\n"
            "• Sit or lie down immediately to prevent a fall\n"
            "• Sip cold water slowly — small sips, not large gulps\n"
            "• Avoid sudden head movements or standing up too quickly\n"
            "• Eat small, bland meals (rice, toast, bananas)\n\n"
            "⚠️ See your doctor if: nausea persists over 6 hours or you cannot keep fluids down."
        )

    # Swelling
    if any(w in msg for w in ["swelling", "swollen", "puffiness", "edema",
                               "सूजन", "వాపు"]):
        return (
            "🦵 Post-surgical swelling management:\n\n"
            "• Elevate the swollen area above heart level when resting\n"
            "• Apply an ice pack wrapped in cloth: 20 min on, 20 min off\n"
            "• Reduce salt intake to prevent fluid retention\n\n"
            "⚠️ See your doctor today if: swelling is red, warm, or spreading — "
            "this may indicate infection or a blood clot."
        )

    # Wound
    if any(w in msg for w in ["wound", "incision", "cut", "stitches", "suture",
                               "bleed", "bleeding", "pus", "घाव", "గాయం"]):
        return (
            "🩹 Wound care essentials:\n\n"
            "• Keep the wound clean and dry at all times\n"
            "• Change dressings on schedule; don't remove stitches yourself\n"
            "• Do NOT use hydrogen peroxide unless prescribed\n\n"
            "🚨 Go to your doctor immediately if: you notice increased redness, warmth, "
            "swelling, foul odor, yellow/green discharge, or if bleeding won't stop."
        )

    # Blood sugar
    if any(w in msg for w in ["sugar", "glucose", "diabetes", "insulin",
                               "शर्करा", "చక్కెర"]):
        return (
            "🩸 Blood sugar control during recovery:\n\n"
            "• Continue your prescribed diabetes medications — do NOT stop them\n"
            "• Eat regular small meals; avoid skipping meals\n"
            "• Target fasting blood sugar: 80–130 mg/dL\n\n"
            "⚠️ Low sugar (<70 mg/dL) → eat glucose tablets or 3 teaspoons of sugar in water RIGHT NOW. "
            "High sugar (>250) → contact your doctor today."
        )

    # Blood pressure
    if any(w in msg for w in ["blood pressure", "bp", "hypertension", "hypotension",
                               "pressure", "रक्तचाप", "రక్తపోటు"]):
        return (
            "💓 Blood pressure monitoring during recovery:\n\n"
            "• Normal range: 90–120 / 60–80 mmHg\n"
            "• Take your BP medications exactly as prescribed\n"
            "• Reduce salt, processed foods, and caffeine\n\n"
            "⚠️ Contact your doctor if BP is consistently above 140/90 or below 90/60. "
            "Severe headache with high BP → emergency care."
        )

    # Fatigue / Sleep
    if any(w in msg for w in ["tired", "fatigue", "weak", "weakness", "sleep",
                               "insomnia", "exhausted", "थकान", "అలసట"]):
        return (
            "💤 Fatigue is very common after surgery or illness:\n\n"
            "• Aim for 7–9 hours of sleep per night\n"
            "• Take short, gentle walks to improve circulation\n"
            "• Eat protein-rich foods (eggs, lentils, paneer) to support tissue repair\n"
            "• Stay well hydrated\n\n"
            "⚠️ See your doctor if weakness is getting worse or accompanied by chest pain."
        )

    # Medication
    if any(w in msg for w in ["medicine", "medication", "tablet", "pill", "drug",
                               "dose", "antibiotic", "दवा", "మందు"]):
        return (
            "💊 Medication guidance:\n\n"
            "• Take all medications exactly as prescribed — don't skip or double doses\n"
            "• Complete the full antibiotic course even if you feel better\n"
            "• Avoid alcohol during medication\n\n"
            "⚠️ Stop and call your doctor if you notice: skin rash, difficulty breathing, "
            "swollen lips/throat, or severe stomach pain."
        )

    # Catchall
    return (
        f"I'd love to help you{greeting_name}! 😊 "
        "Could you describe your symptoms in a bit more detail?\n\n"
        "• Where exactly is the discomfort?\n"
        "• When did it start?\n"
        "• How severe is it (mild / moderate / severe)?\n\n"
        "You can also open the **Health Overview** page to log your vitals for a full AI analysis."
    )


def analyze_vitals(vitals: dict) -> str:
    """Generate a health summary from submitted vitals."""
    issues = []
    recommendations = []

    try:
        temp = float(vitals.get("temperature", 0))
        if temp > 99.5:
            issues.append(f"Elevated temperature ({temp}°F — possible fever)")
            recommendations.append("Stay hydrated, rest, and monitor temperature every 4 hours.")
        elif temp < 96.0 and temp > 0:
            issues.append(f"Low temperature ({temp}°F — possible hypothermia risk)")
            recommendations.append("Keep warm and consult your doctor.")
    except (ValueError, TypeError):
        pass

    try:
        bp = vitals.get("blood_pressure", "")
        if "/" in str(bp):
            systolic, diastolic = [int(x.strip()) for x in str(bp).split("/")]
            if systolic > 140 or diastolic > 90:
                issues.append(f"High blood pressure ({bp} mmHg — hypertension range)")
                recommendations.append("Reduce salt intake, limit stress, and consult your physician.")
            elif systolic < 90 or diastolic < 60:
                issues.append(f"Low blood pressure ({bp} mmHg — hypotension range)")
                recommendations.append("Increase fluid intake, rise slowly from sitting/lying positions.")
    except (ValueError, TypeError):
        pass

    try:
        hr = int(vitals.get("heart_rate", 0))
        if hr > 100:
            issues.append(f"Elevated heart rate ({hr} bpm — tachycardia)")
            recommendations.append("Rest, avoid caffeine, and monitor. Seek care if above 120 bpm.")
        elif hr < 60 and hr > 0:
            issues.append(f"Low heart rate ({hr} bpm — bradycardia)")
            recommendations.append("Rest and monitor. Contact doctor if you feel faint.")
    except (ValueError, TypeError):
        pass

    try:
        sugar = float(vitals.get("blood_sugar", 0))
        if sugar > 180:
            issues.append(f"High blood sugar ({sugar} mg/dL)")
            recommendations.append("Reduce carbohydrate intake and follow your diabetes care plan.")
        elif sugar < 70 and sugar > 0:
            issues.append(f"Low blood sugar ({sugar} mg/dL — hypoglycemia)")
            recommendations.append("Consume fast-acting carbohydrates (juice/glucose tablets) immediately.")
    except (ValueError, TypeError):
        pass

    try:
        spo2 = int(vitals.get("oxygen_level", 0))
        if spo2 < 94 and spo2 > 0:
            issues.append(f"Low oxygen saturation ({spo2}% — below normal range)")
            recommendations.append("Sit upright, breathe slowly. If below 90%, seek emergency care immediately.")
    except (ValueError, TypeError):
        pass

    if not issues:
        return ("✅ All your vitals appear to be within normal ranges. "
                "Keep up the great work! Continue your prescribed regimen, "
                "stay hydrated, and get adequate rest. Your next follow-up looks positive.")

    summary = f"⚠️ Health Analysis Summary — {len(issues)} concern(s) detected:\n\n"
    for issue in issues:
        summary += f"• {issue}\n"
    summary += "\n📋 Recommendations:\n"
    for rec in recommendations:
        summary += f"• {rec}\n"
    summary += "\nPlease share this report with your doctor at your next appointment."
    return summary


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

@app.route("/")
def splash():
    return render_template("splash.html")


@app.route("/language", methods=["GET", "POST"])
def language():
    if request.method == "POST":
        session["language"] = request.form.get("language", "English")
        return redirect(url_for("patient"))
    return render_template("language.html")


@app.route("/patient", methods=["GET", "POST"])
def patient():
    t = get_t()
    if request.method == "POST":
        session["patient_name"] = request.form.get("patient_name", "Patient").strip() or "Patient"
        session["surgery_type"] = request.form.get("surgery_type", "").strip()
        return redirect(url_for("service"))
    return render_template("patient.html", t=t)


@app.route("/service")
def service():
    t = get_t()
    return render_template("service.html", t=t,
                           patient_name=session.get("patient_name", "Patient"))


@app.route("/chat", methods=["GET", "POST"])
def chat():
    t = get_t()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        response = ask_llm(user_message)
        return jsonify({"response": response})
    patient_name = session.get("patient_name", "Patient")
    return render_template("chat.html", t=t,
                           patient_name=patient_name,
                           language=session.get("language", "English"),
                           ai_greeting=t["ai_greeting"].format(name=patient_name))


@app.route("/health", methods=["GET", "POST"])
def health():
    t = get_t()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        summary = analyze_vitals(data)
        return jsonify({"summary": summary})
    patient_name = session.get("patient_name", "Patient")
    return render_template("health.html", t=t,
                           patient_name=patient_name,
                           health_sub=t["health_sub"].format(name=patient_name))


@app.route("/appointments")
def appointments():
    t = get_t()
    patient_name = session.get("patient_name", "Patient")
    return render_template("appointments.html", t=t,
                           patient_name=patient_name,
                           appt_sub=t["appt_sub"].format(name=patient_name))


# ─────────────────────────────────────────────
#  IVR Call Trigger
# ─────────────────────────────────────────────

@app.route("/start-call", methods=["POST"])
def start_call():
    patient_name = session.get("patient_name", "Patient")
    language     = session.get("language", "English")
    ivr_script   = os.path.join(BASE_DIR, "offline_ivr.py")

    try:
        terminal_cmds = [
            ["gnome-terminal", "--", sys.executable, ivr_script, patient_name, language],
            ["xterm", "-e", f"{sys.executable} {ivr_script} \"{patient_name}\" \"{language}\""],
            ["x-terminal-emulator", "-e", f"{sys.executable} {ivr_script} \"{patient_name}\" \"{language}\""],
        ]
        launched = False
        for cmd in terminal_cmds:
            try:
                subprocess.Popen(cmd, cwd=BASE_DIR)
                launched = True
                break
            except FileNotFoundError:
                continue

        if not launched:
            subprocess.Popen([sys.executable, ivr_script, patient_name, language], cwd=BASE_DIR)

        return jsonify({
            "status": "success",
            "message": f"📞 Follow-up call initiated for {patient_name}! Check the terminal window."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to launch IVR: {str(e)}"}), 500


# ─────────────────────────────────────────────
#  Response Log (preserved from original)
# ─────────────────────────────────────────────

@app.route("/log")
def log():
    if not os.path.exists(RESPONSES_FILE):
        return jsonify({"entries": []})
    with open(RESPONSES_FILE, "r") as f:
        entries = [line.strip() for line in f.readlines() if line.strip()]
    return jsonify({"entries": entries})



# ─────────────────────────────────────────────
#  Static SPA — serve index.html and all new JSON APIs
# ─────────────────────────────────────────────

@app.route("/spa")
def spa():
    """Serve the standalone static SPA (index.html + script.js + style.css)."""
    static_dir = os.path.join(BASE_DIR, "static")
    return send_from_directory(static_dir, "index.html")


@app.route("/analyze", methods=["POST"])
def spa_analyze():
    """
    Vitals analysis for the static SPA.
    Expects JSON: {blood_pressure_systolic, blood_pressure_diastolic,
                   blood_sugar, bmi, temperature, patient_name, language}
    """
    data = request.get_json(silent=True) or {}

    # Map SPA field names → internal analyze_vitals() format
    vitals = {
        "blood_pressure":  f"{data.get('blood_pressure_systolic', 0)}/{data.get('blood_pressure_diastolic', 0)}",
        "blood_sugar":     data.get("blood_sugar", 0),
        "temperature":     data.get("temperature", 0),
        "heart_rate":      data.get("heart_rate", 0),
        "oxygen_level":    data.get("oxygen_level", 0),
    }

    summary = analyze_vitals(vitals)

    # Derive severity from the summary text
    if "⚠️" in summary and "DOCTOR ALERT" not in summary:
        severity = "moderate"
        emergency = False
    elif "condition worsened" in summary.lower() or "🚨" in summary:
        severity = "high"
        emergency = True
    elif "✅" in summary:
        severity = "low"
        emergency = False
    else:
        severity = "moderate"
        emergency = False

    return jsonify({
        "severity": severity,
        "message":  summary,
        "emergency": emergency,
        "alert":    emergency,
    })


@app.route("/postop-chat", methods=["POST"])
def spa_postop_chat():
    """
    Chatbot endpoint for the static SPA.
    Expects JSON: {message, patient_name, surgery_type, language}
    """
    data = request.get_json(silent=True) or {}
    message      = data.get("message", "").strip()
    patient_name = data.get("patient_name", "Patient")
    surgery_type = data.get("surgery_type", "")
    language     = data.get("language", "English")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Temporarily inject context into session so ask_llm() picks it up
    session["patient_name"] = patient_name
    session["surgery_type"] = surgery_type
    session["language"]     = language

    response_text = ask_llm(message)

    # Basic severity detection from response keywords
    alert_keywords = ["🚨", "call 108", "emergency", "immediately", "seek care", "doctor now"]
    is_emergency   = any(kw in response_text.lower() for kw in alert_keywords)
    severity       = "high" if is_emergency else ("moderate" if "⚠️" in response_text else "low")

    return jsonify({
        "response_text": response_text,
        "severity":      severity,
        "alert":         is_emergency,
    })


@app.route("/book-appointment", methods=["POST"])
def spa_book_appointment():
    """
    Appointment booking for the static SPA.
    Expects JSON: {patient_name, doctor, date, time, language}
    """
    data         = request.get_json(silent=True) or {}
    patient_name = data.get("patient_name", "Patient")
    doctor       = data.get("doctor", "")
    date         = data.get("date", "")
    time_val     = data.get("time", "")
    language     = data.get("language", "English")

    if not doctor or not date or not time_val:
        return jsonify({"error": "Missing required fields"}), 400

    # Log the appointment to responses.txt
    import datetime as _dt
    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (f"[{timestamp}] APPOINTMENT | Patient: {patient_name} | "
             f"Doctor: {doctor} | Date: {date} | Time: {time_val} | Lang: {language}\n")
    with open(RESPONSES_FILE, "a") as f:
        f.write(entry)

    return jsonify({
        "status": "success",
        "message": f"Appointment confirmed with {doctor} on {date} at {time_val}."
    })


@app.route("/customer-care-call", methods=["POST"])
def spa_customer_care_call():
    """
    Launch the offline IVR system for the SPA's 'Call Customer Care' button.
    Expects JSON: {patient_name, language}
    """
    data         = request.get_json(silent=True) or {}
    patient_name = data.get("patient_name", "Patient")
    language     = data.get("language", "English")
    ivr_script   = os.path.join(BASE_DIR, "offline_ivr.py")

    try:
        terminal_cmds = [
            ["gnome-terminal", "--", sys.executable, ivr_script, patient_name, language],
            ["xterm",          "-e", f'{sys.executable} "{ivr_script}" "{patient_name}" "{language}"'],
            ["x-terminal-emulator", "-e", f'{sys.executable} "{ivr_script}" "{patient_name}" "{language}"'],
        ]
        launched = False
        for cmd in terminal_cmds:
            try:
                subprocess.Popen(cmd, cwd=BASE_DIR)
                launched = True
                break
            except FileNotFoundError:
                continue

        if not launched:
            subprocess.Popen([sys.executable, ivr_script, patient_name, language], cwd=BASE_DIR)

        return jsonify({
            "status": "success",
            "message": f"Follow-up call initiated for {patient_name}!"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    print("🏥 MedFollow AI running at http://localhost:5000")
    print("📱 Static SPA available at http://localhost:5000/spa")
    app.run(debug=False, port=5000)
