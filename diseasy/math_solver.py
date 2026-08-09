"""
diseasy/math_solver.py (v0.3.1)

Built-in math solver — algebra (linear/quadratic/polynomial
equations), simplification, expansion, factoring, evaluation, and
basic calculus (derivatives, definite/indefinite integrals). Not
intended for olympiad-level problems (number theory proofs,
combinatorics, etc.) — this covers what a typical Discord bot "solve
this for me" command needs.

Built on sympy, with input parsing locked down against arbitrary code
execution — since this will typically process raw text a Discord
user types into a command, the parser only allows math syntax, not
arbitrary Python.

Usage:
    from diseasy.math_solver import solve_equation, simplify_expr, evaluate

    solve_equation("2*x + 3 = 7", "x")       # -> [2]
    simplify_expr("(x + 1)**2 - x**2")       # -> "2*x + 1"
    evaluate("2 + 3 * 4")                    # -> 14
"""

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

# Only these transformations are allowed — no code execution,
# no arbitrary function calls beyond sympy's own safe math functions.
_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# Restricting the parser's available names prevents someone from
# passing something like "__import__('os').system('...')" and having
# it evaluate as a "symbol" — only real math symbols/functions here.
_SAFE_LOCALS = {
    "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
    "sqrt": sympy.sqrt, "log": sympy.log, "exp": sympy.exp,
    "pi": sympy.pi, "E": sympy.E, "Abs": sympy.Abs,
}


class MathError(Exception):
    """Raised when an expression can't be parsed or solved."""


# sympy's own recommended safe-eval pattern: populate the global
# namespace with sympy's functions (needed internally by the parser's
# transformations — Symbol, Integer, etc.), but explicitly strip
# __builtins__ so eval() has no access to __import__, open, exec, or
# anything else outside real math.
_SAFE_GLOBALS = {}
exec("from sympy import *", _SAFE_GLOBALS)
_SAFE_GLOBALS["__builtins__"] = {}


def _safe_parse(text: str):
    try:
        return parse_expr(text, local_dict=_SAFE_LOCALS,
                           transformations=_TRANSFORMATIONS,
                           global_dict=_SAFE_GLOBALS)
    except Exception as e:
        raise MathError(f"Couldn't parse '{text}': {e}") from e


def solve_equation(equation: str, variable: str = "x"):
    """
    Solves an equation for the given variable.
    "2*x + 3 = 7" -> [2]
    "x**2 - 4 = 0" -> [-2, 2]
    """
    if "=" not in equation:
        raise MathError("An equation needs an '=' sign, e.g. '2*x + 3 = 7'")

    left_str, right_str = equation.split("=", 1)
    left = _safe_parse(left_str)
    right = _safe_parse(right_str)
    sym = sympy.Symbol(variable)

    try:
        solutions = sympy.solve(sympy.Eq(left, right), sym)
    except Exception as e:
        raise MathError(f"Couldn't solve equation: {e}") from e

    return solutions


def simplify_expr(expression: str) -> str:
    """Simplifies an algebraic expression. Returns the result as a string."""
    expr = _safe_parse(expression)
    return str(sympy.simplify(expr))


def expand_expr(expression: str) -> str:
    """Expands an algebraic expression. e.g. '(x+1)**2' -> 'x**2 + 2*x + 1'"""
    expr = _safe_parse(expression)
    return str(sympy.expand(expr))


def factor_expr(expression: str) -> str:
    """Factors a polynomial expression. e.g. 'x**2 - 4' -> '(x - 2)*(x + 2)'"""
    expr = _safe_parse(expression)
    return str(sympy.factor(expr))


def evaluate(expression: str):
    """
    Evaluates a numeric expression to a number.
    "2 + 3 * 4" -> 14
    "sqrt(16)" -> 4
    """
    expr = _safe_parse(expression)
    try:
        return float(expr.evalf()) if expr.free_symbols == set() else str(expr)
    except Exception as e:
        raise MathError(f"Couldn't evaluate: {e}") from e


def derivative(expression: str, variable: str = "x") -> str:
    """Derivative of an expression with respect to a variable."""
    expr = _safe_parse(expression)
    sym = sympy.Symbol(variable)
    return str(sympy.diff(expr, sym))


def integral(expression: str, variable: str = "x",
             lower_bound=None, upper_bound=None) -> str:
    """
    Integral of an expression. If lower_bound/upper_bound are given,
    computes a definite integral; otherwise indefinite.
    """
    expr = _safe_parse(expression)
    sym = sympy.Symbol(variable)

    if lower_bound is not None and upper_bound is not None:
        lower = _safe_parse(str(lower_bound))
        upper = _safe_parse(str(upper_bound))
        result = sympy.integrate(expr, (sym, lower, upper))
    else:
        result = sympy.integrate(expr, sym)

    return str(result)
