"""Módulos de aritmética: adição, subtração, multiplicação e divisão longa."""
import streamlit as st


# ----------------------------- ADDITION -----------------------------
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


def render_addition():
    st.subheader("Adição com transporte (vai-um)")
    A = int(st.number_input("Número de cima", value=6789, step=1, key="add_A"))
    B = int(st.number_input("Número de baixo", value=4567, step=1, key="add_B"))
    if st.button("Mostrar exemplo", key="add_ex"):
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

    st.markdown("**Passo a passo — cada coluna**")
    lines = []
    for c in reversed(d['cols']):
        carry_txt = f"(vai {c['carryIn']}) " if c['carryIn'] > 0 else ''
        extra = f" + {c['carryIn']}" if c['carryIn'] > 0 else ''
        note = ", vai 1" if c['sum'] >= 10 else ''
        lines.append(f"{carry_txt}{c['top']} + {c['bottom']}{extra} = {c['sum']} → escreve **{c['digit']}**{note}")
    lines.append(f"**Soma final: {d['A']} + {d['B']} = {d['total']}**")
    st.markdown('\n'.join('- ' + l for l in lines))


# ----------------------------- SUBTRACTION -----------------------------
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


def _strike_cell(v, color=''):
    return (f'<span style="position:relative;display:inline-flex;width:1.4em;height:2.2em;'
            f'justify-content:center;align-items:center;font-family:monospace;'
            f'font-size:1.8em;font-weight:600;{color}">'
            f'<span style="position:absolute;width:1.8em;height:2px;background:#111;'
            f'transform:rotate(-22deg);"></span>{v}</span>')


def render_subtraction():
    st.subheader("Subtração com empréstimo (vai-um)")
    A = int(st.number_input("Número de cima", value=5003, step=1, key="sub_A"))
    B = int(st.number_input("Número de baixo", value=2897, step=1, key="sub_B"))
    if st.button("Mostrar exemplo", key="sub_ex"):
        st.session_state.sub_A, st.session_state.sub_B = 5003, 2897
        st.rerun()

    d = subtract_armada(A, B)
    w = len(d['top_arr'])
    rows = []

    # borrow markers row
    row = _gap()
    for c in d['columns']:
        mark = None
        if c['index'] in d['lent_by']:
            mark = (d['lent_by'][c['index']]['newValue'], 'color:#2563eb')
        elif c['borrowedFrom'] is not None:
            mark = (c['displayedTop'], 'color:#dc2626')
        if mark:
            row += f'<span style="display:inline-flex;width:1.4em;height:1.3em;justify-content:center;align-items:center;font-size:1em;{mark[1]}">{mark[0]}</span>'
        else:
            row += _gap('height:1.3em;')
    rows.append('<div>' + row + '</div>')

    # top row
    row = _gap()
    for i, v in enumerate(d['top_arr']):
        struck = i in d['lent_by'] or any(c['index'] == i and c['borrowedFrom'] is not None for c in d['columns'])
        row += _strike_cell(v) if struck else _cell(v)
    rows.append('<div>' + row + '</div>')

    # bottom row with −
    rows.append('<div>' + _cell('−') + ''.join(_cell(c) for c in d['bottom_arr']) + '</div>')
    rows.append(_line(w * 1.4))
    rows.append('<div>' + _gap() + ''.join(_cell(abs(c['result'])) for c in d['columns'])
                + (_cell('−', 'color:#dc2626') if d['negative'] else '') + '</div>')

    st.markdown(
        f'<div style="display:inline-block;padding:1rem;">{"".join(rows)}</div>'
        f'<div style="margin-top:.5rem;font-size:1.4em;font-weight:600">'
        f'{d["A"]} − {d["B"]} = <span style="color:#dc2626">{d["result"]}</span></div>',
        unsafe_allow_html=True)

    st.markdown("**Passo a passo — cada coluna**")
    lines = []
    for c in d['columns']:
        if c['borrowedFrom'] is not None:
            lines.append(f"Empresta 1 da coluna {c['borrowedFrom'] + 1}: {c['originalTop']} → {c['displayedTop']}, então {c['displayedTop']} − {c['bottom']} = **{c['result']}**")
        else:
            lines.append(f"Coluna {c['index'] + 1}: {c['originalTop']} − {c['bottom']} = **{c['result']}**")
    st.markdown('\n'.join('- ' + l for l in lines))


# ----------------------------- MULTIPLICATION -----------------------------
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
    st.subheader("Multiplicação longa (armada)")
    A = int(st.number_input("Multiplicando (cima)", value=234, step=1, key="mul_A"))
    B = int(st.number_input("Multiplicador (baixo)", value=56, step=1, key="mul_B"))
    if st.button("Mostrar exemplo", key="mul_ex"):
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

    st.markdown("**Passo a passo**")
    lines = []
    for p in d['partials']:
        lines.append(f"{d['A']} × {p['digit']} = {d['A'] * p['digit']} (produto parcial, deslocado {p['shift']} casa(s))")
    lines.append(f"**Soma dos parciais = {d['A']} × {d['B']} = {d['product']}**")
    st.markdown('\n'.join('- ' + l for l in lines))


# ----------------------------- LONG DIVISION -----------------------------
def long_divide(dividend, divisor):
    dividend, divisor = int(dividend), int(divisor)
    if divisor == 0:
        return {'error': 'Divisão por zero é indefinida.'}
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
    st.subheader("Divisão longa (notação com chaves)")
    dividend = int(st.number_input("Dividendo", value=4356, step=1, key="div_A"))
    divisor = int(st.number_input("Divisor", value=12, step=1, key="div_B"))
    if st.button("Mostrar exemplo", key="div_ex"):
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
        f'{" (resto " + str(d["remainder"]) + ")" if d["remainder"] else ""}</div>',
        unsafe_allow_html=True)

    st.markdown("**Passo a passo**")
    lines = []
    for s in d['steps']:
        line = f"{s['working']} ÷ {d['divisor']} = {s['qDigit']} → {s['qDigit']} × {d['divisor']} = {s['product']}; {s['working']} − {s['product']} = **{s['remainder']}**"
        if s['bringDown'] is not None:
            line += f"; baixa {s['bringDown']} → {s['remainder'] * 10 + s['bringDown']}"
        lines.append(line)
    lines.append(f"**Quociente: {d['quotient']}**"
                 + (f", resto {d['remainder']}" if d['remainder'] else " (divisão exata)"))
    st.markdown('\n'.join('- ' + l for l in lines))