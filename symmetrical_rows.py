from itertools import product, combinations
from math import gcd

def normalize(row):
    first_pitch = row[0]
    return tuple((pitch - first_pitch) % 12 for pitch in row)

def trivial_operations(prime):
    inversion = tuple((-pitch) % 12 for pitch in prime)
    retrograde = normalize(tuple(reversed(prime)))
    retrograde_inversion = normalize(tuple(reversed(inversion)))

    return inversion, retrograde, retrograde_inversion    

def matrix_finder():
    matrix_classes = {}

    for x in range(1, 12):
        for y in range(1, 12):

            if not (x <= y and x + y < 12):
                continue

            tric_int_A = (x, y)
            tric_int_A_neg = ((-x) % 12, (-y) % 12)
            tric_int_B = (y, x)
            tric_int_B_neg = ((-y) % 12, (-x) % 12)

            forms = [
                tric_int_A,
                tric_int_A_neg,
                tric_int_B,
                tric_int_B_neg,
            ]

            # Python does not allow for repeated dictionary keys. The code below converts the forms into dictionary keys and then back to a list
            # When it becomes the dictionary, repeated forms are deleted. This deletes redundancies when x = y  
            forms = list(dict.fromkeys(forms))

            # Only use the canonical undirected connector sizes.
            # z=7, for example, is already represented by -5 == 7 mod 12.
            for z in range(1, 7):
                # Then check gcd
                if gcd(x, y, z, 12) > 1:
                    continue
                # Usually (z, -z). For z=6, both are 6, so remove the duplicate.
                possible_connectors = tuple(
                    dict.fromkeys((z, (-z) % 12))
                )

                # Generate every three-connector pattern:
                # (+,+,+), (+,+,-), (+,-,+), etc.
                for connectors in product(possible_connectors, repeat=3):
                    # Generates  trichord patterns
                    for distribution in product(forms, repeat=4):
                        row_intervals = []
                        for position, trichord in enumerate(distribution):
                            # extend adds the two elements in my tupled to a list rather than the tuplet in the list
                            row_intervals.extend(trichord)
                            if position < 3: # there are 4 positions (0,1,2,3), one for each trichord. the last one does not have a z added
                                # here append() is fine as the connector is not a tuplet but a single value
                                row_intervals.append(connectors[position])

                        testing_row = [0]
                        used_pitches = {0}

                        # for/else loop (GPT did this)
                        # else block executes only when the loop finishes normally—meaning it did not encounter break. useful
                        for interval in row_intervals:
                            new_pitch = (testing_row[-1] + interval) % 12

                            if new_pitch in used_pitches:
                                break

                            testing_row.append(new_pitch)
                            used_pitches.add(new_pitch)

                        else:
                            # The complete row contains twelve unique pitch classes.
                            # now we find the matrix key (one consisten version for each matrix)
                            prime = normalize(testing_row)
                            inversion, retrograde, retrograde_inversion = trivial_operations(prime)
                            # This chooses a version to represent the matrix consistently.
                            # This canonical version becomes the main row used for all later analysis.
                            matrix_key = min(prime, inversion, retrograde, retrograde_inversion)
                            # Create the connector-sign list in plain syntax.
                            connector_signs = []

                            for connector in connectors:
                                if connector == z:
                                    connector_signs.append(1)
                                else:
                                    connector_signs.append(-1)

                            connector_signs = tuple(connector_signs)

                            # Find the last interval that loops back to 0 (j)
                            j = (-prime[-1]) % 12
                            # Check sign keeping coherence with z
                            if j == z:
                                j_sign = 1
                            elif j == (-z) % 12:
                                j_sign = -1
                            else:
                                j_sign = None
                            # check if j equals z
                            j_equals_z = j_sign is not None
                            #check if z and j signs are coherent
                            if j_sign is not None:
                                j_z_coherence = j_sign in connector_signs
                            else:
                                j_z_coherence = False
                            # add j to interval list
                            row_intervals.append(j)
                            # All information below describes this generated version of the row.
                            # Every generated version is stored as a derivation, including the first one found.
                            derivation = {
                                "x": x,
                                "y": y,
                                "z": z,
                                "j": j,

                                "x_equals_y": x == y,
                                "j_equals_z": j_equals_z,

                                "connectors": connectors,
                                "connector_signs": connector_signs,
                                "j_sign": j_sign,
                                "j_z_coherence": j_z_coherence,

                                "uniform_connectors": (
                                    len(set(connectors)) == 1
                                ),

                                "distribution": distribution,
                                "intervals": tuple(row_intervals),
                                "row": tuple(prime),
                            }

                            # If this matrix class has not appeared before,
                            # create it using the canonical matrix key as the main row.
                            if matrix_key not in matrix_classes:
                                matrix_classes[matrix_key] = {
                                    "row_id": str(len(matrix_classes)),
                                    "row": tuple(matrix_key),

                                    # Every way this matrix was generated is kept here.
                                    # The first-found version is no longer treated differently.
                                    "derivations": [derivation],
                                }


                            # If the matrix class already exists,
                            # save this as an additional derivation.
                            else:
                                matrix_classes[matrix_key][
                                    "derivations"
                                ].append(derivation)




    return list(matrix_classes.values())

###################################### DEEPER ANALYSIS
def get_cyclic_intervals(row):
    cyclic_intervals = []

    # Find the 11 intervals inside the written row.
    for position in range(len(row) - 1):
        interval = (row[position + 1] - row[position]) % 12

        cyclic_intervals.append(interval)
    # Add j: the interval from the last pitch back to the first pitch.
    j = (row[0] - row[-1]) % 12
    cyclic_intervals.append(j)
    return tuple(cyclic_intervals)


def analysis_operations(prime):
    # These operations are not normalized.
    # This allows the later transposition calculation to describe# the exact operation applied to the original prime row.
    inversion = tuple((-pitch) % 12 for pitch in prime)
    retrograde = tuple(reversed(prime))
    retrograde_inversion = tuple(reversed(inversion))

    return inversion, retrograde, retrograde_inversion


def find_rotation_match(source_intervals, target_intervals, exclude_zero=False,):
    doubled_source = source_intervals + source_intervals

    # P against itself must skip rotation 0 because that is the identity.
    # I, R, and RI can use rotation 0 because the operation is still nonidentity.
    if exclude_zero:
        first_rotation = 1
    else:
        first_rotation = 0

    # This will contain every rotation that creates a match.
    rotation_symmetry = []

    # Check each possible rotation of the source interval cycle.
    for rotation in range(first_rotation, len(source_intervals)):
        rotated_source = doubled_source[
            rotation:rotation + len(source_intervals)
        ]

        if rotated_source == target_intervals:
            rotation_symmetry.append(rotation)

    return rotation_symmetry

def calculate_rotation_symmetry(source_row, target_intervals, exclude_zero=False):
    source_intervals = get_cyclic_intervals(source_row)
    rotation = find_rotation_match(source_intervals, target_intervals, exclude_zero)
    rotation_transposition = []

    if not rotation:
        return None
    # After rotating the source, source_row[rotation] becomes its first pitch.
    # This transposition moves that pitch to P0.

    for r in rotation:
        transposition = (-source_row[r]) % 12
        k_t_pair = (r, transposition)
        rotation_transposition.append(k_t_pair)


    return rotation_transposition # rotation k, transposition n

def analyze_row_symmetry(row):
    P = row
    I, R, RI = analysis_operations(P)
    # All altered forms will be compared with the interval cycle of P.
    P_intervals = get_cyclic_intervals(P)

    symmetries = {}
    # Rotation 0 is excluded only when comparing P with itself.
    symmetries["P"] = calculate_rotation_symmetry(P, P_intervals, exclude_zero=True)
    symmetries["I"] = calculate_rotation_symmetry(I, P_intervals)
    symmetries["R"] = calculate_rotation_symmetry(R, P_intervals)
    symmetries["RI"] = calculate_rotation_symmetry(RI, P_intervals)

    return symmetries

def rotational_symmetry_analysis(row_dict):
    analysis_results = []

    # The list index continues to match the row_id.
    for result in row_dict:
        row = result["row"]

        row_symmetries = analyze_row_symmetry(row)

        analysis_results.append(row_symmetries)

    return analysis_results


def affine_relations(row, affine_row, source_intervals, affine_altered_intervals, slices):
    #slices are 3 for trichord symmetry, 4 for tetrachord symmetry, and 6 for hexachord symmetry
    if slices == 3:
        segment_type = "trichords"
    elif slices == 4:
        segment_type = "tetrachords"
    elif slices == 6:
        segment_type = "hexachords"
    
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

    for segment_idx in product(range(len(sliced_source_pitches)), range(len(sliced_source_pitches))):
        source = segment_idx[0]
        target = segment_idx[1]

        source_pitches = sliced_source_pitches[source]
        target_pitches = sliced_target_pitches[target]

        source_intervals = sliced_source_intervals[source]
        target_intervals = sliced_target_intervals[target]

        relations = []
        # Make the source interval forms for P, I, R, and RI
        P_intervals = source_intervals

        I_intervals = tuple(
            (-interval) % 12 for interval in source_intervals
        )

        R_intervals = tuple(
            (-interval) % 12 for interval in reversed(source_intervals)
        )

        RI_intervals = tuple(
            reversed(source_intervals)
        )

        # Get the pitch versions of I, R, and RI
        I, R, RI = analysis_operations(source_pitches)

        # T
        if target_intervals == P_intervals:
            transposition = (
                target_pitches[0] - source_pitches[0]
            ) % 12
            relations.append(f"T{transposition}")

        # I
        if target_intervals == I_intervals:
            transposition = (
                target_pitches[0] - I[0]
            ) % 12
            relations.append(f"T{transposition}I")

        # R
        if target_intervals == R_intervals:
            transposition = (
                target_pitches[0] - R[0]
            ) % 12
            relations.append(f"T{transposition}R")

        # RI
        if target_intervals == RI_intervals:
            transposition = (
                target_pitches[0] - RI[0]
            ) % 12
            relations.append(f"T{transposition}RI")
      
        if relations:
            output_data = {
                "pair": (source, target),
                "relations": relations
            }

            affine_segment_relationships.append(output_data)

    return segment_type, affine_segment_relationships

def affine_analysis(row_classes):
    row_list = []
    affine_row_list = []
    affine_matrix_keys = []
    affine_relationship = []

    #extract rows
    for result in row_classes:
        row_list.append(result["row"])

    #apply affine calculations to intervals
    for row in row_list:
        source_intervals = get_cyclic_intervals(row)
        affine_altered_intervals = [(x * 5) % 12 for x in source_intervals]

        #Generates row with affine itnervals
        affine_row = [0]
        for i in range(1, 12):
            new_pitch = (affine_row[i - 1] + affine_altered_intervals[i - 1]) % 12
            affine_row.append(new_pitch)

        affine_row_list.append(tuple(affine_row)) # creates a list with the affine rows

    # finds the matrix key for each affine row in the list and makes a list with them
    for affine in affine_row_list:
        inversion, retrograde, retrograde_inversion = trivial_operations(affine)
        affine_matrix_key = min(affine, inversion, retrograde, retrograde_inversion)
        affine_matrix_keys.append(affine_matrix_key)

    for index, affine_testing_row in enumerate(affine_matrix_keys):
        affine_relation_id = row_list.index(affine_testing_row)
        affine_row = affine_row_list[index]

        # The source is the canonical row currently being analyzed.
        # affine_testing_row is the canonical P0 of its affine partner.
        source_row = row_list[index]
        source_intervals = get_cyclic_intervals(source_row)
        affine_partner_intervals = get_cyclic_intervals(affine_testing_row)

        #find all segment simmetries between the two canonical rows
        all_segment_relations = {}
        for slice_size in (3, 4, 6):
            segment_type, affine_segment_relationships = affine_relations(source_row, affine_testing_row, source_intervals, affine_partner_intervals, slice_size)
            chord_size_label = f"{segment_type} relations"
            if affine_segment_relationships:
                all_segment_relations[chord_size_label] = (affine_segment_relationships)

        # A new list is created for every row so relations cannot carry over
        # from the previous row.
        relations = []

        if index == affine_relation_id:
            original_row = row_list[index]
            original_intervals = get_cyclic_intervals(original_row)

            affine_rotation_relations = calculate_rotation_symmetry(
                affine_row,
                original_intervals,
                exclude_zero=False,
            )

            # Check every direct M5 relation.
            if affine_rotation_relations is not None:
                for relation in affine_rotation_relations:
                    rotation, transposition = relation

                    relations.append(
                        f"T{transposition}ρ{rotation}M5"
                    )

            # Also check I, R, and RI independently.
            I, R, RI = analysis_operations(affine_row)

            symmetries = {}
            symmetries["I"] = calculate_rotation_symmetry(
                I,
                original_intervals
            )
            symmetries["R"] = calculate_rotation_symmetry(
                R,
                original_intervals
            )
            symmetries["RI"] = calculate_rotation_symmetry(
                RI,
                original_intervals
            )

            for operation_type in ("I", "R", "RI"):
                symmetry_list = symmetries[operation_type]

                if symmetry_list is None:
                    continue

                for symmetry in symmetry_list:
                    rotation, transposition = symmetry

                    relations.append(
                        f"T{transposition}"
                        f"ρ{rotation}"
                        f"{operation_type}M5"
                    )

            affine_relationship.append({
                "partner": "self",
                "relation": relations,
                "segment_relationships": all_segment_relations
            })

        else:
            original_row = row_list[affine_relation_id]
            original_intervals = get_cyclic_intervals(original_row)

            affine_rotation_relations = calculate_rotation_symmetry(
                affine_row,
                original_intervals,
                exclude_zero=False,
            )

            if affine_rotation_relations is not None:
                for symmetry in affine_rotation_relations:
                    rotation, transposition = symmetry

                    relations.append(
                        f"T{transposition}ρ{rotation}M5"
                    )

            # Do this regardless of whether M5 worked.
            I, R, RI = analysis_operations(affine_row)

            symmetries = {}
            symmetries["I"] = calculate_rotation_symmetry(
                I,
                original_intervals
            )
            symmetries["R"] = calculate_rotation_symmetry(
                R,
                original_intervals
            )
            symmetries["RI"] = calculate_rotation_symmetry(
                RI,
                original_intervals
            )

            for operation_type in ("I", "R", "RI"):
                symmetry_list = symmetries[operation_type]

                if symmetry_list is None:
                    continue

                for symmetry in symmetry_list:
                    rotation, transposition = symmetry

                    relations.append(
                        f"T{transposition}"
                        f"ρ{rotation}"
                        f"{operation_type}M5"
                    )
            if all_segment_relations:
                segments_display = all_segment_relations
            else:
                segments_display = None
            affine_relationship.append({
                "partner": affine_relation_id,
                "relation": relations,
                "segment_relationships": segments_display
            })

    return affine_relationship

def segment_relations(row_classes, slices): 
    #slices are 3 for trichord symmetry, 4 for tetrachord symmetry, and 6 for hexachord symmetry
    segment_relationships = []

    for item in row_classes:
        row_relationships = []

        row = item["row"]
        row_intervals = get_cyclic_intervals(row)

        sliced_pitches = []
        sliced_intervals = []

        # Divide the row pitches and intervals into trichords, tetrachords, or hexachords
        for i in range(12):
            if i % slices == 0:
                pitch_group = row[i:i + slices]
                sliced_pitches.append(tuple(pitch_group))

                interval_group = row_intervals[i:i + (slices - 1)]
                sliced_intervals.append(tuple(interval_group))

        # Compare every segment with every other segment
        for segment_idx in combinations(range(len(sliced_pitches)), 2):
            source = segment_idx[0]
            target = segment_idx[1]

            source_pitches = sliced_pitches[source]
            target_pitches = sliced_pitches[target]

            source_intervals = sliced_intervals[source]
            target_intervals = sliced_intervals[target]

            relations = []

            # Make the interval forms for P, I, R, and RI
            P_intervals = source_intervals

            I_intervals = tuple(
                (-interval) % 12 for interval in source_intervals
            )

            R_intervals = tuple(
                (-interval) % 12 for interval in reversed(source_intervals)
            )

            RI_intervals = tuple(
                reversed(source_intervals)
            )

            # Get the pitch versions of I, R, and RI
            I, R, RI = analysis_operations(source_pitches)

            # T
            if target_intervals == P_intervals:
                transposition = (target_pitches[0] - source_pitches[0]) % 12
                relations.append(f"T{transposition}")

            # I
            if target_intervals == I_intervals:
                transposition = (target_pitches[0] - I[0]) % 12
                relations.append(f"T{transposition}I")

            # R
            if target_intervals == R_intervals:
                transposition = (target_pitches[0] - R[0]) % 12
                relations.append(f"T{transposition}R")

            # RI
            if target_intervals == RI_intervals:
                transposition = (target_pitches[0] - RI[0]) % 12
                relations.append(f"T{transposition}RI")

            row_relationships.append({
                "pair": (source, target),
                "relations": relations
            })

        segment_relationships.append(row_relationships)

    return segment_relationships


def symmetry_printing(analysis_results):
    for row_id, symmetries in enumerate(analysis_results):
        operation_labels = []

        for operation_type in ("P", "I", "R", "RI"):
            symmetry_list = symmetries[operation_type]

            if symmetry_list is None:
                continue

            for s in symmetry_list:
                rotation, transposition = s

                if operation_type == "P":
                    label = (f"T{transposition}"f"ρ{rotation}")
                else:
                    label = (
                        f"T{transposition}"
                        f"ρ{rotation}"
                        f"{operation_type}"
                    )

                operation_labels.append(label)

        if operation_labels:
            print(row_id, ", ".join(operation_labels))

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
    for item in row_classes:
        row = item["row"]
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

def main():
    row_classes = matrix_finder()
    analysis_results = rotational_symmetry_analysis(row_classes)
    affine_results = affine_analysis(row_classes)

    trichordal_relations = segment_relations(row_classes, 3)
    tetrachordal_relations = segment_relations(row_classes, 4)
    hexachordal_relations = segment_relations(row_classes, 6)

    invariants = invariance_finder(row_classes)

    #symmetry_printing(analysis_results)
    
    #print(trichordal_relations)
    #print(tetrachordal_relations)
    #print(hexachordal_relations)

    #print(affine_results)

    #print(invariants)

if __name__ == "__main__":
    main()
