from fractions import Fraction


def NewtonRaphson(
    left_expression,
    right_expression,
    initial_guess,
    tolerance,
    max_iterations=100,
    step=1e-6,
    min_derivative=1e-12,
):
    # Define f(x) = left_expression - right_expression
    def f(x):
        return left_expression(x) - right_expression(x)

    # Compute derivative of f(x) numerically or analytically
    def f_prime(x):
        return (f(x + step) - f(x - step)) / (
            2 * step
        )  # Central difference approximation

    x = initial_guess
    iteration = 0

    while iteration < max_iterations:
        # Compute function value and derivative
        fx = f(x)
        fpx = f_prime(x)

        # Check for division by zero (derivative too small)
        if abs(fpx) < min_derivative:
            return "Error: Derivative too small, method may fail"

        # Update x using Newton-Raphson formula
        x_new = x - fx / fpx

        # Check for convergence
        if abs(x_new - x) < tolerance:
            return x_new  # Solution found

        x = x_new
        iteration = iteration + 1

    # If max iterations reached, indicate failure
    return "Error: No convergence within max iterations"


# Example usage:
left_expression = lambda x: 2**x
right_expression = lambda x: x**2
initial_guess = 0.0
tolerance = 1e-8
max_iterations = 100

result = NewtonRaphson(
    left_expression, right_expression, initial_guess, tolerance, max_iterations
)
print("Solution: x =", result)
