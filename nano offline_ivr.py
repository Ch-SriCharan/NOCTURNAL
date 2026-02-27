import os
import pyttsx3
import time

engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print("IVR:", text)
    engine.say(text)
    engine.runAndWait()

def initiate_call(patient_name):

    print(f"📞 Calling {patient_name}...")

    # play ringtone
    os.system("aplay ringtone.wav")

    time.sleep(1)

    speak(f"Hello {patient_name}. This is your hospital follow up assistant.")

    speak("Press 1 if you are feeling fine.")
    speak("Press 2 if you have mild symptoms.")
    speak("Press 3 if your condition worsened.")

    choice = input("Enter choice: ")

    if choice == "1":
        speak("Recovery is normal.")
    elif choice == "2":
        speak("We will follow up tomorrow.")
    elif choice == "3":
        speak("Alerting doctor immediately.")
        print("⚠ DOCTOR ALERT TRIGGERED")
    else:
        speak("Invalid input.")

initiate_call("Adith")