from sympy import Matrix, acos, atan, Abs, deg

def angle_between_vectors(vec1, vec2, in_degrees=True):
    v1 = Matrix(vec1)
    v2 = Matrix(vec2)
    dot_product = v1.dot(v2)
    magnitude_product = v1.norm() * v2.norm()
    angle_rad = acos(dot_product / magnitude_product)
    return deg(angle_rad) if in_degrees else angle_rad

def angle_between_lines(m1, m2, in_degrees=True):
    denominator = 1 + m1 * m2
    if denominator == 0:
        # Perpendicular lines → angle = 90°
        return 90 if in_degrees else deg(1.57079632679)  # approx π/2
    try:
        angle_rad = atan(Abs((m1 - m2) / denominator))
        return deg(angle_rad) if in_degrees else angle_rad
    except Exception as e:
        return f"Error: {e}"