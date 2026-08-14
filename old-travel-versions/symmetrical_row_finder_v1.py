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

    return min(
        prime,
        inversion,
        retrograde,
        retrograde_inversion,
    )


valid_rows = []
seen_matrices = set()


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

        forms = list(dict.fromkeys(forms))

        for z in range(1, 12):

            if gcd(x, y, z, 12) > 1:
                continue

            for distribution in product(forms, repeat=4):

                row_intervals = []

                for position, trichord in enumerate(distribution):
                    row_intervals.extend(trichord)

                    if position < 3:
                        row_intervals.append(z)

                testing_row = [0]
                used_pitches = {0}

                for interval in row_intervals:
                    new_pitch = (testing_row[-1] + interval) % 12

                    if new_pitch in used_pitches:
                        break

                    testing_row.append(new_pitch)
                    used_pitches.add(new_pitch)

                else:
                    matrix_key = get_matrix_key(testing_row)

                    if matrix_key not in seen_matrices:
                        seen_matrices.add(matrix_key)

                        valid_rows.append(
                            {
                                "x": x,
                                "y": y,
                                "z": z,
                                "distribution": distribution,
                                "intervals": tuple(row_intervals),
                                "row": tuple(testing_row),
                                "matrix_key": matrix_key,
                            }
                        )






# PRINT ROWS WHERE x == y ONLY

equal_xy_rows = [
    result for result in valid_rows
    if result["x"] == result["y"]
]
for result in equal_xy_rows:
    print(list(result["row"]))

print(f"Rows where x = y: {len(equal_xy_rows)}")




#PRINT ALL ROWS

# for result in valid_rows:
#     print(list(result["row"]))

# print(f"Total surviving rows: {len(valid_rows)}")