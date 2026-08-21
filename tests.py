# No invariant positions at all
row_no_cycle_a = (4, 5, 7, 8, 0, 10, 1, 9, 2, 3, 11, 6)
row_no_cycle_b = (5, 7, 8, 0, 10, 1, 9, 2, 3, 11, 6, 4)
# Two invariant positions, true cyclic period 6
row_period_6_a = (7, 5, 2, 8, 9, 6, 11, 3, 4, 0, 1, 10)
row_period_6_b = (7, 2, 8, 9, 6, 3, 11, 4, 0, 1, 10, 5)
# Three invariant positions, true cyclic period 4
row_period_4_a = (5, 7, 2, 9, 10, 6, 4, 8, 3, 1, 11, 0)
row_period_4_b = (5, 2, 9, 6, 10, 4, 8, 1, 3, 11, 0, 7)
# Four invariant positions, true cyclic period 3
row_period_3_a = (8, 10, 5, 2, 11, 1, 6, 0, 4, 9, 7, 3)
row_period_3_b = (8, 5, 11, 2, 1, 0, 6, 4, 7, 9, 3, 10)
# Six invariant positions, true cyclic period 2
row_period_2_a = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
row_period_2_b = (2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1)
# Three irregular invariant positions
row_irregular_a = (11, 8, 7, 4, 10, 2, 0, 6, 9, 1, 5, 3)
row_irregular_b = (11, 4, 7, 10, 2, 0, 9, 6, 1, 5, 3, 8)
# Thee invariant positions separated by 5 [0, 5, 10]
row_spacing_5_a = (11, 0, 3, 2, 7, 5, 9, 4, 10, 6, 1, 8)
row_spacing_5_b = (11, 3, 2, 7, 9, 5, 4, 10, 6, 8, 1, 0)
# Double cycle x y . .
double_cycle_1_a = (1, 2, 3, 3, 1, 2, 3, 3, 1, 2, 3, 3)
double_cycle_1_b = (1, 2, 4, 4, 1, 2, 4, 4, 1, 2, 4, 4)
# Every four but dirty
edge_tests_a = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
edge_tests_b = (1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0)
#shifted 4s
shifted_4s_a = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
shifted_4s_b = (0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0)

def cyclic_invariants(source_row, target_row):
    invariance_indices = []

    for i in range(12):
        if source_row[i] == target_row[i]:
            invariance_indices.append(i)
    gaps = []
    for i in range(1, len(invariance_indices)):
        gaps.append(invariance_indices[i] - invariance_indices[i - 1])

    print(gaps)
    return gaps, invariance_indices

def find_gap_pattern(gaps, invariance_indices):
    pattern_size = 1
    repeating_pattern = None
    relevant_invariant_indices = []

    while pattern_size <= len(gaps) // 2:

        # Take the first n gaps as the candidate repeating pattern.
        candidate = gaps[0:pattern_size]

        matches = True
        checking_index = pattern_size

        while checking_index < len(gaps):

            # Take the next chunk.
            # At the end of the row, this chunk may be shorter
            # than the complete candidate pattern.
            checking_chunk = gaps[
                checking_index:checking_index + pattern_size
            ]

            # Compare the chunk with the same-length beginning
            # of the candidate. This allows the row to end partway
            # through an otherwise repeating pattern.
            if checking_chunk != candidate[:len(checking_chunk)]:
                matches = False
                break

            checking_index += pattern_size

        if matches:
            repeating_pattern = candidate
            relevant_invariant_indices = invariance_indices.copy()
            break

        pattern_size += 1

    if repeating_pattern:
        period = sum(repeating_pattern)
        occurrences = len(gaps) // len(repeating_pattern)
    else:
        period = None
        occurrences = None

    return repeating_pattern, period, occurrences, relevant_invariant_indices

def find_hidden_patterns(gaps, candidate_period, invariance_indices):
    gap_index = 0
    gaps_used = 0
    hidden_gaps = []
    repeating_pattern = None
    period = None
    occurrences = None

    relevant_invariant_indices = [invariance_indices[gap_index]]

    while gaps_used < len(gaps):
        gap_sum = 0

        while gap_sum < candidate_period and gap_index < len(gaps):
            #this is very smart. it loops through the list without gettin out of bounds
            #because it stays inside mod n where n is the list lenghth. goes from 0 to n - 1
            #no longer necessary: gap = gaps[gap_index % len(gaps)] 
            gap = gaps[gap_index] 

            gap_sum += gap
            gap_index += 1
            gaps_used += 1

        if gap_sum == candidate_period:
            hidden_gaps.append(gap_sum)
            relevant_invariant_indices.append(invariance_indices[gap_index])
        else:
            break


    if len(hidden_gaps) > 1:
        repeating_pattern, period, occurrences, relevant_invariant_indices = find_gap_pattern(hidden_gaps, relevant_invariant_indices)

    return repeating_pattern, period, occurrences, relevant_invariant_indices

def analyze_invariant_periodicity(source_row, target_row):
    gaps, invariance_indices = cyclic_invariants(source_row, target_row)
    embeded = False
    cyclic = False

    if len(invariance_indices) < 3:
        return None, None, None, False

    repeating_pattern, period, occurrences, relevant_invariant_indices = find_gap_pattern(gaps, invariance_indices)
    
    regular_invariants = []
    for candidate_period in (range(2, 6)):
        if not repeating_pattern:
            repeating_pattern, period, occurrences, relevant_invariant_indices = find_hidden_patterns(gaps,candidate_period, invariance_indices)
            if repeating_pattern:
                embeded = True

        if repeating_pattern:
            pattern_gaps_used = len(relevant_invariant_indices) - 1
            next_pattern_index = (pattern_gaps_used % len(repeating_pattern))
            next_expected_gap = repeating_pattern[next_pattern_index]
            boundary_gap = (12 + relevant_invariant_indices[0] - relevant_invariant_indices[-1])
            if boundary_gap == next_expected_gap:
                cyclic = True
        


        

    return repeating_pattern, period, occurrences, relevant_invariant_indices, embeded

    








#periodicity_data = analyze_invariant_periodicity(row_period_6_a, row_period_6_b)
#periodicity_data = analyze_invariant_periodicity(row_spacing_5_a, row_spacing_5_b)
#periodicity_data = analyze_invariant_periodicity(row_period_4_a, row_period_4_b)
#periodicity_data = analyze_invariant_periodicity(shifted_4s_a, shifted_4s_b)
#periodicity_data = analyze_invariant_periodicity(row_period_3_a, row_period_3_b)
#periodicity_data = analyze_invariant_periodicity(double_cycle_1_a, double_cycle_1_b)
#periodicity_data = analyze_invariant_periodicity(row_no_cycle_a, row_no_cycle_b)
periodicity_data = analyze_invariant_periodicity(edge_tests_a, edge_tests_b)

print(periodicity_data)

