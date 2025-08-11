import time
import pyautogui
from pathlib import Path

CURRENT = Path(__file__).resolve().parent


def move_cursor():
    x, y = pyautogui.position()
    for _i in range(5):
        try:
            pyautogui.moveTo(x + 1, y, 0.1)
        except pyautogui.FailSafeException:
            pass
        time.sleep(0.1)
        x, y = pyautogui.position()
    for _i in range(5):
        try:
            pyautogui.moveTo(x - 1, y, 0.1)
        except pyautogui.FailSafeException:
            pass
        time.sleep(0.1)
        x, y = pyautogui.position()
