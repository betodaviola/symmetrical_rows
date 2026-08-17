from symmetrical_rows import get_cyclic_intervals, analysis_operations, trivial_operations
from itertools import product, combinations

# From the current generated system:
row_69 = (0, 2, 5, 6, 8, 11, 10, 1, 3, 4, 7, 9)
row_1 = (0, 1, 2, 5, 4, 3, 6, 7, 8, 11, 10, 9)

# Arbitrary twelve-tone rows outside the generating system:
row_a = (0, 4, 1, 7, 3, 10, 2, 9, 5, 11, 6, 8)
row_b = (0, 7, 3, 10, 4, 1, 8, 5, 11, 2, 9, 6)

# Deliberately constructed to contain useful local ordered material:
row_c = (0, 2, 5, 9, 1, 7, 4, 10, 3, 11, 6, 8)
row_d = (9, 1, 7, 0, 4, 10, 3, 2, 11, 6, 8, 5)

row_list = [row_69, row_1, row_a, row_b, row_c, row_d]

def get_invariance_comparison(source_row, target_row, segment_size):
#find every segment of size n in a row
    segmented_source = []
    segmented_target = []
    invariance_list = []

    for i in range(len(source_row) - segment_size + 1):
        source_segment = source_row[i:i + segment_size]
        segmented_source.append(source_segment)
        target_segment = target_row[i:i + segment_size]
        segmented_target.append(target_segment)

    for source_index in range(len(segmented_source)):
        for target_index in range(len(segmented_target)):
            source_pitches = segmented_source[source_index]
            target_pitches = segmented_target[target_index]

            invariant_pitches = tuple(sorted(set(source_pitches) & set(target_pitches)))
            invariance_cardinality = len(invariant_pitches)

            if invariance_cardinality != 0:
                if segment_size == 3 and source_index % segment_size == 0 and target_index % segment_size == 0:
                    note = "trichordal"
                elif segment_size == 4 and source_index % segment_size == 0 and target_index % segment_size == 0:
                    note = "tetrachordal"
                elif segment_size == 6 and source_index % segment_size == 0 and target_index % segment_size == 0:
                    note = "hexachordal"
                else:
                    note = "noncanonical/sliding"
                
                invariance_list.append({
                    "index pair": (source_index, target_index),
                    "cardinality": invariance_cardinality,
                    "segment_length": segment_size,
                    "invariant pitches": invariant_pitches,
                    "non-triviality": note
                })

    return invariance_list

def clean_invariants(invariance_results):
    canonical_results = []
    sliding_results = []

    # Separate canonical results from sliding results.
    # Canonical results are always kept.
    # Sliding results are kept only if the whole segment is invariant.
    for result in invariance_results:
        if result["non-triviality"] == "noncanonical/sliding":
            if result["cardinality"] == result["segment_length"]:
                sliding_results.append(result)
        else:
            canonical_results.append(result)

    # Check larger sliding invariants first.
    sliding_results.sort(key=lambda result: result["segment_length"], reverse=True)

    kept_sliding = []

    for result in sliding_results:
        redundant = False

        source_start = result["index pair"][0]
        target_start = result["index pair"][1]
        segment_size = result["segment_length"]

        for larger in kept_sliding:
            larger_source_start = larger["index pair"][0]
            larger_target_start = larger["index pair"][1]
            larger_size = larger["segment_length"]

            # Check whether this result is contained inside the larger
            # invariant in both the source row and target row.
            source_contained = (
                larger_source_start <= source_start
                and larger_source_start + larger_size >= source_start + segment_size
            )

            target_contained = (
                larger_target_start <= target_start
                and larger_target_start + larger_size >= target_start + segment_size
            )

            # Also make sure the smaller invariant pitch collection
            # is actually contained in the larger invariant collection.
            pitches_contained = set(result["invariant pitches"]).issubset(
                larger["invariant pitches"]
            )

            if source_contained and target_contained and pitches_contained:
                redundant = True
                break

        if not redundant:
            kept_sliding.append(result)

    return canonical_results + kept_sliding

def invariance_finder(row_classes):
    invariants = []
    for row in row_classes:
        row_invariants = []
        inversion, retrograde, retrograde_inversion = analysis_operations(row)
        # find the affine version of the row
        source_intervals = get_cyclic_intervals(row)
        affine_altered_intervals = [(x * 5) % 12 for x in source_intervals]
        affine_row = [0]
        for i in range(1, 12):
            new_pitch = (affine_row[i - 1] + affine_altered_intervals[i - 1]) % 12
            affine_row.append(new_pitch)
        #get the afine i r and ri
        affine_row = tuple(affine_row)
        m5_i, m5_r, m5_ri = trivial_operations(affine_row)
        affine_matrix_key = min(affine_row, m5_i, m5_r, m5_ri)
        affine_p = affine_matrix_key
        affine_i, affine_r, affine_ri = analysis_operations(affine_p)

        #generate rows to compare
        p_ts = []
        i_ts = []
        r_ts = []
        ri_ts = []
        m5p_ts = []
        m5i_ts = []
        m5r_ts = []
        m5ri_ts = []

        for t in range(12):
            t_p = tuple((pitch + t) % 12 for pitch in row)
            p_ts.append(t_p)
            i_p = tuple((pitch + t) % 12 for pitch in inversion)
            i_ts.append(i_p)
            r_p = tuple((pitch + t) % 12 for pitch in retrograde)
            r_ts.append(r_p)
            ri_p = tuple((pitch + t) % 12 for pitch in retrograde_inversion)
            ri_ts.append(ri_p)
            m5t_p = tuple((pitch + t) % 12 for pitch in affine_p)
            m5p_ts.append(m5t_p)
            m5i_p = tuple((pitch + t) % 12 for pitch in affine_i)
            m5i_ts.append(m5i_p)
            m5r_p = tuple((pitch + t) % 12 for pitch in affine_r)
            m5r_ts.append(m5r_p)
            m5ri_p = tuple((pitch + t) % 12 for pitch in affine_ri)
            m5ri_ts.append(m5ri_p)

        row_variation_labels = ["T", "I", "R", "RI"]
        comparing_row_list = [p_ts, i_ts, r_ts, ri_ts, m5p_ts, m5i_ts, m5r_ts, m5ri_ts]

        for tgt_ls_i, tgt_ls in enumerate(comparing_row_list):
            op_type = ''

            if tgt_ls_i > 0 and tgt_ls_i < 4:
                op_type = row_variation_labels[tgt_ls_i]

            if tgt_ls_i > 4:
                op_type = row_variation_labels[tgt_ls_i - 4]

            for tgt_i, tgt in enumerate(tgt_ls):
                label = f"T{tgt_i}{f'{op_type}' if op_type else ''}"

                if tgt_ls_i > 3:
                    label += " of affine partner"

                all_invariance_results = []

                for segment_size in range(3, 7):
                    invariance_list = get_invariance_comparison(row, tgt, segment_size)
                    all_invariance_results.extend(invariance_list)

                cleaned_invariants = clean_invariants(all_invariance_results)

                segment_invariants = {}

                for result in cleaned_invariants:
                    segment_size = result["segment_length"]

                    if segment_size not in segment_invariants:
                        segment_invariants[segment_size] = []

                    segment_invariants[segment_size].append(result)

                row_invariants.append({
                    "row-form_relation": label,
                    "invariants": segment_invariants
                })

        invariants.append(row_invariants)

    return invariants

print(invariance_finder(row_list))


