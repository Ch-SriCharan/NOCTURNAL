// Configuration
const API_URL = "http://localhost:5000";

// Global State
let state = {
    language: localStorage.getItem('appLang') || 'English',
    patientName: '',
    patientPhone: '',
    surgeryType: '',
    theme: 'light'
};

// --- Translations Dictionary ---
const translations = {
    'English': {
        emergency_banner: "CRITICAL EMERGENCY DETECTED. PLEASE CONSULT A DOCTOR IMMEDIATELY.",
        app_title: "Autonomous Patient<br>Follow-up System",
        app_subtitle: "AI-powered post-surgery patient monitoring",
        btn_get_started: "Get Started",
        select_language_title: "Select Your Language",
        select_language_subtitle: "Choose your preferred language for the app experience.",
        enter_details_title: "Enter Patient Details",
        label_full_name: "Full Name",
        placeholder_name: "John Doe",
        label_phone: "Phone Number (with country code)",
        placeholder_phone: "+1234567890",
        btn_continue: "Continue",
        dashboard_title: "Dashboard",
        hello_patient: "Hello, {name}",
        regular_checkup_title: "Regular Check-up",
        regular_checkup_desc: "Vitals entry & Appointments",
        postop_title: "Post-Op",
        postop_desc: "AI Assistant Chat",
        btn_call_care: "Can't reach AI? Call Customer Care",
        basic_checkup_title: "Basic Check-up",
        basic_checkup_desc: "Enter your vitals",
        special_treatment_title: "Specialized Treatment",
        special_treatment_desc: "Book an appointment",
        vital_bp: "Blood Pressure",
        placeholder_bp_sys: "Systolic (e.g. 120)",
        placeholder_bp_dia: "Diastolic (e.g. 80)",
        vital_sugar: "Blood Sugar",
        placeholder_sugar: "Level mg/dL",
        vital_bmi: "BMI",
        placeholder_bmi: "BMI Value",
        vital_temp: "Temperature",
        placeholder_temp: "°F",
        btn_analyze: "Analyze Vitals",
        btn_book_doc: "Book Doctor Appointment",
        label_doctor: "Select Doctor / Specialist",
        label_date: "Date",
        label_time: "Time",
        btn_confirm_apt: "Confirm Appointment",
        postop_setup_title: "Post-Op Setup",
        label_surgery_type: "What surgery did you recently have?",
        placeholder_surgery: "e.g. Knee Replacement",
        btn_start_ai: "Start AI Follow-up",
        ai_assistant_title: "Medical AI Assistant",
        ai_welcome_msg: "Hello, I am your post-operative AI assistant. How are you feeling today? What are your symptoms?",
        placeholder_chat: "Type your symptoms...",
        alert_fill_fields: "Please fill out all fields.",
        alert_one_vital: "Please enter at least one vital parameter.",
        alert_server_err: "Error connecting to server.",
        alert_datetime: "Please select date and time.",
        alert_apt_success: "Appointment booked successfully.",
        msg_typing: "typing",
        err_speech: "Microphone error. Please type.",
        err_speech_unsupported: "Speech recognition not supported in this browser.",
        err_phone_missing: "Phone number not provided!",
        msg_call_init: "Initiating voice call...",
        msg_call_success: "Opening phone dialer...",
        severity_label: "Severity: "
    },
    'Hindi': {
        emergency_banner: "गंभीर आपातकाल का पता चला। कृपया तुरंत डॉक्टर से परामर्श लें।",
        app_title: "स्वायत्त रोगी<br>फॉलो-अप प्रणाली",
        app_subtitle: "AI-संचालित सर्जरी के बाद की रोगी निगरानी",
        btn_get_started: "शुरू करें",
        select_language_title: "अपनी भाषा चुनें",
        select_language_subtitle: "ऐप अनुभव के लिए अपनी पसंदीदा भाषा चुनें।",
        enter_details_title: "रोगी विवरण दर्ज करें",
        label_full_name: "पूरा नाम",
        placeholder_name: "जॉन डो",
        label_phone: "फोन नंबर (कंट्री कोड के साथ)",
        placeholder_phone: "+919876543210",
        btn_continue: "जारी रखें",
        dashboard_title: "डैशबोर्ड",
        hello_patient: "नमस्ते, {name}",
        regular_checkup_title: "नियमित जांच",
        regular_checkup_desc: "वाइटल्स दर्ज करें और अपॉइंटमेंट लें",
        postop_title: "सर्जरी के बाद",
        postop_desc: "AI सहायक चैट",
        btn_call_care: "AI से संपर्क नहीं हो रहा? कस्टमर केयर को कॉल करें",
        basic_checkup_title: "बुनियादी जांच",
        basic_checkup_desc: "अपने वाइटल्स दर्ज करें",
        special_treatment_title: "विशेष उपचार",
        special_treatment_desc: "अपॉइंटमेंट बुक करें",
        vital_bp: "रक्तचाप (Blood Pressure)",
        placeholder_bp_sys: "सिस्टोलिक (जैसे 120)",
        placeholder_bp_dia: "डायस्टोलिक (जैसे 80)",
        vital_sugar: "रक्त शर्करा (Blood Sugar)",
        placeholder_sugar: "स्तर mg/dL",
        vital_bmi: "बीएमआई (BMI)",
        placeholder_bmi: "बीएमआई मूल्य",
        vital_temp: "तापमान",
        placeholder_temp: "°F",
        btn_analyze: "वाइटल्स का विश्लेषण करें",
        btn_book_doc: "डॉक्टर का अपॉइंटमेंट बुक करें",
        label_doctor: "डॉक्टर / विशेषज्ञ चुनें",
        label_date: "तारीख",
        label_time: "समय",
        btn_confirm_apt: "अपॉइंटमेंट पक्का करें",
        postop_setup_title: "पोस्ट-ऑप सेटअप",
        label_surgery_type: "हाल ही में आपकी कौन सी सर्जरी हुई थी?",
        placeholder_surgery: "जैसे घुटना बदलना",
        btn_start_ai: "AI फॉलो-अप शुरू करें",
        ai_assistant_title: "मेडिकल AI सहायक",
        ai_welcome_msg: "नमस्ते, मैं आपका पोस्ट-ऑपरेटिव AI सहायक हूँ। आज आप कैसा महसूस कर रहे हैं? आपके लक्षण क्या हैं?",
        placeholder_chat: "अपने लक्षण टाइप करें...",
        alert_fill_fields: "कृपया सभी फ़ील्ड भरें।",
        alert_one_vital: "कृपया कम से कम एक वाइटल पैरामीटर दर्ज करें।",
        alert_server_err: "सर्वर से कनेक्ट करने में त्रुटि।",
        alert_datetime: "कृपया तारीख और समय चुनें।",
        alert_apt_success: "अपॉइंटमेंट सफलतापूर्वक बुक हो गया।",
        msg_typing: "टाइप कर रहा है",
        err_speech: "माइक्रोफ़ोन त्रुटि। कृपया टाइप करें।",
        err_speech_unsupported: "इस ब्राउज़र में स्पीच रिकग्निशन समर्थित नहीं है।",
        err_phone_missing: "फ़ोन नंबर नहीं दिया गया!",
        msg_call_init: "वॉयस कॉल शुरू हो रहा है...",
        msg_call_success: "फ़ोन डायलर खुल रहा है...",
        severity_label: "गंभीरता: "
    },
    'Telugu': {
        emergency_banner: "తీవ్రమైన అత్యవసర పరిస్థితి గుర్తించబడింది. దయచేసి వెంటనే వైద్యుడిని సంప్రదించండి.",
        app_title: "అటానమస్ పేషెంట్<br>ఫాలో-అప్ సిస్టమ్",
        app_subtitle: "AI-ఆధారిత పోస్ట్ సర్జరీ పేషెంట్ పర్యవేక్షణ",
        btn_get_started: "ప్రారంభించండి",
        select_language_title: "మీ భాషను ఎంచుకోండి",
        select_language_subtitle: "యాప్ అనుభవం కోసం మీకు ఇష్టమైన భాషను ఎంచుకోండి.",
        enter_details_title: "రోగి వివరాలను నమోదు చేయండి",
        label_full_name: "పూర్తి పేరు",
        placeholder_name: "జాన్ డో",
        label_phone: "ఫోన్ నంబర్",
        placeholder_phone: "+919876543210",
        btn_continue: "కొనసాగించు",
        dashboard_title: "డాష్‌బోర్డ్",
        hello_patient: "నమస్కారం, {name}",
        regular_checkup_title: "రెగ్యులర్ చెకప్",
        regular_checkup_desc: "వైటల్స్ ఎంట్రీ & అపాయింట్‌మెంట్‌లు",
        postop_title: "పోస్ట్-ఆప్",
        postop_desc: "AI అసిస్టెంట్ చాట్",
        btn_call_care: "AI ని చేరుకోలేకపోతున్నారా? కస్టమర్ కేర్‌కు కాల్ చేయండి",
        basic_checkup_title: "ప్రాథమిక చెకప్",
        basic_checkup_desc: "మీ వైటల్స్ నమోదు చేయండి",
        special_treatment_title: "ప్రత్యేక చికిత్స",
        special_treatment_desc: "అపాయింట్‌మెంట్ బుక్ చేయండి",
        vital_bp: "రక్తపోటు (బ్లడ్ ప్రెషర్)",
        placeholder_bp_sys: "సిస్టోలిక్ (ఉదా. 120)",
        placeholder_bp_dia: "డయాస్టోలిక్ (ఉదా. 80)",
        vital_sugar: "రక్తంలో చక్కెర",
        placeholder_sugar: "స్థాయి mg/dL",
        vital_bmi: "BMI",
        placeholder_bmi: "BMI విలువ",
        vital_temp: "ఉష్ణోగ్రత",
        placeholder_temp: "°F",
        btn_analyze: "విశ్లేషించు",
        btn_book_doc: "డాక్టర్ అపాయింట్‌మెంట్ బుక్ చేయండి",
        label_doctor: "డాక్టర్ / స్పెషలిస్ట్‌ను ఎంచుకోండి",
        label_date: "తేదీ",
        label_time: "సమయం",
        btn_confirm_apt: "అపాయింట్‌మెంట్‌ను నిర్ధారించండి",
        postop_setup_title: "పోస్ట్-ఆప్ సెటప్",
        label_surgery_type: "మీరు ఇటీవల ఏ శస్త్రచికిత్స చేయించుకున్నారు?",
        placeholder_surgery: "ఉదాహరణ: మోకాలి మార్పిడి",
        btn_start_ai: "AI ఫాలో-అప్‌ను ప్రారంభించండి",
        ai_assistant_title: "మెడికల్ AI అసిస్టెంట్",
        ai_welcome_msg: "నమస్కారం, నేను మీ పోస్ట్ ఆపరేటివ్ AI అసిస్టెంట్‌ని. ఈరోజు మీరు ఎలా భావిస్తున్నారు? మీ లక్షణాలు ఏమిటి?",
        placeholder_chat: "మీ లక్షణాలను టైప్ చేయండి...",
        alert_fill_fields: "దయచేసి అన్ని ఫీల్డ్‌లను పూరించండి.",
        alert_one_vital: "దయచేసి కనీసం ఒక వైటల్ పారామితిని నమోదు చేయండి.",
        alert_server_err: "సర్వర్‌కు కనెక్ట్ చేయడంలో లోపం.",
        alert_datetime: "దయచేసి తేదీ మరియు సమయాన్ని ఎంచుకోండి.",
        alert_apt_success: "అపాయింట్‌మెంట్ విజయవంతంగా బుక్ చేయబడింది.",
        msg_typing: "టైప్ చేస్తోంది",
        err_speech: "మైక్రోఫోన్ లోపం. దయచేసి టైప్ చేయండి.",
        err_speech_unsupported: "ఈ బ్రౌజర్‌లో స్పీచ్ రికగ్నిషన్ సపోర్ట్ లేదు.",
        err_phone_missing: "ఫోన్ నంబర్ అందించబడలేదు!",
        msg_call_init: "వాయిస్ కాల్ ప్రారంభించబడుతోంది...",
        msg_call_success: "ఫోన్ డయలర్ తెరవబడుతోంది...",
        severity_label: "తీవ్రత: "
    }
};

function t(key) {
    const langObj = translations[state.language] || translations['English'];
    return langObj[key] || translations['English'][key] || key;
}

function updateDOMTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.innerHTML = t(el.getAttribute('data-i18n'));
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });

    // Update dynamic text
    if (state.patientName) {
        document.getElementById('welcomeText').innerText = t('hello_patient').replace('{name}', state.patientName);
    }
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Theme setup
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    document.getElementById('themeToggle').addEventListener('click', () => {
        setTheme(state.theme === 'light' ? 'dark' : 'light');
    });

    // Language load - STRICTLY force English for splash & language selection
    state.language = 'English';
    updateDOMTranslations(); // Renders Splash and Lang pages freshly in English

    if (!localStorage.getItem('appLang')) {
        navTo('splashScreen');
    } else {
        // If they already chose a language previously, we still show the splash in English first 
        // per your requirements. Wait for user to navigate or we can jump to the next screen if they click 'Get Started'.
        // For now, let's start the app normally from Splash Screen in English. 
        navTo('splashScreen');
    }

    // Replace the chat welcome message bubble's text dynamically with initial lang state
    const msgBubble = document.querySelector('.ai-msg .msg-bubble');
    if (msgBubble) msgBubble.innerHTML = t('ai_welcome_msg');
});

function setTheme(mode) {
    state.theme = mode;
    document.body.setAttribute('data-theme', mode);
    localStorage.setItem('theme', mode);
    const icon = document.querySelector('#themeToggle i');
    icon.className = mode === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// --- Navigation ---
function navTo(screenId) {
    document.querySelectorAll('.page').forEach(el => {
        el.classList.remove('active');
        setTimeout(() => el.classList.add('hidden'), 400);
    });

    setTimeout(() => {
        const target = document.getElementById(screenId);
        target.classList.remove('hidden');
        void target.offsetWidth;
        target.classList.add('active');
    }, 400);
}

// --- Setup flow ---
function setLanguage(lang) {
    state.language = lang;
    localStorage.setItem('appLang', lang);
    updateDOMTranslations();

    const tt = { 'English': 'English', 'Hindi': 'Hindi', 'Telugu': 'Telugu' };
    speak(lang === 'English' ? 'Language set to English' : lang === 'Hindi' ? 'Bhasha Hindi set ho gayi hai' : 'Bhasha Telugu set cheyabadindi');
    navTo('profileScreen');
}

function saveProfile() {
    const n = document.getElementById('patientName').value.trim();
    const p = document.getElementById('patientPhone').value.trim();

    if (!n || !p) {
        showFloatingAlert(t('alert_fill_fields'));
        return;
    }

    state.patientName = n;
    state.patientPhone = p;
    document.getElementById('welcomeText').innerText = t('hello_patient').replace('{name}', n);
    navTo('mainMenu');
}

function startPostOpFlow() {
    if (!state.surgeryType) {
        navTo('postOpCollect');
    } else {
        navTo('chatbotScreen');
    }
}

// --- Basic Checkup ---
function toggleVital(divId) {
    const el = document.getElementById(divId);
    if (el.classList.contains('hidden')) {
        document.querySelectorAll('.vital-inputs').forEach(e => {
            e.classList.add('hidden');
        });
        el.classList.remove('hidden');
    } else {
        el.classList.add('hidden');
    }
}

async function analyzeVitals() {
    const req = {
        patient_name: state.patientName,
        phone_number: state.patientPhone,
        language: state.language,
        blood_pressure_systolic: parseInt(document.getElementById('bpSystolic').value) || 0,
        blood_pressure_diastolic: parseInt(document.getElementById('bpDiastolic').value) || 0,
        blood_sugar: parseInt(document.getElementById('sugar').value) || 0,
        bmi: parseFloat(document.getElementById('bmiVal').value) || 0,
        temperature: parseFloat(document.getElementById('tempVal').value) || 0
    };

    if (!req.blood_pressure_systolic && !req.blood_sugar && !req.temperature) {
        showFloatingAlert(t('alert_one_vital'));
        return;
    }

    try {
        const res = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req)
        });
        const data = await res.json();

        displayVitalsResult(data);
    } catch (e) {
        showFloatingAlert(t('alert_server_err'));
        console.error(e);
    }
}

function displayVitalsResult(data) {
    const resBox = document.getElementById('vitalsResult');
    resBox.classList.remove('hidden');
    const h3 = document.getElementById('vitalsSeverityText');
    const p = document.getElementById('vitalsMessageText');
    const btn = document.getElementById('vitalsBookBtn');

    h3.innerText = t('severity_label') + data.severity.toUpperCase();
    p.innerText = data.message;

    resBox.className = 'result-box mt-2';

    if (data.emergency) {
        resBox.classList.add('critical-res');
        btn.classList.remove('hidden');
        triggerEmergencyBanner();
        speakEmergency();
    } else {
        btn.classList.add('hidden');
        if (data.severity === 'moderate') {
            resBox.style.borderLeftColor = 'var(--warning)';
        }
    }
}

// --- Appointment ---
async function bookAppointment() {
    const doc = document.getElementById('doctorSelect').value;
    const date = document.getElementById('aptDate').value;
    const time = document.getElementById('aptTime').value;

    if (!date || !time) {
        showFloatingAlert(t('alert_datetime'));
        return;
    }

    const confirmMsg = t('confirm_apt_msg') || `Confirm appointment with ${doc} on ${date} at ${time}?`;
    if (!window.confirm(confirmMsg)) {
        return; // User cancelled
    }

    const req = {
        patient_name: state.patientName,
        phone_number: state.patientPhone,
        language: state.language,
        doctor: doc,
        date: date,
        time: time
    };

    try {
        const res = await fetch(`${API_URL}/book-appointment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req)
        });
        const data = await res.json();

        // Already returning to dashboard after waiting for floating alert
        const successMsg = t('alert_apt_success') || "Appointment booked successfully.";
        showFloatingAlert(successMsg);

        // Clear inputs explicitly after submitting
        document.getElementById('aptDate').value = "";
        document.getElementById('aptTime').value = "";

        // Return to Dashboard explicitly
        setTimeout(() => navTo('mainMenu'), 1500);
    } catch (e) {
        showFloatingAlert(t('alert_server_err'));
    }
}

// --- Chatbot ---
function handleChatKey(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    if (!state.surgeryType && document.getElementById('surgeryType').value) {
        state.surgeryType = document.getElementById('surgeryType').value;
    }

    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    input.value = '';

    const req = {
        patient_name: state.patientName,
        phone_number: state.patientPhone,
        surgery_type: state.surgeryType || "General Checkup",
        message: text,
        language: state.language
    };

    const typingId = appendTypingIndicator();

    try {
        const res = await fetch(`${API_URL}/postop-chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req)
        });
        const data = await res.json();

        removeTypingIndicator(typingId);
        appendMessage(data.response_text, 'ai', data.severity);
        speak(data.response_text);

        if (data.alert) {
            triggerEmergencyBanner();
            speakEmergency();
        }

    } catch (e) {
        removeTypingIndicator(typingId);
        appendMessage(t('alert_server_err'), 'ai', 'high');
    }
}

function appendMessage(text, sender, severity = "low") {
    const box = document.getElementById('chatBox');
    const div = document.createElement('div');
    div.className = `message ${sender}-msg`;

    let sevBadge = '';
    if (sender === 'ai' && severity !== 'low' && severity) {
        sevBadge = `<br><span class="badge ${severity} mt-1" style="display:inline-block">${t('severity_label')}${severity}</span>`;
    }

    div.innerHTML = `<div class="msg-bubble">${text}${sevBadge}</div>`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function appendTypingIndicator() {
    const box = document.getElementById('chatBox');
    const div = document.createElement('div');
    const id = 'typing-' + Date.now();
    div.id = id;
    div.className = `message ai-msg`;
    div.innerHTML = `<div class="msg-bubble"><em>${t('msg_typing')} <i class="fas fa-ellipsis-h pulse-anim"></i></em></div>`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// --- Speech Recognition ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('chatInput').value = transcript;
        document.getElementById('micBtn').classList.remove('recording');
        sendMessage();
    };

    recognition.onerror = function (event) {
        document.getElementById('micBtn').classList.remove('recording');
        showFloatingAlert(t('err_speech'));
    };

    recognition.onend = function () {
        document.getElementById('micBtn').classList.remove('recording');
    };
}

function toggleVoice() {
    if (!recognition) {
        showFloatingAlert(t('err_speech_unsupported'));
        return;
    }

    const btn = document.getElementById('micBtn');
    if (btn.classList.contains('recording')) {
        recognition.stop();
        btn.classList.remove('recording');
    } else {
        const langMap = { 'English': 'en-US', 'Hindi': 'hi-IN', 'Telugu': 'te-IN' };
        recognition.lang = langMap[state.language] || 'en-US';
        recognition.start();
        btn.classList.add('recording');
    }
}

// --- Text to Speech & Alerts ---
function speak(text) {
    if (!window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(text);

    const langMap = { 'English': 'en-US', 'Hindi': 'hi-IN', 'Telugu': 'te-IN' };
    utterance.lang = langMap[state.language] || 'en-US';

    window.speechSynthesis.speak(utterance);
}

function speakEmergency() {
    const msgs = {
        'English': 'Emergency detected. Please consult a doctor immediately.',
        'Hindi': 'Aapatkalin sthiti. Kripya turant doctor se milein.',
        'Telugu': 'Athyavasara paristhithi. Ventane doctor ni kalavandi.'
    };
    speak(msgs[state.language] || msgs['English']);
}

function triggerEmergencyBanner() {
    const eb = document.getElementById('emergencyBanner');
    eb.classList.remove('hidden');
    setTimeout(() => eb.classList.add('hidden'), 5000);
}

function showFloatingAlert(msg) {
    const alert = document.getElementById('floatingAlert');
    alert.innerText = msg;
    alert.classList.remove('hidden');
    setTimeout(() => alert.classList.add('hidden'), 3500);
}

// --- Customer Care Calling ---
async function callCustomerCare() {
    if (!state.patientPhone) {
        showFloatingAlert(t('err_phone_missing'));
        return;
    }

    showFloatingAlert(t('msg_call_init'));

    try {
        const res = await fetch(`${API_URL}/customer-care-call`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_name: state.patientName || "Patient",
                phone_number: state.patientPhone,
                language: state.language,
                reason: "User requested customer care assistance."
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            showFloatingAlert("You will receive a voice call on your phone shortly.");
        }
    } catch (e) {
        showFloatingAlert(t('alert_server_err'));
    }
}
