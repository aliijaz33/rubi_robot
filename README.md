# Rubi Robot

This repository contains the **Rubi** robot simulator and voice‑controlled framework. It was developed on a Mac but is designed to eventually run on a Raspberry Pi with an L298N motor driver and a CSI/USB camera.

The project includes:

- `hardware` – motor interfaces and a Tkinter GUI simulator
- `speech` – speech recognizer using `SpeechRecognition` and macOS `say` for TTS
- `vision` – camera capture and YOLOv8 object detection
- `intelligence` – (future) higher‑level behaviours
- `test_robot.py` – quick startup script demonstrating voice/vision control

---

## Environment setup (conda / Python 3.11)

We recommend using a **Conda** (or Miniforge) environment with **Python 3.11**, which is well supported by the machine‑learning/vision libraries and delivers a pre‑built Tkinter binary so you avoid the \_tkinter import errors.

1. Install a conda distribution if you do not already have one. The lightweight [Miniforge](https://github.com/conda-forge/miniforge) is recommended:

   ```bash
   # fetch installer (adjust URL for your architecture if necessary)
   curl -L -o ~/miniforge.sh \
     https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
   bash ~/miniforge.sh
   # follow prompts, then reload your shell
   source "$HOME/miniforge3/etc/profile.d/conda.sh"
   conda --version  # should show something like 'conda 23.3.1'
   ```

   You may of course install full Anaconda or another conda variant; just
   ensure the `conda` command is on your PATH. Running the commands below
   without a conda installation will result in “command not found”.

2. If you have an existing virtual environment active (e.g. `(venv)`),
   deactivate it first:

   ```bash
   deactivate   # or `conda deactivate` if using conda already
   ```

   Then, from the project root run:

   ```bash
   conda env create -f environment.yml
   conda activate rubi_robot
   ```

   The new conda environment will include a Python interpreter that already
   has Tcl/Tk built in; running from any other `venv` will still trigger the
   `_tkinter` error shown earlier.

3. The `environment.yml` file pins Python 3.11 and pulls in the required
   libraries; `conda` will also install Tcl/Tk automatically, so
   `import tkinter` will succeed.

4. **No conda available?** You can still work with a plain venv, but make
   sure you create it from a Python build that includes Tcl/Tk. For
   example:

   ```bash
   # install Python 3.11 via Homebrew
   brew install python@3.11
   /usr/local/opt/python@3.11/bin/python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   Alternatively rebuild a pyenv interpreter with the `LDFLAGS`/`CPPFLAGS`
   shown earlier. Without Tk support the GUI will raise an ImportError.

5. If you prefer to use `venv` instead of conda in the conda environment,
   you can still use the same Python executable and install packages with
   `pip install -r requirements.txt`.

> The code has been tested on macOS 12/13 with Python 3.11. Other 3.x versions should work as long as they include a `_tkinter` module.

---

## Dependencies

- Python >=3.11
- `conda` (recommended) or virtualenv/venv
- packages (see `environment.yml` / `requirements.txt`):
  - `opencv` (via conda-forge or `opencv-python`)
  - `numpy`
  - `ultralytics` (YOLOv8)
  - `SpeechRecognition`
  - `PyAudio` (for microphone)

**Note:** we intentionally do _not_ depend on `pyttsx3` because macOS's built‑in `say` command is reliable across systems and avoids the issues you encountered earlier.

---

## Running the simulator

After activating the environment:

```bash
python test_robot.py
```

Follow the on‑screen instructions: the Tkinter GUI window will show the robot, arrow keys/space drive it manually, and voice commands starting with `Rubi` will control it. Vision commands (`what do you see`, `find chair`, `find person`) work if a webcam is available and the YOLO model (`yolov8n.pt`) is placed in the project root.

---

## Notes for macOS users

- `say` is used for speech output; no additional configuration is necessary.
- The conda environment brings its own Tcl/Tk, so you won't get a `_tkinter` error.
- If you ever switch to the system Python (3.14) or a pyenv build, make sure it was compiled with Tk support, otherwise `import tkinter` will fail.

---

## Next steps

- Deploy to Raspberry Pi: replace the simulator `MotorController` with an `L298N` driver using `RPi.GPIO`.
- Expand `vision` and `intelligence` modules for autonomous behaviors.

Happy hacking! 🤖
