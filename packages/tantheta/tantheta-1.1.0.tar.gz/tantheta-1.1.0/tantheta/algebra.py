from sympy import symbols, Matrix, Eq, sympify, solve, expand, factor, Poly
from sympy.abc import x, y
from sympy import sympify, gcd, lcm, expand

def symbolic_gcd(expr1, expr2):
    expr1 = expand(sympify(expr1))
    expr2 = expand(sympify(expr2))
    return gcd(expr1, expr2)

def symbolic_lcm(expr1, expr2):
    expr1 = expand(sympify(expr1))
    expr2 = expand(sympify(expr2))
    return lcm(expr1, expr2)

def dot_product(v1: list, v2: list):
    return sum(a * b for a, b in zip(v1, v2))

def cross_product(v1: list, v2: list):
    return Matrix(v1).cross(Matrix(v2))

def classify_conic(expr: str) -> str:
    expr = expr.replace('^', '**')
    try:
        poly = sympify(expr).as_poly(x, y)
        A = poly.coeff_monomial(x**2)
        B = poly.coeff_monomial(x * y)
        C = poly.coeff_monomial(y**2)
        Δ = B**2 - 4 * A * C

        if Δ == 0:
            return "Parabola"
        elif Δ > 0:
            return "Hyperbola"
        elif Δ < 0:
            if A == C and B == 0:
                return "Circle"
            return "Ellipse"
    except Exception:
        return "Not a valid conic expression"

def solve_linear_equation(expr: str):
    return solve(sympify(expr), x)

def solve_linear_system(equations: list, variables: list):
    vars = symbols(variables)
    eqs = [Eq(sympify(eq.split('=')[0]), sympify(eq.split('=')[1])) for eq in equations]
    return solve(eqs, vars)

def factor_expression(expr: str):
    return factor(sympify(expr))

def expand_expression(expr: str):
    return expand(sympify(expr))

def is_polynomial(expr: str):
    try:
        return Poly(sympify(expr), x).is_polynomial
    except:
        return False

def degree_of_polynomial(expr: str):
    try:
        return Poly(sympify(expr), x).degree()
    except:
        return "Not a polynomial"
