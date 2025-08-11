# ahk-cursor

<a href="https://pypi.org/project/soda-ahk-cursor/">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/soda-ahk-cursor">
</a>

move cursor randomly

install:
```
pip install -U soda-ahk-cursor
```

Run:
```
soda-ahk-cursor
```

# Reason

This is dedicated for playing game [Eustia][1].

See also [this issue][2].

[1]: https://en.wikipedia.org/wiki/Aiyoku_no_Eustia
[2]: https://www.reddit.com/user/HeronTimeN/comments/1hnpt0k/eustia_move_cursor/

# Thanks

Python standard library:
 - multiprocessing: <https://docs.python.org/3/library/multiprocessing.html>
 - I use [Queues](https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues) to pass massages between processes.

without these great libraries this project won't exist:

- <https://fastapi.tiangolo.com/>
    - used for receving server shutdown message. 
- <https://requests.readthedocs.io/en/latest/>
    - used for sending test/shutdown messages to server.
- <https://www.uvicorn.org/#fastapi>
    - used to run fastapi.
- <https://pyautogui.readthedocs.io/en/latest/index.html>
    - Move cursors.
- <https://github.com/mhammond/pywin32>
    - Create shortcut in startup folder.


This project is developed using [UV](https://docs.astral.sh/uv/) and [ruff](https://docs.astral.sh/ruff/).

Also there are many great doc/blog writers:
 - Official windows API docs: <https://learn.microsoft.com/en-us/>.
 - api taken from <https://gist.github.com/topin89/f8156a64ee79ff034cdf74c238b0dfa7>.
 - idea also from <https://docs.rs/tasklist/latest/src/tasklist/lib.rs.html#77>.
 - also see <https://hellocode.co/blog/post/tracking-active-process-windows-rust/>.


## Other

running without console & taskbar icon is done using [autohotkey](https://www.autohotkey.com/).

Icons created using [Krita](https://krita.org/en/) and [em-keyboard](https://github.com/hugovk/em-keyboard).

developped using vscode and Jedi.

Hosted on GitHub.
