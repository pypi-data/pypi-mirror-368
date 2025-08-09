from math import factorial

def nCr(n, r):
    if r > n:
        return 0
    return factorial(n) // (factorial(r) * factorial(n - r))

def nPr(n, r):
    if r > n:
        return 0
    return factorial(n) // factorial(n - r)

def basic_probability(favorable: int, total: int):
    if total == 0:
        raise ValueError("Total outcomes cannot be zero.")
    return favorable / total
