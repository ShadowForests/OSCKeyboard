# OSC Keyboard by ShadowForest
# https://github.com/ShadowForests/OSCKeyboard

# Copyright (c) 2022 ShadowForest

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__version__ = "2.0.0"

from win32gui import GetWindowText, GetForegroundWindow
from threading import Event, Thread
from pythonosc import udp_client
from tkinter import Tk
import unicodedata
import pyperclip
import datetime
import keyboard
import json
import time

from engineio.async_drivers import gevent
from flask_socketio import SocketIO, emit
from flask import Flask, request

class SingleThread(Thread):
    def __init__(self, callback, event):
        Thread.__init__(self)
        self.stop = event
        self.callback = callback
        self.daemon = True

    def run(self):
        if not self.stop:
            try:
                self.callback()
            except:
                pass

class OSCKeyboard:
    def __init__(self, config_file=""):
        self.load_default_config()
        if config_file != "":
            with open(config_file, "r", encoding="utf-8") as file:
                config = json.load(file)
                # OSC IP
                self.ip = self.load_config_entry(self.ip, config, "ip")
                # OSC Port
                self.port = self.load_config_entry(self.port, config, "port")
                # Target window to restrict inputs in
                self.window = self.load_config_entry(self.window, config, "window")
                # Enables a transcript log of keyboard messages
                self.transcript = self.load_config_entry(self.transcript, config, "transcript")
                # Send text immediately instead of opening the keyboard and populating with text
                self.send_immediate = self.load_config_entry(self.send_immediate, config, "send_immediate")
                # Enables a socket server connection to allow external input to the keyboard
                self.socket_connection = self.load_config_entry(self.socket_connection, config, "socket_connection")
                # Socket IP
                self.socket_ip = self.load_config_entry(self.socket_ip, config, "socket_ip")
                # Socket Port
                self.socket_port = self.load_config_entry(self.socket_port, config, "socket_port")
                # Key to enable keyboard
                self.enable_keyboard_key = self.load_config_entry(self.enable_keyboard_key, config, "enable_keyboard_key")
                # Key to disable keyboard
                self.disable_keyboard_key = self.load_config_entry(self.disable_keyboard_key, config, "disable_keyboard_key")
                # OSC chatbox input path
                self.osc_chatbox_input = self.load_config_entry(self.osc_chatbox_input, config, "osc_chatbox_input")
                # OSC chatbox typing path
                self.osc_chatbox_typing = self.load_config_entry(self.osc_chatbox_typing, config, "osc_chatbox_typing")

        warnings = []

        keyboard._winkeyboard._setup_name_tables()
        if self.enable_keyboard_key not in keyboard._winkeyboard.from_name.keys():
            warnings.append(f"[WARN] Enable keyboard key '{self.enable_keyboard_key}' was not found in valid keys and may not work!")

        if self.enable_keyboard_key not in keyboard._winkeyboard.from_name.keys():
            warnings.append(f"[WARN] Disable keyboard key '{self.disable_keyboard_key}' was not found in valid keys and may not work!")

        if len(warnings) > 0:
            print("\n".join(warnings) + "\n-----------------------------------------------------------")

        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        self.keyboard_enabled = False
        self.input_window_name = "OSCKeyboard - Text Input Listener"
        self.text = ""

        # Threads
        self.socket_stop_flag = None
        self.socket_thread = None

    def load_config_entry(self, entry, config, entry_name):
        if entry_name in config:
            return config[entry_name]
        return entry

    def load_default_config(self):
        self.ip = "127.0.0.1"
        self.port = 9000

        self.window = "VRChat"
        self.transcript = True
        self.send_immediate = True

        self.voice_cutoff_time = 3
        self.socket_connection = True
        self.socket_ip = "127.0.0.1"
        self.socket_port = 3000

        self.enable_keyboard_key = "="
        self.disable_keyboard_key = "esc"
        self.osc_chatbox_input = "/chatbox/input"
        self.osc_chatbox_typing = "/chatbox/typing"

    def is_correct_window(self):
        if not self.require_focus:
            return True
        foreground_window = GetWindowText(GetForegroundWindow()).lower()
        return foreground_window == self.window.lower() or foreground_window == self.input_window_name.lower()

    def print_transcript_line(self, text=None):
        if not self.transcript:
            return

        if text is None:
            text = self.text

        if text != "":
            print(f"[CHAT] {datetime.datetime.fromtimestamp(time.time()).strftime('[%H:%M:%S]')} {text}")

    def send_text(self, text):
        self.client.send_message(self.osc_chatbox_input, [text, self.send_immediate])
        return

    def send_status(self, typing=False):
        self.client.send_message(self.osc_chatbox_typing, typing)
        return

    def handle_socket(self):
        app = Flask(__name__)
        socketio = SocketIO(app, logger=False, cors_allowed_origins='*')
        self.socketio = socketio

        @socketio.on("status")
        def on_status(status):
            print(f"[INFO] Status: {status}")
            pass

        @socketio.on("speech")
        def on_speech(speech, translated_speech, untranslated_speech, input_lang, output_lang, translate_enabled, low_latency_enabled, tts_enabled, interim_addition=False, pad_spacing=False):
            #print(input_lang, output_lang, translate_enabled, low_latency_enabled, tts_enabled, interim_addition, pad_spacing)
            #print("[INFO] Speech: " + speech)

            if interim_addition and pad_spacing:
                self.send_text(" " + speech)
            else:
                self.send_text(speech)
            self.print_transcript_line(text=speech)

        @socketio.on("connect")
        def on_connect():
            print(f"[INFO] Client connected: {request.sid}")
            pass

        @socketio.on("disconnect")
        def on_disconnect():
            print(f"[INFO] Client disconnected: {request.sid}")
            pass

        socketio.run(app, host=self.socket_ip, port=self.socket_port)

    def start(self):
        print("[INFO] OSC Keyboard has started!")
        #print(f"[INFO] Switch to the {self.window} window!")

        if self.socket_connection:
            self.socket_thread = SingleThread(self.handle_socket, self.socket_stop_flag)
            self.socket_thread.start()
            self.socket_stop_flag = Event()

        keyboard.wait()

    def stop(self):
        self.socket_thread = None
        self.socket_stop_flag.set()

if __name__ == "__main__":
    osc_keyboard = OSCKeyboard(config_file="config.json")
    print("\n".join([
        "OSC Keyboard [v{0}] by ShadowForest".format(__version__),
        "https://github.com/ShadowForests/OSCKeyboard",
        "-----------------------------------------------------------",
        "[How To Use]",
        "- View and edit all configurable options inside config.json",
        "- Enable OSC in the VRChat Action Menu under Options -> OSC",
        # "- Press `{0}` to enable your keyboard, press `{1}` to disable".format(osc_keyboard.enable_keyboard_key.upper(), osc_keyboard.disable_keyboard_key.upper()),
        "-----------------------------------------------------------"
    ]))
    osc_keyboard.start()
