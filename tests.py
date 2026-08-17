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

def invariance_finder(row_classes):
    invariants = []
    for row in row_classes:
        row_invariants = []
        for segment_size in range(3, 7):
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

            row_variation_labels = ["T", "I", "R", "RI", "M5"]
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
                        label += "M5"

                    invariance_list = get_invariance_comparison(row, tgt, segment_size)

                    row_invariants.append({
                        "row-form_relation": label, 
                        "invariants": invariance_list
                    })
        
        invariants.append(row_invariants)

    return invariants

print(invariance_finder(row_list))


