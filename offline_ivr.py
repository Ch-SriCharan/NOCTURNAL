#!/usr/bin/env python3
"""
MedFollow AI — Offline IVR System
Uses edge-tts (Microsoft Neural TTS) for high-quality voices.
Falls back to pyttsx3 if edge-tts or internet is unavailable.
Usage: python3 offline_ivr.py "Patient Name" "Language"
"""

import os
import sys
import subprocess
import datetime
import asyncio
import tempfile

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
RESPONSES_FILE = os.path.join(BASE_DIR, "responses.txt")
RINGTONE_FILE  = os.path.join(BASE_DIR, "iphone_14.mp3")

PATIENT_NAME = sys.argv[1] if len(sys.argv) > 1 else "Patient"
LANGUAGE     = sys.argv[2] if len(sys.argv) > 2 else "English"

# ─────────────────────────────────────────────
#  Neural Voice Map  (edge-tts voice names)
# ─────────────────────────────────────────────
# These are free Microsoft neural voices — very natural sounding.
# Full list: https://speech.microsoft.com/portal (no API key needed with edge-tts)
EDGE_VOICES = {
    "English": {"voice": "en-IN-NeerjaNeural",  "rate": "-5%",  "pitch": "+0Hz"},   # Indian English — warm & clear
    "Hindi":   {"voice": "hi-IN-SwaraNeural",   "rate": "-10%", "pitch": "-3Hz"},   # Hindi female — slower, natural
    "Telugu":  {"voice": "te-IN-ShrutiNeural",  "rate": "-12%", "pitch": "-2Hz"},   # Telugu female — clear & calm
}

# ─────────────────────────────────────────────
#  IVR Phrases — per language
# ─────────────────────────────────────────────

PHRASES = {
    "English": {
        "header":        "HOSPITAL PATIENT FOLLOW-UP SYSTEM",
        "greeting":      "Hello {name}. This is your MedFollow AI hospital follow-up assistant. I hope you're recovering well.",
        "listen":        "Please listen carefully and enter your response when prompted.",
        "opt1":          "Press 1 if you are feeling fine.",
        "opt2":          "Press 2 if you have mild symptoms.",
        "opt3":          "Press 3 if your condition has worsened.",
        "choice_prompt": "Enter your choice",
        "choice_1":      "1 - Feeling fine",
        "choice_2":      "2 - Mild symptoms",
        "choice_3":      "3 - Condition worsened",
        "resp_1":        ("That's wonderful to hear, {name}! We're so glad you're feeling well. "
                          "Please continue your prescribed medication and stay hydrated. "
                          "Our care team will check in with you again soon. Take good care of yourself!"),
        "resp_2":        ("We understand you're experiencing some mild symptoms, {name}. "
                          "Please make sure to rest well, drink plenty of fluids, and keep monitoring your condition. "
                          "If your symptoms don't improve within 24 hours, please visit the clinic. "
                          "Our team will follow up with you again tomorrow."),
        "resp_3":        ("We're very sorry to hear that your condition has worsened, {name}. "
                          "Please stay calm and don't worry. We are alerting your doctor right now. "
                          "Help is on its way. Please rest and avoid any physical exertion."),
        "resp_invalid":  ("We're sorry, we didn't receive a valid response. "
                          "Our care team will contact you shortly. Thank you for your time."),
        "closing":       "Thank you for using MedFollow AI. We wish you a speedy recovery. Goodbye!",
        "alert":         "DOCTOR ALERT TRIGGERED",
        "outcome_1":     "Patient feeling fine",
        "outcome_2":     "Patient has mild symptoms",
        "outcome_3":     "Patient condition worsened — DOCTOR ALERT TRIGGERED",
        "outcome_inv":   "Invalid input",
    },

    "Hindi": {
        "header":        "अस्पताल रोगी अनुवर्ती प्रणाली",
        "greeting":      "नमस्ते {name}। मैं आपकी MedFollow AI अस्पताल सहायक हूं। आशा है आप ठीक हो रहे हैं।",
        "listen":        "कृपया ध्यान से सुनें और संकेत मिलने पर अपना जवाब दर्ज करें।",
        "opt1":          "1 दबाएं यदि आप ठीक महसूस कर रहे हैं।",
        "opt2":          "2 दबाएं यदि आपको हल्के लक्षण हैं।",
        "opt3":          "3 दबाएं यदि आपकी स्थिति खराब हुई है।",
        "choice_prompt": "अपना विकल्प दर्ज करें",
        "choice_1":      "1 - ठीक हूं",
        "choice_2":      "2 - हल्के लक्षण",
        "choice_3":      "3 - स्थिति खराब हुई",
        "resp_1":        ("यह सुनकर बहुत अच्छा लगा {name}! हमें खुशी है कि आप ठीक हों। "
                          "कृपया अपनी निर्धारित दवाइयां लेते रहें और पर्याप्त पानी पिएं। "
                          "हमारी देखभाल टीम जल्द ही आपसे संपर्क करेगी। अपना ख्याल रखें!"),
        "resp_2":        ("हम समझते हैं कि आपको कुछ हल्के लक्षण हो रहे हैं {name}। "
                          "कृपया पर्याप्त आराम करें, पानी पिएं और अपनी स्थिति पर नजर रखें। "
                          "यदि 24 घंटे में सुधार न हो तो क्लिनिक जाएं। हम कल फिर संपर्क करेंगे।"),
        "resp_3":        ("हमें बहुत खेद है कि आपकी स्थिति खराब हुई है {name}। "
                          "कृपया शांत रहें और चिंता न करें। हम अभी आपके डॉक्टर को सूचित कर रहे हैं। "
                          "मदद रास्ते में है। कृपया आराम करें और थकान न करें।"),
        "resp_invalid":  ("हमें खेद है, हमें कोई वैध जवाब नहीं मिला। "
                          "हमारी टीम जल्द ही आपसे संपर्क करेगी। आपके समय के लिए धन्यवाद।"),
        "closing":       "MedFollow AI का उपयोग करने के लिए धन्यवाद। हम आपके शीघ्र स्वस्थ होने की कामना करते हैं। नमस्ते!",
        "alert":         "डॉक्टर अलर्ट सक्रिय हुआ",
        "outcome_1":     "रोगी ठीक हैं",
        "outcome_2":     "रोगी को हल्के लक्षण हैं",
        "outcome_3":     "रोगी की स्थिति खराब हुई — डॉक्टर अलर्ट सक्रिय",
        "outcome_inv":   "अमान्य इनपुट",
    },

    "Telugu": {
        "header":        "ఆస్పత్రి రోగి ఫాలో-అప్ వ్యవస్థ",
        "greeting":      "నమస్కారం {name}. నేను మీ MedFollow AI ఆస్పత్రి సహాయకురాలిని. మీరు కోలుకుంటున్నారని ఆశిస్తున్నాను.",
        "listen":        "దయచేసి జాగ్రత్తగా వినండి మరియు సంకేతం వచ్చినప్పుడు మీ సమాధానం నమోదు చేయండి.",
        "opt1":          "మీరు బాగున్నట్లయితే 1 నొక్కండి.",
        "opt2":          "మీకు తేలికపాటి లక్షణాలు ఉంటే 2 నొక్కండి.",
        "opt3":          "మీ పరిస్థితి మరింత దిగజారితే 3 నొక్కండి.",
        "choice_prompt": "మీ ఎంపిక నమోదు చేయండి",
        "choice_1":      "1 - బాగున్నాను",
        "choice_2":      "2 - తేలికపాటి లక్షణాలు",
        "choice_3":      "3 - పరిస్థితి దిగజారింది",
        "resp_1":        ("మీరు బాగున్నారని తెలుసుకుని చాలా సంతోషంగా ఉంది {name}! "
                          "దయచేసి మీ నిర్ధారిత మందులు తీసుకుంటూ నీరు ఎక్కువగా తాగండి. "
                          "మా సంరక్షణ బృందం త్వరలో మీతో సంప్రదిస్తుంది. జాగ్రత్తగా ఉండండి!"),
        "resp_2":        ("మీకు కొన్ని తేలికపాటి లక్షణాలు ఉన్నాయని అర్థమైంది {name}. "
                          "దయచేసి విశ్రాంతి తీసుకోండి, నీరు ఎక్కువగా తాగండి మరియు మీ పరిస్థితిని గమనించండి. "
                          "24 గంటల్లో మెరుగుదల కనిపించకపోతే క్లినిక్‌కు వెళ్ళండి. రేపు మళ్ళీ సంప్రదిస్తాము."),
        "resp_3":        ("మీ పరిస్థితి మరింత దిగజారిందని తెలుసుకుని చాలా బాధగా ఉంది {name}. "
                          "దయచేసి శాంతంగా ఉండండి, ఆందోళన పడకండి. మేము ఇప్పుడే మీ డాక్టర్‌కు అలర్ట్ చేస్తున్నాము. "
                          "సహాయం రాబోతోంది. దయచేసి విశ్రాంతి తీసుకోండి."),
        "resp_invalid":  ("మాకు చెల్లుబాటు అయ్యే సమాధానం అందలేదు. "
                          "మా బృందం త్వరలో మీతో సంప్రదిస్తుంది. ధన్యవాదాలు."),
        "closing":       "MedFollow AI ఉపయోగించినందుకు ధన్యవాదాలు. మీకు త్వరగా కోలుకోవాలని కోరుకుంటున్నాము. నమస్కారం!",
        "alert":         "డాక్టర్ అలర్ట్ యాక్టివేట్ అయింది",
        "outcome_1":     "రోగి బాగున్నారు",
        "outcome_2":     "రోగికి తేలికపాటి లక్షణాలు ఉన్నాయి",
        "outcome_3":     "రోగి పరిస్థితి దిగజారింది — డాక్టర్ అలర్ట్ యాక్టివేట్",
        "outcome_inv":   "చెల్లని ఇన్‌పుట్",
    },
}


def get_p():
    return PHRASES.get(LANGUAGE, PHRASES["English"])


# ─────────────────────────────────────────────
#  Audio Playback Helper
# ─────────────────────────────────────────────

def play_file(filepath):
    """Play an audio file (mp3 or wav) using available system player."""
    players = [
        ["mpg123", "-q", filepath],
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filepath],
        ["cvlc", "--play-and-exit", "--quiet", filepath],
        ["aplay", filepath],
    ]
    for cmd in players:
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    return False


def play_ringtone():
    if not os.path.exists(RINGTONE_FILE):
        print(f"[INFO] Ringtone not found. Skipping.")
        return
    if not play_file(RINGTONE_FILE):
        print("[INFO] No audio player found. Skipping ringtone.")


# ─────────────────────────────────────────────
#  edge-tts  (primary — neural, natural voice)
# ─────────────────────────────────────────────

async def _edge_speak_async(text: str, voice: str, rate: str, pitch: str, out_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(out_path)


def speak_edge(text: str) -> bool:
    """
    Speak using edge-tts neural voice with natural rate and pitch.
    Returns True on success, False if edge-tts unavailable or no internet.
    """
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        return False

    voice_cfg = EDGE_VOICES.get(LANGUAGE, EDGE_VOICES["English"])
    voice = voice_cfg["voice"]
    rate  = voice_cfg["rate"]
    pitch = voice_cfg["pitch"]
    print(f"\n\U0001f50a [{LANGUAGE}] {text}")

    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    tmp_path = tmp.name

    try:
        asyncio.run(_edge_speak_async(text, voice, rate, pitch, tmp_path))
        success = play_file(tmp_path)
        return success
    except Exception as e:
        print(f"[WARN] edge-tts failed: {e}")
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ─────────────────────────────────────────────
#  pyttsx3  (fallback — offline, robotic but works)
# ─────────────────────────────────────────────

_pyttsx3_engine = None

def get_pyttsx3_engine():
    global _pyttsx3_engine
    if _pyttsx3_engine is not None:
        return _pyttsx3_engine
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty("rate", 145)
    engine.setProperty("volume", 1.0)

    voice_code = {"English": None, "Hindi": "hi", "Telugu": "te"}.get(LANGUAGE)
    if voice_code:
        voices = engine.getProperty("voices")
        for v in voices:
            vid = (v.id or "").lower()
            lang0 = v.languages[0] if v.languages else ""
            if isinstance(lang0, bytes):
                lang0 = lang0.decode()
            if voice_code in vid or voice_code in lang0.lower():
                engine.setProperty("voice", v.id)
                break
    _pyttsx3_engine = engine
    return engine


def speak_pyttsx3(text: str):
    print(f"\n🔊 [fallback] {text}")
    engine = get_pyttsx3_engine()
    engine.say(text)
    engine.runAndWait()


# ─────────────────────────────────────────────
#  Unified speak — try edge-tts, fallback pyttsx3
# ─────────────────────────────────────────────

def speak(text: str):
    if not speak_edge(text):
        speak_pyttsx3(text)


# ─────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────

def log_response(patient_name, language, option, outcome):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] Patient: {patient_name} | Language: {language} | Option: {option} | Outcome: {outcome}\n"
    with open(RESPONSES_FILE, "a") as f:
        f.write(line)
    print(f"\n📝 Logged to responses.txt")


# ─────────────────────────────────────────────
#  Main IVR Flow
# ─────────────────────────────────────────────

def run_ivr():
    p = get_p()

    voice_cfg = EDGE_VOICES.get(LANGUAGE, EDGE_VOICES["English"])
    print("=" * 60)
    print(f"   \U0001f3e5  {p['header']}")
    print(f"   \U0001f310  Language : {LANGUAGE}")
    print(f"   \U0001f399\ufe0f  Voice    : {voice_cfg['voice']}  (edge-tts neural, rate={voice_cfg['rate']}, pitch={voice_cfg['pitch']})")
    print("=" * 60)

    # Ringtone
    print("\n📞 Initiating call…")
    play_ringtone()

    # Greeting
    speak(p["greeting"].format(name=PATIENT_NAME))
    speak(p["listen"])
    speak(p["opt1"])
    speak(p["opt2"])
    speak(p["opt3"])

    # Input menu
    print("\n" + "-" * 45)
    print(f"  {p['choice_prompt']}:")
    print(f"  [{p['choice_1']}]")
    print(f"  [{p['choice_2']}]")
    print(f"  [{p['choice_3']}]")
    print("-" * 45)
    choice = input("  > ").strip()

    # Response
    if choice == "1":
        outcome = p["outcome_1"]
        speak(p["resp_1"].format(name=PATIENT_NAME))
    elif choice == "2":
        outcome = p["outcome_2"]
        speak(p["resp_2"].format(name=PATIENT_NAME))
    elif choice == "3":
        outcome = p["outcome_3"]
        speak(p["resp_3"].format(name=PATIENT_NAME))
        print("\n" + "!" * 55)
        print(f"  🚨  {p['alert']}  🚨")
        print(f"  Patient : {PATIENT_NAME}")
        print(f"  Language: {LANGUAGE}")
        print("!" * 55)
    else:
        outcome = f"{p['outcome_inv']}: '{choice}'"
        speak(p["resp_invalid"])

    speak(p["closing"])
    log_response(PATIENT_NAME, LANGUAGE, choice, outcome)
    print("\n✅ Call completed.\n")


if __name__ == "__main__":
    run_ivr()
