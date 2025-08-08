from pydub import AudioSegment

def convert_to_16k_mono(in_wav_path, out_wav_path):
    audio = AudioSegment.from_wav(in_wav_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(out_wav_path, format="wav")

# 用法
# convert_to_16k_mono("input.wav", "output_16k_mono.wav")

