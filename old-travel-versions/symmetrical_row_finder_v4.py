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

        # A new list is created for every row so relations cannot carry over
        # from the previous row.
        relations = []

        if index == affine_relation_id:
            original_row = row_list[index]
            original_intervals = get_cyclic_intervals(original_row)

            affine_relations = calculate_rotation_symmetry(
                affine_row,
                original_intervals,
                exclude_zero=False,
            )

            # Check every direct M5 relation.
            if affine_relations is not None:
                for relation in affine_relations:
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
                "relation": relations
            })
        else:
            original_row = row_list[affine_relation_id]
            original_intervals = get_cyclic_intervals(original_row)
            affine_relations = calculate_rotation_symmetry(
                affine_row,
                original_intervals,
                exclude_zero=False,
            )

            if affine_relations is not None:
                for symmetry in affine_relations:
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
            affine_relationship.append({
                "partner": affine_relation_id,
                "relation": relations
            })

    return affine_relationship

def trichordal_relations(row_classes):
    trichordal_relationships = []
    interval_lists = []

    for index, item in enumerate(row_classes):
        row_relationships = []

        interval_lists.append(get_cyclic_intervals(item["row"]))

        # Find trichordal relations. they will always exist but this displays it better
        trichord_pitches = []
        trichord_intervals = []

        for i in range(12):
            if i % 3 == 0:
                trichord = item["row"][i:i + 3]
                trichord_pitches.append(trichord)

                trichord_int = interval_lists[index][i:i + 2]
                trichord_intervals.append(trichord_int)

        for tric_idx in combinations(range(4), 2):
            source = tric_idx[0]
            target = tric_idx[1]

            source_int_a = trichord_intervals[source][0]
            source_int_b = trichord_intervals[source][1]
            target_int_a = trichord_intervals[target][0]
            target_int_b = trichord_intervals[target][1]

            source_pitches = trichord_pitches[source]
            target_pitches = trichord_pitches[target]

            relations = []

            # T
            if (target_int_a, target_int_b) == (source_int_a, source_int_b):
                transposition = (target_pitches[0] - source_pitches[0]) % 12
                relations.append(f"T{transposition}")

            # I
            if (target_int_a, target_int_b) == ((-source_int_a) % 12, (-source_int_b) % 12):
                altered_source = tuple((-pitch) % 12 for pitch in source_pitches)
                transposition = (target_pitches[0] - altered_source[0]) % 12
                relations.append(f"T{transposition}I")

            # R
            if (target_int_a, target_int_b) == ((-source_int_b) % 12, (-source_int_a) % 12):
                altered_source = tuple(reversed(source_pitches))
                transposition = (target_pitches[0] - altered_source[0]) % 12
                relations.append(f"T{transposition}R")

            # RI
            if (target_int_a, target_int_b) == (source_int_b, source_int_a):
                inversion = tuple((-pitch) % 12 for pitch in source_pitches)
                altered_source = tuple(reversed(inversion))
                transposition = (target_pitches[0] - altered_source[0]) % 12
                relations.append(f"T{transposition}RI")

            row_relationships.append({
                "pair": (source, target),
                "relations": relations
            })

        trichordal_relationships.append(row_relationships)

    return trichordal_relationships

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

def main():
    row_classes = matrix_finder()
    analysis_results = rotational_symmetry_analysis(row_classes)
    affine_results = affine_analysis(row_classes)
    trichordal_relationships = trichordal_relations(row_classes)

    symmetry_printing(analysis_results)
    print(affine_results)
    print(trichordal_relationships)

if __name__ == "__main__":
    main()
