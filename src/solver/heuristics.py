# Provides optional optimization strategies such as MRV for improved performance.

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
    return sorted(variables, key=lambda var: len(domains[var]))