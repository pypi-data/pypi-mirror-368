from huggingface_hub import hf_hub_download
import numpy as np
import phonemizer
import onnxruntime as ort
import re

class KittenTTS:
    def __init__(self, model_path=None, voices_path=None):
        if not model_path:
            model_path = hf_hub_download("KittenML/kitten-tts-nano-0.1","kitten_tts_nano_v0_1.onnx")
        if not voices_path:
            voices_path = hf_hub_download("KittenML/kitten-tts-nano-0.1","voices.npz")
        self.available_voices = ['expr-voice-2-m', 'expr-voice-2-f', 'expr-voice-3-m', 'expr-voice-3-f', 'expr-voice-4-m', 'expr-voice-4-f', 'expr-voice-5-m', 'expr-voice-5-f']
        self._phonemizer = phonemizer.backend.EspeakBackend(language="en-us", preserve_punctuation=True, with_stress=True)
        self._word_index_dictionary = {symbol: i for i, symbol in enumerate(list('$;:,.!?¡¿—…"«»"" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞↓↑→↗↘\'̩\'ᵻ'))}
        self._voices = np.load(voices_path)
        self._session = ort.InferenceSession(model_path)
        
    def generate(self, text: str, voice: str = "expr-voice-2-m", speed: float = 1.0) -> np.ndarray:
        return self._session.run(None, {"input_ids": np.array([[0] + [self._word_index_dictionary[c] for c in ' '.join(re.findall(r"\w+|[^\w\s]", self._phonemizer.phonemize([text])[0])) if c in self._word_index_dictionary] + [0]], dtype=np.int64),"style": self._voices[voice],"speed": np.array([speed], dtype=np.float32),})[0][5000:-10000]
