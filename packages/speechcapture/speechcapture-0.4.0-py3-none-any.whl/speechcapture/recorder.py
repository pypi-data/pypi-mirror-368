import pyaudio
import numpy as np
import wave
import threading
import os
from datetime import datetime
import time
import warnings

class Recorder:
    '''
    The main Recorder class. Used to record and save speech. For simultaneous recordings, create multiple instances.
    You MUST call `terminate()` when done or use this class within a context manager to safely release system resources

    Attributes:
        silence_threshold (int): The minimum amplitude of audio to be considered speech
        max_seconds_of_silence (int): The maximum seconds of silence before ending the recording (set to None to keep recording until .stop() is called)
        max_silence_multiplier (int): The maximum allowed multiplier of the previous amplitude for an outlier to qualify as silence
        standard_deviation_multiplier (int): The multiplier applied to the standard deviation of amplitude values, which is added to the mean when adjusting silence threshold for ambient noise.
        max_duration (boolean): The maximum length of a recording (set to None to remove limit)
        stop_on_pause (boolean): Whether a recording should automatically pause instead of automatically stop
    '''
    def __init__(self,  audio_path: str, device_index: int = pyaudio.PyAudio().get_default_input_device_info()['index'], format: int = pyaudio.paInt16, channels: int = 1, rate: int = 16000, frames_per_buffer: int = 1600, debug=False):
        '''
        Create an instance of the Recorder class.

        Args:
            audio_path (string): The file path to save audio in (must be of format .wav)
            device_index (int): The index of the input device to use (call `speechcapture.list_input_devices()` for a list of all devices)
            format (int): The audio sample format
            channels (int): Number of channels used for input (1 for mono, 2 for stereo)
            rate (int): The sample rate of the audio in Hz
            frames_per_buffer (int): How many audio frames are read/written at a time, lower values are lower latency but more costly to performance
            debug (boolean): Whether the class should log certain values in the console
        Returns:
            None
        '''
        if not audio_path.lower().endswith('.wav'):
            raise ValueError('Audio path must end with .wav')

        self.audio_path = audio_path
        self._input_device_index = device_index
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate
        self.FRAMES_PER_BUFFER = frames_per_buffer
        self.debug = debug

        self.silence_threshold = 500
        self.max_seconds_of_silence = 1
        self.max_silence_multiplier = 2
        self.standard_deviation_multiplier = 1.5
        self.max_duration = None
        self.pause_on_end = False

        self._is_recording = False
        self._is_paused = False

        self._duration = 0
        self._start_time = 0

        self._frames = []
        self._silent_buffers = 0
        self._lock = threading.Lock()

        self._p = pyaudio.PyAudio()
        self._stream = self._p.open(
            input_device_index=self._input_device_index,
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            frames_per_buffer=self.FRAMES_PER_BUFFER,
            input=True,
            start=False
        )
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def __del__(self):
        self.terminate()

    @property
    def is_recording(self):
        return self._is_recording
    
    @property
    def is_paused(self):
        return self._is_paused
    
    @property
    def duration(self):
        if self._is_paused or not self._is_recording:
            return self._duration or 0
        else:
            return time.time() - self._start_time
    
    def get_config(self):
        return {
            'audio_path': self.audio_path,
            'FORMAT': self.FORMAT,
            'CHANNELS': self.CHANNELS,
            'RATE': self.RATE,
            'FRAMES_PER_BUFFER': self.FRAMES_PER_BUFFER,
            'debug': self.debug,
            'silence_threshold': self.silence_threshold,
            'max_seconds_of_silence': self.max_seconds_of_silence,
            'max_silence_multiplier': self.max_silence_multiplier,
            'standard_deviation_multiplier': self.standard_deviation_multiplier
        }

    def _log(self, msg: str):
        if self.debug:
            print(msg)

    def record(self):
        '''
        Start recording audio. If paused, recording again will restart audio.
        Will stop/pause automatically only if max_seconds_of_silence or max_duration is set, otherwise `stop()`/`pause()` must be called.
        '''
        with self._lock:
            self._is_recording = True
            self._is_paused = False
            self._duration = 0
        self.discard()

        if self._stream.is_stopped():
            self._stream.start_stream()
        self._start_time = time.time()
        self._log('Started recording')
        while self._is_recording:
            if self.max_duration:
                if time.time() - self._start_time >= self.max_duration:
                    if (self.pause_on_end):
                        self.pause()
                    else:
                        self.stop()
                        break

            if not self._is_paused:
                try:
                   data = self._stream.read(self.FRAMES_PER_BUFFER)
                except (OSError, IOError) as e:
                    self._log(f'Stream read error: {e}')
                    raise RuntimeError(f'Stream read failed')

                with self._lock:
                    self._frames.append(data)
                
                self._log(f'Buffer: {data}')

                if self.max_seconds_of_silence is not None:
                    audio_data = np.frombuffer(data, np.int16)
                    amplitude = np.abs(audio_data).mean()

                    self._log(f'Audio data: {audio_data}, Amplitude: {amplitude}')

                    try:
                        last_amplitude = np.abs(np.frombuffer(self._frames[-2], np.int16)).mean()
                    except (IndexError, ValueError):
                        last_amplitude = self.silence_threshold
                    
                    self._log(f'Last amplitude: {last_amplitude}')
                    
                    if (amplitude <= self.silence_threshold) or ((amplitude / last_amplitude) <= self.max_silence_multiplier and last_amplitude <= self.silence_threshold):
                        self._silent_buffers += 1
                    else:
                        self._silent_buffers = 0
                    
                    self._log(f'Silent buffers: {self._silent_buffers}')

                    if self._silent_buffers >= (self.max_seconds_of_silence) / (self.FRAMES_PER_BUFFER / self.RATE):
                        if (self.pause_on_end):
                            self.pause()
                        else:
                            self.stop()
                            break
    
    def record_async(self, daemon=False):
        '''
        Calls the record method on a seperate thread. Used to prevent blocking the main thread when recording.
        Ensure that the thread finishes (such as through `join()`) before terminating the session.

        Args:
            daemon (boolean): Whether or not the thread should be a daemon thread
        
        Returns:
            thread (Thread): The thread where the record method is being called
        '''
        thread = threading.Thread(target=self.record, daemon=daemon)
        thread.start()
        return thread
    
    def stop(self):
        '''
        Stop recording and save audio.
        '''
        if self._stream is not None:
            with self._lock:
                self._is_recording = False
                self._duration = time.time() - self._start_time
            if self._stream.is_active():
                self._stream.stop_stream()
            # Error above comment
            with self._lock:
                self.save()
            self.discard()
            self._log('Stopped recording')
    
    def pause(self):
        '''
        Pause recording. Does not save audio.
        '''
        if not self._is_paused and self._stream.is_active():
            self._is_paused = True
            self._stream.stop_stream()
            self._duration = time.time() - self._start_time
    
    def resume(self):
        '''
        Resume recording.
        '''
        if self._is_paused and self._stream.is_stopped():
            self._is_paused = False
            self._silent_buffers = 0
            self._stream.start_stream()

    def discard(self):
        '''
        Discard what has been recorded without saving.
        '''
        with self._lock:
            self._frames = []
            self._silent_buffers = 0

    def save(self, overwrite: bool = True):
        '''
        Save currently recorded audio.

        Args:
            overwrite (boolean): Whether or not the file will overwrite an existing file 
        '''
        save_path = self.audio_path
        if not overwrite and os.path.exists(self.audio_path):
            if os.path.exists(self.audio_path):
                save_path = self.audio_path + f'_{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}'
                self._log(f'New path (to not overwrite): {save_path}')
        
        if not self._frames:
            warnings.warn('No audio recorded to save.')
            return
        
        audio = wave.open(save_path, 'wb')
        audio.setnchannels(self.CHANNELS)
        audio.setsampwidth(self._p.get_sample_size(self.FORMAT))
        audio.setframerate(self.RATE)
        audio.writeframes(b''.join(self._frames))
        audio.close()
    
    def adjust_to_background_noise(self, adjustment_time: int = 1):
        '''
        Adjusts the silence threshold based on the source's background noise.

        Args:
            adjustment_time (int): How many seconds to test for background noise 
        '''
        ambient_amplitudes = []

        if self._stream.is_stopped():
            self._stream.start_stream()

        while len(ambient_amplitudes) < ((adjustment_time) / (self.FRAMES_PER_BUFFER / self.RATE)):
            data = self._stream.read(self.FRAMES_PER_BUFFER)
            audio_data = np.frombuffer(data, np.int16)
            ambient_amplitudes.append(np.abs(audio_data).mean())

            self._log(f'Ambient amplitude: {np.abs(audio_data).mean()}')
        
        self.silence_threshold = np.mean(ambient_amplitudes) + (self.standard_deviation_multiplier * np.std(ambient_amplitudes))
        self._log(f'Silence threshold: {self.silence_threshold}')
        self._stream.stop_stream()
    
    def terminate(self):
        '''
        Terminate the session and release system resources. You must call this method to prevent resource leaks.
        If recording, this method will end the recording without saving.
        '''
        if self._is_recording:
            self.pause()
        self._is_recording = False
        self._is_paused = False
        self.discard()
        self._stream.close()
        self._p.terminate()
    
def list_input_devices():
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"{i}: {info['name']}")
    
r = Recorder()