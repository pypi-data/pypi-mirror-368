from pathlib import Path
import os
import shutil

APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA")) / "ahk_cursor"

CURRENT = Path(__file__).resolve().parent
gen_dir = APP_DATA_DIR
script = gen_dir.joinpath("Cursor.ahk")


def gen():
    gen_dir.mkdir(exist_ok=True)
    shutil.copy(CURRENT.joinpath("mouse.ico"), gen_dir)

    content = CURRENT.joinpath("Cursor.template.ahk").read_text(encoding="utf8")
    content = content.replace("{resources}", str(APP_DATA_DIR))

    script.write_text(content, encoding="utf8")
