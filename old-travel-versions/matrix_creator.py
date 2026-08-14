row2matrix = [0, 8, 4, 9, 1, 5, 10, 2, 6, 11, 7, 3]

def make_matrix(prime_row):
    calculated_rows = {} #used dictionary becauase it makes easier to access specific information when manipulating variable names (now as keys)
    i0 = []

    for pitch in prime_row: # invert row to create the first column of the matrix (I0)
        new_pitch = (pitch * -1) + 12
        if new_pitch == 12:
            new_pitch = 0
        i0.append(new_pitch)

    for line in range(12):
        calculated_rows[f"l{i0[line]}"] = [] # creates dictionary keys
        calculated_rows[f"l{i0[line]}"] = [(n + i0[line]) % 12 for n in prime_row]

    matrix = list(calculated_rows.values())

    return matrix

matrix_dict = make_matrix(row2matrix)
print(matrix_dict)
