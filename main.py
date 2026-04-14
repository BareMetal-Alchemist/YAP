import pyaudio
import audioop
import speech_recognition as sr
import ollama
import pyttsx3
import time



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
                "InputFailed": "Confused",
                "error": "Error",
                "timeout": "Idle",
                "cancel": "Idle",
            },
            "Thinking": {
                "responseReady": "Speaking",
                "error": "Idle",
            },
            "Speaking": {
                "done": "Idle",
                "interrupted": "Listening",
                "follow_up": "Listening",
            },
            "Confused": {
                "done": "Listening"
            },
            "Error": {
                "done": "Idle"
            }
        }

    def handleEvent(self, event):
        stateEvents = self.stateTransition.get(self.state, {})

        if event not in stateEvents:
            raise ValueError(f"Event {event!r} is not a valid for state {self.state!r}")

        self.state = stateEvents[event]
        return self.state


# Initialized Objects

sm = StateMachine()

engine = pyttsx3.init()

r = sr.Recognizer()

text = ""

response = None

res = ""

while True:

    if sm.state == "Idle":
        print("Press 1 to talk.")
        print("Press 2 to quit.")

        userInput = int(input(": "))

        if userInput == 1:
            sm.handleEvent("wake")
            continue
        elif userInput == 2:
            print("Bye!")
            engine.stop()
            engine.say("Bye!")
            engine.runAndWait()
            break

    elif sm.state == "Listening":
        print("Say something!")
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            sm.handleEvent("heardInput")
        except sr.UnknownValueError:
            sm.handleEvent("InputFailed")
            continue
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition")
            sm.handleEvent("error")
            continue



    elif sm.state == "Thinking":
        print("Hmmmm...")
        prompt = f"{text}.\n\n(Please keep responses no longer than 2 sentences)"
        response = ollama.chat(
            model="gemma3",
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 50},
        )
        sm.handleEvent("responseReady")



    elif sm.state == "Speaking":
        res = response["message"]["content"]
        n = len(res.split())
        secs = n * 0.4
        print(res)
        engine.stop()
        engine.say(response["message"]["content"])
        engine.runAndWait()
        time.sleep(secs)
        engine.stop()
        sm.handleEvent("done")
        continue

    elif sm.state == "Confused":
        print("Could not understand audio")
        engine.stop()
        engine.say("I'm sorry, but I can't understand. What did you say?")
        engine.runAndWait()
        time.sleep(1)
        sm.handleEvent("done")
        continue

    elif sm.state == "Error":
        print("Could not request results from Google Speech Recognition")
        engine.stop()
        engine.say("Could not request results from Google Speech Recognition")
        engine.runAndWait()
        time.sleep(1)
        sm.handleEvent("done")
        continue







