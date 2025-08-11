from pathlib import Path
import hashlib
def compute_sha1(path: Path):
    sha1sum = hashlib.sha1()
    with open(path, "rb") as source:
        while block := source.read(2**16):
            sha1sum.update(block)
    return sha1sum

