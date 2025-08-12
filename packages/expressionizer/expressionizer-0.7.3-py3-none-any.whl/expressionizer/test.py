from .expression import *
from .evaluator import EvaluatorContext, evaluate, evaluate_expression, replace_sub
from .render import render, render_latex
from math import pi, sin, log, log10
import traceback

if __name__ == "__main__":
    # 1. Pure numeric sum
    expr1 = Sum([2, 3, 5])
    # Expected: 10

    # 2. Variable substitution (simple)
    expr2 = sum([Symbol("x"), 3])
    # With context {"x": 7}
    # Expected: 10

    # 3. Variable not found (should stay symbolic)
    expr3 = product([2, Symbol("y")])
    # With context {"x": 1}
    # Expected: Product([2, Symbol("y")])

    # 4. Nested arithmetic with variables
    expr4 = sum([product([2, Symbol("x")]), product([3, Symbol("y")]), 5])
    # With context {"x": 4, "y": 6}
    # Expected: 2*4 + 3*6 + 5 = 8 + 18 + 5 = 31

    # 5. Power and negative exponent
    expr5 = power(Symbol("a"), -2)
    # With context {"a": 2}
    # Expected: 2^-2 = 0.25

    # 6. Fractional exponent (square root)
    expr6 = power(Symbol("z"), fraction(1, 2))
    # With context {"z": 25}
    # Expected: 5.0

    # 7. Function call: sin(pi/2)

    sin_function = MathFunction("sin", 1)
    expr7 = FunctionCall(sin_function, [pi / 2])
    # With context {}
    # Expected: 1.0

    # 8. Logarithm with base (log_10(100))
    log_function = MathFunction("log", 1, 1)
    expr8 = FunctionCall(log_function, [100], [10])
    # With context {}
    # Expected: 2.0

    # 9. Partial evaluation (some variables known, some not)
    expr9 = sum([Symbol("x"), Symbol("y")])
    # With context {"x": 2}
    # Expected: Sum([2, Symbol("y")])

    # 10. Nested function: sin(x^2)
    expr10 = FunctionCall(sin_function, [power(Symbol("x"), 2)])
    # With context {"x": pi}
    # Expected: sin(pi^2) (float)

    # 11. Combination: (x + y)^2 at x=3, y=4
    expr11 = power(sum([Symbol("x"), Symbol("y")]), 2)
    # With context {"x": 3, "y": 4}
    # Expected: (3+4)^2 = 49

    # 12. Product of sums: (x + 2)(y + 3) at x=1, y=2
    expr12 = product([sum([Symbol("x"), 2]), sum([Symbol("y"), 3])])
    # With context {"x": 1, "y": 2}
    # Expected: (1+2)*(2+3) = 3*5 = 15

    # 13. Power of sum with unknown
    expr13 = power(sum([Symbol("a"), 1]), 3)
    # With context {"a": 2}
    # Expected: (2+1)^3 = 27

    # 14. Division and fraction context
    expr14 = product([Symbol("n"), power(Symbol("d"), -1)])
    # With context {"n": 6, "d": 2}
    # Expected: 6/2 = 3.0

    # 15. Zero in multiplication
    expr15 = Product([0, Symbol("x")])
    # With any context
    # Expected: 0

    expr16 = Product([91, 998])

    expr17 = Sum([921, 998])
    expr18 = Sum([13500, 146000])

    expr19 = Sum([0, Product([2, 13])])
    # expr19 = Product([2, 3, 4, Sum([10, 11])])
    # expr19 = Product([2, Sum([5, 9])])

    expr20 = Sum([1, 2, 3, 4, 5, Product([3, 5]), Power(3, 2)])

    expr21 = Product([Sum([2]), -1, 10])
    expr22 = Sum(
        [
            Product([Sum([1, 4, Symbol("x")]), -1]),
            Power(2, 2),
            Product([3, Symbol("x")]),
        ]
    )
    expr23 = Sum([-201, 203])
    expr24 = Power(Product([7, 14.707]), 3)
    expr25 = Product([1, 2, -10.248])
    expr26 = Product([1, Product([2, 2])])
    log10_function = MathFunction("log10", functional_parameters=1)
    expr27 = FunctionCall(log10_function, [0])
    expr28 = Power(Product([-2, 0.6]), Power(19, -25))

    # Print results
    test_cases = [  #
        # (expr1, {}, 10),
        # (expr2, {"x": 7}, 10),
        # (expr3, {"x": 1}, product([2, Symbol("y")])),
        # (expr4, {"x": 4, "y": 6}, 31),
        # (expr5, {"a": 2}, 0.25),
        # (expr6, {"z": 25}, 5.0),
        # (expr7, {"sin": lambda x, y, z: sin(x[0])}, 1.0),
        # (expr8, {"log": lambda x, y, z: log(x[0], y[0])}, 2.0),
        # (expr9, {"x": 2}, sum([2, Symbol("y")])),
        # (
        #     expr10,
        #     {"x": pi, "sin": lambda x, y, z: sin(x[0])},
        #     __import__("math").sin(pi**2),
        # ),
        # (expr11, {"x": 3, "y": 4}, 49),
        # (expr12, {"x": 1, "y": 2}, 15),
        # (expr13, {"a": 2}, 27),
        # (expr14, {"n": 6, "d": 2}, 3.0),
        # (expr15, {"x": 100}, 0),
        # (expr16, {}, 90818),
        # (expr17, {}, 1919),
        # (expr18, {}, 159500),
        # (expr19, {}, 112),
        # (expr20, {}, 39),
        # (expr21, {}, 44.79),
        # (expr22, {}, 20),
        # (expr23, {}, -26),
        (expr24, {}, 26),
        # (expr25, {}, 26),
        # (expr26, {}, 14.7),
        # (expr27, {"log10": lambda args, _, __: log10(args[0])}, 2),
        # (expr28, {}, 2),
    ]

    for i, (expr, substitutions, expected) in enumerate(test_cases, 1):
        # print(f"\033[1mProblem {i}\033[0m: ${render_latex(expr)}$")
        # if context:
        #     print(
        #         f"\033[1mGiven:\033[0m ${', '.join(map(lambda x: f'{x[0]} = {render_latex(x[1])}', context.items()))}$"
        #     )
        result, context = evaluate(expr, substitutions)

        print(f"Problem: $", render_latex(expr), "$.")
        print(context.render())
        print(f"Final answer: $\\boxed{{{render_latex(result)}}}$")
        # print(f"Test {i}: {render_latex(result)!r} (Expected: {expected!r})")
        print("\n")
