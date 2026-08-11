import struct
from collections import Counter
import capstone


def get_text_section_bytes(pe_path, sections):
    """
    sections: list of dicts from Day 12's sections_manual.py,
    each with name, virtual_address, raw_size, raw_offset.
    Returns (raw .text bytes, .text's virtual address).
    """
    text = next(s for s in sections if s['name'].startswith('.text'))
    with open(pe_path, 'rb') as f:
        f.seek(text['raw_offset'])
        return f.read(text['raw_size']), text['virtual_address']


def disassemble_opcodes(code_bytes, base_addr, is_64bit=True):
    """
    Walks .text bytes with capstone, returns a flat list of
    mnemonic strings in the order instructions appear.
    """
    mode = capstone.CS_MODE_64 if is_64bit else capstone.CS_MODE_32
    md = capstone.Cs(capstone.CS_ARCH_X86, mode)
    md.detail = False  # only need mnemonics, not operand detail

    return [insn.mnemonic for insn in md.disasm(code_bytes, base_addr)]


def make_ngrams(mnemonics, n):
    """
    Slides a window of size n across the mnemonic list.
    e.g. n=2 turns ['mov','push','call'] into ['mov_push', 'push_call']
    """
    return ['_'.join(mnemonics[i:i + n]) for i in range(len(mnemonics) - n + 1)]


def top_n_vector(ngram_counts, top_n=50):
    """
    Converts a Counter into a fixed-length frequency vector using
    only the top_n most common n-grams (the 'vocabulary').
    Returns (vector, vocab) so the same vocab can be reused across files.
    """
    vocab = [ng for ng, _ in ngram_counts.most_common(top_n)]
    total = sum(ngram_counts.values()) or 1  # avoid div-by-zero on empty .text
    vector = [ngram_counts[ng] / total for ng in vocab]
    return vector, vocab


def extract_opcode_ngram_features(pe_path, sections, top_n=50, is_64bit=True):
    code_bytes, base_addr = get_text_section_bytes(pe_path, sections)
    mnemonics = disassemble_opcodes(code_bytes, base_addr, is_64bit)

    all_ngrams = Counter()
    for n in (1, 2, 3):
        all_ngrams.update(make_ngrams(mnemonics, n))

    return top_n_vector(all_ngrams, top_n)


if __name__ == '__main__':
    import sys
    from static_features.sections_manual import read_sections  # Day 12

    path = sys.argv[1]
    sections = read_sections(path)
    vector, vocab = extract_opcode_ngram_features(path, sections)

    for ng, val in zip(vocab, vector):
        print(f"{ng:30s} {val:.4f}")