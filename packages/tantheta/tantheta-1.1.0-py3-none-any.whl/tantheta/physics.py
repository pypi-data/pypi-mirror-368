# tantheta/physics.py
from math import radians, degrees, sin, cos, sqrt, tan, pi

# Constants
g = 9.8                 # m/s²
epsilon_0 = 8.854e-12   # F/m
k_e = 8.9875517923e9    # N·m²/C²
c = 3e8                 # m/s (speed of light)
h = 6.62607015e-34      # J·s (Planck's constant)
R_universal = 8.314     # J/(mol·K) (Universal gas constant)

# ------------------------ Mechanics ------------------------

def solve_kinematics(u=None, v=None, a=None, t=None, s=None):
    known = sum(x is not None for x in [u, v, a, t, s])
    if known < 3:
        return "Not enough info"

    if u is None and v is not None and a is not None and t is not None:
        u = v - a * t
    if v is None and u is not None and a is not None and t is not None:
        v = u + a * t
    if a is None and u is not None and v is not None and t is not None:
        a = (v - u) / t
    if t is None and u is not None and v is not None and a is not None:
        t = (v - u) / a
    if s is None and u is not None and a is not None and t is not None:
        s = u * t + 0.5 * a * t**2
    if s is None and u is not None and v is not None and a is not None:
        s = (v**2 - u**2) / (2 * a)
    if a is None and u is not None and s is not None and t is not None:
        a = (2 * (s - u * t)) / (t**2)
    
    return {
        "initial_velocity": u,
        "final_velocity": v,
        "acceleration": a,
        "time": t,
        "displacement": s
    }

def projectile_motion(u, angle):
    angle_rad = radians(angle)
    u_x = u * cos(angle_rad)
    u_y = u * sin(angle_rad)
    t_flight = (2 * u_y) / g
    h_max = (u_y**2) / (2 * g)
    r_proj = (u**2) * sin(2 * angle_rad) / g
    trajectory_eq = f"y = x*tan({angle}) - ({g}/(2*{u_x}^2))*x^2"
    return {
        "u_x": round(u_x, 2),
        "u_y": round(u_y, 2),
        "time_of_flight": round(t_flight, 2),
        "max_height": round(h_max, 2),
        "range": round(r_proj, 2),
        "trajectory_equation": trajectory_eq
    }

def work_energy_theorem(m, u, v):
    ke_initial = 0.5 * m * u**2
    ke_final = 0.5 * m * v**2
    return round(ke_final - ke_initial, 2)

def centripetal_force(m, v, r):
    return round(m * v**2 / r, 2)

# ------------------------ Optics ------------------------

def lens_formula(u, v):
    return round((u * v) / (v - u), 2)

def mirror_formula(u, v):
    return round((u * v) / (u + v), 2)

def magnification(height_image, height_object):
    return round(height_image / height_object, 3)

# ------------------------ Unit Conversions ------------------------

def convert_units(expression):
    parts = expression.lower().split()
    val = float(parts[0])
    if "km/hr to m/s" in expression:
        return round(val * 1000 / 3600, 3)
    elif "m/s to km/hr" in expression:
        return round(val * 3.6, 3)
    elif "deg to rad" in expression:
        return round(radians(val), 5)
    elif "rad to deg" in expression:
        return round(degrees(val), 5)
    else:
        return "Conversion not supported"

# ------------------------ Electricity ------------------------

def ohms_law(v=None, i=None, r=None):
    if v is None and i is not None and r is not None:
        v = i * r
    elif i is None and v is not None and r is not None:
        i = v / r
    elif r is None and v is not None and i is not None:
        r = v / i
    else:
        return "Provide any two values"
    return {"voltage(V)": v, "current(A)": i, "resistance(Ω)": r}

def coulombs_law(q1, q2, r):
    force = k_e * abs(q1 * q2) / (r**2)
    return round(force, 4)

# ------------------------ Waves & Sound ------------------------

def wave_speed(frequency=None, wavelength=None, speed=None):
    if speed is None and frequency is not None and wavelength is not None:
        speed = frequency * wavelength
    elif frequency is None and speed is not None and wavelength is not None:
        frequency = speed / wavelength
    elif wavelength is None and speed is not None and frequency is not None:
        wavelength = speed / frequency
    else:
        return "Provide any two values"
    return {"frequency(Hz)": frequency, "wavelength(m)": wavelength, "speed(m/s)": speed}

def shm_motion(amplitude, angular_freq, time, phase=0):
    displacement = amplitude * sin(angular_freq * time + phase)
    velocity = amplitude * angular_freq * cos(angular_freq * time + phase)
    acceleration = -amplitude * (angular_freq**2) * sin(angular_freq * time + phase)
    return {
        "displacement": round(displacement, 4),
        "velocity": round(velocity, 4),
        "acceleration": round(acceleration, 4)
    }

# ------------------------ Thermodynamics ------------------------

def phy_ideal_gas_law(P=None, V=None, n=None, T=None):
    if P is None and V is not None and n is not None and T is not None:
        P = (n * R_universal * T) / V
    elif V is None and P is not None and n is not None and T is not None:
        V = (n * R_universal * T) / P
    elif n is None and P is not None and V is not None and T is not None:
        n = (P * V) / (R_universal * T)
    elif T is None and P is not None and V is not None and n is not None:
        T = (P * V) / (n * R_universal)
    else:
        return "Provide any three values"
    return {"pressure(Pa)": P, "volume(m³)": V, "moles": n, "temperature(K)": T}

# ------------------------ Modern Physics ------------------------

def photon_energy(frequency=None, wavelength=None):
    if frequency is not None:
        return round(h * frequency, 10)
    elif wavelength is not None:
        return round((h * c) / wavelength, 10)
    else:
        return "Provide frequency or wavelength"

def de_broglie_wavelength(mass, velocity):
    return round(h / (mass * velocity), 10)


# ------------------------ Mechanics ------------------------

def impulse(force, time):
    return round(force * time, 4)

def torque(force, distance, angle=90):
    return round(force * distance * sin(radians(angle)), 4)

def gravitational_force(m1, m2, r):
    G = 6.67430e-11
    return round(G * m1 * m2 / (r**2), 10)

# ------------------------ Electricity & Magnetism ------------------------

def capacitance(charge=None, voltage=None):
    if charge is not None and voltage is not None:
        return round(charge / voltage, 12)
    return "Provide charge and voltage"

def inductive_reactance(frequency, inductance):
    return round(2 * pi * frequency * inductance, 4)

def magnetic_force(q, v, B, angle=90):
    return round(q * v * B * sin(radians(angle)), 6)

# ------------------------ Waves & Sound ------------------------

def doppler_effect(frequency, velocity_source=0, velocity_observer=0, wave_speed=343):
    f_observed = ((wave_speed + velocity_observer) / (wave_speed - velocity_source)) * frequency
    return round(f_observed, 4)

# ------------------------ Thermodynamics ------------------------

def heat_transfer(mass, specific_heat, delta_temp):
    return round(mass * specific_heat * delta_temp, 4)

def carnot_efficiency(T_hot, T_cold):
    if T_hot <= 0 or T_cold < 0:
        return "Temperatures must be in Kelvin and > 0"
    return round(1 - (T_cold / T_hot), 4)

# ------------------------ Modern Physics ------------------------

def relativistic_mass(rest_mass, velocity):
    return round(rest_mass / sqrt(1 - (velocity**2 / c**2)), 10)

def time_dilation(proper_time, velocity):
    return round(proper_time / sqrt(1 - (velocity**2 / c**2)), 10)


# ------------------------ Astronomy & Astrophysics ------------------------

def escape_velocity(mass, radius):
    G = 6.67430e-11
    v = sqrt(2 * G * mass / radius)
    return round(v, 4)

def orbital_period(mass_central, radius):
    G = 6.67430e-11
    T = 2 * pi * sqrt(radius**3 / (G * mass_central))
    return round(T, 4)

def schwarzschild_radius(mass):
    G = 6.67430e-11
    return round(2 * G * mass / c**2, 10)

# ------------------------ Fluid Mechanics ------------------------

def buoyant_force(density_fluid, volume_submerged):
    return round(density_fluid * g * volume_submerged, 4)

def bernoulli_pressure(p1, v1, h1, v2, h2, density):
    p2 = p1 + 0.5 * density * (v1**2 - v2**2) + density * g * (h1 - h2)
    return round(p2, 4)

def viscosity_force(viscosity, area, velocity_gradient):
    return round(viscosity * area * velocity_gradient, 6)

# ------------------------ Electromagnetism ------------------------

def magnetic_flux(B, area, angle=0):
    return round(B * area * cos(radians(angle)), 6)

def induced_emf(B, length, velocity, angle=90):
    return round(B * length * velocity * sin(radians(angle)), 6)

def inductance(n_turns, magnetic_flux, current):
    return round(n_turns * magnetic_flux / current, 10)

# ------------------------ Thermodynamics ------------------------

def work_done_pressure_volume(P_initial, V_initial, P_final, V_final):
    # For isobaric or isothermal processes, simplified average pressure method:
    P_avg = (P_initial + P_final) / 2
    W = P_avg * (V_final - V_initial)
    return round(W, 4)

def efficiency(work_done, heat_supplied):
    return round(work_done / heat_supplied, 4)

def entropy_change(heat_transferred, temperature):
    return round(heat_transferred / temperature, 6)

# ------------------------ Quantum Physics ------------------------

def de_broglie_frequency(energy):
    return round(energy / h, 10)

def uncertainty_position(momentum_uncertainty):
    return round(h / (4 * pi * momentum_uncertainty), 10)

def half_life(decay_constant):
    return round(0.693 / decay_constant, 10)
