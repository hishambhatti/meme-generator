import torch.nn.functional as F
import torchvision.models as models
import torch
from torch import nn
from modules.positional_encoding import PositionalEncoding

class ImageCaptionTransformer(nn.Module):
    def __init__(
        self,
        vocab_size,
        d_model=512,
        nhead=8,
        num_encoder_layers=3,
        num_decoder_layers=3,
        dim_feedforward=2048,
        dropout=0.1,
        max_len=100,
        pad_idx=0,
        tokenizer=None,
    ):
        super().__init__()
        # CNN backbone (ResNet50 up to last conv)
        resnet = models.resnet50(pretrained=True)
        modules = list(resnet.children())[:-2]
        self.cnn = nn.Sequential(*modules)
        # project to d_model
        self.conv_proj = nn.Conv2d(2048, d_model, kernel_size=1)

        # positional encodings
        self.pos_encoder = PositionalEncoding(d_model, max_len, dropout)
        self.pos_decoder = PositionalEncoding(d_model, max_len, dropout)

        # standard PyTorch transformer
        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_encoder_layers,
            num_decoder_layers=num_decoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
        )

        # token embedding + output head
        self.token_embed = nn.Embedding(vocab_size, d_model, padding_idx=pad_idx)
        self.fc_out = nn.Linear(d_model, vocab_size)

        self.d_model = d_model
        self.pad_idx = pad_idx

        # pass in the tokenizer object
        self.tokenizer = tokenizer

    def forward(self, images, captions):
        """
        images: (B,3,H,W)
        captions: (B, T) including <start> and <end>
        returns logits: (B, T-1, vocab_size) predicting tokens 1…T-1
        """
        B, _, _, _ = images.shape
        # 1) encode images → sequence of patch‐tokens
        feats = self.cnn(images)                # (B,2048, H', W')
        feats = self.conv_proj(feats)           # (B,d_model, H', W')
        B, d, H, W = feats.shape
        src = feats.flatten(2).permute(2, 0, 1)  # (S=H'*W', B, d_model)
        src = self.pos_encoder(src)

        # 2) prepare target embeddings
        # we feed all tokens except the final <end> for teacher forcing
        tgt_in = captions[:, :-1]               # (B, T-1)
        tgt = self.token_embed(tgt_in)          # (B, T-1, d_model)
        tgt = tgt.permute(1, 0, 2)               # (T-1, B, d_model)
        tgt = self.pos_decoder(tgt)

        # masks
        Tm1 = tgt.size(0)
        # causal mask so each position only attends to previous
        tgt_mask = self.transformer.generate_square_subsequent_mask(Tm1).to(images.device)
        # padding mask: True where padding
        tgt_key_padding_mask = (tgt_in == self.pad_idx)  # (B, T-1)

        # 3) transformer
        output = self.transformer(
            src=src,
            tgt=tgt,
            tgt_mask=tgt_mask,
            tgt_key_padding_mask=tgt_key_padding_mask,
        )  # (T-1, B, d_model)

        # 4) project to vocab
        output = output.permute(1, 0, 2)         # (B, T-1, d_model)
        return self.fc_out(output)

    @torch.no_grad()
    def sample(self, images, max_len=20):
        """
        Greedy decoding: generate one token at a time.
        """
        self.eval()
        B = images.size(0)
        # encode once
        feats = self.cnn(images)
        feats = self.conv_proj(feats)
        src = feats.flatten(2).permute(2, 0, 1)
        src = self.pos_encoder(src)

        ys = torch.full((B, 1), fill_value=self.pad_idx, dtype=torch.long, device=images.device)
        ys[:, 0] = self.tokenizer.stoi["<start>"]

        for i in range(max_len):
            tgt = self.token_embed(ys)         # (B, i+1, d)
            tgt = tgt.permute(1, 0, 2)         # (i+1, B, d)
            tgt = self.pos_decoder(tgt)
            tgt_mask = self.transformer.generate_square_subsequent_mask(tgt.size(0)).to(images.device)

            out = self.transformer(src=src, tgt=tgt, tgt_mask=tgt_mask)  # (i+1, B, d)
            out = out.permute(1, 0, 2)          # (B, i+1, d)
            logits = self.fc_out(out[:, -1, :]) # (B, vocab_size)
            next_tok = logits.argmax(dim=-1, keepdim=True)  # (B,1)
            ys = torch.cat([ys, next_tok], dim=1)           # append
            # stop if all batches generated <end>
            if (next_tok == self.tokenizer.stoi["<end>"]).all():
                break

        return ys  # (B, <=max_len+1)
