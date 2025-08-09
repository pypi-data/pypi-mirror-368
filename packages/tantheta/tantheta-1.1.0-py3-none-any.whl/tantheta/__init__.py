# Core operations
from .core import add, subtract, multiply, divide

# Algebra
from .algebra import (
    dot_product,
    cross_product,
    classify_conic,
    factor_expression,
    expand_expression,
    solve_linear_equation,
    solve_linear_system,
    is_polynomial,
    degree_of_polynomial,
    symbolic_gcd,
    symbolic_lcm,
)

# Calculus
from .calculus import (
    differentiate,
    integration,
    find_limit,
    definite_integral,
    partial_derivative,
    second_derivative,
    taylor_series,
    find_critical_points,
)

# Probability
from .probability import nPr, nCr, basic_probability

# Statistics
from .stats import (
    mean,
    median,
    variance,
    standard_deviation,
    mode,
    range_ as data_range,
    quartiles,
    interquartile_range,
    covariance,
    correlation_coefficient,
    z_scores,
    skewness,
    kurtosis,
    coefficient_of_variation,
    sample_variance,
    sample_standard_deviation,
    percentile,
)


# Trigonometry
from .trigonometry import (
    solve_trig_equation,
    simplify_trig_expression,
    expand_trig_expression,
    factor_trig_expression,
    evaluate_trig_identity,
    verify_trig_identity,
    is_trig_identity,
)

# Linear Algebra
from .linear_algebra import (
    compute_determinant,
    compute_inverse,
    compute_rank,
    compute_eigenvalues,
    compute_eigenvectors,
    compute_transpose,
    compute_trace,
    matrix_multiplication,
    is_symmetric,
    solve_linear_system,
)

# Geometry
from .geometry import angle_between_lines, angle_between_vectors

# Plotting
from .plot import plot_expression

# Physics
from .physics import (
    solve_kinematics,
    projectile_motion,
    work_energy_theorem,
    centripetal_force,
    lens_formula,
    mirror_formula,
    magnification,
    convert_units,
    ohms_law,
    coulombs_law,
    wave_speed,
    shm_motion,
    phy_ideal_gas_law ,  
    photon_energy,
    de_broglie_wavelength,
    impulse,
    torque,
    gravitational_force,
    capacitance,
    inductive_reactance,
    magnetic_force,
    doppler_effect,
    heat_transfer,
    carnot_efficiency,
    relativistic_mass,
    time_dilation,
    escape_velocity,
    orbital_period,
    schwarzschild_radius,
    buoyant_force,
    bernoulli_pressure,
    viscosity_force,
    magnetic_flux,
    induced_emf,
    inductance,
    work_done_pressure_volume,
    efficiency,
    entropy_change,
    de_broglie_frequency,
    uncertainty_position,
    half_life,
)

# Chemistry
from .chemistry import (
    balance_equation,
    ideal_gas_law,
    molarity,
    molality,
    normality,
    dilution,
    percent_composition,
    pH,
    pOH,
    pH_from_pOH,
    pOH_from_pH,
    equilibrium_constant,
    rate_constant,
    reaction_rate,
    enthalpy_change,
    heat,
    combined_gas_law,
    moles_to_particles,
    particles_to_moles,
    partial_pressure,
    daltons_law,
    standard_cell_potential,
    nernst_equation,
    empirical_formula,
    molecular_formula,
    gibbs_free_energy,
    equilibrium_from_gibbs,
    beer_lambert_law,
    mole_fraction,
    mass_percent,
    henderson_hasselbalch,
    average_atomic_mass,
    heat_phase_change,
    arrhenius_rate_constant,
    grams_to_moles,
    moles_to_grams,
    partial_molar_volume,
    ka_from_pka,
)
