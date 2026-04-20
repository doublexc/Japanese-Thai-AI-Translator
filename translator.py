#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#.\.venv\Scripts\Activate.ps1
#python d:/Eclip/VScode/translator.py
import sys
import threading
import numpy as np
import pyaudio
import traceback
from faster_whisper import WhisperModel
from googletrans import Translator
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# --- จุดที่จูนใหม่ ---
MODEL_SIZE = "small"  # ขยับความฉลาดขึ้นมาหนึ่งขั้น
TARGET_LANGUAGE = "ja" # ล็อคเป็นญี่ปุ่น (ถ้าจะดูอังกฤษให้เปลี่ยนเป็น 'en')
MIN_AUDIO_THRESHOLD = 2500 # เพิ่มเกณฑ์เสียง (ถ้าเบากว่านี้ AI จะไม่เสียเวลาแปล)

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 1200, 150)
        
        self.label = QLabel("ระบบจูนนิ่งเรียบร้อย... พร้อมแปลญี่ปุ่น", self)
        self.label.setFont(QFont("Tahoma", 26, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #00FF00; background-color: rgba(0, 0, 0, 200); padding: 15px; border-radius: 15px;")
        self.label.setFixedSize(1200, 110)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_text(self, text):
        self.label.setText(text)

def audio_translation_loop(window):
    try:
        print(f"--- [ระบบ] กำลังโหลดโมเดล {MODEL_SIZE} (อาจใช้เวลาครู่หนึ่ง) ---")
        # จูนโมเดลให้รันบน CPU ได้ลื่นขึ้นด้วย int8
        model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        
        translator = Translator()
        p = pyaudio.PyAudio()
        
        # ค้นหาอุปกรณ์ CABLE Output
        target_id = None
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if "CABLE Output" in info.get('name', ''):
                target_id = i
                break
        
        if target_id is None:
            print("!!! ไม่เจอ CABLE Output !!!")
            return

        device_info = p.get_device_info_by_index(target_id)
        channels = int(device_info.get('maxInputChannels'))
        rate = int(device_info.get('defaultSampleRate'))

        stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate,
                        input=True, input_device_index=target_id, frames_per_buffer=2000)
        
        print("--- [ระบบ] เริ่มดักฟังเสียงภาษาญี่ปุ่น ---")
        audio_buffer = []

        while True:
            data = stream.read(2000, exception_on_overflow=False)
            raw_audio = np.frombuffer(data, dtype=np.int16).reshape(-1, channels)
            mono_audio = raw_audio[:, 0].astype(np.int16)
            
            peak = np.abs(mono_audio).max()
            audio_buffer.append(mono_audio)
            
            # สะสมเสียงประมาณ 2-3 วินาที
            if len(audio_buffer) > 15:
                audio_data = np.concatenate(audio_buffer).astype(np.float32) / 32768.0
                audio_buffer = []
                
                # กรองเฉพาะช่วงที่มีเสียงดังพอจะเป็นเสียงคน
                if peak > MIN_AUDIO_THRESHOLD:
                    print(f"--- วิเคราะห์เสียง (ระดับ: {peak}) ---")
                    # จูนหัวใจหลัก: บังคับภาษา + ใช้ VAD Filter ตัดสัญญาณรบกวน
                    segments, _ = model.transcribe(audio_data, language=TARGET_LANGUAGE, beam_size=5, vad_filter=True, 
                                  repetition_penalty=1.2,no_speech_threshold=0.6,condition_on_previous_text=False)
                    
                    for segment in segments:
                        text = segment.text.strip()
                        if text:
                            try:
                                # แปลจากญี่ปุ่นเป็นไทย
                                translated = translator.translate(text, src=TARGET_LANGUAGE, dest='th').text
                                print(f"[JP]: {text} -> [TH]: {translated}")
                                window.update_text(translated)
                            except:
                                window.update_text(text)
                else:
                    # ถ้าเสียงเบาเกินไป ให้ล้าง Buffer ทิ้งเพื่อไม่ให้สะสมเสียงซ่า
                    audio_buffer = []

    except Exception:
        traceback.print_exc()

def main():
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    threading.Thread(target=audio_translation_loop, args=(window,), daemon=True).start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()