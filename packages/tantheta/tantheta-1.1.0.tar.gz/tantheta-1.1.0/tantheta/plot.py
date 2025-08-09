import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, sympify, lambdify

def plot_expression(expr: str, var: str = "x", range: tuple = (-10, 10), num_points=1000):
    try:
        x = symbols(var)
        expression = sympify(expr)
        func = lambdify(x, expression, modules=["numpy"])

        x_vals = np.linspace(range[0], range[1], num_points)
        y_vals = func(x_vals)

        plt.figure(figsize=(8, 4))
        plt.plot(x_vals, y_vals, label=f"${expr}$")
        plt.xlabel(var)
        plt.ylabel("f({})".format(var))
        plt.title(f"Plot of {expr}")
        plt.grid(True)
        plt.legend()
        plt.show()

    except Exception as e:
        print(f"Plotting failed: {e}")