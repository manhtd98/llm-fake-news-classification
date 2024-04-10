from TTS.tts.utils.text.phonemizers.base import BasePhonemizer
from core.vnabc.phonemizers.vn_phonemizer import VN_Phonemizer


DEF_LANG_TO_PHONEMIZER = {"vn":VN_Phonemizer.name()}

def get_phonemizer_by_name(name: str, **kwargs) -> BasePhonemizer:
    """Initiate a phonemizer by name

    Args:
        name (str):
            Name of the phonemizer that should match `phonemizer.name()`.

        kwargs (dict):
            Extra keyword arguments that should be passed to the phonemizer.
    """

    if name == "vn_phonemizer":
        return VN_Phonemizer(**kwargs)
    raise ValueError(f"Phonemizer {name} not found")


if __name__ == "__main__":
    print(DEF_LANG_TO_PHONEMIZER)
