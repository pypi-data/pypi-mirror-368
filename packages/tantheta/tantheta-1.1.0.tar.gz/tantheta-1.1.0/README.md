# 🧮 tantheta

**tantheta** is a versatile Python library for symbolic computation and problem solving across mathematics, physics, and chemistry — supporting algebra, calculus, mechanics, thermodynamics, stoichiometry, kinetics, and more. Designed for students, educators, and researchers.

Built on top of [SymPy](https://www.sympy.org/), `tantheta` helps students, educators, and developers easily compute and format math expressions.

[![PyPI](https://img.shields.io/pypi/v/tantheta.svg?style=flat&color=blue)](https://pypi.org/project/tantheta/)
[![Downloads](https://static.pepy.tech/badge/tantheta)](https://pepy.tech/project/tantheta)
[![GitHub stars](https://img.shields.io/github/stars/ayushparwal/tantheta?style=flat&logo=github)](https://github.com/ayushparwal/tantheta/stargazers)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ayush-parwal-797a79255/)
[![X](https://img.shields.io/badge/X-%23000000.svg?style=flat&logo=X&logoColor=white)](https://x.com/ayushparwal2004)
[![Kaggle](https://img.shields.io/badge/Kaggle-%2312100E.svg?style=flat&logo=kaggle&logoColor=white)](https://kaggle.com/ayushparwal)


---

## ✨ Features

- 🔢 Algebraic simplification and equation solving.
- ∫ Symbolic calculus. (differentiation and integration)
- 📐 Trigonometric equation solving.
- 📊 Basic statistics. (mean, median, variance, etc.)
- ⚛️ Chemistry tools: chemical equation balancing, ideal gas law, stoichiometry, equilibrium, thermochemistry.
- ⚙️ Physics modules: kinematics, projectile motion, optics, unit conversions.
- 🧠 Expression formatting with LaTeX.

---

## 📦 Installation

```bash
pip install tantheta
```


## Examples 

```bash
import tantheta
from tantheta.calculus import second_derivative, partial_derivative, definite_integral
print(second_derivative("x**3 + 2*x"))
print(partial_derivative("x**2 + y**2", "y"))
print(definite_integral("x**2", 0, 2))
```
```bash
from tantheta.maths import ap_nth_term, gp_sum, triangle_area, is_prime, prime_factors
print(ap_nth_term(2, 3, 5))                            
print(gp_sum(3, 2, 4))                                
print(triangle_area(3, 4, 5))                          
print(is_prime(17))                                   
print(prime_factors(28))  
```

```bash                            
from tantheta.physics import solve_kinematics, projectile_motion, ohms_law
print(solve_kinematics(u=0, a=9.8, t=5))              
print(projectile_motion(20, 30))                         
print(ohms_law(i=2, r=5))      
```

```bash
from tantheta.chemistry import balance_equation, ideal_gas_law, molarity, pH
print(balance_equation("H2 + O2 = H2O"))                
print(ideal_gas_law(V=5, n=2, T=300))                   
print(molarity(2, 1))                                   
print(pH(1e-7))
```
