import logging
from faster_whisper import WhisperModel
from tempfile import NamedTemporaryFile


class SPEECH2TEXT:
    def __init__(
        self,
        model_name="manhtd98/whisperPho-FasterWhisper",
        device="cpu",
        compute_type="int8",
        download_root="./cache",
    ):
        self.model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            download_root=download_root,
        )
        logging.info("Success init speech to text model !!!")

    def __call__(self, audio_record):
        response_texts = []
        with NamedTemporaryFile(suffix=".mp3") as temp:
            with open(f"{temp.name}", "wb") as f:
                f.write(audio_record.export().read())
            segments, info = self.model.transcribe(
                f"{temp.name}",
                beam_size=5,
                language="en",
                condition_on_previous_text=False,
            )
            # prompt = self.model.extract_text(result)
            # logging.info("Success running inference speech to text")
            for segment in segments:
                print(
                    "[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)
                )
                if segment.text:
                    response_texts.append(segment.text)

            if len(response_texts):
                response = " ".join(response_texts)
                return response
            else:
                return None


if __name__ == "__main__":
    w = SPEECH2TEXT(compute_type="float32")
    w("file.mp3")
