from __future__ import annotations
import torch.nn as nn
import torch
import numpy as np
from typing import List
from pathlib import Path

from fasr.models.asr.base import ASRModel
from fasr.data import AudioToken
from fasr.config import registry

from .conformer_encoder import ConformerEncoder
from .transformer_decoder import TransformerDecoder
from .feats import KaldiFbankExtractor
from .tokenizer import ChineseCharEnglishSpmTokenizer


@registry.asr_models.register("firered_aed")
class FireRedAEDForASR(ASRModel):
    checkpoint: str = "FireRedTeam/FireRedASR-AED-L"
    endpoint: str = "hf-mirror"

    model: FireRedAED | None = None
    feature_extractor: KaldiFbankExtractor | None = None
    tokenizer: ChineseCharEnglishSpmTokenizer | None = None
    beam_size: int = 1
    nbest: int = 1
    decode_max_len: int = 0
    softmax_smoothing: float = 1.0
    aed_length_penalty: float = 0.0
    eos_penalty: float = 1.0
    device: str | None = None

    def transcribe(
        self, batch: List[np.ndarray | torch.Tensor], sample_rate, **kwargs
    ) -> List[List[AudioToken]]:
        (
            feats,
            lengths,
        ) = self.feature_extractor(batch_data=batch, sample_rate=sample_rate)
        with torch.inference_mode():
            hyps = self.model.transcribe(
                feats.to(self.device),
                lengths.to(self.device),
                self.beam_size,
                self.nbest,
                self.decode_max_len,
                self.softmax_smoothing,
                self.aed_length_penalty,
                self.eos_penalty,
            )
            results = []
            for hyp in hyps:
                hyp = hyp[0]  # only return 1-best
                hyp_ids = [int(id) for id in hyp["yseq"].cpu()]
                tokens = [self.tokenizer.detokenize([token_id]) for token_id in hyp_ids]
                tokens = [AudioToken(text=token) for token in tokens]
                results.append(tokens)
        return results

    def from_checkpoint(
        self,
        checkpoint_dir: str | Path | None = None,
        device: str | None = None,
        **kwargs,
    ):
        if not checkpoint_dir:
            checkpoint_dir = self.download_checkpoint()
        checkpoint_dir = Path(checkpoint_dir)
        if not checkpoint_dir.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_dir}")
        dict_path = checkpoint_dir / "dict.txt"
        spm_model_path = checkpoint_dir / "train_bpe1000.model"
        self.tokenizer = ChineseCharEnglishSpmTokenizer(
            dict_path=str(dict_path), spm_model=str(spm_model_path)
        )
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        states = torch.load(checkpoint_dir / "model.pth.tar")
        args = states["args"]
        self.model = FireRedAED(args)
        self.model.load_state_dict(states["model_state_dict"], strict=True)
        self.model.eval()
        self.model.to(self.device)
        self.feature_extractor = KaldiFbankExtractor(
            kaldi_cmvn_file=str(checkpoint_dir / "cmvn.ark")
        )
        return self

    def get_config(self):
        pass

    def load(self, save_dir, **kwargs):
        pass

    def save(self, save_dir, **kwargs):
        pass


class FireRedAED(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.encoder = ConformerEncoder(
            args.idim,
            args.n_layers_enc,
            args.n_head,
            args.d_model,
            args.residual_dropout,
            args.dropout_rate,
            args.kernel_size,
            args.pe_maxlen,
        )

        self.decoder = TransformerDecoder(
            args.sos_id,
            args.eos_id,
            args.pad_id,
            args.odim,
            args.n_layers_dec,
            args.n_head,
            args.d_model,
            args.residual_dropout,
            args.pe_maxlen,
        )

    def transcribe(
        self,
        padded_input,
        input_lengths,
        beam_size=1,
        nbest=1,
        decode_max_len=0,
        softmax_smoothing=1.0,
        length_penalty=0.0,
        eos_penalty=1.0,
    ):
        enc_outputs, _, enc_mask = self.encoder(padded_input, input_lengths)
        nbest_hyps = self.decoder.batch_beam_search(
            enc_outputs,
            enc_mask,
            beam_size,
            nbest,
            decode_max_len,
            softmax_smoothing,
            length_penalty,
            eos_penalty,
        )
        return nbest_hyps
