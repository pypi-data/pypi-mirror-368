from sympy import symbols, limit, diff, integrate, sin, cos, tan, ln, exp, oo, sympify, series, solve

x = symbols('x')

def find_limit(expr: str, point: float):
    expr_sym = sympify(expr)
    return limit(expr_sym, x, point)

def differentiate(expr: str):
    expr_sym = sympify(expr)
    return diff(expr_sym, x)

def second_derivative(expr: str):
    expr_sym = sympify(expr)
    return diff(expr_sym, x, 2)

def partial_derivative(expr: str, var: str):
    v = symbols(var)
    expr_sym = sympify(expr)
    return diff(expr_sym, v)

def integration(expr: str):
    expr_sym = sympify(expr)
    return integrate(expr_sym, x)

def definite_integral(expr: str, lower, upper):
    expr_sym = sympify(expr)
    return integrate(expr_sym, (x, lower, upper))

def taylor_series(expr: str, point=0, order=6):
    expr_sym = sympify(expr)
    return series(expr_sym, x, point, order).removeO()

def find_critical_points(expr: str):
    expr_sym = sympify(expr)
    first_derivative = diff(expr_sym, x)
    return solve(first_derivative, x)
