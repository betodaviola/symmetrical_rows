small = {
    "index pair": (2, 6),
    "cardinality": 3,
    "segment_length": 3,
    "invariant pitches": (1, 4, 8),
    "segment type": "noncanonical/sliding"
}

medium = {
    "index pair": (2, 6),
    "cardinality": 4,
    "segment_length": 4,
    "invariant pitches": (1, 4, 8, 10),
    "segment type": "noncanonical/sliding"
}

large = {
    "index pair": (1, 5),
    "cardinality": 5,
    "segment_length": 5,
    "invariant pitches": (1, 4, 8, 10, 11),
    "segment type": "noncanonical/sliding"
}

invariants = [small, medium, large]

def cleanup_invariance_results(invariants):
    print(invariants)
    for seg_len in  




cleanup_invariance_results(invariants)