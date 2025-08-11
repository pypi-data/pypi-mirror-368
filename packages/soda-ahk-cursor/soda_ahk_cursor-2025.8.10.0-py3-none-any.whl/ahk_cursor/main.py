from ahk_cursor.gen import gen, script  # 调用生成器
from ahk_cursor.autostart import create  # 调用创建器
import os

def main():
    gen()
    print(f"Generated: {script}")
    create(script)
    os.startfile(script)


if __name__ == "__main__":
    main()
