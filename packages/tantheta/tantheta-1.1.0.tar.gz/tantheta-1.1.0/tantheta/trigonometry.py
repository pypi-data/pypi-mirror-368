from sympy import Eq, solve, sin, cos, tan, cot, sec, csc, symbols, simplify, expand_trig, factor, trigsimp, sympify
from sympy.abc import x

def solve_trig_equation(equation_str, var_str='x'):
    x = symbols(var_str)
    expr = eval(equation_str.replace("^", "**").replace(var_str, "x"))
    eq = Eq(expr, 0)
    return solve(eq, x)

def simplify_trig_expression(expr_str):
    expr = sympify(expr_str.replace("^", "**"))
    return trigsimp(expr)

def expand_trig_expression(expr_str):
    expr = sympify(expr_str.replace("^", "**"))
    return expand_trig(expr)

def factor_trig_expression(expr_str):
    expr = sympify(expr_str.replace("^", "**"))
    return factor(expr)

def evaluate_trig_identity(expr_str):
    expr = sympify(expr_str.replace("^", "**"))
    simplified = trigsimp(expr)
    return simplified == 0

def verify_trig_identity(lhs_str, rhs_str):
    lhs = trigsimp(sympify(lhs_str.replace("^", "**")))
    rhs = trigsimp(sympify(rhs_str.replace("^", "**")))
    return lhs == rhs

def is_trig_identity(expr_str):
    expr = sympify(expr_str.replace("^", "**"))
    return trigsimp(expr) == 0
