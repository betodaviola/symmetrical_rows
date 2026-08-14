from symmetrical_row_finder_v4 import get_cyclic_intervals
from itertools import product
from itertools import combinations

row_list = [(0, 6, 2, 7, 11, 5, 10, 4, 8, 1, 9, 3)]
interval_list = []

for row in row_list:
    interval_list.append(get_cyclic_intervals(row))
# Find trichordal relations. they will always exist but this displays it better
for trichord in interval_list:
    trichord_intervals = [(trichord[0], trichord[1]), (trichord[3], trichord[4]), (trichord[6], trichord[7]), (trichord[9], trichord[10])]
    for tric_int in combinations(trichord_intervals, 2):
        print(tric_int)

test = ("a", "b", "c", "d")
for testitem in combinations(test, 2):
    print(testitem)
