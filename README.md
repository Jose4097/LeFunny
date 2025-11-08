# LeFunny

Small desktop overlay app that shows random jumpscares on your screen. Each jumpscare has its own animation and sound. Built with PyQt6.

## Quick description

LeFunny displays fullscreen animated jumpscares (GIF or PNG frames) together with a WAV sound. It usually runs on a schedule (random intervals) or be triggered manually via the UI. Settings are controlled from the small "Le Funny - Control" window.

If you are lazy and don't care about the code just install the EXE from the folder dist lmao.

Windows will for sure not like running it the first time since it doesn't have a signature but I assure you it's safe, you got the code anyways.

## Requirements (if intended to be ran by python and not the EXE)

- Windows (tested)
- Python 3.8+
- PyQt6

Install deps:

```
pip install PyQt6
```

## Running from source

1. Put the `assets/` folder next to `LeFunny.py`. Each jumpscare should live in its own subfolder inside `assets/`.
2. Run:

```
python LeFunny.py
```

## Adding new jumpscares

1. Create a subfolder under `assets/`, e.g. `assets/MyScare/`.
2. Add `animation.gif` (or a sequence of PNGs) and `sound.wav` into that folder.
3. Add the jumpscare name to the `desired_order` list in `LeFunny.py` (near the top of the UI setup) so it appears in the selector, and add a duration in milliseconds to `JUMPSCARE_DURATIONS`.

Example structure:

```
assets/
  icon.ico
  Foxy/
    animation.gif
    sound.wav
  MyScare/
    animation.gif
    sound.wav
```

## Building a single executable (PyInstaller)

From the project folder run:

```
pyinstaller --noconfirm --onefile --windowed --add-data "assets;assets" --icon "assets/icon.ico" LeFunny.py
```

- After building, the standalone executable will be placed in the `dist\` folder. You can distribute that EXE (and keep the `assets` folder next to it if you prefer to edit assets externally).
- On Windows the `--add-data "assets;assets"` syntax bundles the `assets` folder; when using `--onefile` PyInstaller extracts files at runtime. If you want to ship editable assets, copy the `dist\<your exe name>.exe` and the `assets\` folder together.

## Notes

- If you add many or large assets, packaging size and memory usage will increase.
- For troubleshooting, run the script from source to see printed logs and errors.

License: personal / use as you like.
