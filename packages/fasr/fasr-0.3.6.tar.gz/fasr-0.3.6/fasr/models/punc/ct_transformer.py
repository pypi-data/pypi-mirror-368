from .base import PuncModel
from fasr.data import AudioSpan, AudioToken, AudioTokenList, AudioSpanList
from funasr import AutoModel
from typing_extensions import Self
from typing import List
from pathlib import Path
from fasr.config import registry
import re


@registry.punc_models.register("ct_transformer")
class CTTransformerForPunc(PuncModel):
    checkpoint: str = "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch"
    endpoint: str = "modelscope"

    ct_transformer: AutoModel | None = None

    def restore(self, text: str) -> AudioSpanList[AudioSpan]:
        result = self.ct_transformer.generate(input=text)[0]
        punc_array = result.get("punc_array", []).tolist()
        sents = AudioSpanList[AudioSpan]()
        sent_tokens = []
        all_tokens = AudioTokenList[AudioToken](
            [AudioToken(text=t) for t in self.tokenize(text=text)]
        )
        assert len(all_tokens) == len(punc_array), (
            f"{len(all_tokens)} != {len(punc_array)}"
        )
        for i, punc_res in enumerate(punc_array):
            all_tokens[i].follow = self.id_to_punc(punc_res)
            if punc_res == 1:
                sent_tokens.append(all_tokens[i])
            else:
                sent_tokens.append(all_tokens[i])
                sents.append(
                    AudioSpan(
                        tokens=AudioTokenList(docs=sent_tokens),
                    )
                )
                sent_tokens = []
        if len(sent_tokens) > 0:
            sents.append(
                AudioSpan(
                    tokens=AudioTokenList(docs=sent_tokens),
                )
            )
        return sents

    def id_to_punc(self, id: int):
        punc_list = []
        for pun in self.ct_transformer.model.punc_list:
            if pun == "_":
                pun = ""
            punc_list.append(pun)
        id2punc = {i: punc for i, punc in enumerate(punc_list)}
        return id2punc[id]

    def tokenize(self, text: str) -> List[str]:
        return split_words(text=text)

    def from_checkpoint(
        self,
        checkpoint_dir: str | Path | None = None,
        disable_update: bool = True,
        disable_log: bool = True,
        disable_pbar: bool = True,
        **kwargs,
    ) -> Self:
        if not checkpoint_dir:
            checkpoint_dir = self.download_checkpoint()
        checkpoint_dir = Path(checkpoint_dir)
        if not checkpoint_dir.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_dir}")
        model = AutoModel(
            model=checkpoint_dir,
            disable_update=disable_update,
            disable_log=disable_log,
            disable_pbar=disable_pbar,
            **kwargs,
        )
        self.ct_transformer = model
        return self

    def get_config(self):
        raise NotImplementedError

    def load(self, save_dir, **kwargs):
        raise NotImplementedError

    def save(self, save_dir, **kwargs):
        raise NotImplementedError


def split_to_mini_sentence(words: list, word_limit: int = 20):
    assert word_limit > 1
    if len(words) <= word_limit:
        return [words]
    sentences = []
    length = len(words)
    sentence_len = length // word_limit
    for i in range(sentence_len):
        sentences.append(words[i * word_limit : (i + 1) * word_limit])
    if length % word_limit > 0:
        sentences.append(words[sentence_len * word_limit :])
    return sentences


def split_words(text: str, jieba_usr_dict=None, **kwargs):
    if jieba_usr_dict:
        input_list = text.split()
        token_list_all = []
        langauge_list = []
        token_list_tmp = []
        language_flag = None
        for token in input_list:
            if isEnglish(token) and language_flag == "Chinese":
                token_list_all.append(token_list_tmp)
                langauge_list.append("Chinese")
                token_list_tmp = []
            elif not isEnglish(token) and language_flag == "English":
                token_list_all.append(token_list_tmp)
                langauge_list.append("English")
                token_list_tmp = []

            token_list_tmp.append(token)

            if isEnglish(token):
                language_flag = "English"
            else:
                language_flag = "Chinese"

        if token_list_tmp:
            token_list_all.append(token_list_tmp)
            langauge_list.append(language_flag)

        result_list = []
        for token_list_tmp, language_flag in zip(token_list_all, langauge_list):
            if language_flag == "English":
                result_list.extend(token_list_tmp)
            else:
                seg_list = jieba_usr_dict.cut(
                    join_chinese_and_english(token_list_tmp), HMM=False
                )
                result_list.extend(seg_list)

        return result_list

    else:
        words = []
        segs = text.split()
        for seg in segs:
            # There is no space in seg.
            current_word = ""
            for c in seg:
                if len(c.encode()) == 1:
                    # This is an ASCII char.
                    current_word += c
                else:
                    # This is a Chinese char.
                    if len(current_word) > 0:
                        words.append(current_word)
                        current_word = ""
                    words.append(c)
            if len(current_word) > 0:
                words.append(current_word)
        return words


def isEnglish(text: str):
    if re.search("^[a-zA-Z']+$", text):
        return True
    else:
        return False


def join_chinese_and_english(input_list):
    line = ""
    for token in input_list:
        if isEnglish(token):
            line = line + " " + token
        else:
            line = line + token

    line = line.strip()
    return line
