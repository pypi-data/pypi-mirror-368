import operator
import re
from functools import cache
from itertools import combinations
from pathlib import Path
from typing import TypeAlias

from loguru import logger
from pydantic import BaseModel, Field

from flui.dna import SegmentType, iter_fasta, open_as_text
from flui.header import FastaHeader

from .kmer_set import KmerSet

RE_SUBTYPE = re.compile(r"H(?P<ha>\d+)N(?P<na>\d+)")

KmerSetDict: TypeAlias = dict[str, KmerSet]


class PairwiseDistances(BaseModel):
    distances: dict[str, float] = Field(default_factory=dict)
    mean: float = 0.0
    minimum: float = 0.0

    def load(self, kmers_dict: KmerSetDict):
        """Build a matrix of pairwise distances between all KmerSets."""
        dists = {}
        total = 0.0
        minimum = 1.0
        n = 0
        for key1, key2 in combinations(kmers_dict.keys(), 2):
            if key1 == key2:
                dist = 0.0
            else:
                d1 = kmers_dict[key1]
                d2 = kmers_dict[key2]
                dist = d1.jensen_shannon_distance(d2)
                total += dist
                n += 1

            # Measure is symmetric, so we store both directions.
            if key1 > key2:
                key1, key2 = key2, key1
            dists[f"{key1}-{key2}"] = dist
            if dist < minimum:
                minimum = dist

        self.distances = dists
        self.mean = total / n
        self.minimum = minimum

    def lookup(self, key1: str, key2: str) -> float:
        if key1 > key2:
            key1, key2 = key2, key1
        return self.distances[f"{key1}-{key2}"]


def to_npdm_score(dist: float, normaliser: float) -> float:
    """Normalise a distance to a percentage decrease from the mean."""
    normed = dist / normaliser
    return max(0.0, 1.0 - normed) * 100.0


# Extracted to avoid method cache issues.
@cache
def to_npdm(sm: "SegmentMatch") -> tuple[tuple[str, float], ...]:
    return tuple((st, to_npdm_score(dist, sm.mean)) for st, dist in sm.distances)


class SegmentMatch(BaseModel, frozen=True):
    # Which segment this is.
    segment: SegmentType

    # These will be sorted with the smallest first.
    # These are jensen-shannon distances.
    distances: tuple[tuple[str, float], ...]

    # The mean distance from the KmerIndex.
    # Used for normalising.
    mean: float

    def as_npdm(self) -> tuple[tuple[str, float], ...]:
        return to_npdm(self)

    def best_score(self) -> float:
        return self.as_npdm()[0][1]

    def best_subtype(self) -> str:
        return self.as_npdm()[0][0]

    def assigned_subtype(self, min_score: float, min_lead: float) -> str:
        """Returns something depending on scores + ranges."""
        if self.best_score() < min_score:
            return "?"

        # ensure that the best subtype is at least min_lead better than the second best
        top_2 = self.as_npdm()[:2]
        if len(top_2) == 2 and top_2[0][1] - top_2[1][1] < min_lead:
            return "???"

        return self.best_subtype()

    def __rich__(self) -> str:
        text = f"[bold]{self.best_subtype()}[/bold]"
        text += f": {self.best_score():.2f}"
        return text

    def __repr__(self):
        top_3 = self.as_npdm()[:3]
        scored_types = " / ".join(f"{st}:{score:.3f}" for st, score in top_3)
        return f"SegmentMatch({scored_types} / ...)"

    def __str__(self):
        return self.__repr__()


class KmerIndexFlu(BaseModel):
    """A collection of kmer sets for a particular segment."""

    location: Path

    # Which segment does this capture?
    segment: SegmentType

    # The size of kmers
    size: int

    # A dictionary of KmerSets, keyed by the name of the set.
    index: KmerSetDict = Field(repr=False, default_factory=dict)

    all_kmers: set[int] = Field(repr=False, default_factory=set)
    pairwise: PairwiseDistances = Field(repr=False, default_factory=PairwiseDistances)

    def load(self):
        if self.index:
            msg = "Already loaded"
            raise RuntimeError(msg)

        # Recognise
        header_parser = FastaHeader.get_parser_for_file(self.location)
        if header_parser is None:
            msg = "Cannot recognise FastaHeaders"
            raise RuntimeError(msg)

        with open_as_text(self.location) as fd:
            for nm, dna in iter_fasta(fd):
                header = header_parser.parse(nm)

                # We only want sequences for this segment.
                if header.segment != self.segment:
                    continue

                segment_type = header.classify_segment()
                if segment_type is None:
                    logger.warning(
                        "Sequence does not have a recognisable subtype for "
                        f"{self.segment}: {header}"
                    )
                    continue

                if segment_type not in self.index:
                    ks = KmerSet(size=self.size)
                    self.index[segment_type] = ks
                else:
                    ks = self.index[segment_type]
                # Add the kmers.
                ks.add_read(dna.to_bytes())

        self.all_kmers = {k for ks in self.index.values() for k in ks.distn}
        self.pairwise.load(self.index)

    def calc_match(self, reads: KmerSet) -> SegmentMatch:
        if not self.index:
            msg = "KmerIndex not loaded"
            raise RuntimeError(msg)

        def score(st: str) -> float:
            jsd = self.index[st].jensen_shannon_distance(
                reads, only_kmers=self.all_kmers
            )
            return jsd

        distances = sorted(
            [(subtype, score(subtype)) for subtype in self.index],
            key=operator.itemgetter(1),
        )

        return SegmentMatch(
            segment=self.segment,
            distances=tuple(distances),
            mean=self.pairwise.mean,
        )
