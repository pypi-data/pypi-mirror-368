from collections import defaultdict

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

MIN_KMER_SIZE = 7
MAX_KMER_SIZE = 31

# Mapping of bases to 2-bit representations.
BASE_TO_BITS = {ord("A"): 0b00, ord("C"): 0b01, ord("G"): 0b10, ord("T"): 0b11}

# Reverse mapping of 2-bit representations to bases.
BITS_TO_BASE = {
    0b00: "A",
    0b01: "C",
    0b10: "G",
    0b11: "T",
}


def kmer_to_int(kmer: bytes) -> int | None:
    """Convert a kmer to an integer representation.

    If any bases are not ACGT, then return None.
    """
    kmer_int = 0
    for base in kmer:
        b = BASE_TO_BITS.get(base)
        if b is None:
            return None
        kmer_int = (kmer_int << 2) | b
    return kmer_int


def py_add_kmers(kmer_counts: defaultdict[int, int], sequence: bytes, kmer_size: int):
    """Find kmers, convert them to integers, keeping counts."""
    sequence_bytes = np.frombuffer(sequence, dtype=np.uint8)
    windows = sliding_window_view(sequence_bytes, window_shape=kmer_size)

    for window in windows:
        kmer = window.tobytes()
        kmer_int = kmer_to_int(kmer)
        # If we get None, then there were bases we could not parse.
        if kmer_int is not None:
            kmer_counts[kmer_int] += 1


def int_to_kmer(kmer_int: int, kmer_size: int) -> str:
    """Turn an encoded integer back into readable bases."""
    kmer = []
    for _ in range(kmer_size):
        # Extract the last 2 bits
        bits = kmer_int & 0b11
        # Map bits to base and prepend to the kmer list
        kmer.append(BITS_TO_BASE[bits])
        # Shift right by 2 bits to process the next base
        kmer_int >>= 2

    # Reverse the kmer list to get the correct order and join into a string
    return "".join(reversed(kmer))


# This marks any non-ACGT base as invalid
NOT_ACGT = 255


def make_lookup_table() -> np.ndarray:
    # Create a lookup table initialized with the invalid value
    lookup_table = np.full(256, NOT_ACGT, dtype=np.uint8)

    # Map 'A' (65) to 0
    lookup_table[ord("A")] = 0
    # Map 'C' (67) to 1
    lookup_table[ord("C")] = 1
    # Map 'G' (71) to 2
    lookup_table[ord("G")] = 2
    # Map 'T' (84) to 3
    lookup_table[ord("T")] = 3
    return lookup_table


BIT_LOOKUP_TABLE = make_lookup_table()


def numpy_get_kmers(
    sequence: bytes,
    kmer_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Use numpy vectorized functions to find kmers.

    This is equivalent to the py_find_kmers above, but around 5-10x faster.
    only is a set of kmers to keep, all others are ignored.
    """
    # Generate a set of bit-shifts amounts for the kmer size.
    # We use high to low for consistency with the python version.
    bit_shifts = np.arange(kmer_size - 1, -1, -1) * 2

    # Covert to a numpy array (no-copy), and get the kmer sliding windows.
    buf = np.frombuffer(sequence, dtype=np.uint8)
    windows = sliding_window_view(buf, window_shape=kmer_size)

    # Convert to bits (see above BITS), and the filter any rows that have NOT_ACGT
    as_bits = BIT_LOOKUP_TABLE[windows]
    use_bits = as_bits[np.all(as_bits != NOT_ACGT, axis=1)]

    # Now use the bit shifts, and sum them to make a single integer.
    kmers = np.sum(use_bits << bit_shifts, axis=1)

    # Group-by to get counts (there may be repeats), then translate to a python dict.
    kmers, counts = np.unique(kmers, return_counts=True)
    return kmers, counts


def numpy_add_kmers(
    kmer_counts: defaultdict[int, int],
    sequence: bytes,
    kmer_size: int,
    only: set[int] | None = None,
) -> None:
    """This just adds to an existing default dict."""
    kmers, counts = numpy_get_kmers(sequence, kmer_size)

    # If only is defined, then we discard any kmers that are not in the "only" set.
    if only:
        for k, c in zip(kmers, counts, strict=True):
            ik = int(k)
            if ik in only:
                kmer_counts[ik] += int(c)

    else:
        for k, c in zip(kmers, counts, strict=True):
            kmer_counts[int(k)] += int(c)
