# AI-Based-Real-Time-Camera-Guidance-System-Using-Computer-Vision-and-Voice-Feedback

A fully functional real-time camera guidance application built using Python, OpenCV, and machine learning techniques. The project processes live video feed, detects objects, and provides actionable guidance to the user.


# Features
1. Real-time object detection and tracking

2. Camera movement guidance system (left/right/up/down)

3. Optimized for fast frame processing

4. Windows executable included

5. Customizable settings through config files

6. Easy-to-use folder structure

 
# Folder Structure
 Directory of C:\Users\dellj\Desktop\Camera Guidance Project

09-11-2025  15:58    <DIR>          .
18-11-2025  10:55    <DIR>          ..
09-11-2025  15:29    <DIR>          build
31-10-2025  17:58           189,151 camera.ico
09-11-2025  15:50             1,292 camera_guidance.spec
09-11-2025  15:53    <DIR>          dist
27-10-2025  15:28    <DIR>          DLLs
27-10-2025  15:28    <DIR>          Doc
28-10-2025  19:08    <DIR>          HOW TO RUN PROGRAM
27-10-2025  15:28    <DIR>          include
27-10-2025  15:28    <DIR>          Lib
27-10-2025  15:28    <DIR>          libs
02-04-2024  12:43            36,874 LICENSE.txt
31-10-2025  17:45            11,735 main.py
09-11-2025  14:50            14,662 main1.py
24-10-2025  18:17    <DIR>          Microsoft VS Code
02-04-2024  12:44         1,563,659 NEWS.txt
02-04-2024  12:43           103,192 python.exe
02-04-2024  12:43            67,352 python3.dll
02-04-2024  12:43         5,800,216 python311.dll
02-04-2024  12:43           101,656 pythonw.exe
27-10-2025  16:27             4,448 realtime_camera_guidance.py
27-10-2025  16:35             6,779 realtime_camera_guidance_final_AI.py
09-11-2025  15:51    <DIR>          Scripts
27-10-2025  15:32    <DIR>          share
27-10-2025  15:28    <DIR>          tcl
27-10-2025  15:28    <DIR>          Tools
02-04-2024  12:43           119,192 vcruntime140.dll
02-04-2024  12:43            49,528 vcruntime140_1.dll
09-11-2025  15:45    <DIR>          venv
              14 File(s)      8,069,736 bytes
              16 Dir(s)  292,587,692,032 bytes free


# Installation (from source)

Clone the repository:

git clone https://github.com/mohitbt66/AI-Based-Real-Time-Camera-Guidance-System-Using-Computer-Vision-and-Voice-Feedback

Step: Download "_internal" file and "AI Real Time Camera Guidance" exe file in same folder. Then run the exe file. The system will start running in your laptop using your laptop's integrated web camera.


# Install dependencies:

pip install -r requirements.txt


Run the application:

python src/main.py



# Build Your Own EXE (PyInstaller)

If you want to generate the EXE yourself:

# 1. Install PyInstaller

pip install pyinstaller


# 2. Run PyInstaller

pyinstaller --noconfirm --onefile --windowed \
 --icon=resources/icon.ico \
 --add-data "models;models" \
 --add-data "config;config" \
 src/main.py


This will generate:

dist/RealTimeCamera.exe


Move it to the build/ folder.



# Requirements

1. Development Software
   Windows 10 / Windows 11 Operating System
   Python 3.10+
   PyCharm / VS Code / Jupyter Notebook (any IDE)
   Tkinter (Built-in Python GUI framework)

2. Required Python Libraries
   OpenCV 4.8+ — for image/video processing
   MediaPipe 0.10+ — for face and hand detection
   NumPy 1.26+ — for mathematical operations
   Pyttsx3 — for offline text-to-speech
   PyInstaller — for packaging into .exe


# Contribution

Contributions are welcome!
Feel free to submit issues or pull requests.

---
