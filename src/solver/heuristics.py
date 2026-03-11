# Provides optional optimization strategies such as MRV for improved performance.
"""Heuristics used by the timetable backtracking solver."""

def mrv_heuristic(variables: list, domains: dict) -> list:
    """
    Minimum Remaining Values (MRV) heuristic for variable selection in constraint satisfaction problems.
    This heuristic selects the variable with the fewest legal values left in its domain.

    Args:
        variables: A list of variables to choose from.
        domains: A dictionary mapping each variable to its current domain of legal values.

    Returns:
        list: A list of variables sorted by the number of remaining values in their domain, with the variable having the fewest values first.
    """
    variable_with_size = []

    for variable in variables:
        domain_size = len(domains[variable])
        variable_with_size.append((variable, domain_size))

    variable_with_size.sort(key=_domain_size_key)

    ordered_variables = []
    for pair in variable_with_size:
        ordered_variables.append(pair[0])

    return ordered_variables


def _domain_size_key(item):
    """Returns the domain size part of a `(variable, domain_size)` tuple."""
    return item[1]