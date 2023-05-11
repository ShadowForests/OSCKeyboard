# OSC Keyboard
OSC Keyboard is a program for Windows that utilizes VRC's avatar OSC capabilities and KillFrenzy Avatar Text to allow users to type in VRChat.

![OSCKeyboardDemo](OSCKeyboardDemo.gif)

## Requirements
- Windows is required for foreground window detection
- Your avatar must have [KillFrenzy Avatar Text](https://github.com/killfrenzy96/KillFrenzyAvatarText) on it
- Download and run the executable in [releases](https://github.com/ShadowForests/OSCKeyboard/releases)
- Alternatively `pip install -r requirements.txt` and run the python program

## How To Use
- Edit config such as key delay and mappings in config.json
- Enable OSC in the VRChat Action Menu under Options -> OSC
- Press `=` to enable your keyboard, press `ESC` to disable
- While the keyboard is enabled...
    - Type to write - inputs will be handled to ensure sync
    - Supported input: A-Z, 0-9, spacebar, backspace, enter
    - Press `ENTER` to clear out the current displayed text
    - Press `F1` to turn on or off typing mode to allow for
      other actions while keeping the existing text visible
    - Copy, cut, paste, and control+backspace are supported
    - Japanese hiragana and katakana input is also possible

- OSC Keyboard is only active when you are focused on the VRChat window, unless the `require_focus` config option is `false`
- OSC events are sent to VRChat when the keyboard and typing mode are enabled and in use
- All other inputs to the game (such as walking or opening menus) are disabled to allow ease of typing
- If you have sync issues with other players, you can try increasing the `key_delay` config option

## Config Parameters
These parameters can be adjusted inside `config.json`, which must be in the same directory as the program. This can also potentially allow usage of this program with other custom avatar keyboards.
- `ip`: OSC IP
- `port`: OSC Port
- `realtime_input`: Whether to enable instant feedback typing with delayed sync or use buffered text input
- `require_focus`: Require focusing on the window for inputs
- `window`: Target window to restrict inputs in
- `key_delay`: Delay between key presses - setting this below 0.25 seconds may increase sync issues for other players
- `sync_param_count`: Amount of parameters to use for syncing text
- `transcript`: Enables a transcript log of keyboard messages
- `auto_format_text`: Enable some automatic text formatting such as normalizing unicode characters or splitting dakuten and handakuten from katakana
- `socket_connection`: Enables a socket server connection to allow external input to the keyboard
- `socket_ip`: Socket IP
- `socket_port`: Socket Port
- `enable_keyboard_key`: Key to enable keyboard
- `disable_keyboard_key`: Key to disable keyboard
- `typing_mode_key`: Key to toggle typing mode
- `key_mapping`: Mapping of key to parameter value
- `max_length`: Max length of keyboard display
- `osc_prefix`: OSC path prefix
- `keyboard_param`: OSC keyboard parameter name
- `pointer_param`: OSC pointer parameter name
- `key_params`: OSC key parameter names
