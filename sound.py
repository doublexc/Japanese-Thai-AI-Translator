import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    print("\n--- รายชื่ออุปกรณ์เสียงที่โปรแกรมตรวจพบ ---")
    
    count = p.get_device_count()
    for i in range(count):
        info = p.get_device_info_by_index(i)
        # เราเน้นหาอุปกรณ์ที่เป็น Input (ช่องที่มีค่า maxInputChannels > 0)
        if info.get('maxInputChannels') > 0:
            print(f"ID {i}: {info.get('name')}")
            
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()