import pyaudio
import audioop
import speech_recognition as sr
import ollama
import pyttsx3
import time

engine = pyttsx3.init()

r = sr.Recognizer()

text = ""

# State Machine
class StateMachine:
    def __init__(self):

        self.state = "Idle"
        self.stateTransition = {
            "Idle": {
                "wake": "Listening",
            },
            "Listening": {
                "heardInput": "Thinking",
                "InputFailed": "Listening",
                "timeout": "Idle",
                "cancel": "Idle",
            },
            "Thinking": {
                "responseReady": "Speaking",
                "error": "Idle",
            },
            "Speaking": {
                "done": "Idle",
                "interupted": "Listening",
                "follow_up": "Listening",
            },
        }

    def changeState(self, event):
        stateEvents = self.stateTransition.get(self.state, {})

        if event not in stateEvents:
            raise ValueError(f"Event {event!r} is not a valid for state {self.state!r}")

        self.state = stateEvents[event]
        return self.state















while not text == "bye":
    print("Say something!")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")  
    except sr.UnknownValueError:
        print("Could not understand audio")
        engine.say("Could not understand audio")
        engine.runAndWait()
        time.sleep(1)
        continue
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition")
        engine.say("Could not request results from Googl Speech Recognition")
        engine.runAndWait()
        time.sleep(1)
        continue

    if text == "exit":
        engine.say("Bye")
        engine.runAndWait()
        break
    prompt = f"{text}.\n\n(Please keep responses no longer than 2 sentences)"
    response = ollama.chat(
        model="gemma3",
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": 50},
    )
    res = response["message"]["content"]
    n = len(res.split())
    secs = n * 0.4
    print(response["message"]["content"])
    engine.say(response["message"]["content"])
    engine.runAndWait()
    time.sleep(secs)
