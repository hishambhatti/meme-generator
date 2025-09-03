from collections import Counter
import re
import json

class Tokenizer:
    def __init__(self, captions=None, freq_threshold=5, path=None):
        if captions:
            self.freq_threshold = freq_threshold
            self.itos = {0: "<pad>", 1: "<start>", 2: "<end>", 3: "<unk>"}
            self.stoi = {v:k for k,v in self.itos.items()}
            self.build_vocab(captions)
        else:
            self.deserialize(path)

    def tokenize(self, text):
        return re.findall(r"\w+'?\w+|[.,!?;]", text.lower())

    def build_vocab(self, captions):
        freqs = Counter()
        for cap in captions:
            freqs.update(self.tokenize(cap))
        idx = len(self.itos)
        for tok, cnt in freqs.items():
            if cnt >= self.freq_threshold:
                self.stoi[tok] = idx
                self.itos[idx] = tok
                idx += 1

    def numericalize(self, text):
        tokens = self.tokenize(text)
        nums = [self.stoi.get(tok, self.stoi["<unk>"]) for tok in tokens]
        return [self.stoi["<start>"]] + nums + [self.stoi["<end>"]]
    
    def serialize(self, path):
        with open(path, "w") as f:
            serialized = {
                "itos": self.itos,
                "freq_threshold": self.freq_threshold
            }
            json.dump(serialized, f)
    
    def deserialize(self, path):
        with open(path, "r") as f:
            serialized = json.load(f)
            self.itos = serialized["itos"]
            self.stoi = {v:int(k) for k,v in self.itos.items()}
            self.itos = {v:k for k,v in self.stoi.items()}
            self.freq_threshold = serialized["freq_threshold"]