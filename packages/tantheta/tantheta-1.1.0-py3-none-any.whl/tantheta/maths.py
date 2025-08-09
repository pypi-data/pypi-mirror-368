# tantheta/maths.py
def ap_nth_term(a, d, n):
    return a + (n - 1) * d

def gp_sum(a, r, n):
    return a * ((r ** n - 1) / (r - 1)) if r != 1 else a * n

def triangle_area(a, b, c):
    s = (a + b + c) / 2
    return (s * (s - a) * (s - b) * (s - c)) ** 0.5

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

def prime_factors(n):
    i, factors = 2, []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors
