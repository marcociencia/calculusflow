"""
CalculusFlow — Streamlit version (single self-contained file)
==============================================================
Step-by-step math app (arithmetic, calculus, and algebra).
Symbolic computation with SymPy — no API key, free to run on Streamlit Cloud.

How to run locally:
    pip install streamlit sympy matplotlib numpy
    streamlit run app.py

How to publish on Streamlit Community Cloud:
    1. Push this file (app.py) to a GitHub repository.
    2. Create a requirements.txt file in the root with:
            streamlit>=1.30
            sympy>=1.12
            matplotlib>=3.7
            numpy>=1.24
    3. On https://streamlit.io/cloud -> New app -> Main file path: app.py -> Deploy.

IMPORTANT: If you see "ModuleNotFoundError: No module named 'matplotlib'",
make sure requirements.txt is at the repository root (next to app.py)
and lists matplotlib. Then reboot the app on Streamlit Cloud.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import lambdify


# =============================================================================
#  CORE — parsing and helpers
# =============================================================================
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
        raise ValueError(f"Variable '{name}' is not supported. Use x, y, or z.")
    return _VAR_MAP[name]


def parse_expr(s, var_name='x'):
    if s is None or str(s).strip() == '':
        raise ValueError("Empty expression.")
    expr_str = str(s).strip().replace('^', '**')
    try:
        return sp.sympify(expr_str, locals=_LOCALS)
    except Exception as ex:
        raise ValueError(f"Could not interpret '{s}': {ex}")


def parse_equation(s):
    if '=' not in str(s):
        raise ValueError("The equation must contain '='.")
    lhs, rhs = str(s).split('=', 1)
    return parse_expr(lhs) - parse_expr(rhs)


def for_plot(expr, var):
    return expr.subs(var, X) if var != X else expr


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def plot_functions(exprs, x_min, x_max, points=None, shade=None, title=None):
    if not HAS_MPL:
        st.info(" matplotlib não está instalado no ambiente — o gráfico foi oculto. "
                "Adicione `matplotlib>=3.7` ao requirements.txt para habilitá-lo.")
        return None
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    xs = np.linspace(float(x_min), float(x_max), 400)
    for e in exprs:
        f = lambdify(X, e['expr'], modules=['numpy'])
        try:
            ys = f(xs)
            ys = np.array(ys, dtype=float)
            finite = np.isfinite(ys)
            ax.plot(xs[finite], ys[finite], label=e.get('label', ''),
                    linestyle='--' if e.get('dashed') else '-', color=e.get('color'))
        except Exception:
            pass
    if shade:
        f = lambdify(X, shade['expr'], modules=['numpy'])
        ys = np.array(f(xs), dtype=float)
        mask = (xs >= float(shade['from'])) & (xs <= float(shade['to']))
        ax.fill_between(xs, ys, 0, where=mask, alpha=0.25, color='C0')
    if points:
        for p in points:
            ax.plot(float(p['x']), float(p['y']), 'o', color=p.get('color', 'red'))
            ax.annotate(p.get('label', ''), (float(p['x']), float(p['y'])),
                        textcoords='offset points', xytext=(6, 6), fontsize=8)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.set_xlim(float(x_min), float(x_max))
    if title:
        ax.set_title(title)
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def _show(steps, final, plot=None):
    for title, detail in steps:
        st.markdown(f"**{title}**")
        st.markdown(detail)
    st.markdown("**Final answer**")
    if final.startswith('$$'):
        st.markdown(final)
    else:
        st.latex(final)
    if plot:
        fig = plot_functions(**plot)
        if fig is not None:
            st.pyplot(fig)


# =============================================================================
#  ARITHMETIC
# =============================================================================
def _cell(v, extra=''):
    content = '' if v is None else str(v)
    return (f'<span style="display:inline-flex;width:1.4em;height:2.2em;'
            f'justify-content:center;align-items:center;'
            f'font-family:ui-monospace,monospace;font-size:1.8em;font-weight:600;{extra}">'
            f'{content}</span>')


def _gap(extra=''):
    return f'<span style="display:inline-flex;width:1.4em;height:2.2em;{extra}"></span>'


def _line(em):
    return f'<div style="height:2px;background:#111;width:{em}em;margin:3px 0;"></div>'


def _strike_cell(v, color=''):
    return (f'<span style="position:relative;display:inline-flex;width:1.4em;height:2.2em;'
            f'justify-content:center;align-items:center;font-family:monospace;'
            f'font-size:1.8em;font-weight:600;{color}">'
            f'<span style="position:absolute;width:1.8em;height:2px;background:#111;'
            f'transform:rotate(-22deg);"></span>{v}</span>')


def add_armada(A, B):
    A, B = abs(int(A)), abs(int(B))
    a_str, b_str = str(A), str(B)
    maxlen = max(len(a_str), len(b_str))
    W = maxlen + 1
    top = [None] * W
    bottom = [None] * W
    carry = [None] * W
    result = [None] * W
    for p in range(len(a_str)):
        top[W - 1 - p] = int(a_str[-1 - p])
    for p in range(len(b_str)):
        bottom[W - 1 - p] = int(b_str[-1 - p])
    c = 0
    cols = []
    for p in range(maxlen):
        g = W - 1 - p
        carry[g] = c
        t = top[g] or 0
        b = bottom[g] or 0
        s = t + b + c
        result[g] = s % 10
        c = s // 10
        cols.insert(0, {'top': t, 'bottom': b, 'carryIn': carry[g], 'sum': s, 'digit': result[g]})
    if c > 0:
        result[W - 1 - maxlen] = c
    return {'A': A, 'B': B, 'W': W, 'top': top, 'bottom': bottom,
            'carry': carry, 'result': result, 'cols': cols, 'total': A + B}


def render_addition():
    st.subheader("Addition with carrying")
    A = int(st.number_input("Top number", value=6789, step=1, key="add_A"))
    B = int(st.number_input("Bottom number", value=4567, step=1, key="add_B"))
    if st.button("Show example", key="add_ex"):
        st.session_state.add_A, st.session_state.add_B = 6789, 4567
        st.rerun()
    d = add_armada(A, B)
    rows = []
    rows.append('<div>' + _gap() + ''.join(
        _cell(c if c and c > 0 else None, 'color:#6b21a8;font-size:1em;height:1.3em;')
        for c in d['carry']) + '</div>')
    rows.append('<div>' + _gap() + ''.join(_cell(c) for c in d['top']) + '</div>')
    rows.append('<div>' + _cell('+') + ''.join(_cell(c) for c in d['bottom']) + '</div>')
    rows.append(_line(d['W'] * 1.4))
    rows.append('<div>' + _gap() + ''.join(_cell(c, 'color:#dc2626;') for c in d['result']) + '</div>')
    st.markdown(
        f'<div style="display:inline-block;padding:1rem;">{"".join(rows)}</div>'
        f'<div style="margin-top:.5rem;font-size:1.4em;font-weight:600">'
        f'{d["A"]} + {d["B"]} = <span style="color:#dc2626">{d["total"]}</span></div>',
        unsafe_allow_html=True)
    st.markdown("**Step by step — each column**")
    lines = []
    for c in reversed(d['cols']):
        carry_txt = f"(carry {c['carryIn']}) " if c['carryIn'] > 0 else ''
        extra = f" + {c['carryIn']}" if c['carryIn'] > 0 else ''
        note = ", carry 1" if c['sum'] >= 10 else ''
        lines.append(f"{carry_txt}{c['top']} + {c['bottom']}{extra} = {c['sum']} → write **{c['digit']}**{note}")
    lines.append(f"**Final sum: {d['A']} + {d['B']} = {d['total']}**")
    st.markdown('\n'.join('- ' + l for l in lines))


def subtract_armada(A, B):
    A, B = int(A), int(B)
    negative = A < B
    larger, smaller = max(A, B), min(A, B)
    top_str = str(larger)
    bottom_str = str(smaller).rjust(len(top_str), '0')
    top_arr = list(map(int, top_str))
    bottom_arr = list(map(int, bottom_str))
    working = top_arr[:]
    lent_by = {}
    columns = []
    for i in range(len(top_str) - 1, -1, -1):
        t = working[i]
        b = bottom_arr[i]
        borrowed = None
        if t < b:
            j = i - 1
            while j >= 0 and working[j] == 0:
                j -= 1
            if j >= 0:
                old = working[j]
                working[j] -= 1
                for k in range(j + 1, i):
                    working[k] = 9
                t = working[i] + 10
                borrowed = j
                lent_by[j] = {'newValue': working[j], 'oldValue': old}
        columns.insert(0, {'index': i, 'originalTop': top_arr[i],
                           'displayedTop': t, 'bottom': b, 'result': t - b,
                           'borrowedFrom': borrowed})
    magnitude = int(''.join(str(c['result']) for c in columns))
    result = -magnitude if negative else magnitude
    return {'A': A, 'B': B, 'top_arr': top_arr, 'bottom_arr': bottom_arr,
            'columns': columns, 'lent_by': lent_by, 'negative': negative,
            'larger': larger, 'smaller': smaller, 'result': result}


def render_subtraction():
    st.subheader("Subtraction with borrowing")
    A = int(st.number_input("Top number", value=5003, step=1, key="sub_A"))
    B = int(st.number_input("Bottom number", value=2897, step=1, key="sub_B"))
    if st.button("Show example", key="sub_ex"):
        st.session_state.sub_A, st.session_state.sub_B = 5003, 2897
        st.rerun()
    d = subtract_armada(A, B)
    w = len(d['top_arr'])
    rows = []
    row = _gap()
    for c in d['columns']:
        mark = None
        if c['index'] in d['lent_by']:
            mark = (d['lent_by'][c['index']]['newValue'], 'color:#2563eb')
        elif c['borrowedFrom'] is not None:
            mark = (c['displayedTop'], 'color:#dc2626')
        if mark:
            row += (f'<span style="display:inline-flex;width:1.4em;height:1.3em;'
                    f'justify-content:center;align-items:center;font-size:1em;{mark[1]}">{mark[0]}</span>')
        else:
            row += _gap('height:1.3em;')
    rows.append('<div>' + row + '</div>')
    row = _gap()
    for i, v in enumerate(d['top_arr']):
        struck = i in d['lent_by'] or any(c['index'] == i and c['borrowedFrom'] is not None for c in d['columns'])
        row += _strike_cell(v) if struck else _cell(v)
    rows.append('<div>' + row + '</div>')
    rows.append('<div>' + _cell('−') + ''.join(_cell(c) for c in d['bottom_arr']) + '</div>')
    rows.append(_line(w * 1.4))
    rows.append('<div>' + _gap() + ''.join(_cell(abs(c['result'])) for c in d['columns'])
                + (_cell('−', 'color:#dc2626') if d['negative'] else '') + '</div>')
    st.markdown(
        f'<div style="display:inline-block;padding:1rem;">{"".join(rows)}</div>'
        f'<div style="margin-top:.5rem;font-size:1.4em;font-weight:600">'
        f'{d["A"]} − {d["B"]} = <span style="color:#dc2626">{d["result"]}</span></div>',
        unsafe_allow_html=True)
    st.markdown("**Step by step — each column**")
    lines = []
    for c in d['columns']:
        if c['borrowedFrom'] is not None:
            lines.append(f"Borrow 1 from column {c['borrowedFrom'] + 1}: {c['originalTop']} → {c['displayedTop']}, then {c['displayedTop']} − {c['bottom']} = **{c['result']}**")
        else:
            lines.append(f"Column {c['index'] + 1}: {c['originalTop']} − {c['bottom']} = **{c['result']}**")
    st.markdown('\n'.join('- ' + l for l in lines))


def multiply_armada(A, B):
    A, B = abs(int(A)), abs(int(B))
    top_str, bottom_str = str(A), str(B)
    top_arr = list(map(int, top_str))
    bottom_arr = list(map(int, bottom_str))
    top_len = len(top_arr)
    W = top_len + len(bottom_arr)
    top_cells = [None] * W
    bottom_cells = [None] * W
    for p in range(top_len):
        top_cells[W - 1 - p] = top_arr[-1 - p]
    for p in range(len(bottom_arr)):
        bottom_cells[W - 1 - p] = bottom_arr[-1 - p]
    partials = []
    shift = 0
    for i in range(len(bottom_arr) - 1, -1, -1):
        d = bottom_arr[i]
        cells = [None] * W
        carry_cells = [None] * W
        carry = 0
        last_g = 0
        for j in range(top_len - 1, -1, -1):
            g = (W - top_len + j) - shift
            last_g = g
            prod = top_arr[j] * d + carry
            cells[g] = prod % 10
            carry = prod // 10
            if j > 0:
                carry_cells[g - 1] = carry
        if carry > 0:
            cells[last_g - 1] = carry
        partials.append({'shift': shift, 'digit': d, 'cells': cells, 'carry_cells': carry_cells})
        shift += 1
    sum_str = str(A * B)
    sum_cells = [None] * W
    for p in range(len(sum_str)):
        sum_cells[W - 1 - p] = int(sum_str[-1 - p])
    return {'A': A, 'B': B, 'W': W, 'top_cells': top_cells,
            'bottom_cells': bottom_cells, 'partials': partials,
            'sum_cells': sum_cells, 'product': A * B}


def render_multiplication():
    st.subheader("Long multiplication")
    A = int(st.number_input("Multiplicand (top)", value=234, step=1, key="mul_A"))
    B = int(st.number_input("Multiplier (bottom)", value=56, step=1, key="mul_B"))
    if st.button("Show example", key="mul_ex"):
        st.session_state.mul_A, st.session_state.mul_B = 234, 56
        st.rerun()
    d = multiply_armada(A, B)
    rows = []
    rows.append('<div>' + _gap() + ''.join(_cell(c) for c in d['top_cells']) + '</div>')
    rows.append('<div>' + _cell('×') + ''.join(_cell(c) for c in d['bottom_cells']) + '</div>')
    rows.append(_line(d['W'] * 1.4))
    for idx, p in enumerate(d['partials']):
        is_last = idx == len(d['partials']) - 1
        rows.append('<div>' + _gap() + ''.join(
            _cell(c if c is not None and c > 0 else None, 'color:#6b21a8;font-size:1em;height:1.3em;')
            for c in p['carry_cells']) + '</div>')
        row = _cell('+' if is_last else '')
        for i, c in enumerate(p['cells']):
            color = 'color:#2563eb' if (c is not None and i < len(p['carry_cells']) and p['carry_cells'][i]) else ''
            row += _cell(c, color)
        rows.append('<div>' + row + '</div>')
    rows.append(_line(d['W'] * 1.4))
    rows.append('<div>' + _gap() + ''.join(_cell(c, 'font-weight:800;') for c in d['sum_cells']) + '</div>')
    st.markdown(
        f'<div style="display:inline-block;padding:1rem;">{"".join(rows)}</div>'
        f'<div style="margin-top:.5rem;font-size:1.4em;font-weight:600">'
        f'{d["A"]} × {d["B"]} = <span style="color:#dc2626">{d["product"]}</span></div>',
        unsafe_allow_html=True)
    st.markdown("**Step by step**")
    lines = []
    for p in d['partials']:
        lines.append(f"{d['A']} × {p['digit']} = {d['A'] * p['digit']} (partial product, shifted {p['shift']} place(s))")
    lines.append(f"**Sum of partials = {d['A']} × {d['B']} = {d['product']}**")
    st.markdown('\n'.join('- ' + l for l in lines))


def long_divide(dividend, divisor):
    dividend, divisor = int(dividend), int(divisor)
    if divisor == 0:
        return {'error': 'Division by zero is undefined.'}
    neg = (dividend < 0) ^ (divisor < 0)
    dividend, divisor = abs(dividend), abs(divisor)
    digits = list(map(int, str(dividend)))
    N = len(digits)
    quotient_digits = []
    steps = []
    cur = 0
    working_start = 0
    for i in range(len(digits)):
        cur = cur * 10 + digits[i]
        qd = cur // divisor
        if not steps and qd == 0:
            continue
        product = qd * divisor
        rem = cur - product
        steps.append({'working': cur, 'qDigit': qd, 'product': product,
                      'remainder': rem, 'endCol': i, 'startCol': working_start})
        quotient_digits.append(qd)
        cur = rem
        working_start = i
    last_nonzero = max((i for i, s in enumerate(steps) if s['product'] > 0), default=-1)
    for i, s in enumerate(steps):
        s['moreWork'] = i < last_nonzero
        s['bringDown'] = digits[s['endCol'] + 1] if s['moreWork'] and s['endCol'] + 1 < N else None
    quotient_str = ''.join(map(str, quotient_digits)) or '0'
    quotient = (-1 if neg else 1) * int(quotient_str)
    remainder = cur
    return {'dividend': dividend, 'divisor': divisor, 'quotient': quotient,
            'remainder': remainder, 'quotient_str': quotient_str, 'steps': steps, 'neg': neg}


def render_long_division():
    st.subheader("Long division")
    dividend = int(st.number_input("Dividend", value=4356, step=1, key="div_A"))
    divisor = int(st.number_input("Divisor", value=12, step=1, key="div_B"))
    if st.button("Show example", key="div_ex"):
        st.session_state.div_A, st.session_state.div_B = 4356, 12
        st.rerun()
    d = long_divide(dividend, divisor)
    if 'error' in d:
        st.error(d['error'])
        return
    st.markdown(
        f'<div style="font-family:ui-monospace,monospace;font-size:1.7em;padding:1rem;">'
        f'<div style="margin-bottom:2px;color:#dc2626;font-weight:600;">'
        f'{"&nbsp;"*(len(str(d["divisor"]))+2)}{d["quotient_str"]}</div>'
        f'<div style="border-top:2px solid #111;border-left:2px solid #111;'
        f'padding-left:.3em;padding-top:2px;display:inline-block;">'
        f'{d["divisor"]})&nbsp;{d["dividend"]}</div></div>'
        f'<div style="margin-top:.4rem;font-size:1.4em;font-weight:600">'
        f'{d["dividend"]} ÷ {d["divisor"]} = <span style="color:#dc2626">{d["quotient"]}</span>'
        f'{" (remainder " + str(d["remainder"]) + ")" if d["remainder"] else ""}</div>',
        unsafe_allow_html=True)
    st.markdown("**Step by step**")
    lines = []
    for s in d['steps']:
        line = f"{s['working']} ÷ {d['divisor']} = {s['qDigit']} → {s['qDigit']} × {d['divisor']} = {s['product']}; {s['working']} − {s['product']} = **{s['remainder']}**"
        if s['bringDown'] is not None:
            line += f"; bring down {s['bringDown']} → {s['remainder'] * 10 + s['bringDown']}"
        lines.append(line)
    lines.append(f"**Quotient: {d['quotient']}**"
                 + (f", remainder {d['remainder']}" if d['remainder'] else " (exact division)"))
    st.markdown('\n'.join('- ' + l for l in lines))


# =============================================================================
#  CALCULUS
# =============================================================================
def solve_limit(expr_str, point):
    f = parse_expr(expr_str)
    x = X
    p = sp.nsimplify(point)
    lim = sp.limit(f, x, p)
    sub = f.subs(x, p)
    steps = [("Statement", f"$$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)}$$")]
    steps.append(("Direct substitution", f"$$f({sp.latex(p)}) = {sp.latex(sp.simplify(sub))}$$"))
    if sub == sp.zoo or sub.has(sp.nan) or (getattr(sub, 'is_infinite', None) and sub.is_infinite):
        steps.append(("Indeterminate form", "Direct substitution yields an infinite/indeterminate form; algebraic simplification is needed."))
    steps.append(("Compute the limit", f"$$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}$$"))
    try:
        near = [f.subs(x, p + sp.Rational(1, 10**k)) for k in range(1, 4)]
        steps.append(("Numerical check", "Nearby values: " + ", ".join(f"{sp.latex(p + sp.Rational(1,10**k))} → {sp.latex(sp.N(v,5))}" for k, v in enumerate(near, 1))))
    except Exception:
        pass
    final = f"\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}"
    yv = num(lim)
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'}],
            'x_min': num(p) - 3, 'x_max': num(p) + 3,
            'points': [{'x': float(p), 'y': yv, 'label': f'L = {lim}', 'color': 'red'}] if yv is not None else None}
    return steps, final, plot


def render_limit():
    st.subheader("Limits")
    expr = st.text_input("Function f(x)", value="sin(x)/x", key="lim_expr")
    point = st.number_input("x approaches", value=0.0, key="lim_point")
    if st.button("Show example", key="lim_ex"):
        st.session_state.lim_expr, st.session_state.lim_point = "sin(x)/x", 0.0
        st.rerun()
    try:
        steps, final, plot = solve_limit(expr, point)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


def solve_derivative_limit(expr_str, point, var_name='x'):
    var = get_var(var_name)
    x = var
    f = parse_expr(expr_str, var_name)
    h = sp.Symbol('h')
    f_xh = sp.simplify(f.subs(x, x + h))
    quotient = sp.simplify((f_xh - f) / h)
    deriv = sp.limit(quotient, h, 0)
    slope = sp.simplify(deriv.subs(x, point))
    f_pt = f.subs(x, point)
    tangent = sp.simplify(f_pt + slope * (x - point))
    steps = [
        ("Definition", f"$$f'({sp.latex(x)}) = \\lim_{{h \\to 0}} \\frac{{f({sp.latex(x)}+h)-f({sp.latex(x)})}}{{h}}$$"),
        ("Compute f(x+h)", f"$$f({sp.latex(x)}+h) = {sp.latex(f_xh)}$$"),
        ("Difference quotient", f"$$\\frac{{f({sp.latex(x)}+h)-f({sp.latex(x)})}}{{h}} = {sp.latex(quotient)}$$"),
        ("Take the limit h→0", f"$$f'({sp.latex(x)}) = \\lim_{{h\\to0}} {sp.latex(quotient)} = {sp.latex(deriv)}$$"),
        ("Slope at the point", f"$$f'({sp.latex(point)}) = {sp.latex(slope)}$$"),
        ("Tangent line", f"$$y = {sp.latex(tangent)}$$"),
    ]
    final = f"f'({sp.latex(x)}) = {sp.latex(deriv)}, \\quad y = {sp.latex(tangent)}"
    yv = num(f_pt)
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'},
                      {'expr': for_plot(tangent, x), 'label': 'tangent', 'dashed': True, 'color': 'orange'}],
            'x_min': float(point) - 4, 'x_max': float(point) + 4,
            'points': [{'x': float(point), 'y': yv, 'label': f'({point}, {f_pt})'}] if yv is not None else None}
    return steps, final, plot


def render_derivative_limit():
    st.subheader("Derivative — limit definition")
    expr = st.text_input("f(x)", value="x^2", key="dl_expr")
    point = st.number_input("At point x =", value=1.0, key="dl_point")
    if st.button("Show example", key="dl_ex"):
        st.session_state.dl_expr, st.session_state.dl_point = "x^2", 1.0
        st.rerun()
    try:
        steps, final, plot = solve_derivative_limit(expr, point)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


def solve_integral_limit(expr_str, a, b, n, var_name='x'):
    var = get_var(var_name)
    x = var
    f = parse_expr(expr_str, var_name)
    a, b, n = float(a), float(b), int(n)
    dx = (b - a) / n
    riemann = sum(float(f.subs(x, a + i * dx)) * dx for i in range(1, n + 1))
    exact = sp.integrate(f, (x, a, b))
    steps = [
        ("Definition", f"$$\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} {sp.latex(f)}\\,dx = \\lim_{{n\\to\\infty}} \\sum_{{i=1}}^{{n}} f(x_i)\\,\\Delta x$$"),
        ("Width and points", f"$$\\Delta x = \\frac{{{b}-{a}}}{{{n}}} = {dx}, \\quad x_i = {a} + i\\Delta x$$"),
        ("Riemann sum (n=" + str(n) + ")", f"$$S_{{{n}}} = \\sum_{{i=1}}^{{{n}}} f(x_i)\\,\\Delta x = {round(riemann, 4)}$$"),
        ("Exact integral", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = {sp.latex(exact)} = {sp.latex(sp.N(exact, 5))}$$"),
    ]
    final = f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = {sp.latex(exact)}"
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'}],
            'x_min': a - 1, 'x_max': b + 1,
            'shade': {'expr': for_plot(f, x), 'from': a, 'to': b}}
    return steps, final, plot


def render_integral_limit():
    st.subheader("Integral — limit of Riemann sums")
    expr = st.text_input("f(x)", value="x^2", key="il_expr")
    a = st.number_input("Lower limit a", value=0.0, key="il_a")
    b = st.number_input("Upper limit b", value=2.0, key="il_b")
    n = st.number_input("Rectangles n", value=5, step=1, key="il_n")
    if st.button("Show example", key="il_ex"):
        st.session_state.il_expr, st.session_state.il_a, st.session_state.il_b, st.session_state.il_n = "x^2", 0.0, 2.0, 5
        st.rerun()
    try:
        steps, final, plot = solve_integral_limit(expr, a, b, n)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


def solve_derivative(expr_str, var_name, rule):
    var = get_var(var_name)
    x = var
    f = parse_expr(expr_str, var_name)
    deriv = sp.diff(f, x)
    steps = [("Function", f"$$f({sp.latex(x)}) = {sp.latex(f)}$$")]
    if f.is_Add:
        steps.append(("Sum rule", "Apply the sum rule, differentiating term by term."))
        parts = []
        for term in sp.Add.make_args(f):
            d = sp.diff(term, x)
            parts.append(f"\\frac{{d}}{{d{sp.latex(x)}}}\\left({sp.latex(term)}\\right) = {sp.latex(d)}")
        steps.append(("Differentiating each term", "$$" + " \\quad ".join(parts) + "$$"))
    else:
        steps.append(("Apply rules", f"Apply the **{rule}** rule."))
    steps.append(("Result", f"$$f'({sp.latex(x)}) = {sp.latex(deriv)}$$"))
    final = f"f'({sp.latex(x)}) = {sp.latex(deriv)}"
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'},
                      {'expr': for_plot(deriv, x), 'label': "f'(x)", 'dashed': True, 'color': 'green'}],
            'x_min': -5, 'x_max': 5}
    return steps, final, plot


def render_derivative():
    st.subheader("Derivatives — rules")
    expr = st.text_input("f(variable)", value="x^3 + 2*x^2 + sin(x)", key="der_expr")
    col1, col2 = st.columns(2)
    variable = col1.selectbox("Variable", ['x', 'y', 'z'], key="der_var")
    rule = col2.selectbox("Rule to demonstrate", ['General', 'Constant', 'Power', 'Sum/Difference', 'Product', 'Quotient', 'Chain'], key="der_rule")
    if st.button("Show example", key="der_ex"):
        st.session_state.der_expr, st.session_state.der_var, st.session_state.der_rule = "x^3 + 2*x^2 + sin(x)", "x", "General"
        st.rerun()
    try:
        steps, final, plot = solve_derivative(expr, variable, rule)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


def solve_integral(expr_str, var_name, rule, kind, a, b):
    var = get_var(var_name)
    x = var
    f = parse_expr(expr_str, var_name)
    definite = kind == 'Definite'
    if definite:
        result = sp.integrate(f, (x, a, b))
        steps = [
            ("Integral", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)}$$"),
            ("Method", f"Rule: **{rule}**."),
            ("Apply the Fundamental Theorem", f"Find the antiderivative F, then compute F({b}) − F({a})."),
            ("Result", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)}$$"),
        ]
        final = f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)}"
        plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'}],
                'x_min': float(a) - 1, 'x_max': float(b) + 1,
                'shade': {'expr': for_plot(f, x), 'from': float(a), 'to': float(b)}}
    else:
        result = sp.integrate(f, x)
        steps = [
            ("Integral", f"$$\\int {sp.latex(f)}\\,d{sp.latex(x)}$$"),
            ("Method", f"Rule: **{rule}**."),
            ("Antiderivative", f"$$\\int {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)} + C$$"),
            ("Check", "Differentiate the result to confirm."),
        ]
        final = f"\\int {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)} + C"
        plot = None
    return steps, final, plot


def render_integral():
    st.subheader("Integrals — rules")
    expr = st.text_input("Integrand", value="x^2 + 3*x + 2", key="int_expr")
    col1, col2 = st.columns(2)
    variable = col1.selectbox("Variable", ['x', 'y', 'z'], key="int_var")
    rule = col2.selectbox("Method/rule", ['Antiderivatives', 'Substitution', 'By parts', 'Definite', 'Indefinite', 'Fundamental Theorem'], key="int_rule")
    definite = rule in ('Definite', 'Fundamental Theorem')
    a = b = 0.0
    if definite:
        a = st.number_input("Lower limit a", value=0.0, key="int_a")
        b = st.number_input("Upper limit b", value=2.0, key="int_b")
    if st.button("Show example", key="int_ex"):
        st.session_state.int_expr, st.session_state.int_var, st.session_state.int_rule = "x^2 + 3*x + 2", "x", "Indefinite"
        st.rerun()
    try:
        steps, final, plot = solve_integral(expr, variable, rule,
                                            'Definite' if definite else 'Indefinite', a, b)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


# =============================================================================
#  ALGEBRA
# =============================================================================
def solve_linear(eq_str):
    eq = parse_equation(eq_str)
    x = X
    poly = sp.Poly(eq, x)
    coeffs = poly.all_coeffs()
    if len(coeffs) > 2:
        raise ValueError("The equation is not of degree 1.")
    a = coeffs[0]
    b = coeffs[1] if len(coeffs) == 2 else 0
    if a == 0:
        raise ValueError("The coefficient of x is zero — not a degree-1 equation.")
    root = sp.simplify(-b / a)
    lhs = parse_expr(eq_str.split('=')[0])
    rhs = parse_expr(eq_str.split('=')[1])
    steps = [
        ("Original equation", f"$$ {sp.latex(sp.Eq(lhs, rhs))} $$"),
        ("Standard form", f"$$ {sp.latex(a)}\\,x + {sp.latex(b)} = 0 $$"),
        ("Identify coefficients", f"$$a = {sp.latex(a)}, \\quad b = {sp.latex(b)}$$"),
        ("Isolate x", f"$$a\\,x = -b \\implies x = \\frac{{-b}}{{a}} = \\frac{{{sp.latex(-b)}}}{{{sp.latex(a)}}}$$"),
        ("Result", f"$$x = {sp.latex(root)}$$"),
        ("Check", f"Substituting x = {sp.latex(root)}: {sp.latex(sp.simplify(eq.subs(x, root)))} = 0 ✓"),
    ]
    final = f"x = {sp.latex(root)}"
    rv = num(root)
    plot = {'exprs': [{'expr': for_plot(eq, x), 'label': 'a·x + b'}],
            'x_min': (rv - 5) if rv is not None else -5,
            'x_max': (rv + 5) if rv is not None else 5,
            'points': [{'x': float(root), 'y': 0, 'label': f'x = {root}', 'color': 'red'}] if rv is not None else None}
    return steps, final, plot


def render_linear():
    st.subheader("Linear equation (degree 1)")
    eq = st.text_input("Equation", value="2*x + 3 = 7", key="lin_eq")
    if st.button("Show example", key="lin_ex"):
        st.session_state.lin_eq = "2*x + 3 = 7"
        st.rerun()
    try:
        steps, final, plot = solve_linear(eq)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


def solve_quadratic(eq_str):
    eq = parse_equation(eq_str)
    x = X
    poly = sp.Poly(eq, x)
    coeffs = poly.all_coeffs()
    if len(coeffs) != 3:
        raise ValueError("The equation must be of degree 2 (a·x² + b·x + c).")
    a, b, c = coeffs
    disc = sp.simplify(b**2 - 4 * a * c)
    roots = sp.solve(eq, x)
    lhs = parse_expr(eq_str.split('=')[0])
    rhs = parse_expr(eq_str.split('=')[1])
    steps = [
        ("Original equation", f"$$ {sp.latex(sp.Eq(lhs, rhs))} $$"),
        ("Standard form", f"$$ {sp.latex(a)}\\,x^2 + {sp.latex(b)}\\,x + {sp.latex(c)} = 0 $$"),
        ("Coefficients", f"$$a = {sp.latex(a)}, \\quad b = {sp.latex(b)}, \\quad c = {sp.latex(c)}$$"),
        ("Discriminant", f"$$\\Delta = b^2 - 4ac = {sp.latex(b)}^2 - 4({sp.latex(a)})({sp.latex(c)}) = {sp.latex(disc)}$$"),
        ("Quadratic formula", f"$$x = \\frac{{-b \\pm \\sqrt{{\\Delta}}}}{{2a}} = \\frac{{{sp.latex(-b)} \\pm \\sqrt{{{sp.latex(disc)}}}}}{{{sp.latex(2*a)}}}$$"),
        ("Solutions", f"$$x = {sp.latex(roots)}$$"),
    ]
    final = "x = " + (", \\quad ".join(sp.latex(r) for r in roots) if isinstance(roots, list) else sp.latex(roots))
    real_roots = [num(r) for r in roots if isinstance(roots, list) and num(r) is not None and abs(num(r).imag) < 1e-9]
    pts = [{'x': float(r.real), 'y': 0.0, 'label': f'x={r.real:.3g}'} for r in real_roots] if real_roots else None
    if real_roots:
        cx = sum(r.real for r in real_roots) / len(real_roots)
        span = max(3, max(abs(r.real - cx) for r in real_roots) + 2)
        xmin, xmax = cx - span, cx + span
    else:
        xmin, xmax = -5, 5
    plot = {'exprs': [{'expr': for_plot(eq, x), 'label': 'a·x² + b·x + c'}],
            'x_min': xmin, 'x_max': xmax, 'points': pts}
    return steps, final, plot


def render_quadratic():
    st.subheader("Quadratic equation (degree 2)")
    eq = st.text_input("Equation", value="x^2 - 5*x + 6 = 0", key="quad_eq")
    if st.button("Show example", key="quad_ex"):
        st.session_state.quad_eq = "x^2 - 5*x + 6 = 0"
        st.rerun()
    try:
        steps, final, plot = solve_quadratic(eq)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


def solve_system(equations, variables):
    syms = [sp.Symbol(v) for v in variables]
    eqs = [parse_equation(e) for e in equations]
    A, bb = sp.linear_eq_to_matrix(eqs, syms)
    sol = sp.linsolve((A, bb), syms)
    aug = A.row_join(bb)
    rref, pivots = aug.rref()
    cases = []
    for i in range(A.rows):
        lhs = sp.Add(*[A[i, j] * syms[j] for j in range(len(syms))])
        cases.append(sp.latex(sp.Eq(lhs, bb[i])))
    steps = [
        ("System", "$$\\begin{cases}" + " \\\ ".join(cases) + "\\end{cases}$$"),
        ("Matrix form", f"$$A = {sp.latex(A)}, \\quad b = {sp.latex(bb)}$$"),
        ("Augmented matrix [A | b]", f"$$[A \\mid b] = {sp.latex(aug)}$$"),
        ("Row-reduced form (RREF)", f"$$\\text{{RREF}} = {sp.latex(rref)}$$"),
        ("Solution", f"$$({', '.join(str(v) for v in variables)}) = {sp.latex(sol)}$$"),
    ]
    if isinstance(sol, sp.FiniteSet) and sol:
        vals = list(sol)[0]
        verify = []
        for e in eqs:
            sub = sp.simplify(e.subs(dict(zip(syms, vals))))
            verify.append(f"{sp.latex(e)} → {sp.latex(sub)} = 0" + (" ✓" if sub == 0 else ""))
        steps.append(("Check", "  ".join(verify)))
    final = "(" + ", ".join(str(v) for v in variables) + ") = " + sp.latex(sol)
    return steps, final, None


def render_system():
    st.subheader("Linear systems")
    size = st.radio("Size", ['2x2', '3x3'], horizontal=True, key="sys_size")
    variables = ['x', 'y'] if size == '2x2' else ['x', 'y', 'z']
    eq1 = st.text_input("Equation 1", value="2*x + 3*y = 5", key="sys_e1")
    eq2 = st.text_input("Equation 2", value="x - y = 1", key="sys_e2")
    eq3 = None
    if size == '3x3':
        eq3 = st.text_input("Equation 3", value="x + y + z = 6", key="sys_e3")
    if st.button("Show example", key="sys_ex"):
        st.session_state.sys_size = '2x2'
        st.session_state.sys_e1, st.session_state.sys_e2 = "2*x + 3*y = 5", "x - y = 1"
        st.rerun()
    equations = [eq1, eq2] + ([eq3] if size == '3x3' and eq3 else [])
    try:
        steps, final, plot = solve_system(equations, variables)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


# =============================================================================
#  MAIN APP
# =============================================================================
st.set_page_config(page_title="CalculusFlow", page_icon="➗", layout="centered")

st.title("CalculusFlow")
st.caption("Interactive math companion — arithmetic, calculus, and algebra, step by step.")

MODULES = {
    "Arithmetic": {
        "Addition (carrying)": render_addition,
        "Subtraction (borrowing)": render_subtraction,
        "Long multiplication": render_multiplication,
        "Long division": render_long_division,
    },
    "Calculus": {
        "Limits": render_limit,
        "Derivative by definition": render_derivative_limit,
        "Integral by Riemann sums": render_integral_limit,
        "Derivatives (rules)": render_derivative,
        "Integrals (rules)": render_integral,
    },
    "Algebra": {
        "Linear equation": render_linear,
        "Quadratic equation": render_quadratic,
        "Linear systems": render_system,
    },
}

group = st.sidebar.radio("Area", list(MODULES.keys()))
modules = MODULES[group]
choice = st.sidebar.radio("Module", list(modules.keys()))
st.sidebar.markdown("---")
st.sidebar.markdown("Symbolic computation with **SymPy** — no API key.")
modules[choice]()
