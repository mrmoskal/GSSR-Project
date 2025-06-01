# for Gemini API,
import google.generativeai as genai

# speech to text & vise versa
import speech_recognition as sr
import pyttsx3

# for flask server:
# from flask import Flask, render_template, jsonify, request
# from flask_cors import CORS
# import requests

# other useful imports
import json
import os

# global vars:
PROGRAM_QUIT = "[EXIT]"


# A class for the Gemini API requests and general prompt settings
class GeminiAPI:
    def __init__(self):
        # INIT VARS:
        # init settings in order to use Gemini in our server
        # get config from config.json
        with open(os.path.join("config.json")) as config_file:
            config = json.load(config_file)
            # setting the api key to the Gemini api
            genai.configure(api_key=config.get("GEMINI").get("api_key"))
            # prompt rules for this server
            self.PROMPT_RULES = str(config.get("GEMINI").get("prompt_rules"))

        self.model = genai.GenerativeModel("gemini-pro")

    def chat_response(self, prompt: str) -> str:
        # return a response from chat gpt based on a given prompt, and the PROMPT RULES - set in the servers config file.
        response = self.model.generate_content(self.PROMPT_RULES + prompt)

        return response.text  # .strip() - removes any starting or trailing spacing from the message (to make sure there is no unneeded spacing)


# A class for the text to speech & speech to text aspect of the project
class SpeechAndText:
    def __init__(self):
        self.recognizer = sr.Recognizer()  # init the recogniser

    @staticmethod
    def text_to_speech(text: str) -> None:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def speech_to_text(self) -> str:
        STOP_KEY = "end of request"

        with sr.Microphone() as source:
            print("🎤 Say something... ")
            self.recognizer.adjust_for_ambient_noise(source)  # Reduce background noise

            while True:
                try:
                    audio = self.recognizer.listen(source)  # No timeout or phrase time limit
                    text = self.recognizer.recognize_google(audio)  # Convert speech to text
                    if text.strip():
                        print("📝 Recognized Text:", text)
                        return text

                except sr.UnknownValueError:
                    print("😕 Could not understand the audio, please try again...")
                except sr.RequestError:
                    print("🚨 Could not request results, check your internet connection")
                    return ""


# class Server(Flask):
#     def __init__(self, *args, **kwargs):
#         super(Server, self).__init__(__name__, *args, **kwargs)  # INIT FLASK
#         CORS(self)  # Enable CORS
#
#         # INIT VARS:
#         self.gemini_api = GeminiAPI()  # to send user prompt to gemini
#
#         # FUNCTIONS:
#         def get_gemini_response(prompt: str) -> str:
#             return self.gemini_api.chat_response(prompt)
#
#         # FLASK SERVER MAIN RESPONSE:
#         @self.route('/', methods=["GET"])
#         def get_result_from_prompt():
#             print(request.args)
#             prompt = request.args.get('prompt', default="", type=str)
#
#             if not prompt:
#                 return jsonify({"error": "[ERROR]: prompt can not be empty"}), 400
#
#             result = get_gemini_response(prompt)
#
#             if result:
#                 return jsonify({"result": result}), 200
#
#             return jsonify({"error": "[ERROR]: An error occurred while generating response"}), 500


# The function to be run at launch
def main():
    # app_server = Server()
    # app_server.run(host='localhost', port=5555)

    gemini_api = GeminiAPI()  # init Gemini API class
    speech_and_text = SpeechAndText()  # init speech and text class
    request, response = "", ""  # the users request and gemini response - no request/response yet

    # endlessly listen to users requests (until they ask the program to close)
    while True:
        request = speech_and_text.speech_to_text()

        # in case the user did not say anything
        if not request:
            continue

        response = gemini_api.chat_response(request)

        print(response)
        speech_and_text.text_to_speech(response)

        if response.__contains__(PROGRAM_QUIT):
            print("The user requested to quit. shutting down program")
            break


if __name__ == '__main__':
    main()
