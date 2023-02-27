import pyaudio
import wave

pa = pyaudio.PyAudio()

stream = pa.open(format=pyaudio.paInt16, channels=1,
                 rate=16000, input=True, frames_per_buffer=2048)
record_buf = []
count = 0
while count < 8 * 3:
    audio_data = stream.read(2048)
    record_buf.append(audio_data)
    count += 1

    wf = wave.open('tmp/rec.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes("".encode().join(record_buf))
    wf.close()

stream.stop_stream()
stream.close()
pa.terminate()
