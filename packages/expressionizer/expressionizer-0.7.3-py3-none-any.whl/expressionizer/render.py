import math
from .expression import *


@dataclass
class LaTeXRenderOptions:
    group_exponentiation: bool = (
        False  # Always add a group around exponentiation, even when it is otherwise clear.
    )
    parentheses_function_call: bool = False  # Use parentheses rather than {}
    backslash_function_call: bool = True  # Put a backslash before the function call
    product_separator: str = (
        ""  # Default product separator for cases when it is clear either way.
    )
    always_use_product_parentheses = False  # Always used parentheses around factors in a product, even if it is clear otherwise
    use_parentheses_for_literal_product = (
        True  # Use parentheses rather than \cdot when multiplying literals
    )
    group_on_one_argument_function: bool = (
        True  # Do you need the grouping ({} or ()) if it only has one argument
    )
    fraction_as_inline: bool = False  # \frac vs just using /
    negative_exponent_as_fraction: bool = (
        True  # Convert negative exponents to fractions.
    )
    compact_exponents: bool = (
        True  # In cases where it is clear either way, compact_exponents will use x^y instead of x^{y}
    )


def apply_group(text, paren=False, square=False, curly=False):
    if paren:
        return "(" + text + ")"
    elif square:
        return "[" + text + "]"
    elif curly:
        return "{" + text + "}"
    else:
        return text


def render(expression: Union[Numerical, Equation, InEquality], group=False):
    match expression:
        case int() | float():
            if expression == math.pi:
                return "π"
            return str(expression)
        case Power(base, exponent) if (
            isinstance(expression.exponent, int)
            or isinstance(expression.exponent, float)
        ) and exponent < 0:
            output = f"1/{render(power(base, -exponent), True)}"
            if group:
                return "(" + output + ")"
            else:
                return output
        case Power(value, Power(base, exponent)) if (
            isinstance(exponent, int) or isinstance(exponent, float)
        ) and exponent < 0:
            # Root
            root = base ** (-exponent)
            if root == 2:
                return f"sqrt({render(value)})"
            else:
                return f"root({render(value, True)}, {root})"

        case Power():
            output = (
                f"{render(expression.base, True)}^{render(expression.exponent, True)}"
            )
            if group:
                return apply_group(output, True)
            else:
                return output
        case Product():
            positive_exponents = []
            negative_exponents = []
            for factor in expression.factors:
                match factor:
                    case Power(base, exponent) if (
                        isinstance(exponent, int) or isinstance(exponent, float)
                    ) and exponent < 0:
                        negative_exponents.append(power(base, -exponent))
                    case _:
                        positive_exponents.append(factor)
            if len(negative_exponents) > 0:
                output = f"{render(product(positive_exponents), True)}/{render(product(negative_exponents), True)}"
                if group:
                    return "(" + output + ")"
                else:
                    return output
            else:
                return "".join(
                    map(lambda factor: render(factor, True), expression.factors)
                )
        case Sum():
            if len(expression.terms) > 1 and group:
                return "(" + " + ".join(map(render, expression.terms)) + ")"
            else:
                return " + ".join(map(render, expression.terms))
        case FunctionCall():
            if len(expression.subscript_arguments) == 0:
                subscript = ""
            elif len(expression.subscript_arguments) == 1:
                subscript = f"_{", ".join(map(repr, expression.subscript_arguments))}"
            else:
                subscript = (
                    f"_{{{', '.join(map(repr, expression.subscript_arguments))}}}"
                )

            if len(expression.superscript_arguments) == 0:
                superscript = ""
            elif len(expression.superscript_arguments) == 1:
                superscript = (
                    f"^{", ".join(map(repr, expression.superscript_arguments))}"
                )
            else:
                superscript = (
                    f"^{{{', '.join(map(repr, expression.superscript_arguments))}}}"
                )

            return f"{expression.function.name}{subscript}{superscript}({', '.join(map(repr, expression.functional_arguments))})"
        case Symbol():
            return expression.name
        case Equation():
            return " = ".join(map(render, expression.expressions))
        case InEquality():
            return f"{render(expression.expression1)} {expression.sign} {render(expression.expression2)}"


def render_latex(
    expression: Union[Numerical, Equation, InEquality],
    renderOptions: LaTeXRenderOptions = LaTeXRenderOptions(),
    paren_group=False,
    square_group=False,
    curly_group=False,
):
    match expression:
        case int() | float():
            if expression == math.pi:
                return "\\pi"
            return str(expression)
        case complex():
            return f"({expression.real} + {expression.imag}i)"
        case Power(base, exponent) if (
            isinstance(expression.exponent, int)
            or isinstance(expression.exponent, float)
        ) and exponent < 0 and renderOptions.negative_exponent_as_fraction:
            if renderOptions.fraction_as_inline:
                return apply_group(
                    f"1/{render_latex(power(base, -exponent), renderOptions, True)}",
                    paren_group,
                    square_group,
                    curly_group,
                )
            else:
                return apply_group(
                    f"\\frac{{1}}{{{render_latex(power(base, -exponent), renderOptions)}}}",
                    paren_group,
                    square_group,
                    curly_group,
                )
        case Power(value, Power(base, exponent)) if (
            isinstance(exponent, int) or isinstance(exponent, float)
        ) and exponent < 0:
            # Root
            root = base ** (-exponent)
            if root == 2:
                return f"\\sqrt{{{render_latex(value, renderOptions)}}}"
            else:
                return f"\\sqrt[{root}]{{{render_latex(value, renderOptions)}}}"

        case Power() if (
            isinstance(expression.exponent, int)
            or isinstance(expression.exponent, float)
            and renderOptions.compact_exponents
        ):
            return apply_group(
                f"{render_latex(expression.base, renderOptions, True)}^{render_latex(expression.exponent, renderOptions)}",
                paren_group and renderOptions.group_exponentiation,
                square_group and renderOptions.group_exponentiation,
                curly_group and renderOptions.group_exponentiation,
            )
        case Power():
            return apply_group(
                f"{render_latex(expression.base, renderOptions, True)}^{{{render_latex(expression.exponent, renderOptions)}}}",
                paren_group and renderOptions.group_exponentiation,
                square_group and renderOptions.group_exponentiation,
                curly_group and renderOptions.group_exponentiation,
            )
        case Product():
            positive_exponents = []
            negative_exponents = []
            for factor in expression.factors:
                match factor:
                    case Power(base, exponent) if (
                        isinstance(exponent, int) or isinstance(exponent, float)
                    ) and exponent < 0:
                        negative_exponents.append(power(base, -exponent))
                    case _:
                        positive_exponents.append(factor)
            if len(negative_exponents) > 0:
                if renderOptions.fraction_as_inline:
                    return apply_group(
                        f"{render_latex(product(positive_exponents), renderOptions, True)}/{render_latex(product(negative_exponents), renderOptions, True)}",
                        paren_group,
                        square_group,
                        curly_group,
                    )
                return apply_group(
                    f"\\frac{{{render_latex(product(positive_exponents), renderOptions)}}}{{{render_latex(product(negative_exponents), renderOptions)}}}",
                    paren_group,
                    square_group,
                    curly_group,
                )
            else:
                result = ""
                prev = None
                prev_rendered = None
                for i, factor in enumerate(expression.factors):
                    rendered_factor = render_latex(factor, renderOptions, True)

                    if i > 0:
                        can_use_implicit = (
                            not (
                                (
                                    rendered_factor[0].isnumeric()
                                    and (prev_rendered[-1].isnumeric())
                                )
                                or rendered_factor[0] == "-"
                            )
                        ) or renderOptions.product_separator != ""
                        if (
                            not can_use_implicit
                            and renderOptions.use_parentheses_for_literal_product
                        ) or renderOptions.always_use_product_parentheses:
                            result += "(" + rendered_factor + ")"
                        elif not can_use_implicit:
                            result += " \\cdot " + rendered_factor
                        else:
                            result += renderOptions.product_separator + rendered_factor
                    else:
                        result += rendered_factor
                    prev_rendered = rendered_factor
                    prev = factor
                return result
        case Sum():
            if len(expression.terms) > 1:
                return apply_group(
                    " + ".join(
                        map(
                            lambda term: render_latex(term, renderOptions),
                            expression.terms,
                        )
                    ),
                    paren_group,
                    square_group,
                    curly_group,
                )
            else:
                return " + ".join(
                    map(
                        lambda term: render_latex(term, renderOptions), expression.terms
                    )
                )
        case FunctionCall():
            if len(expression.subscript_arguments) == 0:
                subscript = ""
            elif len(expression.subscript_arguments) == 1:
                subscript = f"_{", ".join(map(lambda term: render_latex(term, renderOptions), expression.subscript_arguments))}"
            else:
                subscript = f"_{{{', '.join(map(lambda term: render_latex(term, renderOptions), expression.subscript_arguments))}}}"

            if len(expression.superscript_arguments) == 0:
                superscript = ""
            elif len(expression.superscript_arguments) == 1:
                superscript = f"^{", ".join(map(lambda term: render_latex(term, renderOptions), expression.superscript_arguments))}"
            else:
                superscript = f"^{{{', '.join(map(lambda term: render_latex(term, renderOptions), expression.superscript_arguments))}}}"
            arguments = ", ".join(
                map(
                    lambda term: render_latex(term, renderOptions),
                    expression.functional_arguments,
                )
            )
            if (
                len(expression.functional_arguments) == 1
                and not renderOptions.group_on_one_argument_function
            ):
                output = (
                    f"{expression.function.name}{subscript}{superscript} {arguments}"
                )
            elif renderOptions.parentheses_function_call:
                output = (
                    f"{expression.function.name}{subscript}{superscript}({arguments})"
                )
            else:
                output = (
                    f"{expression.function.name}{subscript}{superscript}{{{arguments}}}"
                )
            if renderOptions.backslash_function_call:
                output = "\\" + output
            return output
        case Symbol():
            return expression.name
        case Equation():
            return " = ".join(
                map(
                    lambda term: render_latex(term, renderOptions),
                    expression.expressions,
                )
            )
        case InEquality():
            return f"{render_latex(expression.expression1, renderOptions)} {expression.sign} {render_latex(expression.expression2, renderOptions)}"


def render_type(expression: Numerical, indent=0):
    indent_str = ""  # 2 * indent * " "
    match expression:
        case int() | float():
            result = str(expression)
        case Power():
            result = f"Power(\n{render_type(expression.base, indent + 1)},\n{render_type(expression.exponent, indent + 1)}\n{indent_str})"
        case Product():
            result = f"Product([\n{",\n".join([render_type(factor, indent + 1) for factor in expression.factors])}\n{indent_str}])"
        case Sum():
            result = f"Sum([\n{",\n".join([render_type(term, indent + 1) for term in expression.terms])}\n{indent_str}])"
        case FunctionCall():
            result = f"FunctionCall([\n{",\n".join([render_type(term, indent + 1) for term in expression.functional_arguments])}\n],\n[\n{",\n".join([render_type(term, indent + 1) for term in expression.subscript_arguments])}\n],\n[\n{",\n".join([render_type(term, indent + 1) for term in expression.superscript_arguments])}\n{indent_str}])"
        case Symbol():
            result = f'Symbol("{expression.name}")'
        case complex():
            result = f"complex({expression.real}, {expression.imag})"
        case _:
            result = "Unknown"

    return (indent_str + result).replace("\n", "")


if __name__ == "__main__":
    # expression = sum([power(2, 3), product([2, power(Symbol("x"), 2)])])
    # expression = (expression * 2) / 3
    # print(render_latex(expression))

    # expression = power(2, fraction(1, 3))
    # print(render_latex(expression))

    # 1. Simple sum and product
    expression1 = Sum([Power(-18, -1.9), 4, Product([-47, 0])])
    print(render(expression1))
    print(render_latex(expression1))
    print()
