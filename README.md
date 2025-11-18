# AI-Based-Real-Time-Camera-Guidance-System-Using-Computer-Vision-and-Voice-Feedback

A fully functional real-time camera guidance application built using Python, OpenCV, and machine learning techniques. The project processes live video feed, detects objects, and provides actionable guidance to the user.

---

## 🚀 Features

* 🟢 *Real-time object detection and tracking*
* 🎯 *Camera movement guidance system* (left/right/up/down)
* ⚡ Optimized for fast frame processing
* 🖥️ Windows executable included
* 🔧 Customizable settings through config files
* 📦 Easy-to-use folder structure

---

## 📁 Folder Structure


YourProjectName/
│
├── src/
│   ├── main.py
│   ├── detection.py
│   ├── camera.py
│   ├── utils.py
│
├── models/
│   └── model.onnx
│
├── config/
│   ├── settings.yaml
│   └── labels.txt
│
├── resources/
│   └── icon.png
│
├── build/
│   └── RealTimeCamera.exe       # Download from Releases
│
├── requirements.txt
├── README.md
└── .gitignore


---

## 🛠️ Installation (from source)

Clone the repository:

bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>


Install dependencies:

bash
pip install -r requirements.txt


Run the application:

bash
python src/main.py


---

## 🖥️ Download EXE (Windows)

You can download the ready-to-use EXE from the *Releases* section on GitHub:

👉 *Go to Releases → Download RealTimeCamera.exe*

---

## ⚙️ Build Your Own EXE (PyInstaller)

If you want to generate the EXE yourself:

### 1. Install PyInstaller

bash
pip install pyinstaller


### 2. Run PyInstaller

bash
pyinstaller --noconfirm --onefile --windowed \
 --icon=resources/icon.ico \
 --add-data "models;models" \
 --add-data "config;config" \
 src/main.py


This will generate:


dist/RealTimeCamera.exe


Move it to the build/ folder.

---

## 🤖 Requirements

* Python 3.8+
* OpenCV
* numpy
* onnxruntime (or TensorFlow/PyTorch—based on your model)
* PyQt5 / Tkinter (if GUI)

---

## 📜 License

MIT License (or whichever license you want).

---

## 🙌 Contribution

Contributions are welcome!
Feel free to submit issues or pull requests.

---
