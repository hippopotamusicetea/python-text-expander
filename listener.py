from pynput import keyboard
from collections import deque
from string import ascii_letters, digits
import win32clipboard as w32c
import multiprocessing

mp_event = multiprocessing.Event()


def set_clipboard_data(data):
    w32c.OpenClipboard()
    w32c.EmptyClipboard()
    w32c.SetClipboardText(data)
    w32c.CloseClipboard()


def start_listener(hotkey_dict):
    p = multiprocessing.Process(target=load_listener, args=(hotkey_dict,), daemon=True)
    p.run()


def load_listener(hotkey_dict):
    event_queue = deque(maxlen=get_longest_hotkey(hotkey_dict))
    key_sequence = ""

    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                break
            elif mp_event.is_set():
                break
            else:
                if isinstance(event, keyboard.Events.Press):
                    try:
                        if event.key.char in ascii_letters or digits:
                            event_queue.append(str(event.key.char))
                            key_sequence = "".join(event_queue)
                            for h in hotkey_dict.values():
                                if h["hotkey"] in key_sequence:
                                    r = h["replacement"]
                                    set_clipboard_data(r)
                                    for i in range(len(h["hotkey"])):
                                        keyboard.Controller().tap(
                                            keyboard.Key.backspace
                                        )

                                    keyboard.Controller().press(keyboard.Key.ctrl)
                                    keyboard.Controller().tap("v")
                                    keyboard.Controller().release(keyboard.Key.ctrl)
                                    event_queue.clear()

                    except AttributeError:
                        pass


def get_longest_hotkey(hotkey_dict):
    queue_length = 10
    for v in hotkey_dict.values():
        l = len(v["hotkey"])
        if l > queue_length:
            queue_length = l
    return queue_length


if __name__ == "__main__":
    test_dict = {
        1: {"hotkey": "abc", "replacement": "helo"},
        2: {
            "hotkey": "1234",
            "replacement": "thisis a second helo",
        },
        3: {"hotkey": "qwerty", "replacement": "terd helo"},
        4: {
            "hotkey": "aaaaaa",
            "replacement": "fert",
        },
    }
