from pprint import pprint

from symmetrical_rows import get_related_rows
from symmetrical_rows import matrix_finder

def cyclic_invariants(source_row, target_row):
    invariance_indices = []

    for i in range(12):
        if source_row[i] == target_row[i]:
            invariance_indices.append(i)
    gaps = []
    for i in range(1, len(invariance_indices)):
        gaps.append(invariance_indices[i] - invariance_indices[i - 1])

    return gaps, invariance_indices

def find_gap_pattern(gaps, invariance_indices):
    repeating_pattern = None
    relevant_invariant_indices = []

    # First test the complete circular gap sequence.
    boundary_gap = (
        12
        + invariance_indices[0]
        - invariance_indices[-1]
    )

    circular_gaps = gaps + [boundary_gap]

    pattern_size = 1

    while pattern_size <= len(circular_gaps) // 2:

        # A repeating pattern must divide the complete
        # circular gap sequence evenly.
        if len(circular_gaps) % pattern_size != 0:
            pattern_size += 1
            continue

        candidate = circular_gaps[0:pattern_size]

        repetitions = (
            len(circular_gaps) // pattern_size
        )

        if candidate * repetitions == circular_gaps:
            repeating_pattern = candidate
            relevant_invariant_indices = invariance_indices.copy()
            break

        pattern_size += 1

    # If the complete circular sequence is not periodic,
    # look for a repeating pattern visible within the written row.
    if not repeating_pattern:
        pattern_size = 1

        while pattern_size <= len(gaps) // 2:

            candidate = gaps[0:pattern_size]

            matches = True
            checking_index = pattern_size

            while checking_index < len(gaps):

                checking_chunk = gaps[
                    checking_index:checking_index + pattern_size
                ]

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
        occurrences = (
            len(gaps) // len(repeating_pattern)
        )
    else:
        period = None
        occurrences = None

    return (repeating_pattern, period, occurrences, relevant_invariant_indices)

def find_hidden_patterns(gaps, candidate_period, invariance_indices):
    hidden_results = []

    # Try every gap as a possible beginning of a hidden pattern.
    for starting_gap in range(len(gaps)):
        gap_index = starting_gap
        hidden_gaps = []
        relevant_invariant_indices = [invariance_indices[starting_gap]]

        while gap_index < len(gaps):
            gap_sum = 0

            # Keep combining consecutive gaps until we reach
            # or exceed the candidate period.
            while gap_sum < candidate_period and gap_index < len(gaps):
                gap_sum += gaps[gap_index]
                gap_index += 1

            if gap_sum == candidate_period:
                hidden_gaps.append(gap_sum)
                relevant_invariant_indices.append(
                    invariance_indices[gap_index]
                )
            else:
                break

        # Normal in-row periodicity needs at least two occurrences.
        # Period 6 is the exception: one occurrence can become
        # periodic when the same row comparison repeats.
        if (len(hidden_gaps) > 1 or (candidate_period == 6 and len(hidden_gaps) == 1)):
            embedded = (len(relevant_invariant_indices) < len(invariance_indices))

            result = {
                "period": candidate_period,
                "pattern": (candidate_period,),
                "gap_occurrences": len(hidden_gaps),
                "indices": tuple(relevant_invariant_indices),
                "embedded": embedded
            }

            # Avoid storing exactly the same result twice.
            if result not in hidden_results:
                hidden_results.append(result)

    return hidden_results


def analyze_invariant_periodicity(row_classes):
    periodic_invariants = []
    for item in row_classes:
        source_row = item["row"]

        labels_list, related_row_lists = get_related_rows(source_row)
        regular_invariants = {}
        for target_list_i, target_list in enumerate(related_row_lists):
            for target_i, target_row in enumerate(target_list):
                label = labels_list[target_list_i][target_i]

                if target_list_i == 0 and target_i == 0:
                    continue

                gaps, invariance_indices = cyclic_invariants(source_row, target_row)

                
                periodicity_results = []

                # Fewer than two invariants cannot produce even the
                # special repeat-only period-6 case.
                if len(invariance_indices) < 2:
                    continue

                # First find a pattern directly visible in the complete gap list.
                (
                    repeating_pattern,
                    period,
                    occurrences,
                    relevant_invariant_indices
                ) = find_gap_pattern(gaps, invariance_indices)

                if repeating_pattern:
                    periodicity_results.append({
                        "period": period,
                        "pattern": tuple(repeating_pattern),
                        "gap_occurrences": occurrences,
                        "indices": tuple(relevant_invariant_indices),
                        "embedded": False
                    })

                # Search ALL candidate periods even if a direct pattern
                # was already found.
                for candidate_period in range(2, 7):
                    hidden_results = find_hidden_patterns(
                        gaps,
                        candidate_period,
                        invariance_indices
                    )

                    for result in hidden_results:
                        duplicate = False

                        for existing_result in periodicity_results:
                            if (
                                result["period"] == existing_result["period"]
                                and result["pattern"] == existing_result["pattern"]
                                and set(result["indices"]).issubset(existing_result["indices"])
                            ):
                                duplicate = True
                                break

                        if not duplicate:
                            periodicity_results.append(result)

                # Test each discovered pattern independently for continuation
                # across repetition of the same row comparison.
                for result in periodicity_results:
                    pattern = result["pattern"]
                    relevant_indices = result["indices"]

                    pattern_gaps_used = len(relevant_indices) - 1

                    next_pattern_index = (
                        pattern_gaps_used % len(pattern)
                    )

                    next_expected_gap = pattern[next_pattern_index]

                    boundary_gap = (
                        12
                        + relevant_indices[0]
                        - relevant_indices[-1]
                    )

                    # The boundary must continue the expected pattern,
                    # and the pattern phase must reset correctly for the
                    # next copy of the row.
                    if (
                        boundary_gap == next_expected_gap
                        and len(relevant_indices) % len(pattern) == 0
                        and 12 % result["period"] == 0
                    ):
                        result["cyclic"] = True
                    else:
                        result["cyclic"] = False

                related_row = label

                if periodicity_results:
                    regular_invariants[related_row] = periodicity_results

        periodic_invariants.append(regular_invariants)
    return periodic_invariants
    

row_classes = matrix_finder()

periodicity_data = analyze_invariant_periodicity(row_classes)


with open("periodicity_output.txt", "w") as file:
    pprint(periodicity_data, stream=file, width=120, sort_dicts=False)

