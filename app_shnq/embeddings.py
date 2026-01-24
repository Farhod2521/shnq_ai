import hashlib
import math
import re


_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _tokenize(text):
    return _TOKEN_RE.findall(text.lower())


def embed_text(text, dim=256):
    vec = [0.0] * dim
    for token in _tokenize(text):
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        idx = int(digest, 16) % dim
        vec[idx] += 1.0

    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine_similarity(a, b):
    return sum(x * y for x, y in zip(a, b))
