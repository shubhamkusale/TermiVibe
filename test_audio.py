import numpy as np
import soundfile as sf
import time
import os
from audio_engine import AudioEngine

def create_sine_wave(filename, duration=3, samplerate=44100, frequency=440):
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    data = 0.5 * np.sin(2 * np.pi * frequency * t)
    sf.write(filename, data, samplerate)
    print(f"Created {filename}")

def test_engine():
    filename = "test_tone.wav"
    create_sine_wave(filename)
    
    engine = AudioEngine()
    print("Loading file...")
    if not engine.load_file(filename):
        print("Failed to load file")
        return
    
    print("Playing...")
    engine.play()
    
    time.sleep(0.5)
    
    print("Checking spectrum...")
    spectrum = engine.get_spectrum()
    print(f"Spectrum max: {np.max(spectrum)}")
    
    if np.max(spectrum) > 0:
        print("SUCCESS: Spectrum data detected.")
    else:
        print("FAILURE: No spectrum data.")
        
    time.sleep(1)
    engine.stop()
    print("Stopped.")
    
    # Cleanup
    try:
        os.remove(filename)
    except:
        pass

if __name__ == "__main__":
    test_engine()
