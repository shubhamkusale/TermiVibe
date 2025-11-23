import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time

class AudioEngine:
    def __init__(self):
        self.data = None
        self.samplerate = None
        self.stream = None
        self.current_frame = 0
        self.is_playing = False
        self.lock = threading.Lock()

    def load_file(self, file_path):
        try:
            data, samplerate = sf.read(file_path, always_2d=True)
            self.data = data
            self.samplerate = samplerate
            self.current_frame = 0
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def play(self):
        if self.data is None:
            return

        if self.is_playing:
            return

        self.is_playing = True
        
        def callback(outdata, frames, time, status):
            if status:
                print(status)
            
            chunk_size = len(outdata)
            with self.lock:
                if not self.is_playing:
                    outdata.fill(0)
                    raise sd.CallbackStop

                remaining = len(self.data) - self.current_frame
                if remaining <= 0:
                    outdata.fill(0)
                    self.is_playing = False
                    raise sd.CallbackStop
                
                valid_frames = min(frames, remaining)
                outdata[:valid_frames] = self.data[self.current_frame:self.current_frame + valid_frames]
                
                if valid_frames < frames:
                    outdata[valid_frames:].fill(0)
                
                self.current_frame += valid_frames

        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=self.data.shape[1],
            callback=callback,
            blocksize=2048
        )
        self.stream.start()

    def pause(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.is_playing = False

    def stop(self):
        self.pause()
        self.current_frame = 0

    def get_spectrum(self, num_bands=64):
        if self.data is None or not self.is_playing:
            return np.zeros(num_bands)

        # Get a chunk of data around the current frame for FFT
        fft_window_size = 2048
        start = max(0, self.current_frame - fft_window_size)
        end = self.current_frame
        
        if end - start < fft_window_size:
            return np.zeros(num_bands)

        # Use only the first channel for visualization
        audio_chunk = self.data[start:end, 0]
        
        # Apply Hanning window
        window = np.hanning(len(audio_chunk))
        audio_chunk = audio_chunk * window
        
        # FFT
        fft_data = np.abs(np.fft.rfft(audio_chunk))
        
        # Normalize and bin
        # We want to map the FFT bins to num_bands
        # Simple linear interpolation for now, can be improved to logarithmic
        
        # Take the first half of the spectrum (up to Nyquist) which rfft does
        # But we might want to focus on lower frequencies for visuals
        
        fft_data = fft_data[:len(fft_data)//2] # Focus on lower half
        
        if len(fft_data) < num_bands:
            return np.zeros(num_bands)
            
        # Resample to num_bands
        indices = np.linspace(0, len(fft_data) - 1, num_bands).astype(int)
        spectrum = fft_data[indices]
        
        # Normalize to 0-1 range (roughly)
        spectrum = spectrum / (np.max(spectrum) + 1e-6)
        
        return spectrum
