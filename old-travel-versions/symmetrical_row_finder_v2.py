from itertools import product
from math import gcd

def normalize(row):
    first_pitch = row[0]
    return tuple((pitch - first_pitch) % 12 for pitch in row)


def get_matrix_key(row):
    prime = normalize(row)

    inversion = tuple((-pitch) % 12 for pitch in prime)

    retrograde = normalize(tuple(reversed(prime)))

    retrograde_inversion = normalize(tuple(reversed(inversion)))

# This chooses a version to represent the row consistently for comparison and deletion of redundant rows
# It is not musically relevant
    return min( 
        prime,
        inversion,
        retrograde,
        retrograde_inversion,
    )

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
                            # now we run the function that finds the matrix key (one consisten version for each matrix)
                            matrix_key = get_matrix_key(testing_row)
                            # Create the connector-sign list in plain syntax.
                            connector_signs = []

                            for connector in connectors:
                                if connector == z:
                                    connector_signs.append(1)
                                else:
                                    connector_signs.append(-1)

                            connector_signs = tuple(connector_signs)


                            # If this matrix class has not appeared before,
                            # store this as the main, first-found row.
                            if matrix_key not in matrix_classes:
                                matrix_classes[matrix_key] = {
                                    "row_id": str(len(matrix_classes)),
                                    "matrix_key": matrix_key,

                                    # Information about the first row found
                                    "x": x,
                                    "y": y,
                                    "x_equals_y": x == y,

                                    "z": z,
                                    "connectors": connectors,
                                    "connector_signs": connector_signs,

                                    "uniform_connectors": (
                                        len(set(connectors)) == 1
                                    ),

                                    "distribution": distribution,
                                    "intervals": tuple(row_intervals),
                                    "row": tuple(testing_row),

                                    # This will contain only later discoveries
                                    # of the same matrix class.
                                    "derivations": [],
                                }


                            # If the matrix class already exists,
                            # save this as an additional derivation.
                            else:
                                derivation = {
                                    "x": x,
                                    "y": y,
                                    "x_equals_y": x == y,

                                    "z": z,
                                    "connectors": connectors,
                                    "connector_signs": connector_signs,

                                    "uniform_connectors": (
                                        len(set(connectors)) == 1
                                    ),

                                    "distribution": distribution,
                                    "intervals": tuple(row_intervals),
                                    "row": tuple(testing_row),
                                }

                                matrix_classes[matrix_key][
                                    "derivations"
                                ].append(derivation)




    return list(matrix_classes.values())








def main():
    row_classes = matrix_finder()

    for result in row_classes:
        print(
            result["row_id"],
            result["row"],
        )

if __name__ == "__main__":
    main()