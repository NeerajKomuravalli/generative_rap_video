import argparse
import json
import os
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

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


class AudioDataset(Dataset):
    def __init__(self, audio_files):
        self.audio_files = audio_files

    def __len__(self):
        return len(self.audio_files)

    def __getitem__(self, idx):
        audio_file = self.audio_files[idx]
        result = pipe(audio_file)
        return result


def main(args):
    chunks_dir = input("Enter the path to directory containing audio chunks: ")

    audio_files = []
    for filename in os.listdir(chunks_dir):
        if filename.endswith(".wav"):
            audio_file = os.path.join(chunks_dir, filename)
            audio_files.append(audio_file)

    dataset = AudioDataset(audio_files)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    results = []

    for batch in dataloader:
        batch_results = []
        for result in batch:
            batch_results.append(result)
        results.extend(batch_results)

    for result in results:
        audio_file = result["audio_file"]
        audio_dir, audio_filename = os.path.split(audio_file)
        json_file = os.path.join(
            audio_dir, f"{os.path.splitext(audio_filename)[0]}.json"
        )
        json.dump(result, open(json_file, "w"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process audio chunks using OpenAI Whisper"
    )
    parser.add_argument(
        "chunks_dir", type=str, help="Path to directory containing audio chunks"
    )
    args = parser.parse_args()
    main(args)
