# OCS Keyboard
OCS Keyboard is a program for Windows that utilizes VRC's avatar OSC capabilities and KillFrenzy's VRC Avatar Keyboard to allow users to type in VRChat.

![OCSKeyboardDemo](OSCKeyboardDemo.gif)

## Requirements
- Windows is required for foreground window detection
- Your avatar must have [KillFrenzy's VRC Avatar Keyboard](
https://github.com/killfrenzy96/KillFrenzyVRCAvatarKeyboard) on it.
    - This package is not currently working by itself, however, **it does work with OSC**
    - Follow the provided setup, but you can skip any setup relating to gestures, colliders, and actions menu setup as all input will be handled using parameters and OSC
    - Things you can skip adding or delete include:
        - `Trigger Left`, `Trigger Right`, `Keyboard Collider Left`, `Keyboard Collider Right` layers in the provided animator controllers `VRCAC_KeyboardController_Action` and `VRCAC_KeyboardController_FX`
        - `VRCEM_KeyboardMenu` and `VRCEM_KeyboardSubMenu`
- `pip install -r requirements.txt` and run the python program
- Alternatively download the executable in [releases](https://github.com/ShadowForests/OSCKeyboard/releases)

## How To Use
- Edit config such as key delay and mappings in config.json
- Enable OSC in the VRChat Action Menu under Options -> OSC
- Press `=` to toggle the keyboard on and off
- While the keyboard is enabled:
    - Type to write - inputs are buffered to help with sync
    - Supported input: A-Z, 0-9, spacebar, backspace, enter
    - Press `ENTER` to clear out the current displayed text
    - Press `]` to mirror text to either face you or others
    - Press `-` to toggle typing mode to allow movement and
      other actions while keeping text and keyboard visible

- OSC Keyboard is only active when you are focused on the VRChat window, unless the `require_focus` config option is `false`
- The visual keyboard is non-functional and only present as part of the keyboard prefab
- Only OSC events are sent to VRChat when the keyboard and typing mode are enabled
- All other keyboard inputs to the game (such as walking or opening menus) are disabled to allow ease of typing
- If you have sync issues with other players, you can adjust the `key_delay` config option

## Config Parameters
These parameters can be adjusted inside `config.json`, which must be in the same directory as the program. This can also potentially allow usage of this program with other custom avatar keyboards.
- `ip`: OSC IP
- `port`: OSC Port
- `require_focus`: Require focusing on the window for inputs
- `window`: Target window to restrict inputs in
- `key_delay`: Delay between key presses
- `keyboard_key`: Key to toggle keyboard
- `typing_mode_key`: Key to toggle typing mode
- `mirror_key`: Key to toggle text mirror
- `enter_key`: Key to clear text
- `key_mapping`: Mapping of key to parameter value
- `osc_prefix`: OSC path prefix
- `keyboard_param`: OSC keyboard parameter name
- `key_params`: OSC key parameter names
