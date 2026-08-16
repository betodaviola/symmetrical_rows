from symmetrical_rows import get_cyclic_intervals, analysis_operations
from itertools import product

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

def affine_relations(row, slices):
    #slices are 3 for trichord symmetry, 4 for tetrachord symmetry, and 6 for hexachord symmetry
    if slices == 3:
        segment_type = "trichords"
    elif slices == 4:
        segment_type = "tetrachords"
    elif slices == 6:
        segment_type = "hexachords"
    
#already in affine_analysis()
    source_intervals = get_cyclic_intervals(row)
    affine_altered_intervals = [(x * 5) % 12 for x in source_intervals]

    #Generates row with affine itnervals
    affine_row = [0]
    for i in range(1, 12):
        new_pitch = (affine_row[i - 1] + affine_altered_intervals[i - 1]) % 12
        affine_row.append(new_pitch)

#new
    affine_segment_relationships = []

    sliced_source_pitches = []
    sliced_source_intervals = []
    sliced_target_pitches = []
    sliced_target_intervals = []

    # Divide the row pitches and intervals into trichords, tetrachords, or hexachords
    for i in range(12):
        if i % slices == 0:
            pitch_source_group = row[i:i + slices]
            sliced_source_pitches.append(tuple(pitch_source_group))

            interval_source_group = source_intervals[i:i + (slices - 1)]
            sliced_source_intervals.append(tuple(interval_source_group))

            pitch_target_group = affine_row[i:i + slices]
            sliced_target_pitches.append(tuple(pitch_target_group))

            interval_target_group = affine_altered_intervals[i:i + (slices - 1)]
            sliced_target_intervals.append(tuple(interval_target_group))

    print(f"Sliced row: {sliced_source_pitches}")
    print(f"Sliced row intervals: {sliced_source_intervals}")
    print(f"Sliced affine row: {sliced_target_pitches}")
    print(f"Afine sliced intervals: {sliced_target_intervals}")

    for segment_idx in product(range(len(sliced_source_pitches)), range(len(sliced_source_pitches))):
        source = segment_idx[0]
        target = segment_idx[1]

        source_pitches = sliced_source_pitches[source]
        target_pitches = sliced_target_pitches[target]

        source_intervals = sliced_source_intervals[source]
        target_intervals = sliced_target_intervals[target]

        relations = []
        operation_names = ("P", "I", "R", "RI")

        # Make the source interval forms for P, I, R, and RI
        P_source_intervals = source_intervals
        I_source_intervals = tuple((-interval) % 12 for interval in source_intervals)
        R_source_intervals = tuple((-interval) % 12 for interval in reversed(source_intervals))
        RI_source_intervals = tuple(reversed(source_intervals))

        # Make the affine interval forms for P, I, R, and RI
        P_target_intervals = target_intervals
        I_target_intervals = tuple((-interval) % 12 for interval in target_intervals)
        R_target_intervals = tuple((-interval) % 12 for interval in reversed(target_intervals))
        RI_target_intervals = tuple(reversed(target_intervals))

        for source_form_index, source_form_intervals in enumerate((P_source_intervals, I_source_intervals, R_source_intervals, RI_source_intervals)):
            for target_form_index, target_form_intervals in enumerate((P_target_intervals, I_target_intervals, R_target_intervals, RI_target_intervals)):
                source_operation = operation_names[source_form_index]
                target_operation = operation_names[target_form_index]

                P_source_pitches = source_pitches
                I_source_pitches, R_source_pitches, RI_source_pitches = analysis_operations(source_pitches)
                source_pitch_forms = (P_source_pitches, I_source_pitches, R_source_pitches, RI_source_pitches)

                P_target_pitches = target_pitches
                I_target_pitches, R_target_pitches, RI_target_pitches = analysis_operations(target_pitches)
                target_pitch_forms = (P_target_pitches, I_target_pitches, R_target_pitches, RI_target_pitches)

                if source_form_intervals == target_form_intervals:
                    transposition = (target_pitch_forms[target_form_index][0] - source_pitch_forms[source_form_index][0]) % 12
                    relation_data = {
                        "source_form": source_operation,
                        "target_form": target_operation,
                        "transposition": transposition
                    }
                    relations.append(relation_data)
                
        output_data = {
            "pair": (source, target),
            "relations": relations
        }

        affine_segment_relationships.append(output_data)

    return segment_type, affine_segment_relationships



for row in row_list:
    relashionships = affine_relations(row, 3)
    print(relashionships)