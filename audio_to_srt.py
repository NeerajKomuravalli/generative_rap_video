import json
import time

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import modal

stub = modal.Stub()


@stub.function(gpu="any")
def predict(audio_file):
    print("Predicting...")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        chunk_length_s=30,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device,
    )
    return pipe(audio_file)


audio_file = "./data/chunks/karna_kya_hai_tujhe/chunk_13.wav"
result = predict(audio_file)
# Save result file with timestamps so there is no clash
timestamp = str(time.time())
json.dump(result, open(f"result_{timestamp}.json", "w"))
print(result["text"])
print(result["chunks"])
