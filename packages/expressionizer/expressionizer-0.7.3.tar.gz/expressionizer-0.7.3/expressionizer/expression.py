from __future__ import annotations

from dataclasses import dataclass
from typing import *
from collections import Counter


def numerical_sort_key(numerical: Numerical):
    if is_int_or_float(numerical):
        return (0, -numerical)  # 0 means number, -x for descending order
    else:
        return (1, str(numerical))  # 1 means non-number, sort alphabetically by str(x)


def numerical_sort_key_reverse(numerical: Numerical):
    if is_int_or_float(numerical):
        return (1, numerical)
    else:
        return (0, str(numerical))


class Symbol:
    __match_args__ = ("name",)
    name: str

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.name == other.name
        return False

    def __mul__(self, other):
        return Product([self, other])

    def __rmul__(self, other):
        return Product([other, self])

    def __truediv__(self, other):
        return Product([self, Power(other, -1)])

    def __rtruediv__(self, other):
        return Product([Power(self, -1), other])

    def __pow__(self, other):
        return Power(self, other)

    def __rpow__(self, other):
        return Power(other, self)

    def __neg__(self):
        return Product([-1, self])

    def __pos__(self):
        return self

    def __call__(self, other):
        return Product([self, other])

    def __add__(self, other):
        return Sum([self, other])

    def __radd__(self, other):
        return Sum([other, self])

    def __bool__(self):
        return True

    def __len__(self):
        return 1


class MathFunction:
    __match_args__ = (
        "name",
        "functional_parameters",
        "subscript_parameters",
        "superscript_parameters",
        "functional_min_parameters",
        "subscript_min_parameters",
        "superscript_min_parameters",
    )
    name: str
    functional_parameters: int
    subscript_parameters: int
    superscript_parameters: int
    functional_min_parameters: Optional[int]
    subscript_min_parameters: Optional[int]
    superscript_min_parameters: Optional[int]

    def __init__(
        self,
        name: str,
        functional_parameters: int = 0,
        subscript_parameters: int = 0,
        superscript_parameters: int = 0,
        functional_min_parameters: Optional[int] = None,
        subscript_min_parameters: Optional[int] = None,
        superscript_min_parameters: Optional[int] = None,
    ):
        self.name = name
        self.functional_parameters = functional_parameters
        self.subscript_parameters = subscript_parameters
        self.superscript_parameters = superscript_parameters
        self.functional_min_parameters = (
            functional_min_parameters
            if functional_min_parameters is not None
            else functional_parameters
        )
        self.subscript_min_parameters = (
            subscript_min_parameters
            if subscript_min_parameters is not None
            else subscript_parameters
        )
        self.superscript_min_parameters = (
            superscript_min_parameters
            if superscript_min_parameters is not None
            else superscript_parameters
        )

    def __eq__(self, other: "MathFunction"):
        return (
            self.name == other.name
            and self.functional_parameters == other.functional_parameters
            and self.subscript_parameters == other.subscript_parameters
            and self.superscript_parameters == other.superscript_parameters
        )

    def __call__(
        self,
        functional_arguments: List[Numerical] = [],
        subscript_arguments: List[Numerical] = [],
        superscript_arguments: List[Numerical] = [],
    ):
        # Check if the number of arguments meets the minimum requirements
        if len(functional_arguments) < self.functional_min_parameters:
            raise ValueError(
                f"Not enough functional arguments: expected at least {self.functional_min_parameters}, got {len(functional_arguments)}"
            )
        if len(subscript_arguments) < self.subscript_min_parameters:
            raise ValueError(
                f"Not enough subscript arguments: expected at least {self.subscript_min_parameters}, got {len(subscript_arguments)}"
            )
        if len(superscript_arguments) < self.superscript_min_parameters:
            raise ValueError(
                f"Not enough superscript arguments: expected at least {self.superscript_min_parameters}, got {len(superscript_arguments)}"
            )

        # Check if the number of arguments exceeds the maximum allowed
        if len(functional_arguments) > self.functional_parameters:
            raise ValueError(
                f"Too many functional arguments: expected at most {self.functional_parameters}, got {len(functional_arguments)}"
            )
        if len(subscript_arguments) > self.subscript_parameters:
            raise ValueError(
                f"Too many subscript arguments: expected at most {self.subscript_parameters}, got {len(subscript_arguments)}"
            )
        if len(superscript_arguments) > self.superscript_parameters:
            raise ValueError(
                f"Too many superscript arguments: expected at most {self.superscript_parameters}, got {len(superscript_arguments)}"
            )

        return FunctionCall(
            self, functional_arguments, subscript_arguments, superscript_arguments
        )

    def __hash__(self):
        return hash(
            (
                self.name,
                self.functional_parameters,
                self.subscript_parameters,
                self.superscript_parameters,
            )
        )

    def __bool__(self):
        return True


class Power:
    __match_args__ = ("base", "exponent")
    base: Numerical
    exponent: Numerical

    def __init__(self, base: Numerical, exponent: Numerical = 1):
        self.base = base
        self.exponent = exponent

    def __str__(self) -> str:
        return f"{self.base}^{self.exponent}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.base, self.exponent))

    def render_group(self):
        return f"{self}"

    def __eq__(self, other: Numerical) -> bool:
        factor = None
        match other:
            case Power():
                factor = other
            case Product() if len(other.factors) == 1 and isinstance(
                other.factors[0], Power
            ):
                factor = other.factors[0]
            case Sum() if len(other.terms) == 1 and isinstance(other.terms[0], Power):
                factor = other.terms[0]
            case int() | float():
                return self.base == other and self.exponent == 1
        return (
            isinstance(factor, Power)
            and factor.base == self.base
            and factor.exponent == self.exponent
        )

    def __ne__(self, other) -> bool:
        return not self == other

    def __add__(self, other: Numerical):
        return sum([self, other])

    def __radd__(self, other: Numerical):
        return self.__add__(other)

    def __sub__(self, other: Numerical):
        return self.__add__(-other)

    def __rsub__(self, other: Numerical):
        return (-self) + other

    def __mul__(self, other: Numerical):
        return product([self, other])

    def __rmul__(self, other: Numerical):
        return self.__mul__(other)

    def __truediv__(self, other: Numerical):
        return product([self, power(other, -1)])

    def __rtruediv__(self, other: Numerical):
        return product([power(self.base, -self.exponent), other])

    def __pow__(self, other: Numerical):
        return power(
            self.base,
            self.exponent * other,
        )

    def __rpow__(self, other: Numerical):
        return power(other, self)

    def __neg__(self):
        return Product([-1, Power(self.base, self.exponent)])

    def __call__(self, other: Numerical):
        return self.__mul__(other)

    def __bool__(self):
        return True

    def __len__(self):
        return (1 if is_int_or_float(self.base) else len(self.base)) + (
            1 if is_int_or_float(self.exponent) else len(self.exponent)
        )


class FunctionCall:
    __match_args__ = (
        "function",
        "functional_arguments",
        "subscript_arguments",
        "superscript_arguments",
    )
    function: MathFunction
    functional_arguments: list[Numerical]
    subscript_arguments: list[Numerical]
    superscript_arguments: list[Numerical]

    def __init__(
        self,
        function: MathFunction,
        functional_arguments: list[Numerical] = [],
        subscript_arguments: list[Numerical] = [],
        superscript_arguments: list[Numerical] = [],
    ):
        self.function = function
        self.functional_arguments = functional_arguments
        self.subscript_arguments = subscript_arguments
        self.superscript_arguments = superscript_arguments

    def __str__(self):
        if len(self.subscript_arguments) == 0:
            subscript = ""
        elif len(self.subscript_arguments) == 1:
            subscript = f"_{", ".join(map(repr, self.subscript_arguments))}"
        else:
            subscript = f"_{{{', '.join(map(repr, self.subscript_arguments))}}}"

        if len(self.superscript_arguments) == 0:
            superscript = ""
        elif len(self.superscript_arguments) == 1:
            superscript = f"^{", ".join(map(repr, self.superscript_arguments))}"
        else:
            superscript = f"^{{{', '.join(map(repr, self.superscript_arguments))}}}"

        return f"{self.function.name}{subscript}{superscript}({', '.join(map(repr, self.functional_arguments))})"

    def __repr__(self):
        return str(self)

    def render_group(self):
        return f"{self}"

    def __hash__(self):
        return hash(
            (
                self.function,
                tuple(self.functional_arguments),
                tuple(self.subscript_arguments),
                tuple(self.superscript_arguments),
            )
        )

    def __bool__(self):
        return True

    def __eq__(self, other: Numerical):
        if (
            isinstance(other, FunctionCall)
            and self.function == other.function
            and len(self.functional_arguments) == len(other.functional_arguments)
            and len(self.subscript_arguments) == len(other.subscript_arguments)
            and len(self.superscript_arguments) == len(other.superscript_arguments)
        ):
            for i in range(len(self.functional_arguments)):
                if self.functional_arguments[i] != other.functional_arguments[i]:
                    return False
            for i in range(len(self.subscript_arguments)):
                if self.subscript_arguments[i] != other.subscript_arguments[i]:
                    return False
            for i in range(len(self.superscript_arguments)):
                if self.superscript_arguments[i] != other.superscript_arguments[i]:
                    return False
            return True
        return False

    def __neg__(self):
        return Product([self, -1])

    def __len__(self):
        total = 0
        for arg in (
            self.functional_arguments
            + self.subscript_arguments
            + self.superscript_arguments
        ):
            total += 1 if is_int_or_float(arg) else len(arg)
        return total


class Product:
    __match_args__ = ("factors",)
    factors: list[Numerical]

    def __init__(self, factors: list[Numerical]):
        self.factors = factors

    def __str__(self):
        return "".join(map(repr, self.factors))

    def __repr__(self):
        return str(self)

    def render_group(self):
        return f"{self}"

    def __hash__(self):
        factors = sorted(self.factors, key=numerical_sort_key)
        return hash(tuple(factors))

    def __mul__(self, other: Numerical):
        return product([other] + self.factors)

    def __rmul__(self, other: Numerical):
        return self.__mul__(other)

    def __truediv__(self, other: Numerical):
        return product(self.factors + [power(other, -1)])

    def __rtruediv__(self, other: Numerical):
        return product([power(self, -1)] + [other])

    def __pow__(self, other: Numerical):
        return power(self, other)

    def __rpow__(self, other: Numerical):
        return power(other, self)

    def __neg__(self):
        return product([-1] + self.factors)

    def __pos__(self):
        return self

    def __call__(self, other: Numerical):
        return self.__mul__(other)

    def __eq__(self, other: Numerical):
        if isinstance(other, Product):
            self_factors, other_factors = [], []
            for factor in self.factors:
                if isinstance(factor, Power) and (
                    factor.exponent == 0 or factor.base == 1
                ):
                    pass
                elif factor == 1:
                    pass
                else:
                    self_factors.append(factor)
            for factor in other.factors:
                if isinstance(factor, Power) and (
                    factor.exponent == 0 or factor.base == 1
                ):
                    pass
                elif factor == 1:
                    pass
                else:
                    other_factors.append(factor)
            if len(self_factors) != len(other_factors):
                return False
            for i in range(len(self_factors)):
                if self_factors[i] != other_factors[i]:
                    return False
            return True
        elif (
            len(self.factors) == 1
            and is_int_or_float(other)
            and self.factors[0] == other
        ):
            return True
        return False

    def __ne__(self, other: Numerical):
        return not self == other

    def __add__(self, other: Numerical):
        return sum([self, other])

    def __radd__(self, other: Numerical):
        return self.__add__(other)

    def __sub__(self, other: Numerical):
        return self.__add__(-other)

    def __rsub__(self, other: Numerical):
        return (-self) + other

    def __contains__(self, other: Numerical):
        if isinstance(other, Product) and len(other.factors) > 0:
            other_factors = []
            for factor in other.factors:
                if isinstance(factor, Product):
                    other_factors.extend(
                        [
                            (abs(factor) if is_int_or_float(factor) else factor)
                            for factor in factor.factors
                        ]
                    )
                elif isinstance(factor, Sum) and len(factor.terms) <= 1:
                    other_factors.extend(
                        [
                            (abs(term) if is_int_or_float(term) else term)
                            for term in factor.terms
                        ]
                    )
                elif is_int_or_float(factor):
                    other_factors.append(abs(factor))
                else:
                    other_factors.append(factor)
            self_factors = []
            for factor in self.factors:
                if isinstance(factor, Product):
                    self_factors.extend(
                        [
                            (abs(factor) if is_int_or_float(factor) else factor)
                            for factor in factor.factors
                        ]
                    )
                elif isinstance(factor, Sum) and len(factor.terms) <= 1:
                    self_factors.extend(
                        [
                            (abs(term) if is_int_or_float(term) else term)
                            for term in factor.terms
                        ]
                    )
                elif is_int_or_float(factor):
                    self_factors.append(abs(factor))
                else:
                    self_factors.append(factor)
            # Determine if other is a subset of self
            c1, c2 = Counter(other_factors), Counter(self_factors)
            return all(c1[x] <= c2[x] for x in c1)
        return False  # other in self.factors

    def __bool__(self):
        return True

    def __neg__(self):
        return Product(self.factors.copy() + [-1])

    def __len__(self):
        total = 0
        for factor in self.factors:
            total += 1 if is_int_or_float(factor) else len(factor)
        return total


class Sum:
    __match_args__ = ("terms",)
    terms: list[Numerical]

    def __init__(self, terms: list[Numerical]):
        self.terms = terms

    def __str__(self):
        return " + ".join(map(repr, self.terms))

    def __repr__(self):
        return str(self)

    def render_group(self):
        return f"({self})"

    def __hash__(self):
        terms = sorted(self.terms, key=numerical_sort_key)
        return hash(tuple(terms))

    def __mul__(self, other: Numerical):
        return product([self, other])

    def __rmul__(self, other: Numerical):
        return self.__mul__(other)

    def __truediv__(self, other: Numerical):
        return product([self, power(other, -1)])

    def __rtruediv__(self, other: Numerical):
        return product([power(self, -1), other])

    def __pow__(self, other: Numerical):
        return power(self, other)

    def __rpow__(self, other: Numerical):
        return power(other, self)

    def __neg__(self):
        return product([-1, self])

    def __pos__(self):
        return self

    def __call__(self, other: Numerical):
        return self.__mul__(other)

    def __eq__(self, other: Numerical):
        if isinstance(other, Sum):
            if len(self.terms) != len(other.terms):
                return False
            for i in range(len(self.terms)):
                if self.terms[i] != other.terms[i]:
                    return False
            return True
        elif len(self.terms) == 1 and is_int_or_float(other) and self.terms[0] == other:
            return True
        return False

    def __ne__(self, other: Numerical):
        return not self == other

    def __add__(self, other: Numerical):
        return sum([other] + self.terms)

    def __radd__(self, other: Numerical):
        return self.__add__(other)

    def __sub__(self, other: Numerical):
        return self.__add__(-other)

    def __rsub__(self, other: Numerical):
        return (-self) + other

    def __contains__(self, other: Numerical):

        if isinstance(other, Sum) and len(other.terms) > 0:
            # Determine if other is a subset of self
            other_terms = []
            for term in other.terms:
                if isinstance(term, Sum):
                    other_terms.extend(term.terms)
                elif isinstance(term, Product) and len(term.factors) <= 1:
                    other_terms.extend(term.factors)
                elif (
                    isinstance(term, Product)
                    and len(term.factors) == 2
                    and -1 in term.factors
                ):
                    other_terms.append(term.factors[0] * term.factors[1])
                else:
                    other_terms.append(term)
            self_terms = []
            for term in self.terms:
                if isinstance(term, Sum):
                    self_terms.extend(term.terms)
                elif isinstance(term, Product) and len(term.factors) <= 1:
                    self_terms.extend(term.factors)
                elif (
                    isinstance(term, Product)
                    and len(term.factors) == 2
                    and -1 in term.factors
                ):
                    self_terms.append(term.factors[0] * term.factors[1])
                else:
                    self_terms.append(term)
            c1, c2 = Counter(other_terms), Counter(self_terms)
            return all(c1[x] <= c2[x] for x in c1)
        return False  # other in self.terms

    def __bool__(self):
        return True

    def __len__(self):
        total = 0
        for term in self.terms:
            total += 1 if is_int_or_float(term) else len(term)
        return total


Numerical = int | float | Power | Product | Sum | FunctionCall | Symbol


class Equation:
    __match_args__ = "expressions"

    def __init__(self, expressions: List[Numerical]):
        self.expressions = expressions

    def __str__(self) -> str:
        return " = ".join(map(repr, self.expressions))

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash(tuple(self.expressions))

    def __bool__(self):
        return True


class InEquality:
    __match_args__ = ("expression1", "expression2", "sign", "inclusive")

    def __init__(
        expression1: Numerical,
        expression2: Numerical,
        sign: Union[Literal[-1], Literal[1]] = 1,
        inclusive: bool = False,
    ):
        self.expression1 = expression1
        self.expression2 = expression2
        self.sign = sign
        self.inclusive = inclusive

    def __str__(self) -> str:
        operator = ">" if self.sign > 0 else "<"
        if self.inclusive:
            operator += "="
        return str(self.expression1) + f" {operator} " + str(self.expression2)

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash((self.expression1, self.expression2, self.sign, self.inclusive))

    def __bool__(self):
        return True


def symbol(name: str):
    return Symbol(name)


def power(base: Numerical, exponent: Numerical = 1):
    if exponent == 0:
        return 1
    elif exponent == 1:
        return base
    elif isinstance(base, Power):
        return Power(base.base, base.exponent * exponent)
    else:
        return Power(base, exponent)


def product(factors: list[Numerical]):
    expanded_factors = []
    coefficient = 1
    for factor in factors:
        match factor:
            case int() | float():
                coefficient *= factor
                if coefficient == 0:
                    return 0
            case Product():
                expanded_factors.extend(factor.factors)
            case _:
                expanded_factors.append(factor)

    powers = {}
    sums = {}
    function_calls = {}
    for factor in expanded_factors:
        match factor:
            case Symbol():
                if factor in powers:
                    powers[factor] += 1
                else:
                    powers[factor] = 1
            case Power():
                if factor.base in powers:
                    powers[factor.base] += factor.exponent
                else:
                    powers[factor.base] = factor.exponent
            case Sum():
                if factor in sums:
                    sums[factor] += 1
                else:
                    sums[factor] = 1
            case FunctionCall():
                if factor in function_calls:
                    function_calls[factor] += 1
                else:
                    function_calls[factor] = 1

    if len(powers) + len(sums) + len(function_calls) == 0:
        return coefficient
    new_factors = [coefficient] if coefficient != 1 else []
    for base, exponent in powers.items():
        new_factors.append(power(base, exponent))
    for sum, count in sums.items():
        new_factors.append(power(sum, count))
    for function_call, count in function_calls.items():
        new_factors.append(power(function_call, count))
    if len(new_factors) == 1:
        return new_factors[0]
    return Product(new_factors)


def sum(terms: list[Numerical] | Sum):
    # Just combine like terms
    if isinstance(terms, Sum):
        terms = terms.terms
    expanded_terms = []
    numerical = 0
    for term in terms:
        match term:
            case int() | float():
                numerical += term
            case Sum():
                expanded_terms.extend(term.terms)
            case _:
                expanded_terms.append(term)

    if len(expanded_terms) == 0:
        return numerical

    terms_count = {}
    for term in expanded_terms:
        if term in terms_count:
            terms_count[term] += 1
        else:
            terms_count[term] = 1

    new_terms = [numerical] if numerical != 0 else []
    for term, count in terms_count.items():
        if count == 1:
            new_terms.append(term)
        else:
            new_terms.append(product(term, count))

    return Sum(new_terms)


def fraction(numerator: Numerical, denominator: Numerical):
    return product([numerator, power(denominator, -1)])


def is_int_or_float(value):
    return isinstance(value, int) or isinstance(value, float)
