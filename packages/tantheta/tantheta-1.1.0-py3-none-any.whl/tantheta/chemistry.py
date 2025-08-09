import re
from sympy import Matrix, lcm, symbols
from sympy.solvers.solveset import linsolve
import math

# --------------------- Stoichiometry ---------------------

def molarity(moles, volume_liters):
    return round(moles / volume_liters, 4)

def molality(moles, mass_kg):
    return round(moles / mass_kg, 4)

def normality(equivalents, volume_liters):
    return round(equivalents / volume_liters, 4)

def dilution(C1, V1, V2=None, C2=None):
    # C1V1 = C2V2
    if C2 is None and V2 is not None:
        return round((C1 * V1) / V2, 4)
    elif V2 is None and C2 is not None:
        return round((C1 * V1) / C2, 4)
    else:
        raise ValueError("Provide either C2 or V2, not both.")

def percent_composition(mass_element, mass_compound):
    return round((mass_element / mass_compound) * 100, 2)

# --------------------- Acids & Bases ---------------------

def pH(H_concentration):
    if H_concentration <= 0:
        raise ValueError("Concentration must be positive.")
    return round(-math.log10(H_concentration), 4)

def pOH(OH_concentration):
    if OH_concentration <= 0:
        raise ValueError("Concentration must be positive.")
    return round(-math.log10(OH_concentration), 4)

def pH_from_pOH(pOH_val):
    return round(14 - pOH_val, 4)

def pOH_from_pH(pH_val):
    return round(14 - pH_val, 4)

# --------------------- Equilibrium ---------------------

def equilibrium_constant(concentrations_products, concentrations_reactants, stoich_products, stoich_reactants):
    # concentrations and stoich are lists aligned in order
    K = 1
    for c, n in zip(concentrations_products, stoich_products):
        K *= c ** n
    for c, n in zip(concentrations_reactants, stoich_reactants):
        K /= c ** n
    return round(K, 6)

# --------------------- Reaction Kinetics ---------------------

def rate_constant(first_order_half_life):
    # k = ln2 / t_half for first order
    return round(0.693 / first_order_half_life, 6)

def reaction_rate(rate_constant, concentration, order=1):
    return round(rate_constant * (concentration ** order), 6)

# --------------------- Thermochemistry ---------------------

def enthalpy_change(bond_energies_broken, bond_energies_formed):
    # ΔH = sum(bonds broken) - sum(bonds formed)
    return round(sum(bond_energies_broken) - sum(bond_energies_formed), 2)

def heat(q, m, c, delta_t):
    # q = m * c * ΔT
    return round(m * c * delta_t, 4)

# --------------------- Gas Laws ---------------------

def combined_gas_law(P1, V1, T1, P2=None, V2=None, T2=None):
    # P1V1/T1 = P2V2/T2, solve for whichever missing
    if P2 is None:
        return (P1 * V1 * T2) / (V2 * T1)
    elif V2 is None:
        return (P1 * V1 * T2) / (P2 * T1)
    elif T2 is None:
        return (P2 * V2 * T1) / (P1 * V1)
    else:
        raise ValueError("One of P2, V2, or T2 must be None.")

# --------------------- Avogadro & Constants ---------------------

def moles_to_particles(moles):
    N_Avogadro = 6.022e23
    return round(moles * N_Avogadro)

def particles_to_moles(particles):
    N_Avogadro = 6.022e23
    return round(particles / N_Avogadro, 6)

def parse_formula(formula):
    elements = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    atom_counts = {}
    for elem, count in elements:
        atom_counts[elem] = atom_counts.get(elem, 0) + int(count or 1)
    return atom_counts

def parse_side(side):
    return [parse_formula(comp.strip()) for comp in side.split('+')]

def extract_elements(compounds):
    elements = set()
    for comp in compounds:
        elements.update(comp.keys())
    return sorted(elements)

def construct_matrix(lhs, rhs, elements):
    matrix = []
    for elem in elements:
        row = []
        for compound in lhs:
            row.append(compound.get(elem, 0))
        for compound in rhs:
            row.append(-compound.get(elem, 0))
        matrix.append(row)
    return Matrix(matrix)

def balance_equation(equation):
    lhs_str, rhs_str = equation.split('=')
    lhs = parse_side(lhs_str)
    rhs = parse_side(rhs_str)
    elements = extract_elements(lhs + rhs)

    mat = construct_matrix(lhs, rhs, elements)
    nullspace = mat.nullspace()

    if not nullspace:
        return "No solution found."

    coeffs = nullspace[0]
    lcm_val = lcm([term.q for term in coeffs])
    final_coeffs = [int(term * lcm_val) for term in coeffs]

    lhs_comps = lhs_str.split('+')
    rhs_comps = rhs_str.split('+')

    lhs_bal = ' + '.join(f"{final_coeffs[i]}{lhs_comps[i].strip()}" for i in range(len(lhs_comps)))
    rhs_bal = ' + '.join(f"{final_coeffs[i+len(lhs_comps)]}{rhs_comps[i].strip()}" for i in range(len(rhs_comps)))

    return f"{lhs_bal} = {rhs_bal}"



def ideal_gas_law(P=None, V=None, n=None, T=None, R=0.0821):
    """
    Solves for one missing variable in the ideal gas law equation: PV = nRT

    Parameters:
    - P: Pressure in atm
    - V: Volume in liters
    - n: Number of moles
    - T: Temperature in Kelvin
    - R: Ideal gas constant (default: 0.0821 L·atm/mol·K)

    Returns:
    - Calculated value of the missing parameter
    """
    if [P, V, n, T].count(None) != 1:
        raise ValueError("Exactly one of P, V, n, T must be None.")

    if P is None:
        return (n * R * T) / V
    elif V is None:
        return (n * R * T) / P
    elif n is None:
        return (P * V) / (R * T)
    elif T is None:
        return (P * V) / (n * R)


# --------------------- Gas Mixtures ---------------------

def partial_pressure(total_pressure, mole_fraction):
    return round(total_pressure * mole_fraction, 4)

def daltons_law(partial_pressures):
    # Sum of partial pressures
    return round(sum(partial_pressures), 4)

# --------------------- Electrochemistry ---------------------

def standard_cell_potential(E_cathode, E_anode):
    return round(E_cathode - E_anode, 4)

def nernst_equation(E0, n, Q, T=298):
    R = 8.314
    F = 96485
    return round(E0 - (R * T) / (n * F) * math.log(Q), 4)

# --------------------- Advanced Stoichiometry ---------------------

def empirical_formula(mass_elements, atomic_masses):
    moles = [mass / atomic for mass, atomic in zip(mass_elements, atomic_masses)]
    min_moles = min(moles)
    ratios = [round(m / min_moles) for m in moles]
    return ratios

def molecular_formula(empirical_formula_ratios, molar_mass, empirical_mass):
    multiplier = round(molar_mass / empirical_mass)
    return [r * multiplier for r in empirical_formula_ratios]

# --------------------- More Thermodynamics ---------------------

def gibbs_free_energy(delta_H, delta_S, temperature):
    # ΔG = ΔH - TΔS
    return round(delta_H - temperature * delta_S, 4)

def equilibrium_from_gibbs(delta_G):
    R = 8.314
    T = 298  # default temperature in K
    K = math.exp(-delta_G / (R * T))
    return round(K, 6)

# --------------------- Spectroscopy ---------------------

def beer_lambert_law(absorbance=None, molar_absorptivity=None, concentration=None, path_length=None):
    # A = ε * c * l
    if absorbance is None and molar_absorptivity and concentration and path_length:
        return round(molar_absorptivity * concentration * path_length, 6)
    elif concentration is None and absorbance and molar_absorptivity and path_length:
        return round(absorbance / (molar_absorptivity * path_length), 6)
    elif path_length is None and absorbance and molar_absorptivity and concentration:
        return round(absorbance / (molar_absorptivity * concentration), 6)
    else:
        return "Provide exactly three parameters"

# --------------------- Solution Properties ---------------------

def mole_fraction(moles_component, moles_total):
    return round(moles_component / moles_total, 6)

def mass_percent(mass_component, mass_total):
    return round((mass_component / mass_total) * 100, 4)

def henderson_hasselbalch(pKa, acid_conc, base_conc):
    import math
    ratio = base_conc / acid_conc
    return round(pKa + math.log10(ratio), 4)

def average_atomic_mass(isotopes, abundances):
    # isotopes and abundances as lists of equal length, abundances in decimals (sum=1)
    return round(sum(i * a for i, a in zip(isotopes, abundances)), 6)

def heat_phase_change(mass, latent_heat):
    return round(mass * latent_heat, 4)

def arrhenius_rate_constant(A, Ea, T):
    # k = A * exp(-Ea / RT)
    import math
    R = 8.314  # J/mol·K
    return round(A * math.exp(-Ea / (R * T)), 6)

def grams_to_moles(mass, molar_mass):
    return round(mass / molar_mass, 6)

def moles_to_grams(moles, molar_mass):
    return round(moles * molar_mass, 6)

def partial_molar_volume(total_volume, volumes, mole_fractions):
    # volumes, mole_fractions are lists; weighted average approx
    return round(sum(v * x for v, x in zip(volumes, mole_fractions)), 6)

def ka_from_pka(pKa):
    return round(10 ** (-pKa), 6)
