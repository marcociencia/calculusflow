"""Shared math helpers: expression parsing and LaTeX conversion."""
import sympy as sp

X, Y, Z = sp.symbols('x y z')
_VAR_MAP = {'x': X, 'y': Y, 'z': Z}

_LOCALS = {
    'x': X, 'y': Y, 'z': Z,
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
    'log': sp.log, 'ln': sp.log, 'exp': sp.exp,
    'sqrt': sp.sqrt, 'abs': sp.Abs,
    'pi': sp.pi, 'e': sp.E, 'oo': sp.oo,
}


def get_var(name):
    if name not in _VAR_MAP:
        raise ValueError(f"Variável '{name}' não suportada. Use x, y ou z.")
    return _VAR_MAP[name]


def parse_expr(s, var_name='x'):
    if s is None or str(s).strip() == '':
        raise ValueError("Expressão vazia.")
    expr_str = str(s).strip().replace('^', '**')
    try:
        return sp.sympify(expr_str, locals=_LOCALS)
    except Exception as ex:
        raise ValueError(f"Não foi possível interpretar '{s}': {ex}")


def parse_equation(s):
    if '=' not in str(s):
        raise ValueError("A equação precisa conter '='.")
    lhs, rhs = str(s).split('=', 1)
    return parse_expr(lhs) - parse_expr(rhs)


def for_plot(expr, var):
    """Converte uma expressão para função de x (para plotagem)."""
    return expr.subs(var, X) if var != X else expr


def num(v):
    """Tenta converter em float; devolve None se não for numérico."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
