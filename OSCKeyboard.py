# OSC Keyboard by ShadowForest
# https://github.com/ShadowForests/OSCKeyboard

from win32gui import GetWindowText, GetForegroundWindow
from pythonosc import udp_client
import keyboard
import json
import time

class OSCKeyboard:
    def __init__(self, config_file=""):
        self.load_default_config()
        if config_file != "":
            with open(config_file, "r") as f:
                config = json.load(f)
                # OSC IP
                self.ip = self.load_config_entry(self.ip, config, "ip")
                # OSC Port
                self.port = self.load_config_entry(self.port, config, "port")
                # Require focusing on the window for inputs
                self.require_focus = self.load_config_entry(self.require_focus, config, "require_focus")
                # Target window to restrict inputs in
                self.window = self.load_config_entry(self.window, config, "window")
                # Delay between key presses
                self.key_delay = self.load_config_entry(self.key_delay, config, "key_delay")
                # Key to toggle keyboard
                self.keyboard_key = self.load_config_entry(self.keyboard_key, config, "keyboard_key")
                # Key to toggle typing mode
                self.typing_mode_key = self.load_config_entry(self.typing_mode_key, config, "typing_mode_key")
                # Key to toggle text mirror
                self.mirror_key = self.load_config_entry(self.mirror_key, config, "mirror_key")
                # Key to clear text
                self.enter_key = self.load_config_entry(self.enter_key, config, "enter_key")
                # Mapping of key to parameter value
                self.key_mapping = self.load_config_entry(self.key_mapping, config, "key_mapping")
                # OSC path prefix
                self.osc_prefix = self.load_config_entry(self.osc_prefix, config, "osc_prefix")
                # OSC keyboard parameter name
                self.keyboard_param = self.load_config_entry(self.keyboard_param, config, "keyboard_param")
                # OSC key parameter names
                self.key_params = self.load_config_entry(self.key_params, config, "key_params")

        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        self.keyboard_enabled = False
        self.typing_mode_enabled = True
        self.mirror_enabled = False
        self.input_hook = None
        self.enabler_hook = None

    def load_config_entry(self, entry, config, entry_name):
        if entry_name in config:
            return config[entry_name]
        return entry

    def load_default_config(self):
        self.ip = "127.0.0.1"
        self.port = 9000
        self.require_focus = True
        self.window = "VRChat"
        self.key_delay = 0.25
        self.keyboard_key = "="
        self.typing_mode_key = "-"
        self.mirror_key = "]"
        self.enter_key = "enter"
        self.key_mapping = {
            "0": 16,
            "1": 17,
            "2": 18,
            "3": 19,
            "4": 20,
            "5": 21,
            "6": 22,
            "7": 23,
            "8": 24,
            "9": 25,
            "a": 33,
            "b": 34,
            "c": 35,
            "d": 36,
            "e": 37,
            "f": 38,
            "g": 39,
            "h": 40,
            "i": 41,
            "j": 42,
            "k": 43,
            "l": 44,
            "m": 45,
            "n": 46,
            "o": 47,
            "p": 48,
            "q": 49,
            "r": 50,
            "s": 51,
            "t": 52,
            "u": 53,
            "v": 54,
            "w": 55,
            "x": 56,
            "y": 57,
            "z": 58,
            "space": 95,
            "backspace": 254,
            "enter": 255
        }
        self.osc_prefix = "/avatar/parameters/"
        self.keyboard_param = "Keyboard"
        self.key_params = [
            "KeyboardLetterSync1",
            "KeyboardLetterSync2"
        ]

    def is_correct_window(self):
        if not self.require_focus:
            return True
        return GetWindowText(GetForegroundWindow()).lower() == self.window.lower()

    def enable_keyboard(self):
        if self.mirror_enabled:
            self.client.send_message(self.osc_prefix + self.keyboard_param, 12)
        else:
            self.client.send_message(self.osc_prefix + self.keyboard_param, 1)
        time.sleep(self.key_delay)

    def disable_keyboard(self):
        self.client.send_message(self.osc_prefix + self.keyboard_param, 0)
        time.sleep(self.key_delay)

    def press_enable(self, key_name):
        if not self.typing_mode_enabled and self.press_disable(key_name):
            # Disable keyboard and typing mode
            return

        if self.keyboard_enabled and key_name == self.typing_mode_key and not self.typing_mode_enabled:
            # Toggle typing mode
            self.typing_mode_enabled = True
            self.input_hook = keyboard.hook(self.handle_inputs, suppress=True)
            keyboard.restore_state([]) # Release any held keys
        elif not self.keyboard_enabled and key_name == self.keyboard_key:
            # Enable keyboard
            self.input_hook = keyboard.hook(self.handle_inputs, suppress=True)
            self.enable_keyboard()
            self.keyboard_enabled = True
            self.typing_mode_enabled = True
            keyboard.restore_state([]) # Release any held keys

    def press_disable(self, key_name):
        if self.keyboard_enabled and key_name == self.keyboard_key:
            # Disable keyboard
            if self.typing_mode_enabled:
                keyboard.unhook(self.input_hook)
            self.disable_keyboard()
            self.keyboard_enabled = False
            self.typing_mode_enabled = False
            return True
        return False
        
    def press_key(self, key_name):
        if self.press_disable(key_name):
            return

        if self.keyboard_enabled:
            if key_name == self.typing_mode_key and self.typing_mode_enabled:
                # Disable typing mode
                self.typing_mode_enabled = False
                keyboard.unhook(self.input_hook)
            elif key_name == self.mirror_key:
                # Toggle mirror
                self.mirror_enabled = not self.mirror_enabled
                self.enable_keyboard()
            elif key_name in self.key_mapping.keys():
                # Typing
                osc_path = self.osc_prefix + self.key_params[0]
                self.client.send_message(osc_path, self.key_mapping[key_name])
                time.sleep(self.key_delay)
                self.client.send_message(osc_path, 0)

                # Shift keyboard message paths array
                self.key_params.append(self.key_params.pop(0))

    def handle_inputs(self, event):
        if self.is_correct_window() and event.event_type == "down":
            self.press_key(event.name)

    def handle_enable(self, event):
        if self.is_correct_window() and event.event_type == "down":
            self.press_enable(event.name)

    def start(self, announce=True):
        if announce:
            print("Switch to the {0} window!".format(self.window))
        self.enabler_hook = keyboard.hook(self.handle_enable)
        keyboard.wait()

    def stop(self):
        keyboard.unhook(self.enabler_hook)

if __name__ == "__main__":
    osc_keyboard = OSCKeyboard(config_file="config.json")
    print("\n".join([
        "OSC Keyboard by ShadowForest",
        "https://github.com/ShadowForests/OSCKeyboard",
        "-----------------------------------------------------------",
        "Recommended Keyboard: KillFrenzy's VRC Avatar Keyboard",
        "https://github.com/killfrenzy96/KillFrenzyVRCAvatarKeyboard",
        "-----------------------------------------------------------",
        "[How To Use]",
        "- Edit config such as key delay and mappings in config.json",
        "- Enable OSC in the VRChat Action Menu under Options -> OSC",
        "- Press `{0}` to toggle the keyboard on and off".format(osc_keyboard.keyboard_key.upper()),
        "- While the keyboard is enabled...",
        "    - Type to write - inputs are buffered to help with sync",
        "    - Supported input: A-Z, 0-9, spacebar, backspace, enter",
        "    - Press `{0}` to clear out the current displayed text".format(osc_keyboard.enter_key.upper()),
        "    - Press `{0}` to mirror text to either face you or others".format(osc_keyboard.mirror_key.upper()),
        "    - Press `{0}` to toggle typing mode to allow movement and".format(osc_keyboard.typing_mode_key.upper()),
        "      other actions while keeping text and keyboard visible",
        "-----------------------------------------------------------"
    ]))
    osc_keyboard.start()
