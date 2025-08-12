import builtins
import inspect
import math
import sys
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Union

from .expression import (
    FunctionCall,
    Numerical,
    Power,
    Product,
    Sum,
    Symbol,
    is_int_or_float,
    numerical_sort_key,
    numerical_sort_key_reverse,
    power,
    product,
    sum,
)
from .render import render_latex, render_type


class MathDomainError(ValueError):
    """Custom exception for math domain errors that stores the problematic expression."""

    def __init__(self, message, expression):
        super().__init__(message)
        self.expression = expression


from expressionizer.expression import (
    Product,
    Sum,
    Symbol,
    numerical_sort_key,
    numerical_sort_key_reverse,
    power,
    sum,
    product,
    FunctionCall,
    is_int_or_float,
)
from expressionizer.render import render_latex, render_type
from decimal import Decimal
import inspect


def get_caller_line():

    return frame.f_lineno, frame.f_code.co_filename


def round_sig(x, sig=2):
    if x == 0:
        return 0  # Zero is a special case
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)


@dataclass
class EvaluatorOptions:
    implicit_multiplication_limit: int = 12
    implicit_addition_limit: int = 100
    slow_step_addition: bool = True
    expand_powers: bool = True
    max_precision: int = 5
    max_exponent: int = 100


class Snapshot:
    portion: Numerical
    original: Numerical
    previous_tree: Numerical
    full_tree: Numerical
    explanation: Optional[str]
    approximate: bool = False

    def __init__(
        self,
        original,
        portion,
        previous_tree,
        full_tree,
        explanation=None,
        approximate=False,
    ):
        self.original = original
        self.portion = portion
        self.previous_tree = previous_tree
        self.full_tree = full_tree
        self.explanation = explanation
        self.approximate = approximate

    def __eq__(self, other):
        if isinstance(other, Snapshot):
            return (
                self.full_tree == other.full_tree
                and self.explanation == other.explanation
            )
        return self.full_tree == other

    def __ne__(self, other):
        return not self == other

    def __bool__(self):
        return True


class TextSnapshot:
    text: str
    breakpoint: bool

    def __init__(self, text: str, breakpoint: bool = False):
        self.text = text
        self.breakpoint = breakpoint

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


class BlockContext:
    trees: list[Numerical]
    context: "EvaluatorContext"

    def __init__(self, trees: list[Numerical], context: "EvaluatorContext"):
        self.trees = trees
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.blocks.remove(self)

    def __iter__(self):
        return iter(self.trees)

    def __len__(self):
        return len(self.trees)

    def __getitem__(self, index):
        return self.trees[index]

    def __setitem__(self, index, value):
        self.trees[index] = value

    def __delitem__(self, index):
        del self.trees[index]

    def __contains__(self, item):
        return item in self.trees


class EvaluatorContext:
    substitutions: dict[str, int | float]
    steps: list[str]
    snapshots: list[Numerical]
    current_tree: Numerical
    options: EvaluatorOptions
    error_on_invalid_snap: bool
    error_count: int
    is_approximate: bool
    blocks: list[BlockContext]

    def __init__(
        self,
        tree: Numerical,
        substitutions: dict[str, int | float] = {},
        options: EvaluatorOptions = EvaluatorOptions(),
        error_on_invalid_snap: bool = True,
    ):
        self.substitutions = substitutions
        self.snapshots = [Snapshot(tree, tree, tree, tree)]
        self.blocks = []
        self.current_tree = tree
        self.original_tree = tree
        self.options = options
        self.error_on_invalid_snap = error_on_invalid_snap
        self.error_count = 0
        self.is_approximate = False

    def snap(
        self,
        original: Union[Numerical, str],
        simplified: Union[Numerical, bool] = None,
        explanation: Optional[str] = None,
        approximate=False,
    ):
        if approximate:
            self.is_approximate = True
        if isinstance(original, str):
            # print(original)
            return self.snapshots.append(TextSnapshot(original, bool(simplified)))
        if contains(self.current_tree, original) <= 0:
            if self.error_on_invalid_snap:
                raise ValueError(
                    f"Original {render_latex(original)} not found in current tree {render_latex(self.current_tree)}.\n{render_type(self.original_tree)}"
                )
            else:
                self.error_count += 1
                return
        previous = self.current_tree

        new_tree = replace_sub(self.current_tree, original, simplified)

        snapshot = Snapshot(
            original, simplified, previous, new_tree, approximate=approximate
        )
        frame = inspect.currentframe().f_back
        line = frame.f_lineno

        # print(f"Called from line {line}.")
        # print("Old tree:", render_type(previous))
        # print("Original:", render_type(original))
        # print("Simplified:", render_type(simplified))
        # print("New tree:", render_type(new_tree))
        # print("\n")

        for i, block in enumerate(self.blocks):
            for j, tree in enumerate(block.trees):

                block.trees[j] = replace_sub(tree, original, simplified)
                # print(
                #     "block tree convert from to",
                #     render_latex(tree),
                #     render_latex(block.trees[j]),
                # )

        if explanation:
            snapshot.explanation = explanation.format(
                snapshot=render_latex(new_tree),
                previous=render_latex(previous),
                original=render_latex(original),
                simplified=render_latex(simplified),
            )
            self.snapshots.append(snapshot)
        elif snapshot != previous or len(self.snapshots) == 0:
            self.snapshots.append(snapshot)
        self.current_tree = new_tree

    def replace(self, state: Numerical, *args, **kwargs):
        self.current_tree = state
        self.snap(*args, **kwargs)

    def save_state(self):
        return self.current_tree

    def render_expressions(self, snapshots: list[Snapshot]):
        if len(snapshots) == 0:
            return ""
        if len(snapshots) == 1 and snapshots[0].previous_tree != snapshots[0].full_tree:
            return f"$$ {render_latex(snapshots[0].previous_tree)} = {render_latex(snapshots[0].full_tree)} $$"
        else:
            text = "$$"
            i = 0
            while i < len(snapshots):
                if i > 0:
                    text += "= "
                text += render_latex(snapshots[i].full_tree)
                if i < len(snapshots) - 1:
                    text += " \\\\\n"
                i += 1
            text += "$$\n"
            return text

    def render(self):
        steps = [[]]
        consecutive = []
        consecutive_portion = []
        last_consecutive_last = None
        current_portion = None
        previous = None
        previous_is_snapshot = False
        previous_snapshot = None
        for snapshot in self.snapshots:
            is_snapshot = isinstance(snapshot, Snapshot)
            if (
                previous_snapshot
                and is_snapshot
                and contains(previous_snapshot.portion, snapshot.original) > 0
            ):
                if (
                    current_portion
                    and current_portion != previous_snapshot.portion
                    and contains(current_portion, snapshot.original) > 0
                ):
                    current_portion = replace_sub(
                        current_portion,
                        snapshot.original,
                        snapshot.portion,
                    )
                else:
                    current_portion = replace_sub(
                        previous_snapshot.portion,
                        snapshot.original,
                        snapshot.portion,
                    )
                if not consecutive_portion:
                    consecutive_portion.append(previous_snapshot)
                consecutive_portion.append(snapshot)

            elif (
                previous_snapshot
                and is_snapshot
                and contains(snapshot.full_tree, previous_snapshot.portion)
                < contains(previous_snapshot.full_tree, previous_snapshot.original)
            ):
                current_portion = snapshot.portion
                if not consecutive_portion:
                    consecutive_portion.append(previous_snapshot)
                consecutive_portion.append(snapshot)
            elif is_snapshot and not (
                not previous_is_snapshot and (previous and previous.breakpoint)
            ):
                if last_consecutive_last and len(consecutive) > 0:
                    steps[-1].append(
                        self.render_expressions([last_consecutive_last, *consecutive])
                    )
                elif len(consecutive) > 1:
                    steps[-1].append(self.render_expressions(consecutive))
                last_consecutive_last = (
                    consecutive[-1] if len(consecutive) > 0 else None
                )

                steps.append([])
                current_portion = None

                consecutive_portion = []
                consecutive = []
            if isinstance(snapshot, TextSnapshot) or snapshot.explanation:
                if last_consecutive_last and len(consecutive) > 0:
                    steps[-1].append(
                        self.render_expressions([last_consecutive_last, *consecutive])
                    )
                elif len(consecutive) > 1:
                    steps[-1].append(self.render_expressions(consecutive))
                last_consecutive_last = (
                    consecutive[-1] if len(consecutive) > 0 else None
                )
                steps[-1].append(
                    str(snapshot)
                    if isinstance(snapshot, TextSnapshot)
                    else snapshot.explanation + "\n"
                )
                consecutive = []
            else:
                # Only add new expressions that aren't duplicate, and aren't the final result unless chaining
                is_duplicate = (
                    previous_snapshot
                    and snapshot.full_tree == previous_snapshot.full_tree
                )
                is_final = snapshot == self.current_tree
                if (
                    is_duplicate
                    and snapshot.explanation
                    and not consecutive[-1].explanation
                ):
                    # Take the last element off of consecutive and replace it with the new one
                    consecutive.pop()
                    is_duplicate = False

                if not is_duplicate:
                    consecutive.append(snapshot)
            if is_snapshot:
                previous_snapshot = snapshot
            previous = snapshot
            previous_is_snapshot = is_snapshot
        if last_consecutive_last:
            steps[-1].append(
                self.render_expressions([last_consecutive_last, *consecutive])
            )
        elif len(consecutive) > 0:
            steps[-1].append(self.render_expressions(consecutive))
        filtered_steps = []
        for step in steps:
            step = [substep for substep in step if substep != ""]
            if step:
                filtered_steps.append(step)
        if len(filtered_steps) == 1:
            return "\n".join(filtered_steps[0])
        text = ""
        for i, step in enumerate(filtered_steps):
            text += f"## Step {i+1}\n"
            for substep in step:
                text += substep + "\n"
        return text

    def block(self, trees: list[Numerical]):
        self.blocks.append(BlockContext(trees, self))
        return self.blocks[-1]


def pad(iterable, size, value=None, side="left"):
    if isinstance(iterable, str):
        pad_value = value if isinstance(value, str) else " "
        length = len(iterable)
        pad_len = max(size - length, 0)
        padding = pad_value * pad_len
        return padding + iterable if side == "left" else iterable + padding
    elif isinstance(iterable, list):
        pad_value = value
        length = len(iterable)
        pad_len = max(size - length, 0)
        padding = [pad_value] * pad_len
        return padding + iterable if side == "left" else iterable + padding
    else:
        raise TypeError("Only str and list types are supported.")


def generate_table(rows: list) -> str:
    if not rows:
        return ""
    # Convert all values to strings
    str_rows = [[str(cell) for cell in row] for row in rows]
    # Transpose for column width calculation
    columns = list(zip(*str_rows))
    col_widths = [max(len(cell) for cell in col) for col in columns]

    def format_row(row):
        return (
            "| "
            + " | ".join(cell.ljust(width) for cell, width in zip(row, col_widths))
            + " |"
        )

    header = format_row(str_rows[0])
    separator = "| " + " | ".join("-" * width for width in col_widths) + " |"
    body = [format_row(row) for row in str_rows[1:]]

    return "\n".join([header, separator] + body)


def get_coefficient_exponent(x):
    if x == 0:
        return 0, 0  # Special case: zero

    # Work with positive values, restore sign later
    sign = -1 if x < 0 else 1
    x = abs(x)

    # Convert to string to handle float or int accurately
    s = f"{x:.15g}"  # Prevent float artifacts
    if "." in s:
        # Remove trailing zeros
        s = s.rstrip("0").rstrip(".")
    if "e" in s or "E" in s:
        # Handle scientific notation directly
        coeff_str, exp_str = s.lower().split("e")
        coeff = int(coeff_str.replace(".", ""))
        exp = int(exp_str) - (len(coeff_str.split(".")[-1]) if "." in coeff_str else 0)
        return sign * coeff, exp

    # If decimal present, move decimal to integer and count how many places moved
    if "." in s:
        integer_part, decimal_part = s.split(".")
        if integer_part == "0":
            # e.g. 0.005 → coeff=5, exp=-3
            first_nonzero = next(i for i, c in enumerate(decimal_part) if c != "0")
            coeff = int(decimal_part[first_nonzero:])
            exp = -(first_nonzero + 1)
        else:
            # e.g. 3.28 → 328, -2
            coeff = int(integer_part + decimal_part)
            exp = -len(decimal_part)
        return sign * coeff, exp
    else:
        # Integer: remove trailing zeros, count them
        zeros = 0
        num = s
        while num.endswith("0"):
            num = num[:-1]
            zeros += 1
        coeff = int(num)
        return sign * coeff, zeros


def render_number_with_power_of_ten(number: int | float) -> str:
    coefficient, exponent = get_coefficient_exponent(number)
    if coefficient == 0:
        return "$0$"
    return f"${coefficient} \\cdot 10^{{{exponent}}}$"


def decompose_number(n):
    s = str(format(Decimal(str(n)), "f")).replace("-", "")
    sign = -1 if n < 0 else 1
    if "." in s:
        int_part, frac_part = s.split(".")
    else:
        int_part, frac_part = s, ""
    result = []
    # Integer part
    for i, digit in enumerate(int_part):
        power = len(int_part) - i - 1
        value = int(digit) * (10**power) * sign
        result.append(value)
    # Fractional part
    for i, digit in enumerate(frac_part):
        value = int(digit) * (10 ** -(i + 1)) * sign
        result.append(value)
    return result


def solve_sum(components, context: EvaluatorContext):
    from math import floor

    # ---------- helpers ----------
    def split_parts(s):
        sign = -1 if s.startswith("-") else 1
        if sign == -1:
            s = s[1:]
        if "." in s:
            a, b = s.split(".", 1)
        else:
            a, b = s, ""
        return sign, a, b

    def lpad(s, width):
        return "0" * (width - len(s)) + s

    def rpad(s, width):
        return s + "0" * (width - len(s))

    # ---------- build aligned block ----------
    parts = [split_parts(str(format(Decimal(str(x)), "f"))) for x in components]
    left_max = max(len(a) for sign, a, b in parts)
    right_max = max(len(b) for _, _, b in parts)
    has_decimal = right_max > 0
    has_negative = any(sign == -1 for sign, _, _ in parts)

    lines = []
    signs = []
    for sign, a, b in parts:
        signs.append(sign)
        left = a
        if has_decimal:
            line = lpad(left, left_max) + "." + rpad(b, right_max)
        else:
            line = lpad(left, left_max + right_max)  # behave like old code
        if has_negative and sign == -1:
            line = "-" + line
        elif has_negative:
            line = " " + line
        lines.append(line)

    max_length = len(lines[0]) - 1 if has_negative else len(lines[0])
    # old snapshot (exact behavior retained)
    addition = "```\n" + "\n".join(lines) + "\n```"
    context.snap(addition, False)

    # For backward-compat with your later indexing:
    addition = addition.split("\n")[1:-1]  # trim the fences

    # ---------- power map ----------
    if has_decimal:
        dot_idx = left_max  # same for all lines
        power_for_col = []
        for c in range(max_length):
            if c == dot_idx:
                power_for_col.append(None)
            elif c < dot_idx:
                power_for_col.append(dot_idx - c - 1)
            else:
                power_for_col.append(-(c - dot_idx))
    else:
        power_for_col = [None] * max_length  # will compute like before

    carry = 0
    final = [None] * (max_length)

    for i in range(max_length):
        col = max_length - i - 1  # right to left
        # Decimal point column?
        if has_decimal and col == dot_idx:
            final[col] = "."
            continue

        values = []
        for j in range(len(addition)):
            ch = addition[len(addition) - j - 1][col + (1 if has_negative else 0)]
            if ch.isdigit():
                values.append(int(ch) * signs[len(addition) - j - 1])
        if carry != 0:
            values.append(carry)

        sum_values = sum(values)
        carry = (
            math.floor(sum_values / 10)
            if sum_values > 0
            else math.ceil(sum_values / 10)
        )
        digit = sum_values - carry * 10
        if digit < 0:  # Borrow
            digit += 10
            carry -= 1
        final[col] = digit

        # Determine exponent for snap text
        if has_decimal:
            p = power_for_col[col]
            # Skip dot, p can be None only if no decimal or legacy path
        else:
            p = i  # replicate original integer behavior

        # keep your step text shape
        if p is not None:
            if len(values) > 1:
                step = f"$10^{{{p}}}$: ${' + '.join(map(str, values))} = {sum_values}$"
            else:
                step = f"$10^{{{p}}}$: ${sum_values}$"
            if carry > 0:
                step += f", carry the {carry}."
            elif carry < 0:
                step += f", borrow a {-carry} and add 10 to get {digit}."
            context.snap(step, False)
    # leftover carry
    if carry > 0:
        # put carry to the left of everything (may need more than 1 digit)
        c_str = str(abs(carry))
        final = list(c_str) + final
        context.snap(f"$10^{{{p+1}}}$: {carry} (carried)", False)
        carry = 0
    result_str = "".join(str(x) for x in final).strip()

    # Convert for return (keep int for old path)
    result = float(result_str) if "." in result_str else int(result_str)
    if carry < 0:
        result = -(-carry * 10 ** (p + 1) - result)
    context.snap(f"Putting it together, we get ${result}$.", False)
    context.snap(Sum(components), result)
    return result


def add(a, b, context: EvaluatorContext):
    limit = context.options.implicit_addition_limit
    a_coefficient, a_exponent = get_coefficient_exponent(a)
    b_coefficient, b_exponent = get_coefficient_exponent(b)
    if (
        -limit <= a_coefficient <= limit
        and -limit <= b_coefficient <= limit
        or (a_coefficient == 1 or b_coefficient == 1)
    ):
        context.snap(Sum([a, b]), a + b)
        return a + b
    a_components = decompose_number(a)
    b_components = decompose_number(b)
    all_components = a_components + b_components
    context.snap(f"Let's break ${a}$ and ${b}$ down into their components.", False)
    context.snap(Sum([a, b]), Sum(all_components))
    if context.options.slow_step_addition:
        result = solve_sum(all_components, context)
    else:
        context.snap(Sum(all_components), a + b)
        result = a + b
    context.snap("", True)
    return result


def multiply(a, b, context: EvaluatorContext, quick_compute=True):
    limit = context.options.implicit_multiplication_limit
    a_coefficient, a_exponent = get_coefficient_exponent(a)
    b_coefficient, b_exponent = get_coefficient_exponent(b)
    if (
        -limit <= a_coefficient <= limit
        and -limit <= b_coefficient <= limit
        or (a_coefficient == 1 or b_coefficient == 1)
    ):
        context.snap(Product([a, b]), a * b)
        return a * b
    a_nearest_round = 10 ** (len(str(a)))
    b_nearest_round = 10 ** (len(str(b)))
    a_round_distance = a_nearest_round - a
    b_round_distance = b_nearest_round - b
    if (
        a_round_distance < limit
        and a > limit
        and a_round_distance < b_round_distance
        and quick_compute
    ):
        context.snap(
            Product([a, b]), Product([Sum([a_nearest_round, -a_round_distance]), b])
        )
        if -limit <= b_coefficient <= limit:
            context.snap(
                Product([Sum([a_nearest_round, -a_round_distance]), b]),
                a * b,
            )
        else:
            context.snap(
                Product([Sum([a_nearest_round, -a_round_distance]), b]),
                Sum([a_nearest_round * b, -Product([a_round_distance, b])]),
            )
            result = multiply(a_round_distance, b, context, quick_compute=False)
            context.snap(
                Sum([a_nearest_round * b, -result]),
                a_nearest_round * b - result,
            )
        return a * b

    elif (
        b_round_distance < limit
        and b > limit
        and b_round_distance < a_round_distance
        and quick_compute
    ):
        # initial snap breaking b into (b_nearest_round - b_round_distance)
        context.snap(
            Product([a, b]), Product([a, Sum([b_nearest_round, -b_round_distance])])
        )

        if -limit <= a_coefficient <= limit:
            # if small coefficient, we can compute directly
            context.snap(
                Product([a, Sum([b_nearest_round, -b_round_distance])]),
                a * b,
            )
        else:
            # otherwise, express as difference of two products
            context.snap(
                Product([a, Sum([b_nearest_round, -b_round_distance])]),
                Sum([a * b_nearest_round, -Product([a, b_round_distance])]),
            )
            # compute the hard part a * b_round_distance
            result = multiply(a, b_round_distance, context, quick_compute=False)
            # show the final subtraction
            context.snap(
                Sum([a * b_nearest_round, -result]),
                a * b_nearest_round - result,
            )

        return a * b
    context.snap(
        f"Because ${a}$ and ${b}$ are both too complex, let's break their product down into components and use a table to multiply each product. Then, we can sum the problems to find the solution to ${a} \\cdot {b}$.",
        False,
    )
    if len(str(a_coefficient)) > context.options.max_precision:
        a_approx = (
            round_sig(a_coefficient, context.options.max_precision) * 10**a_exponent
        )
        context.snap(
            a,
            a_approx,
            f"${a}$ has too many decimal places. Let's approximate it to {a_approx} to make the multiplication easier.",
            approximate=True,
        )
    else:
        a_approx = a
    if len(str(b_coefficient)) > context.options.max_precision:
        b_approx = (
            round_sig(b_coefficient, context.options.max_precision) * 10**b_exponent
        )
        if b != a:
            context.snap(
                b,
                b_approx,
                (
                    f"${b}$ has too many decimal places. Let's approximate it to {b_approx} to make the multiplication easier."
                    if b != a
                    else None
                ),
                approximate=True,
            )
    else:
        b_approx = b
    a = a_approx
    b = b_approx
    a_coefficient, a_exponent = get_coefficient_exponent(a)
    b_coefficient, b_exponent = get_coefficient_exponent(b)
    total_exponent = 0
    if a_exponent != 0:
        context.snap(
            f"Multiply ${a}$ by $10^{{{a_exponent}}}$ to shift the decimal point to make the math easier.",
            False,
        )
        total_exponent += a_exponent

    if b_exponent != 0:
        if not (b_coefficient == a_coefficient and b_exponent == a_exponent):
            context.snap(
                f"Multiply ${b}$ by $10^{{{b_exponent}}}$ to shift the decimal point to make the math easier.",
                False,
            )
        total_exponent += b_exponent
    if a != a_coefficient or b != b_coefficient:
        context.snap(
            Product([a, b]),
            Product([a_coefficient, b_coefficient, Power(10, total_exponent)]),
        )
    a = a_coefficient
    b = b_coefficient

    a = int(a)
    b = int(b)
    a_str, b_str = str(a), str(b)
    a_components = decompose_number(a)
    b_components = decompose_number(b)

    rows = [
        [""]
        + [render_number_with_power_of_ten(a_component) for a_component in a_components]
    ]
    grid = []
    max_length = 0
    for b_component in b_components:
        rows.append([render_number_with_power_of_ten(b_component)])
        grid.append([])
        for a_component in a_components:
            result = a_component * b_component
            grid[-1].append(result)
            if len(str(result)) > max_length:
                max_length = len(str(result))
            coefficient, exponent = get_coefficient_exponent(result)
            if coefficient == 0:
                rows[-1].append("$0$")
            else:
                rows[-1].append(f"${coefficient} \\cdot 10^{{{exponent}}}$")

    w = len(a_components)
    h = len(b_components)
    all_components = []
    for d in range(w + h - 1):
        for x in range(d, -1, -1):
            y = d - x
            if x < w and y < h:
                all_components.append(grid[y][x])
    context.snap(Product([a, b]), Product([Sum(a_components), Sum(b_components)]))
    context.snap("\n**Table of products:**", False)
    table = generate_table(rows)
    context.snap(table, False)
    context.snap(Product([Sum(a_components), Sum(b_components)]), Sum(all_components))
    if context.options.slow_step_addition:
        context.snap("**List of values to add:**", False)
        result = solve_sum(all_components, context)
        if total_exponent != 0:
            context.snap(
                Product([result, Power(10, total_exponent)]),
                result * 10**total_exponent,
            )
            result *= 10**total_exponent
        context.snap("", True)
        return result
    else:
        context.snap(Sum(all_components), a * b)
        if total_exponent != 0:
            context.snap(
                Product([result, Power(10, -total_exponent)]),
                result * 10**total_exponent,
            )
            result *= 10**total_exponent
        context.snap("", True)
        return a * b


def replace_symbols(expression: Numerical, context: EvaluatorContext):
    match expression:
        case Symbol():
            if expression.name in context.substitutions:
                return context.substitutions[expression.name]
            else:
                return expression
        case Product():
            return Product(
                [replace_symbols(factor, context) for factor in expression.factors]
            )
        case Sum():
            return Sum([replace_symbols(term, context) for term in expression.terms])
        case Power():
            return Power(
                replace_symbols(expression.base, context),
                replace_symbols(expression.exponent, context),
            )
        case FunctionCall():
            return expression.function(
                [
                    replace_symbols(arg, context)
                    for arg in expression.functional_arguments
                ],
                [
                    replace_symbols(arg, context)
                    for arg in expression.subscript_arguments
                ],
                [
                    replace_symbols(arg, context)
                    for arg in expression.superscript_arguments
                ],
            )
        case _:
            return expression


def replace_sub(expr, target, replacement):
    """
    Return a *new* expression obtained by replacing `target`
    (a subtree) with `replacement` inside `expr`.
    Works recursively for all node types.
    """
    if expr == target:
        return replacement
    elif expr == -target:
        return -replacement
    match expr:
        case Power():
            return Power(
                replace_sub(expr.base, target, replacement),
                replace_sub(expr.exponent, target, replacement),
            )
        case Product():
            if isinstance(target, Product) and target in expr:
                if isinstance(replacement, Product):
                    new_factors = replacement.factors.copy()
                else:
                    new_factors = [replacement]
                target_factors = []
                expr_factors = []
                expr_sign = 1
                target_sign = 1
                for factor in expr.factors:
                    if isinstance(factor, Product):
                        expr_factors.extend(factor.factors)
                    elif isinstance(factor, Sum) and len(factor.terms) <= 1:
                        expr_factors.extend(factor.terms)
                    elif is_int_or_float(factor):
                        expr_sign *= 1 if factor >= 0 else -1
                        if abs(factor) != 1:
                            expr_factors.append(abs(factor))
                    else:
                        expr_factors.append(factor)
                for factor in target.factors:
                    if isinstance(factor, Product):
                        target_factors.extend(factor.factors)
                    elif isinstance(factor, Sum) and len(factor.terms) == 1:
                        target_factors.append(factor.terms[0])
                    elif is_int_or_float(factor):
                        target_sign *= 1 if factor >= 0 else -1
                        if abs(factor) != 1:
                            target_factors.append(abs(factor))
                    else:
                        target_factors.append(factor)
                for factor in expr_factors:
                    for target_factor in target_factors:
                        if factor == target_factor:
                            target_factors.remove(target_factor)
                            break
                    else:
                        new_factors.append(factor)
                new_sign = expr_sign * target_sign
                if new_sign < 0:
                    new_factors.append(-1)
                if len(target_factors) == 0:
                    if len(new_factors) == 1:
                        return new_factors[0]
                    return Product(new_factors)
            elif (
                len(expr.factors) == 2
                and -1 in expr.factors
                and -target in expr.factors
            ):
                return replacement
            return Product([replace_sub(f, target, replacement) for f in expr.factors])
        case Sum():
            if (
                isinstance(target, Sum) and target in expr
            ):  # Issue here. See error on test.py
                if isinstance(replacement, Sum):
                    new_terms = replacement.terms.copy()
                else:
                    new_terms = [replacement]
                expr_terms = []
                for term in expr.terms:
                    if isinstance(term, Sum):
                        expr_terms.extend(term.terms)
                    # elif isinstance(term, Product) and len(term.factors) == 1:
                    #     expr_terms.append(term.factors[0])
                    elif (
                        isinstance(term, Product)
                        and len(term.factors) == 2
                        and -1 in term.factors
                    ):
                        expr_terms.append(term.factors[0] * term.factors[1])
                    else:
                        expr_terms.append(term)
                target_terms = []
                for term in target.terms:
                    if isinstance(term, Sum):
                        target_terms.extend(term.terms)
                    if isinstance(term, Product) and len(term.factors) == 1:
                        target_terms.append(term.factors[0])
                    elif (
                        isinstance(term, Product)
                        and len(term.factors) == 2
                        and -1 in term.factors
                    ):
                        target_terms.append(term.factors[0] * term.factors[1])
                    else:
                        target_terms.append(term)
                for term in expr_terms:
                    for target_term in target_terms:
                        if term == target_term:
                            target_terms.remove(target_term)
                            break
                    else:
                        new_terms.append(term)
                if len(target_terms) == 0:
                    if len(new_terms) == 1:
                        return new_terms[0]
                    return Sum(new_terms)
            return Sum([replace_sub(t, target, replacement) for t in expr.terms])
        case FunctionCall():
            return FunctionCall(
                expr.function,
                [
                    replace_sub(a, target, replacement)
                    for a in expr.functional_arguments
                ],
                [replace_sub(a, target, replacement) for a in expr.subscript_arguments],
                [
                    replace_sub(a, target, replacement)
                    for a in expr.superscript_arguments
                ],
            )
        case _:
            return expr  # atom


def contains(expr, target):
    """
    Return a *new* expression obtained by replacing `target`
    (a subtree) with `replacement` inside `expr`.
    Works recursively for all node types.
    """
    if expr == target:
        return 1
    elif expr == -target:
        return 1
    match expr:
        case Power():
            return contains(expr.base, target) or contains(expr.exponent, target)
        case Product():
            if isinstance(target, Product) and target in expr:
                return 1
            return any([contains(f, target) for f in expr.factors])
        case Sum():
            if isinstance(target, Sum) and target in expr:
                return 1
            return any([contains(t, target) for t in expr.terms])
        case FunctionCall():
            return sum(
                [contains(a, target) for a in expr.functional_arguments]
                + [contains(a, target) for a in expr.subscript_arguments]
                + [contains(a, target) for a in expr.superscript_arguments]
            )
        case _:
            return 0


def _get_term_parts(term):
    """Separates a term into its coefficient and variable parts."""
    if isinstance(term, (int, float)):
        return term, 1

    if isinstance(term, Product):
        coefficient = 1
        variable_factors = []
        for factor in term.factors:
            if isinstance(factor, (int, float)):
                coefficient *= factor
            else:
                variable_factors.append(factor)

        if not variable_factors:
            return coefficient, 1
        if len(variable_factors) == 1:
            return coefficient, variable_factors[0]
        return coefficient, Product(variable_factors)

    # For Symbols, Powers, and other expressions, the coefficient is 1
    return 1, term


def get_fraction(expr):
    # Helper: single object to Product([obj])
    def to_product(lst):
        if len(lst) == 1:
            return lst[0]
        else:
            return Product(lst)

    # Case 1: Power
    if isinstance(expr, Power):
        if expr.exponent < 0:
            numerator = 1
            denominator = Power(expr.base, -expr.exponent)
            return (numerator, denominator)
        else:
            return None

    # Case 2: Product
    if isinstance(expr, Product):
        num_factors = []
        den_factors = []
        for factor in expr.factors:
            if isinstance(factor, Power) and factor.exponent < 0:
                den_factors.append(Power(factor.base, -factor.exponent))
            elif factor == 1:
                num_factors.append(factor)  # Keep '1' in numerator (harmless)
            else:
                num_factors.append(factor)

        if den_factors:
            numerator = to_product(num_factors) if num_factors else 1
            denominator = to_product(den_factors)
            return (numerator, denominator)
        else:
            return None

    # Otherwise, not a fraction
    return None


def evaluate_expression(expression: Numerical, context: EvaluatorContext):

    result = None
    match expression:
        case int() | float():
            result = expression
        case Power():
            with context.block([expression.exponent]) as block:
                base = evaluate_expression(expression.base, context)
                exponent = block[0]
            exponent_fraction = get_fraction(exponent)
            if exponent_fraction and exponent_fraction[0] == 1:
                new_exponent = evaluate_expression(
                    exponent,
                    EvaluatorContext(exponent),
                )  # Fake context so we don't get intermediate steps on roots.
                result = base**new_exponent
                context.snap(
                    Power(base, exponent),
                    result,
                )
                return result
            else:
                exponent = evaluate_expression(exponent, context)
            expression = Power(base, exponent)
            if base in [0, 1]:
                result = base
                context.snap(expression, result, f"{base} to any power is {base}.")
                return result
            if base == -1 and is_int_or_float(exponent) and exponent.is_integer():
                # Determine sign
                if exponent % 2 == 0:
                    result = 1
                else:
                    result = -1
                context.snap(
                    expression,
                    result,
                    f"When $-1$ is raised to an even power, the result is $1$. When $-1$ is raised to an odd power, the result is $-1$. "
                    + (
                        f"Since in this case, our power is {exponent}, which is even, the result is $1$."
                        if exponent % 2 == 0
                        else f"Since in this case, our power is {exponent}, which is odd, the result is $-1$."
                    ),
                )
                return result

            if is_int_or_float(base) and is_int_or_float(exponent):
                if exponent > context.options.max_exponent and base > 1:
                    context.snap(
                        expression,
                        float("inf"),
                        explanation="${previous}$ is too large to compute, so let's call it $\\infty$.",
                        approximate=True,
                    )
                    return float("inf")  # Infinity, too large to compute
                elif exponent < -context.options.max_exponent and base > 1:
                    context.snap(
                        expression,
                        0,
                        explanation="${previous}$ is too small to compute, so let's call it $0$.",
                        approximate=True,
                    )
                    return float("-inf")  # Infinity, too large to compute
                elif exponent > context.options.max_exponent and base < 1:
                    context.snap(
                        expression,
                        0,
                        explanation="${previous}$ is too small to compute, so let's call it $0$.",
                        approximate=True,
                    )
                    return 0
                elif exponent < -context.options.max_exponent and base < 1:
                    context.snap(
                        expression,
                        float("inf"),
                        explanation="${previous}$ is too large to compute, so let's call it $\\infty$.",
                        approximate=True,
                    )
                    return float("inf")  # Infinity, too large to compute
                if context.options.expand_powers and exponent > 1:
                    new_expression = Product(
                        [base] * math.floor(exponent)
                        + (
                            [Power(base, math.floor(exponent) % 1)]
                            if math.floor(exponent) % 1 > 0
                            else []
                        )
                    )
                    context.snap(
                        expression,
                        new_expression,
                    )
                    result = evaluate_expression(new_expression, context)
                else:
                    result = base**exponent
                    context.snap(
                        expression,
                        result,
                    )
            else:
                result = power(base, exponent)
                context.snap(
                    expression,
                    result,
                )
        case Product():
            if 0 in expression.factors:
                context.snap(expression, 0)
                return 0
            factors = [
                evaluate_expression(factor, context)
                for factor in expression.factors
                if factor != 1
            ]
            current_expression = Product(factors)
            if len(factors) == 1:
                context.snap(current_expression, factors[0])
                return factors[0]
            if len(factors) == 0:
                context.snap(current_expression, 1)
                return 1
            if len(factors) != len(expression.factors):
                context.snap(expression, current_expression)
            elif 0 in factors:
                context.snap(current_expression, 0)
                return 0
            else:
                # Check for a Sum to distribute
                sum_to_distribute = None
                for i, factor in enumerate(factors):
                    if isinstance(factor, Sum):
                        sum_to_distribute = factor
                        # Keep track of which factor was the sum
                        sum_index = i
                        break

                if sum_to_distribute:
                    other_factors = [
                        factor for i, factor in enumerate(factors) if i != sum_index
                    ]
                    new_terms = []
                    for term in sum_to_distribute.terms:
                        # Create a new product for each term in the sum
                        new_factors = other_factors + [term]
                        new_product = product(new_factors)
                        new_terms.append(new_product)

                    # The new expression is a sum of these new products
                    distributed_sum = Sum(new_terms)
                    context.snap(current_expression, distributed_sum)
                    return evaluate_expression(distributed_sum, context)
                # Original logic if no distribution is needed
                factors = sorted(factors, key=numerical_sort_key)
                if all(is_int_or_float(factor) for factor in factors):
                    with context.block(factors) as block:
                        result = block[0]
                        i = 1
                        while i < len(block):
                            factor = block[i]
                            result = multiply(result, factor, context)
                            i += 1
                else:
                    new_expression = product([arg for arg in factors])
                    context.snap(current_expression, new_expression)
                    return new_expression
        case Sum():
            # Stage 1: Recursively evaluate all terms first.
            terms = [evaluate_expression(term, context) for term in expression.terms]
            expression = Sum(terms)

            # Stage 2: Flatten nested Sums.
            flattened_terms = []
            needs_flattening = any(isinstance(t, Sum) for t in terms)
            if needs_flattening:
                for term in terms:
                    if isinstance(term, Sum):
                        flattened_terms.extend(term.terms)
                    elif isinstance(term, Product) and len(term.factors) == 1:
                        flattened_terms.append(term.factors[0])
                    else:
                        flattened_terms.append(term)
                new_sum = Sum(flattened_terms)
                context.snap(expression, new_sum)
                expression = new_sum
                terms = flattened_terms

            # Stage 3: Combine numeric terms.
            numeric_terms = [t for t in terms if is_int_or_float(t)]
            variable_terms = [t for t in terms if not is_int_or_float(t)]
            if len(numeric_terms) > 1:
                numeric_sum = numeric_terms[0]
                with context.block(numeric_terms) as block:
                    i = 1
                    while i < len(block):
                        term = block[i]
                        numeric_sum = add(numeric_sum, term, context)
                        i += 1
                new_terms = [numeric_sum] + variable_terms
                new_sum = Sum(new_terms)
                expression = new_sum
                terms = new_terms
                numeric_terms = [numeric_sum]
            elif len(numeric_terms) == 1:
                numeric_sum = numeric_terms[0]
            if len(variable_terms) == 0 and len(numeric_terms) == 1:
                return numeric_terms[0]

            # Stage 4: Combine like variable terms.
            grouped_terms = {}
            for term in variable_terms:
                coefficient, variable_part = _get_term_parts(term)
                if variable_part not in grouped_terms:
                    grouped_terms[variable_part] = [0, variable_part]
                grouped_terms[variable_part][0] += coefficient

            reconstructed_terms = []
            for _, (coefficient, variable_part) in grouped_terms.items():
                if coefficient == 0:
                    continue
                if variable_part == 1:
                    reconstructed_terms.append(coefficient)
                elif coefficient == 1:
                    reconstructed_terms.append(variable_part)
                else:
                    reconstructed_terms.append(Product([coefficient, variable_part]))
            final_terms = numeric_terms + reconstructed_terms
            if len(final_terms) != len(terms):
                if not final_terms:
                    result = 0
                elif len(final_terms) == 1:
                    result = final_terms[0]
                else:
                    result = Sum(final_terms)
                context.snap(expression, result)
                return result
            if len(final_terms) == 1:
                result = final_terms[0]
                context.snap(expression, result)
                return result

            return expression

        case FunctionCall():
            state = context.save_state()
            with context.block(
                expression.functional_arguments
            ) as functional_arguments, context.block(
                expression.subscript_arguments
            ) as subscript_arguments, context.block(
                expression.superscript_arguments
            ) as superscript_arguments:
                functional_arguments = [
                    evaluate_expression(arg, context) for arg in functional_arguments
                ]
                subscript_arguments = [
                    evaluate_expression(arg, context) for arg in subscript_arguments
                ]
                superscript_arguments = [
                    evaluate_expression(arg, context) for arg in superscript_arguments
                ]
            if (
                expression.function in context.substitutions
                and all(is_int_or_float(arg) for arg in functional_arguments)
                and all(is_int_or_float(arg) for arg in subscript_arguments)
                and all(is_int_or_float(arg) for arg in superscript_arguments)
            ):
                try:
                    result = context.substitutions[expression.function](
                        [arg for arg in functional_arguments],
                        [arg for arg in subscript_arguments],
                        [arg for arg in superscript_arguments],
                    )
                except Exception as e:  # TODO more specific.
                    raise MathDomainError(
                        str(e),
                        FunctionCall(
                            expression.function,
                            functional_arguments,
                            subscript_arguments,
                            superscript_arguments,
                        ),
                    )
            elif expression.function.name in context.substitutions and all(
                is_int_or_float(arg) for arg in functional_arguments
            ):
                try:
                    result = context.substitutions[expression.function.name](
                        [arg for arg in functional_arguments],
                        [arg for arg in subscript_arguments],
                        [arg for arg in superscript_arguments],
                    )
                except ValueError as e:
                    raise MathDomainError(
                        str(e),
                        FunctionCall(
                            expression.function,
                            functional_arguments,
                            subscript_arguments,
                            superscript_arguments,
                        ),
                    )
            else:
                result = FunctionCall(
                    expression.function,
                    [arg for arg in functional_arguments],
                    [arg for arg in subscript_arguments],
                    [arg for arg in superscript_arguments],
                )
            context.replace(state, expression, result)
        case Symbol():
            if expression.name in context.substitutions:
                result = context.substitutions[expression.name]
            else:
                result = expression
    return result


def evaluate(
    expression: Numerical,
    substitutions: dict[str, int | float] = {},
    error_on_invalid_snap: bool = True,
):
    context = EvaluatorContext(
        expression,
        substitutions,
        error_on_invalid_snap=error_on_invalid_snap,
    )
    # context.snap(f"Given the expression:\n$${render_latex(expression)}$$")
    new_expression = replace_symbols(expression, context)
    if new_expression != expression:
        variable_substitutions = {
            k: v
            for (k, v) in substitutions.items()
            if isinstance(k, str)
            and isinstance(
                v, (int, float, complex, Sum, Product, Power, FunctionCall, Symbol)
            )
        }
        keys = list(variable_substitutions.keys())
        substitutions = []
        for i, (k, v) in enumerate(variable_substitutions.items()):
            sub = f"${k} = {render_latex(v)}$"
            if i == len(keys) - 2:
                sub += " and "
            elif i < len(keys) - 2:
                sub += ", "
            substitutions.append(sub)
        context.snap(f"Substitute {''.join(substitutions)}:", False)
        context.snap(
            expression,
            new_expression,
        )
    else:
        context.snap(expression, new_expression)
    try:
        result = evaluate_expression(new_expression, context)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
    except MathDomainError as e:
        # The evaluation failed. The 'result' is the expression before the error.
        result = new_expression
        # Add a final step explaining the domain error.
        error_message = f"We cannot simplify the expression any further because ${render_latex(e.expression)}$ is undefined. Those values are out of domain for {e.expression.function.name}."
        context.snap(error_message)

    return result, context
