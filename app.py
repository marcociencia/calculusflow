"""
CalculusFlow — Streamlit Version (Self-contained single file)
==============================================================
Step-by-step math application (arithmetic, calculus, and algebra).
Symbolic calculation with SymPy — no API key, free to run on Streamlit Cloud.
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
        raise ValueError(f"Variable '{name}' not supported. Use x, y, or z.")
    return _VAR_MAP[name]


def parse_expr(s, var_name='x'):
    if s is None or str(s).strip() == '':
        raise ValueError("Empty expression.")
    expr_str = str(s).strip().replace('^', '**')
    try:
        return sp.sympify(expr_str, locals=_LOCALS)
    except Exception as ex:
        raise ValueError(f"Could not parse '{s}': {ex}")


def parse_equation(s):
    if '=' not in str(s):
        raise ValueError("Equation must contain '='.")
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
    for i, (title, detail) in enumerate(steps, 1):
        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="background: #111; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 14px;">{i}</div>
                <h4 style="margin: 0; padding: 0;">{title}</h4>
            </div>
            <div style="margin-left: 34px;">{detail}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""<div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-top: 15px;">
        <h4 style="margin: 0 0 10px 0;">Final Result</h4>""", unsafe_allow_html=True)
    if final.startswith('$$'):
        st.markdown(final)
    else:
        st.latex(final)
    st.markdown("</div>", unsafe_allow_html=True)
        
    if plot:
        st.pyplot(plot_functions(**plot))


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
    st.title("Addition with Carrying")
    st.markdown("Column addition (armada) showing the carried digits above each column and the step-by-step column sums.")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
        A = col1.number_input("Top number", value=7654, step=1, key="add_A")
        B = col2.number_input("Bottom number", value=3823, step=1, key="add_B")
        submit = col3.button("Add", use_container_width=True)
        example = col4.button("Show example", icon="✨", use_container_width=True)
        
    if example:
        st.session_state.add_A, st.session_state.add_B = 7654, 3823
        st.rerun()
        
    d = add_armada(A, B)
    
    with st.container(border=True):
        rows = []
        rows.append('<div>' + _gap() + ''.join(
            _cell(c if c and c > 0 else None, 'color:#6b21a8;font-size:1em;height:1.3em;')
            for c in d['carry']) + '</div>')
        rows.append('<div>' + _gap() + ''.join(_cell(c) for c in d['top']) + '</div>')
        rows.append('<div>' + _cell('+') + ''.join(_cell(c) for c in d['bottom']) + '</div>')
        rows.append(_line(d['W'] * 1.4))
        rows.append('<div>' + _gap() + ''.join(_cell(c, 'color:#dc2626;') for c in d['result']) + '</div>')
        st.markdown(
            f'<div style="font-size:1.4em;font-weight:600;margin-bottom:15px;">'
            f'{d["A"]} + {d["B"]} = <span style="color:#dc2626">{d["total"]}</span></div>'
            f'<div style="display:inline-block;padding:1rem;">{"".join(rows)}</div>',
            unsafe_allow_html=True)
            
    with st.container(border=True):
        st.markdown("**Step by step — each column**")
        lines = []
        for i, c in enumerate(reversed(d['cols']), 1):
            carry_txt = f"(carry {c['carryIn']}) " if c['carryIn'] > 0 else ''
            extra = f" + {c['carryIn']}" if c['carryIn'] > 0 else ''
            note = f", carry {c['sum'] // 10}" if c['sum'] >= 10 else ''
            lines.append(f"Column {i}: {c['top']} + {c['bottom']}{extra} = {c['sum']} &rarr; write {c['digit']}{note}")
            
        st.markdown('<br>'.join(lines) + f"<br><br>**Final sum: {d['A']} + {d['B']} = {d['total']}**", unsafe_allow_html=True)


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
    st.title("Subtraction with Borrowing")
    st.markdown("Column subtraction (armada) showing crossed-out digits, borrowing, the place-value decomposition and the final signed answer.")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
        A = col1.number_input("Top number", value=523, step=1, key="sub_A")
        B = col2.number_input("Bottom number", value=268, step=1, key="sub_B")
        submit = col3.button("Subtract", use_container_width=True)
        example = col4.button("Show example", icon="✨", use_container_width=True)
        
    if example:
        st.session_state.sub_A, st.session_state.sub_B = 523, 268
        st.rerun()
        
    d = subtract_armada(A, B)
    w = len(d['top_arr'])
    
    with st.container(border=True):
        st.markdown(f'<div style="font-size:1.4em;font-weight:600;margin-bottom:15px;">'
                    f'{d["A"]} &minus; {d["B"]} = <span style="color:#111">{d["result"]}</span></div>',
                    unsafe_allow_html=True)
        
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
        rows.append('<div>' + _cell('&minus;') + ''.join(_cell(c) for c in d['bottom_arr']) + '</div>')
        rows.append(_line(w * 1.4))
        rows.append('<div>' + _gap() + ''.join(_cell(abs(c['result'])) for c in d['columns'])
                    + (_cell('&minus;', 'color:#dc2626') if d['negative'] else '') + '</div>')
                    
        st.markdown(f'<div style="display:inline-block;padding:1rem;">{"".join(rows)}</div>', unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top:10px;color:#555;'>Subtracting directly: {d['A']} &minus; {d['B']} = {d['result']}.</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**Step by step — each column**")
        lines = []
        for i, c in enumerate(reversed(d['columns']), 1):
            if c['borrowedFrom'] is not None:
                lines.append(f"Borrow 1 from column {w - c['borrowedFrom']}: {c['originalTop']} &rarr; {c['displayedTop']}, then {c['displayedTop']} &minus; {c['bottom']} = {c['result']}")
            else:
                lines.append(f"Column {i}: {c['originalTop']} &minus; {c['bottom']} = {c['result']}")
        st.markdown('<br>'.join(lines), unsafe_allow_html=True)
        
    with st.container(border=True):
        st.markdown("**Place-value decomposition**")
        places = ["units", "tens", "hundreds", "thousands", "ten thousands", "hundred thousands"]
        decomp_lines = []
        diff_sum = 0
        for i in range(len(d['top_arr'])):
            power = 10 ** (len(d['top_arr']) - 1 - i)
            t_val = d['top_arr'][i] * power
            b_val = d['bottom_arr'][i] * power
            diff = t_val - b_val
            diff_sum += diff
            place_name = places[len(d['top_arr']) - 1 - i]
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            decomp_lines.append(f"<div style='font-family:monospace;'>{t_val} - {b_val} &rarr; {place_name} (diff = {diff})</div>")
        
        diff_parts = [f"+{x*10**(len(d['top_arr'])-1-i)}" if (x*10**(len(d['top_arr'])-1-i))>0 else str(x*10**(len(d['top_arr'])-1-i)) for i,x in enumerate([c['originalTop'] - c['bottom'] for c in d['columns']])]
        decomp_lines.append(f"<div style='font-family:monospace; margin-top:5px;'>{' '.join(diff_parts)} = {diff_sum}</div>")
        
        st.markdown("".join(decomp_lines), unsafe_allow_html=True)


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
    st.title("Long Multiplication")
    st.markdown("Column multiplication (armada) with the carried digits in purple, every partial product shifted correctly, and the final sum.")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
        A = col1.number_input("Multiplicand (top)", value=152, step=1, key="mul_A")
        B = col2.number_input("Multiplier (bottom)", value=153, step=1, key="mul_B")
        submit = col3.button("Multiply", use_container_width=True)
        example = col4.button("Show example", icon="✨", use_container_width=True)
        
    if example:
        st.session_state.mul_A, st.session_state.mul_B = 152, 153
        st.rerun()
        
    d = multiply_armada(A, B)
    
    with st.container(border=True):
        st.markdown(f'<div style="font-size:1.4em;font-weight:600;margin-bottom:15px;">'
                    f'{d["A"]} &times; {d["B"]} = <span style="color:#dc2626">{d["product"]}</span></div>',
                    unsafe_allow_html=True)
                    
        rows = []
        rows.append('<div>' + _gap() + ''.join(_cell(c) for c in d['top_cells']) + '</div>')
        rows.append('<div>' + _cell('&times;') + ''.join(_cell(c) for c in d['bottom_cells']) + '</div>')
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
        
        st.markdown(f'<div style="display:inline-block;padding:1rem;">{"".join(rows)}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**Step by step**")
        lines = []
        for p in d['partials']:
            lines.append(f"<div style='font-family:monospace;'>{d['A']} &times; {p['digit']} = {d['A'] * p['digit']} (partial product, shifted {p['shift']} place{'s' if p['shift'] != 1 else ''} left)</div>")
        lines.append(f"<div style='font-family:monospace; margin-top:5px; font-weight:bold;'>Sum of partials = {d['A']} &times; {d['B']} = {d['product']}</div>")
        st.markdown('\n'.join(lines), unsafe_allow_html=True)


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
        s['bringDown'] = digits[s['endCol'] + 1] if s['endCol'] + 1 < N else None
    quotient_str = ''.join(map(str, quotient_digits)) or '0'
    quotient = (-1 if neg else 1) * int(quotient_str)
    remainder = cur
    return {'dividend': dividend, 'divisor': divisor, 'quotient': quotient,
            'remainder': remainder, 'quotient_str': quotient_str, 'steps': steps, 'neg': neg, 'digits': digits}


def render_long_division():
    st.title("Long Division")
    st.markdown("Classic long-division notation — divisor on the left, quotient on top, dividend inside the bracket — with each subtraction step, brought-down digits in orange, and the final remainder.")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
        dividend = col1.number_input("Dividend", value=1250, step=1, key="div_A")
        divisor = col2.number_input("Divisor", value=5, step=1, key="div_B")
        submit = col3.button("Divide", use_container_width=True)
        example = col4.button("Show example", icon="✨", use_container_width=True)
        
    if example:
        st.session_state.div_A, st.session_state.div_B = 1250, 5
        st.rerun()
        
    d = long_divide(dividend, divisor)
    if 'error' in d:
        st.error(d['error'])
        return
        
    with st.container(border=True):
        # Draw the L-shaped bracket layout
        left_html = f"<div style='display:flex; flex-direction:column; align-items:flex-end;'>"
        
        # Header / bars
        bars = "<div style='display:flex; justify-content:flex-end; gap:5px; margin-bottom:5px;'>"
        colors = ["#4285F4", "#EA4335", "#FBBC05", "#34A853"]
        for i, s in enumerate(d['steps']):
            w = len(str(s['working']))
            bars += f"<div style='height:4px; width:{w*1.5}em; background-color:{colors[i%len(colors)]}; border-radius:2px;'></div>"
        bars += "</div>"
        left_html += bars
        
        # Dividend
        left_html += f"<div style='letter-spacing:0.8em; font-weight:bold;'>{''.join(map(str, d['digits']))}</div>"
        
        # Steps
        indent = 0
        for i, s in enumerate(d['steps']):
            # Product
            prod_str = str(s['product'])
            bd_str = f"<span style='color:#E67C22;'>{s['bringDown']}</span>" if s['bringDown'] is not None else ""
            
            left_html += f"<div style='display:flex; justify-content:flex-end; margin-top:5px; padding-right: {len(d['digits']) - 1 - s['endCol']}em;'>"
            left_html += f"<div style='margin-right:10px;'>-</div>"
            left_html += f"<div style='letter-spacing:0.8em; border-bottom: 2px solid #111; padding-bottom:5px;'>{''.join(prod_str)}</div>"
            left_html += f"</div>"
            
            # Remainder
            rem_str = str(s['remainder']).zfill(len(str(s['working'])) - len(prod_str) + 1)
            left_html += f"<div style='display:flex; justify-content:flex-end; padding-right: {len(d['digits']) - 1 - s['endCol']}em; margin-top:5px;'>"
            left_html += f"<div style='letter-spacing:0.8em;'>{''.join(rem_str)} {bd_str}</div>"
            left_html += f"</div>"
            
        left_html += "</div>"
        
        right_html = f"""
        <div style="border-left: 2px solid #111; padding-left: 20px; height: 100%; display: flex; flex-direction: column;">
            <div style="font-weight:bold; letter-spacing:0.2em;">{d['divisor']}</div>
            <div style="border-top: 2px solid #111; padding-top: 10px; color: #34A853; font-weight:bold; letter-spacing:0.5em; margin-top: 5px;">
                {d['quotient_str']}
            </div>
        </div>
        """
        
        st.markdown(f"""
        <div style="display:flex; font-family: ui-monospace, monospace; font-size: 1.5em; padding: 20px;">
            <div style="flex: 1; display:flex; justify-content:flex-end; padding-right: 20px;">
                {left_html}
            </div>
            <div style="flex: 1;">
                {right_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with st.container(border=True):
        st.markdown("##### Result")
        st.markdown(f"<div style='font-family:monospace; font-size:1.2em;'>{d['dividend']} &divide; {d['divisor']} = <span style='color:#34A853;'>{d['quotient']}</span></div>", unsafe_allow_html=True)
        
    with st.container(border=True):
        st.markdown("**Step by step**")
        lines = []
        for i, s in enumerate(d['steps'], 1):
            line = f"Step {i}: Working number {s['working']} &divide; {d['divisor']} = <span style='color:#34A853; font-weight:bold;'>{s['qDigit']}</span>. "
            line += f"{s['qDigit']} &times; {d['divisor']} = {s['product']}. Subtract &rarr; remainder <span style='color:#673AB7; font-weight:bold;'>{s['remainder']}</span>"
            if s['bringDown'] is not None:
                line += f"; bring down <span style='color:#E67C22; font-weight:bold;'>{s['bringDown']}</span>."
            else:
                line += "."
            lines.append(f"<div style='font-family:monospace; margin-bottom:10px;'>{line}</div>")
        
        lines.append(f"<div style='font-family:monospace; margin-top:15px; font-weight:bold;'>Quotient: <span style='color:#34A853;'>{d['quotient']}</span></div>")
        st.markdown("".join(lines), unsafe_allow_html=True)


# =============================================================================
#  CALCULUS
# =============================================================================
def solve_limit(expr_str, point):
    f = parse_expr(expr_str)
    x = X
    p = sp.nsimplify(point)
    sub = f.subs(x, p)
    
    num_part, den_part = f.as_numer_denom()
    sub_num = num_part.subs(x, p)
    sub_den = den_part.subs(x, p)
    
    steps = [("Define the limit", f"We are tasked to evaluate the limit $L = \\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)}$.")]

    if sub_num == 0 and sub_den == 0:
        steps.append(("Perform direct substitution", f"Substituting $x = {sp.latex(p)}$ into the function gives $\\frac{{0}}{{0}}$. This is an indeterminate form."))
        deriv_num = sp.diff(num_part, x)
        deriv_den = sp.diff(den_part, x)
        steps.append(("Apply L'Hôpital's Rule", f"Since the limit results in an indeterminate form $\\frac{{0}}{{0}}$, we can apply L'Hôpital's Rule, which states that $\\lim_{{x \\to c}} \\frac{{f(x)}}{{g(x)}} = \\lim_{{x \\to c}} \\frac{{f'(x)}}{{g'(x)}}$."))
        steps.append(("Differentiate numerator and denominator", f"Differentiating the numerator $\\frac{{d}}{{dx}}\\left({sp.latex(num_part)}\\right) = {sp.latex(deriv_num)}$ and the denominator $\\frac{{d}}{{dx}}\\left({sp.latex(den_part)}\\right) = {sp.latex(deriv_den)}$."))
        lim = sp.limit(deriv_num/deriv_den, x, p)
        steps.append(("Evaluate the new limit", f"We now evaluate $\\lim_{{x \\to {sp.latex(p)}}} \\frac{{{sp.latex(deriv_num)}}}{{{sp.latex(deriv_den)}}} = {sp.latex(lim)}$."))
    else:
        steps.append(("Perform direct substitution", f"Substituting $x = {sp.latex(p)}$ gives $f({sp.latex(p)}) = {sp.latex(sp.simplify(sub))}$."))
        if sub == sp.zoo or sub.has(sp.nan) or (getattr(sub, 'is_infinite', None) and sub.is_infinite):
            steps.append(("Indeterminate form", "Direct substitution results in an infinite/indeterminate form; algebraic simplification is needed."))
        lim = sp.limit(f, x, p)
        steps.append(("Calculate the limit", f"$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}$"))
        
    try:
        near = [f.subs(x, p + sp.Rational(1, 10**k)) for k in range(1, 4)]
        steps.append(("Numerical verification", "Values close to the point: " + ", ".join(f"{sp.latex(p + sp.Rational(1,10**k))} \\to {sp.latex(sp.N(v,5))}" for k, v in enumerate(near, 1))))
    except Exception:
        pass
        
    final = f"\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}"
    yv = num(lim)
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'}],
            'x_min': num(p) - 3, 'x_max': num(p) + 3,
            'points': [{'x': float(p), 'y': yv, 'label': f'L = {lim}', 'color': 'red'}] if yv is not None else None}
    return steps, final, plot


def render_limit():
    st.title("Limits")
    st.markdown("Direct substitution, algebraic manipulation and L'Hôpital's rule — with a graph near the point.")
    
    with st.container(border=True):
        expr = st.text_input("Function f(x)", value="sin(x)/x", key="lim_expr")
        point = st.number_input("x approaches", value=0.0, key="lim_point")
        
        col1, col2 = st.columns([1, 4])
        submit = col1.button("Solve", use_container_width=True)
        example = col2.button("Show example", icon="✨")
        
    if example:
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
        ("Calculate f(x+h)", f"$$f({sp.latex(x)}+h) = {sp.latex(f_xh)}$$"),
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
    st.title("Derivative — Limit Definition")
    
    with st.container(border=True):
        expr = st.text_input("f(x)", value="x^2", key="dl_expr")
        point = st.number_input("At point x =", value=1.0, key="dl_point")
        col1, col2 = st.columns([1, 4])
        submit = col1.button("Solve", use_container_width=True)
        example = col2.button("Show example", icon="✨")
        
    if example:
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
        (f"Riemann sum (n={n})", f"$$S_{{{n}}} = \\sum_{{i=1}}^{{{n}}} f(x_i)\\,\\Delta x = {round(riemann, 4)}$$"),
        ("Exact integral", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = {sp.latex(exact)} = {sp.latex(sp.N(exact, 5))}$$"),
    ]
    final = f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = {sp.latex(exact)}"
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'}],
            'x_min': a - 1, 'x_max': b + 1,
            'shade': {'expr': for_plot(f, x), 'from': a, 'to': b}}
    return steps, final, plot


def render_integral_limit():
    st.title("Integral — Riemann Sums Limit")
    
    with st.container(border=True):
        expr = st.text_input("f(x)", value="x^2", key="il_expr")
        col1, col2, col3 = st.columns(3)
        a = col1.number_input("Lower limit a", value=0.0, key="il_a")
        b = col2.number_input("Upper limit b", value=2.0, key="il_b")
        n = col3.number_input("Rectangles n", value=5, step=1, key="il_n")
        
        c1, c2 = st.columns([1, 4])
        submit = c1.button("Solve", use_container_width=True)
        example = c2.button("Show example", icon="✨")
        
    if example:
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
    st.title("Derivatives — Rules")
    
    with st.container(border=True):
        expr = st.text_input("f(variable)", value="x^3 + 2*x^2 + sin(x)", key="der_expr")
        col1, col2 = st.columns(2)
        variable = col1.selectbox("Variable", ['x', 'y', 'z'], key="der_var")
        rule = col2.selectbox("Rule to demonstrate", ['General', 'Constant', 'Power', 'Sum/Difference', 'Product', 'Quotient', 'Chain'], key="der_rule")
        
        c1, c2 = st.columns([1, 4])
        submit = c1.button("Solve", use_container_width=True)
        example = c2.button("Show example", icon="✨")
        
    if example:
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
            ("Apply Fundamental Theorem", f"Find the antiderivative F, then calculate F({b}) − F({a})."),
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
            ("Verification", "Differentiate the result to confirm."),
        ]
        final = f"\\int {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)} + C"
        plot = None
    return steps, final, plot


def render_integral():
    st.title("Integrals — Rules")
    
    with st.container(border=True):
        expr = st.text_input("Integrand", value="x^2 + 3*x + 2", key="int_expr")
        col1, col2 = st.columns(2)
        variable = col1.selectbox("Variable", ['x', 'y', 'z'], key="int_var")
        rule = col2.selectbox("Method/Rule", ['Primitives', 'Substitution', 'By parts', 'Definite', 'Indefinite', 'Fundamental Theorem'], key="int_rule")
        
        definite = rule in ('Definite', 'Fundamental Theorem')
        a = b = 0.0
        if definite:
            c_a, c_b = st.columns(2)
            a = c_a.number_input("Lower limit a", value=0.0, key="int_a")
            b = c_b.number_input("Upper limit b", value=2.0, key="int_b")
            
        c1, c2 = st.columns([1, 4])
        submit = c1.button("Solve", use_container_width=True)
        example = c2.button("Show example", icon="✨")
        
    if example:
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
        raise ValueError("Equation is not linear (1st degree).")
    a = coeffs[0]
    b = coeffs[1] if len(coeffs) == 2 else 0
    if a == 0:
        raise ValueError("Coefficient of x is zero — not a linear equation.")
    root = sp.simplify(-b / a)
    lhs = parse_expr(eq_str.split('=')[0])
    rhs = parse_expr(eq_str.split('=')[1])
    steps = [
        ("Original equation", f"$$ {sp.latex(sp.Eq(lhs, rhs))} $$"),
        ("Standard form", f"$$ {sp.latex(a)}\\,x + {sp.latex(b)} = 0 $$"),
        ("Identify coefficients", f"$$a = {sp.latex(a)}, \\quad b = {sp.latex(b)}$$"),
        ("Isolate x", f"$$a\\,x = -b \\implies x = \\frac{{-b}}{{a}} = \\frac{{{sp.latex(-b)}}}{{{sp.latex(a)}}}$$"),
        ("Result", f"$$x = {sp.latex(root)}$$"),
        ("Verification", f"Substituting x = {sp.latex(root)}: {sp.latex(sp.simplify(eq.subs(x, root)))} = 0 ✓"),
    ]
    final = f"x = {sp.latex(root)}"
    rv = num(root)
    plot = {'exprs': [{'expr': for_plot(eq, x), 'label': 'a·x + b'}],
            'x_min': (rv - 5) if rv is not None else -5,
            'x_max': (rv + 5) if rv is not None else 5,
            'points': [{'x': float(root), 'y': 0, 'label': f'x = {root}', 'color': 'red'}] if rv is not None else None}
    return steps, final, plot


def render_linear():
    st.title("Linear Equation (1st degree)")
    
    with st.container(border=True):
        eq = st.text_input("Equation", value="2*x + 3 = 7", key="lin_eq")
        col1, col2 = st.columns([1, 4])
        submit = col1.button("Solve", use_container_width=True)
        example = col2.button("Show example", icon="✨")
        
    if example:
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
        raise ValueError("Equation must be quadratic (a·x² + b·x + c).")
    a, b, c = coeffs
    disc = sp.simplify(b**2 - 4 * a * c)
    roots = sp.solve(eq, x)
    lhs = parse_expr(eq_str.split('=')[0])
    rhs = parse_expr(eq_str.split('=')[1])
    steps = [
        ("Original equation", f"$$ {sp.latex(sp.Eq(lhs, rhs))} $$"),
        ("Standard form", f"$$ {sp.latex(a)}\\,x^2 + {sp.latex(b)}\\,x + {sp.latex(c)} = 0 $$"),
        ("Coefficients", f"$$a = {sp.latex(a)}, \\quad b = {sp.latex(b)}, \\quad c = {sp.latex(c)}$$"),
        ("Discriminant", f"$$\\Delta = b^2 - 4ac = ({sp.latex(b)})^2 - 4({sp.latex(a)})({sp.latex(c)}) = {sp.latex(disc)}$$"),
        ("Quadratic formula", f"$$x = \\frac{{-b \\pm \\sqrt{{\\Delta}}}}{{2a}} = \\frac{{-({sp.latex(b)}) \\pm \\sqrt{{{sp.latex(disc)}}}}}{{{sp.latex(2*a)}}}$$"),
        ("Solutions", f"$$x = {sp.latex(roots)}$$"),
    ]
    final = "x = " + (", \\quad ".join(sp.latex(r) for r in roots) if isinstance(roots, list) else sp.latex(roots))
    
    real_roots = [num(r) for r in roots if isinstance(roots, list) and num(r) is not None and abs(num(r).imag) < 1e-9]
    points = [{'x': r, 'y': 0, 'label': f'Root', 'color': 'red'} for r in real_roots]
    
    plot = {'exprs': [{'expr': for_plot(eq, x), 'label': 'a·x² + b·x + c'}],
            'x_min': min(real_roots) - 5 if real_roots else -5,
            'x_max': max(real_roots) + 5 if real_roots else 5,
            'points': points if points else None}
            
    return steps, final, plot

def render_quadratic():
    st.title("Quadratic Equation")
    
    with st.container(border=True):
        eq = st.text_input("Equation", value="x^2 - 5*x + 6 = 0", key="quad_eq")
        col1, col2 = st.columns([1, 4])
        submit = col1.button("Solve", use_container_width=True)
        example = col2.button("Show example", icon="✨")
        
    if example:
        st.session_state.quad_eq = "x^2 - 5*x + 6 = 0"
        st.rerun()
    try:
        steps, final, plot = solve_quadratic(eq)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


def solve_linear_system(eq1_str, eq2_str):
    eq1 = parse_equation(eq1_str)
    eq2 = parse_equation(eq2_str)
    
    sol = sp.solve((eq1, eq2), (X, Y))
    
    steps = [
        ("System of equations", f"$$ \\begin{{cases}} {sp.latex(parse_expr(eq1_str.split('=')[0]))} = {sp.latex(parse_expr(eq1_str.split('=')[1]))} \\\\ {sp.latex(parse_expr(eq2_str.split('=')[0]))} = {sp.latex(parse_expr(eq2_str.split('=')[1]))} \\end{{cases}} $$"),
        ("Solving for x and y", "Applying substitution or elimination method."),
    ]
    
    if isinstance(sol, dict):
        final = f"x = {sp.latex(sol.get(X, 'Any'))}, \\quad y = {sp.latex(sol.get(Y, 'Any'))}"
        steps.append(("Result", f"$${final}$$"))
    else:
        final = "No unique solution or infinitely many solutions."
        steps.append(("Result", final))
        
    return steps, final, None

def render_linear_systems():
    st.title("Linear Systems (2x2)")
    
    with st.container(border=True):
        eq1 = st.text_input("Equation 1", value="2*x + y = 5", key="sys_eq1")
        eq2 = st.text_input("Equation 2", value="x - y = 1", key="sys_eq2")
        col1, col2 = st.columns([1, 4])
        submit = col1.button("Solve", use_container_width=True)
        example = col2.button("Show example", icon="✨")
        
    if example:
        st.session_state.sys_eq1 = "2*x + y = 5"
        st.session_state.sys_eq2 = "x - y = 1"
        st.rerun()
    try:
        steps, final, plot = solve_linear_system(eq1, eq2)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))


# =============================================================================
#  MAIN APP ROUTING
# =============================================================================
def main():
    st.set_page_config(page_title="Advanced Math Solver", layout="wide")
    
    st.sidebar.title("Advanced Math Solver")
    st.sidebar.markdown("---")

    menu = {
        "⌂ Home": "home",
        "+ Addition (carrying)": "addition",
        "− Subtraction (borrowing)": "subtraction",
        "× Multiplication": "multiplication",
        "÷ Long Division (L)": "long_division",
        "∞ Limits": "limits",
        "f' Derivative (limit def.)": "derivative_limit",
        "Σ Integral (Riemann)": "integral_limit",
        "x= Linear Equation": "linear_equation",
        "x² Quadratic Equation": "quadratic_equation",
        "⊞ Linear Systems": "linear_systems",
        "dy Derivatives (rules)": "derivatives",
        "∫ Integrals (rules)": "integrals"
    }

    choice = st.sidebar.radio("Navigation", list(menu.keys()))

    if menu[choice] == "home":
        st.title("Advanced Math Solver")
        st.markdown("Welcome! Select an operation from the sidebar to view step-by-step mathematical solutions with proper formatting and charts.")
    elif menu[choice] == "addition":
        render_addition()
    elif menu[choice] == "subtraction":
        render_subtraction()
    elif menu[choice] == "multiplication":
        render_multiplication()
    elif menu[choice] == "long_division":
        render_long_division()
    elif menu[choice] == "limits":
        render_limit()
    elif menu[choice] == "derivative_limit":
        render_derivative_limit()
    elif menu[choice] == "integral_limit":
        render_integral_limit()
    elif menu[choice] == "linear_equation":
        render_linear()
    elif menu[choice] == "quadratic_equation":
        render_quadratic()
    elif menu[choice] == "linear_systems":
        render_linear_systems()
    elif menu[choice] == "derivatives":
        render_derivative()
    elif menu[choice] == "integrals":
        render_integral()

if __name__ == '__main__':
    main()
