from modules.tokenizer import Tokenizer
from modules.img_caption_trans import ImageCaptionTransformer
import torch
from torchvision import transforms
import torchvision.transforms as T
import os
from PIL import Image
import numpy as np



class CaptionGenerator:
    def __init__(self, tok_path=None, weights_path=None):
        self.tokenizer = Tokenizer(path=tok_path)

        # load the model
        self.weights_path = weights_path

        self.device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        vocab_size = 26380
        pad_idx    = self.tokenizer.stoi["<pad>"]
        print(f"Using device: {self.device}")

        # Instantiate the model with the exact parameters used during training [9]
        model = ImageCaptionTransformer(
            vocab_size=vocab_size,
            d_model=512,
            nhead=8,
            num_encoder_layers=3,
            num_decoder_layers=3,
            dim_feedforward=2048,
            dropout=0.1,
            max_len=100,
            pad_idx=pad_idx,
            tokenizer=self.tokenizer,
        ).to(self.device)

        print(f"Model instantiated with {vocab_size} vocabulary size.")

        # Load the saved state dictionary [1]
        model.load_state_dict(torch.load(self.weights_path, map_location=self.device))
        print(f"Model weights loaded successfully from {self.weights_path}")

        # Set the model to evaluation mode (important for inference)
        model.eval()
        print("Model set to evaluation mode.")

        self.model = model
        # Now the 'model' variable holds your loaded model, ready for inference.
        # You can verify by printing the model structure or trying a sample inference.
        # print(model) # Uncomment to see the model architecture

    def generate_caption(self, img=None, file=None):
        # Define your two transforms (you already have shitty_transform; here we assume
        # `transform` is your model’s preprocessing, add ToTensor/Normalize there too)
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

        shitty_transform = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
        ])

        self.model.eval()

        with torch.no_grad():
            # 1) Load and convert
            img_pil = Image.open(file).convert('RGB')

            # 2) Center-crop to square
            w, h = img_pil.size
            m = min(w, h)
            left = (w - m) // 2
            top  = (h - m) // 2
            img_pil = img_pil.crop((left, top, left + m, top + m))

            # 3) Apply your transforms
            img_tensor       = transform(img_pil).unsqueeze(0).to(self.device)
            shitty_img_tensor = shitty_transform(img_pil).unsqueeze(0).to(self.device)

            # 4) Generate caption
            token_ids = self.model.sample(img_tensor, max_len=20)[0].cpu().tolist()
            tokens = []
            for tid in token_ids[1:]:  # skip <start>
                tok = self.tokenizer.itos[tid]
                if tok == "<end>": break
                tokens.append(tok)
            
            # Create caption (without adding unnecessary spaces)
            caption = ""
            punctuations = ['.', ',', '?', '!', ':', ';']
            for tok in tokens:
                if not tok in punctuations:
                    caption += " "
                caption += tok
            
            caption = caption[1:]
            caption = caption[0].upper() + caption[1:] # Capitalize first character

            # 5) Prepare for display
            img_np = shitty_img_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
            img_np = img_np * np.array([0.229, 0.224, 0.225]) + \
                    np.array([0.485, 0.456, 0.406])
            img_np = np.clip(img_np, 0, 1)

        # 6) Show
        # print(f"Image: {os.path.basename(file)}")
        print(f"Caption: {caption}\n{'-'*40}")

        return caption