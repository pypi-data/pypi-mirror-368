from typing import Callable
from .evaluator import evaluate
from .render import render_latex, render_type
from .expression import (
    Product,
    Power,
    Sum,
    Symbol,
    Numerical,
    FunctionCall,
    MathFunction,
    is_int_or_float,
)

import numpy as np
import math
import random
import math
import statistics

# Latin letters and their relative preferences
latin_chars = {
    "x": 1.0,
    "y": 0.9,
    "z": 0.8,
    "a": 0.8,
    "b": 0.8,
    "c": 0.7,
    "d": 0.6,
    "n": 0.5,
    "m": 0.5,
    "t": 0.5,
    "u": 0.4,
    "v": 0.4,
    "w": 0.4,
    "r": 0.4,
    "s": 0.4,
    "k": 0.3,
    "p": 0.3,
    "f": 0.2,
    "g": 0.2,
    "q": 0.1,
    "j": 0.1,
    "l": 0.1,
    "h": 0.1,
    "o": 0.01,
    "i": 0.001,
    "e": 0.001,  # discouraged due to special meaning
}

# Greek letters (lowercase)
greek_chars = {
    "α": 1.0,
    "β": 0.9,
    "γ": 0.7,
    "δ": 0.6,
    "ε": 0.5,
    "ζ": 0.4,
    "η": 0.4,
    "θ": 0.5,
    "ι": 0.3,
    "κ": 0.6,
    "λ": 0.7,
    "μ": 0.5,
    "ν": 0.3,
    "ξ": 0.2,
    "ο": 0.01,
    "π": 0.01,
    "ρ": 0.4,
    "σ": 0.5,
    "τ": 0.4,
    "υ": 0.3,
    "φ": 0.3,
    "χ": 0.2,
    "ψ": 0.1,
    "ω": 0.2,
}

# Hebrew characters
hebrew_chars = {
    "א": 1.0,
    "ב": 0.8,
    "ג": 0.6,
    "ד": 0.5,
    "ה": 0.4,
    "ו": 0.3,
    "ז": 0.3,
    "ח": 0.2,
    "ט": 0.1,
    "י": 0.1,
    "כ": 0.1,
    "ל": 0.1,
    "מ": 0.1,
    "נ": 0.1,
    "ס": 0.1,
    "ע": 0.05,
    "פ": 0.05,
    "צ": 0.05,
    "ק": 0.05,
    "ר": 0.05,
    "ש": 0.05,
    "ת": 0.05,
}

# Cyrillic characters
cyrillic_chars = {
    "а": 1.0,
    "б": 0.8,
    "в": 0.7,
    "г": 0.6,
    "д": 0.6,
    "е": 0.01,
    "ж": 0.4,
    "з": 0.3,
    "и": 0.3,
    "й": 0.3,
    "к": 0.6,
    "л": 0.4,
    "м": 0.5,
    "н": 0.5,
    "о": 0.01,
    "п": 0.5,
    "р": 0.3,
    "с": 0.3,
    "т": 0.3,
    "у": 0.2,
    "ф": 0.2,
    "х": 0.2,
    "ц": 0.2,
    "ч": 0.2,
    "ш": 0.1,
    "щ": 0.1,
    "ы": 0.1,
    "э": 0.05,
    "ю": 0.05,
    "я": 0.05,
}

# Script multipliers (adjust here for influence)
script_weights = {"latin": 1.0, "greek": 0.3, "hebrew": 0.05, "cyrillic": 0.05}


# Combine all characters with adjusted weights
def build_weighted_pool(taken: set[str]) -> list[tuple[str, float]]:
    pool = []

    def add_characters(char_dict: dict[str, float], multiplier: float):
        for ch, weight in char_dict.items():
            if ch not in taken:
                pool.append((ch, weight * multiplier))

    add_characters(latin_chars, script_weights["latin"])
    add_characters(greek_chars, script_weights["greek"])
    add_characters(hebrew_chars, script_weights["hebrew"])
    add_characters(cyrillic_chars, script_weights["cyrillic"])

    return pool


# Main function
def random_variable_name(
    taken: set[str], allow_subscript_superscript: bool = True
) -> str:
    pool = build_weighted_pool(taken)
    if not pool:
        raise ValueError("No available variable names not already taken.")
    variables, weights = zip(*pool)
    total = sum(weights)
    normalized_weights = [w / total for w in weights]
    variable_name = random.choices(variables, weights=normalized_weights, k=1)[0]
    if random.random() < 0.1 and not variable_name in taken:
        variable_name = variable_name.upper()
    if random.random() < 0.05:
        variable_name = (
            f"{variable_name}_{random_variable_name({*taken, variable_name}, False)}"
        )
    if random.random() < 0.01:
        variable_name = (
            f"{variable_name}^{random_variable_name({*taken, variable_name}, False)}"
        )
    if variable_name in taken:
        return random_variable_name(taken)
    return variable_name


def generate_number(
    mean=5,
    std=3,
    exponent=1.5,
    negative_probability=0.7,
    decimal_probability=0.7,
    allow_negative=True,
    allow_zero=True,
    require_integer=False,
):
    """Generates a random number with certain constraints."""
    while True:
        # Step 1: Generate magnitude using a power law
        magnitude = abs(np.random.normal(mean, std)) ** exponent

        # Step 2: Randomly make it negative or positive
        sign = 1
        if allow_negative and np.random.rand() >= negative_probability:
            sign = -1
        value = magnitude * sign

        # Step 3: Round to a certain number of decimal places
        if require_integer:
            decimal_places = 0
        else:
            # Bias toward fewer decimal places
            decimal_places = np.random.geometric(p=decimal_probability) - 1

        rounded = round(value, decimal_places)

        # Step 4: Convert to int if possible
        if decimal_places == 0 or rounded == int(rounded):
            result = int(rounded)
        else:
            result = rounded

        # Step 5: Validate against constraints
        if not allow_zero and result == 0:
            continue  # Retry if zero is not allowed

        return result


class ExpressionContext:
    taken: set[str] = set()
    substitutions: dict[str, int | float | Callable] = {}

    def __init__(self):
        self.taken = set()
        self.substitutions = {}


FUNCTIONS = {
    # Trigonometric Functions
    MathFunction("sin", functional_parameters=1): lambda args, _, __: math.sin(args[0]),
    MathFunction("cos", functional_parameters=1): lambda args, _, __: math.cos(args[0]),
    MathFunction("tan", functional_parameters=1): lambda args, _, __: math.tan(args[0]),
    MathFunction("asin", functional_parameters=1): lambda args, _, __: math.asin(
        args[0]
    ),
    MathFunction("acos", functional_parameters=1): lambda args, _, __: math.acos(
        args[0]
    ),
    MathFunction("atan", functional_parameters=1): lambda args, _, __: math.atan(
        args[0]
    ),
    MathFunction("atan2", functional_parameters=2): lambda args, _, __: math.atan2(
        args[0], args[1]
    ),
    MathFunction("csc", functional_parameters=1): lambda args, _, __: 1
    / math.sin(args[0]),
    MathFunction("sec", functional_parameters=1): lambda args, _, __: 1
    / math.cos(args[0]),
    MathFunction("cot", functional_parameters=1): lambda args, _, __: 1
    / math.tan(args[0]),
    # Hyperbolic Functions
    MathFunction("sinh", functional_parameters=1): lambda args, _, __: math.sinh(
        args[0]
    ),
    MathFunction("cosh", functional_parameters=1): lambda args, _, __: math.cosh(
        args[0]
    ),
    MathFunction("tanh", functional_parameters=1): lambda args, _, __: math.tanh(
        args[0]
    ),
    MathFunction("asinh", functional_parameters=1): lambda args, _, __: math.asinh(
        args[0]
    ),
    MathFunction("acosh", functional_parameters=1): lambda args, _, __: math.acosh(
        args[0]
    ),
    MathFunction("atanh", functional_parameters=1): lambda args, _, __: math.atanh(
        args[0]
    ),
    # Logarithmic and Exponential Functions
    MathFunction(
        "log",
        functional_parameters=1,
        functional_min_parameters=1,
        subscript_parameters=1,
        subscript_min_parameters=0,
    ): lambda args, subs, __: (
        math.log(args[0], subs[0]) if subs else math.log(args[0])
    ),
    MathFunction("ln", functional_parameters=1): lambda args, _, __: math.log(args[0]),
    MathFunction("log10", functional_parameters=1): lambda args, _, __: math.log10(
        args[0]
    ),
    MathFunction("log2", functional_parameters=1): lambda args, _, __: math.log2(
        args[0]
    ),
    MathFunction("log1p", functional_parameters=1): lambda args, _, __: math.log1p(
        args[0]
    ),
    MathFunction("exp", functional_parameters=1): lambda args, _, __: math.exp(args[0]),
    MathFunction("expm1", functional_parameters=1): lambda args, _, __: math.expm1(
        args[0]
    ),
    # Power Functions
    MathFunction("pow", functional_parameters=2): lambda args, _, __: math.pow(
        args[0], args[1]
    ),
    MathFunction("sqrt", functional_parameters=1): lambda args, _, __: math.sqrt(
        args[0]
    ),
    MathFunction(
        "root",
        functional_parameters=1,
        subscript_parameters=1,
        subscript_min_parameters=0,
    ): lambda args, subs, __: math.pow(args[0], 1 / (subs[0] if subs else 2)),
    # Rounding and Number-Theoretic Functions
    MathFunction("ceil", functional_parameters=1): lambda args, _, __: math.ceil(
        args[0]
    ),
    MathFunction("floor", functional_parameters=1): lambda args, _, __: math.floor(
        args[0]
    ),
    MathFunction("trunc", functional_parameters=1): lambda args, _, __: math.trunc(
        args[0]
    ),
    MathFunction("abs", functional_parameters=1): lambda args, _, __: abs(args[0]),
    MathFunction(
        "factorial", functional_parameters=1
    ): lambda args, _, __: math.factorial(int(args[0])),
    MathFunction(
        "gcd", functional_parameters=2, functional_min_parameters=2
    ): lambda args, _, __: math.gcd(*[int(a) for a in args]),
    MathFunction(
        "lcm", functional_parameters=2, functional_min_parameters=2
    ): lambda args, _, __: math.lcm(*[int(a) for a in args]),
    MathFunction("perm", functional_parameters=2): lambda args, _, __: math.perm(
        int(args[0]), int(args[1])
    ),
    MathFunction("comb", functional_parameters=2): lambda args, _, __: math.comb(
        int(args[0]), int(args[1])
    ),
    # Statistical Functions
    # MathFunction(
    #     "mean", functional_parameters=20, functional_min_parameters=1
    # ): lambda args, _, __: statistics.mean(args),
    # MathFunction(
    #     "median", functional_parameters=20, functional_min_parameters=1
    # ): lambda args, _, __: statistics.median(args),
    # MathFunction(
    #     "mode", functional_parameters=20, functional_min_parameters=1
    # ): lambda args, _, __: statistics.mode(args),
    # MathFunction(
    #     "stdev", functional_parameters=20, functional_min_parameters=2
    # ): lambda args, _, __: statistics.stdev(args),
    # MathFunction(
    #     "variance", functional_parameters=20, functional_min_parameters=2
    # ): lambda args, _, __: statistics.variance(args),
    # MathFunction(
    #     "min", functional_parameters=20, functional_min_parameters=1
    # ): lambda args, _, __: min(args),
    # MathFunction(
    #     "max", functional_parameters=20, functional_min_parameters=1
    # ): lambda args, _, __: max(args),
    # Special Functions
    MathFunction("gamma", functional_parameters=1): lambda args, _, __: math.gamma(
        args[0]
    ),
    MathFunction("lgamma", functional_parameters=1): lambda args, _, __: math.lgamma(
        args[0]
    ),
    MathFunction("erf", functional_parameters=1): lambda args, _, __: math.erf(args[0]),
    MathFunction("erfc", functional_parameters=1): lambda args, _, __: math.erfc(
        args[0]
    ),
}


def generate_weighted_random_int(min_val, max_val, power=3):
    """Generates a random integer with weights skewed towards the minimum value."""
    numbers = range(min_val, max_val + 1)
    weights = [1 / ((i - min_val + 1) ** power) for i in numbers]
    return random.choices(numbers, weights=weights, k=1)[0]


def generate_random_expression(
    max_depth=5,
    _depth=0,
    mean=5,
    std=3,
    gen_exponent=1.5,
    negative_probability=0.7,
    decimal_probability=0.7,
    max_variables=3,
    allow_negative=True,
    allow_zero=True,
    require_integer=False,
    allow_functions=True,
    context: ExpressionContext = ExpressionContext(),
):
    """
    Generates a random mathematical expression, now with support for functions.
    """

    def get_variable():
        if (random.random() < (1 - len(context.taken) / max_variables) * 0.5) or len(
            context.taken
        ) == 0:
            variable_name = random_variable_name(context.taken)
        else:
            variable_name = random.choice(list(context.taken))
        context.taken.add(variable_name)
        if random.random() < 0.8:  # 80% chance to generate a substitution
            context.substitutions[variable_name] = generate_number(
                mean=mean,
                std=std,
                exponent=gen_exponent,
                negative_probability=negative_probability,
                decimal_probability=decimal_probability,
                allow_negative=allow_negative,
                allow_zero=allow_zero,
                require_integer=require_integer,
            )
        return Symbol(variable_name)

    # Base case for recursion
    p = 0.3 + 0.7 * (_depth / max_depth)
    if (_depth >= max_depth or random.random() < p) and (
        _depth > 0 or random.random() < 0.0005
    ):
        if random.random() < 0.8:
            return generate_number(
                mean=mean,
                std=std,
                exponent=gen_exponent,
                negative_probability=negative_probability,
                decimal_probability=decimal_probability,
                allow_negative=allow_negative,
                allow_zero=allow_zero,
                require_integer=require_integer,
            )
        else:
            return get_variable()

    # Pass constraints down the recursion
    recursive_args = {
        "max_depth": max_depth,
        "_depth": _depth + 1,
        "mean": mean,
        "std": std,
        "gen_exponent": gen_exponent,
        "max_variables": max_variables,
        "negative_probability": negative_probability,
        "decimal_probability": decimal_probability,
        "allow_negative": allow_negative,
        "allow_zero": allow_zero,
        "require_integer": require_integer,
        "context": context,
    }

    # Decide the type of expression to generate
    choices = ["sum", "product", "power", "function"]
    weights = [4, 3, 1, 0.5]  # Adjust weights as needed
    if not allow_functions:
        choices.remove("function")
        weights = weights[:-1]
    expr_type = random.choices(choices, weights=weights, k=1)[0]

    if expr_type == "sum":
        num_terms = generate_weighted_random_int(2, 15)
        terms = [generate_random_expression(**recursive_args) for _ in range(num_terms)]
        return Sum(terms)

    elif expr_type == "product":
        num_factors = generate_weighted_random_int(2, 15)
        factors = [
            generate_random_expression(**recursive_args) for _ in range(num_factors)
        ]
        return Product(factors)

    elif expr_type == "power":
        base = generate_random_expression(**recursive_args)
        evaluated_base, _ = evaluate(base)
        exponent_args = recursive_args.copy()
        if isinstance(evaluated_base, (int, float)):
            if evaluated_base < 0:
                exponent_args["require_integer"] = True
            elif evaluated_base == 0:
                exponent_args["allow_negative"] = False
        exponent_args["decimal_probability"] = 0.9
        exponent = generate_random_expression(**exponent_args)
        return Power(base, exponent)

    elif expr_type == "function":
        func_def = random.choice(list(FUNCTIONS.keys()))

        # Generate functional arguments
        num_functional = random.randint(
            func_def.functional_min_parameters, func_def.functional_parameters
        )
        functional_args = [
            generate_random_expression(**recursive_args) for _ in range(num_functional)
        ]

        # Generate subscript arguments
        num_subscript = random.randint(
            func_def.subscript_min_parameters, func_def.subscript_parameters
        )
        subscript_args = [
            generate_random_expression(**recursive_args) for _ in range(num_subscript)
        ]

        # Generate superscript arguments
        num_superscript = random.randint(
            func_def.superscript_min_parameters, func_def.superscript_parameters
        )
        superscript_args = [
            generate_random_expression(**recursive_args) for _ in range(num_superscript)
        ]

        return FunctionCall(func_def, functional_args, subscript_args, superscript_args)


if __name__ == "__main__":
    # for i in range(100):
    #     print(generate_number())
    for i in range(100):
        # try:
        print("\n")
        expression_context = ExpressionContext()
        expression = generate_random_expression(2)
        print("Expression: $", render_latex(expression), "$")
        print(render_type(expression))
        substitutions = expression_context.substitutions
        substitutions.update(FUNCTIONS)
        answer, context = evaluate(expression, substitutions)
        text = context.render()
        print(text)
        print(f"Final answer: $\\boxed{{{render_latex(answer)}}}$")
    # except Exception as e:
    #     pass
