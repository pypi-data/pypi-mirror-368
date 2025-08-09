from sympy import Matrix, symbols

def compute_determinant(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.det()

def compute_inverse(matrix_list):
    matrix = Matrix(matrix_list)
    if matrix.det() == 0:
        return "Matrix is singular; no inverse exists."
    return matrix.inv()

def compute_rank(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.rank()

def compute_eigenvalues(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.eigenvals()

def compute_eigenvectors(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.eigenvects()

def compute_transpose(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.T

def compute_trace(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix.trace()

def matrix_multiplication(matrix_list1, matrix_list2):
    m1 = Matrix(matrix_list1)
    m2 = Matrix(matrix_list2)
    if m1.shape[1] != m2.shape[0]:
        return "Matrix multiplication not possible due to dimension mismatch."
    return m1 * m2

def is_symmetric(matrix_list):
    matrix = Matrix(matrix_list)
    return matrix == matrix.T

def solve_linear_system(coeff_matrix_list, constants_list):
    matrix = Matrix(coeff_matrix_list)
    constants = Matrix(constants_list)
    if matrix.det() == 0:
        return "No unique solution exists."
    solution = matrix.LUsolve(constants)
    return solution
