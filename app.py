"""
CalculusFlow — versão com design compacto corrigido
Corrige StreamlitAPIException + desalinhamento da armada
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import lambdify

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
    for title, detail in steps:
        st.markdown(f"**{title}**")
        st.markdown(detail)
    st.markdown("**Resposta final**")
    if final.startswith('$$'):
        st.markdown(final)
    else:
        st.latex(final)
    if plot:
        st.pyplot(plot_functions(**plot))

# =============================================================================
#  ARITMÉTICA — DESIGN COMPACTO CORRIGIDO (modelo ideal)
# =============================================================================

def _armada_wrapper_start(W, font_size=36):
    # Wrapper + grid start
    return f'''
    <div style="display:inline-block; background:#ffffff; padding:14px 22px 10px 22px; border-radius:12px; border:1px solid #e5e7eb; box-shadow:0 1px 2px rgba(0,0,0,0.04);">
      <div style="display:grid; grid-template-columns:repeat({W}, 1.05em); justify-items:center; align-items:end; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-weight:700; font-size:{font_size}px; line-height:1.05; column-gap:2px; row-gap:1px;">
    '''

def _armada_wrapper_end():
    return '</div></div>'

def _carry_cells_html(carry_list, W, hide_overflow=True, total_str=None, max_orig_len=None):
    html=''
    # se total tem digito extra, não mostra o vai-um da coluna 0 como no modelo ideal
    for i in range(W):
        val = carry_list[i] if i < len(carry_list) else None
        show = ''
        if val is not None and val != 0 and str(val).strip()!='':
            if hide_overflow and i==0 and total_str is not None and max_orig_len is not None:
                if W > max_orig_len and total_str.lstrip()[0]==str(val):
                    show='' # esconde vai-um que virou digito do resultado
                else:
                    show=str(val)
            else:
                show=str(val)
        if show:
            html+=f'<div style="color:#7c3aed; font-size:14px; font-weight:700; height:18px; display:flex; align-items:flex-end; justify-content:center;">{show}</div>'
        else:
            html+=f'<div style="height:18px;"></div>'
    return html

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
        carry[W - 1 - maxlen] = c
    return {'A': A, 'B': B, 'W': W, 'top': top, 'bottom': bottom,
            'carry': carry, 'result': result, 'cols': cols, 'total': A + B}

def render_addition():
    st.subheader("Adição com transporte (vai-um)")
    def _reset():
        st.session_state["add_A"] = 6789
        st.session_state["add_B"] = 4567
    A = int(st.number_input("Número de cima", value=6789, step=1, key="add_A"))
    B = int(st.number_input("Número de baixo", value=4567, step=1, key="add_B"))
    st.button("Mostrar exemplo", key="add_ex", on_click=_reset)

    d = add_armada(A, B)
    total_str = str(d['total'])
    W = len(total_str)
    max_orig = max(len(str(A)), len(str(B)))
    # garante W correto
    if W < max_orig:
        W = max_orig

    top_str = str(A).rjust(W)
    b_str_raw = str(B)
    bottom_str = b_str_raw.rjust(W)
    # bottom com + posicionado
    plus_pos = W - len(b_str_raw) - 1
    bottom_cells = []
    for i,ch in enumerate(bottom_str):
        if i==plus_pos:
            bottom_cells.append('+')
        else:
            bottom_cells.append(ch if ch!=' ' else '')

    # se não coube o +, coloca na frente
    if plus_pos < 0:
        # coloca + antes do primeiro digito
        bottom_cells[0] = '+' + bottom_cells[0]

    carry_html = _carry_cells_html(d['carry'], W, hide_overflow=True, total_str=total_str, max_orig_len=max_orig)

    html = _armada_wrapper_start(W, font_size=36)
    html += carry_html
    # top
    for ch in top_str:
        html+=f'<div>{ch if ch!=" " else ""}</div>'
    # bottom
    for ch in bottom_cells:
        if ch=='+':
            html+=f'<div style="font-size:30px; line-height:1;">+</div>'
        else:
            html+=f'<div>{ch}</div>'
    # linha
    html+=f'<div style="grid-column:1 / -1; height:3px; background:#111; margin:5px 0 6px 0; border-radius:1px;"></div>'
    # resultado vermelho
    for ch in total_str.rjust(W):
        html+=f'<div style="color:#dc2626;">{ch if ch!=" " else ""}</div>'

    html+= _armada_wrapper_end()
    html+= f'<div style="margin-top:10px; font-size:18px; font-weight:600;">{A} + {B} = <span style="color:#dc2626">{d["total"]}</span></div>'

    st.markdown(html, unsafe_allow_html=True)

    st.markdown("**Passo a passo — cada coluna**")
    lines=[]
    for c in reversed(d['cols']):
        carry_txt = f"(vai {c['carryIn']}) " if c['carryIn']>0 else ''
        extra = f" + {c['carryIn']}" if c['carryIn']>0 else ''
        note = ", vai 1" if c['sum']>=10 else ''
        lines.append(f"{carry_txt}{c['top']} + {c['bottom']}{extra} = {c['sum']} → escreve **{c['digit']}**{note}")
    lines.append(f"**Soma final: {A} + {B} = {d['total']}**")
    st.markdown('\n'.join('- '+l for l in lines))

# ---- Subtração compacta ----
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
    for i in range(len(top_str)-1, -1, -1):
        t = working[i]
        b = bottom_arr[i]
        borrowed = None
        if t < b:
            j = i-1
            while j>=0 and working[j]==0:
                j-=1
            if j>=0:
                old = working[j]
                working[j]-=1
                for k in range(j+1,i):
                    working[k]=9
                t = working[i]+10
                borrowed=j
                lent_by[j]={'newValue':working[j], 'oldValue':old}
        columns.insert(0, {'index':i, 'originalTop':top_arr[i], 'displayedTop':t, 'bottom':b, 'result':t-b, 'borrowedFrom':borrowed})
    magnitude = int(''.join(str(c['result']) for c in columns))
    result = -magnitude if negative else magnitude
    return {'A':A,'B':B,'top_arr':top_arr,'bottom_arr':bottom_arr,'columns':columns,'lent_by':lent_by,'negative':negative,'larger':larger,'smaller':smaller,'result':result}

def render_subtraction():
    st.subheader("Subtração com empréstimo (vai-um)")
    def _reset():
        st.session_state["sub_A"]=5003
        st.session_state["sub_B"]=2897
    A = int(st.number_input("Número de cima", value=5003, step=1, key="sub_A"))
    B = int(st.number_input("Número de baixo", value=2897, step=1, key="sub_B"))
    st.button("Mostrar exemplo", key="sub_ex", on_click=_reset)

    d = subtract_armada(A, B)
    W = len(str(d['larger']))
    top_str = str(d['larger']).rjust(W)
    bottom_raw = str(d['smaller']).rjust(W)
    result_abs = str(abs(d['result'])).rjust(W)

    # linha de empréstimo: mostra novo valor pequeno em azul quando houve empréstimo
    borrow_top_small = ['']*W
    for col in d['columns']:
        idx = col['index']
        if col['borrowedFrom'] is not None:
            borrow_top_small[idx] = str(col['displayedTop'])
    # linha de riscado
    borrow_from_marks = set(d['lent_by'].keys())

    html = _armada_wrapper_start(W, font_size=34)
    # small row
    for i in range(W):
        ch = borrow_top_small[i]
        if ch:
            html+=f'<div style="color:#2563eb; font-size:14px; font-weight:700; height:18px; display:flex; align-items:flex-end; justify-content:center;">{ch}</div>'
        else:
            # mostra novo valor do doador se houver
            if i in d['lent_by']:
                html+=f'<div style="color:#2563eb; font-size:14px; font-weight:700; height:18px; display:flex; align-items:flex-end; justify-content:center;">{d["lent_by"][i]["newValue"]}</div>'
            else:
                html+=f'<div style="height:18px;"></div>'
    # top row com riscado
    for i,ch in enumerate(top_str):
        if ch.strip()=='':
            html+=f'<div></div>'
        else:
            if i in borrow_from_marks or any(c['index']==i and c['borrowedFrom'] is not None for c in d['columns']):
                # riscado
                html+=f'<div style="position:relative;">{ch}<span style="position:absolute; left:10%; top:50%; width:80%; height:2px; background:#111; transform:rotate(-18deg);"></span></div>'
            else:
                html+=f'<div>{ch}</div>'
    # bottom row
    plus_pos = W - len(str(d['smaller'])) -1
    for i,ch in enumerate(bottom_raw):
        if i==plus_pos:
            html+=f'<div style="font-size:28px;">−</div>'
        else:
            html+=f'<div>{ch if ch!=" " else ""}</div>'
    html+=f'<div style="grid-column:1 / -1; height:3px; background:#111; margin:5px 0 6px 0;"></div>'
    for i,ch in enumerate(result_abs):
        if d['negative'] and i==0 and ch.strip()=='':
            continue
        html+=f'<div style="color:#dc2626;">{ch if ch.strip()!="" else ""}</div>'
    html+= _armada_wrapper_end()
    html+= f'<div style="margin-top:10px; font-size:18px; font-weight:600;">{d["A"]} − {d["B"]} = <span style="color:#dc2626">{d["result"]}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("**Passo a passo — cada coluna**")
    lines=[]
    for c in d['columns']:
        if c['borrowedFrom'] is not None:
            lines.append(f"Empresta 1 da coluna {c['borrowedFrom']+1}: {c['originalTop']} → {c['displayedTop']}, então {c['displayedTop']} − {c['bottom']} = **{c['result']}**")
        else:
            lines.append(f"Coluna {c['index']+1}: {c['originalTop']} − {c['bottom']} = **{c['result']}**")
    st.markdown('\n'.join('- '+l for l in lines))

# ---- Multiplicação compacta ----
def multiply_armada(A, B):
    A, B = abs(int(A)), abs(int(B))
    top_str, bottom_str = str(A), str(B)
    top_arr = list(map(int, top_str))
    bottom_arr = list(map(int, bottom_str))
    top_len = len(top_arr)
    W = len(str(A*B))
    if W < max(top_len, len(bottom_arr)):
        W = max(top_len, len(bottom_arr))
    # garante espaço para parciais deslocadas
    W = max(W, top_len + len(bottom_arr))

    partials=[]
    shift=0
    for i in range(len(bottom_arr)-1, -1, -1):
        dig = bottom_arr[i]
        prod = A * dig
        prod_str = str(prod)
        # posição direita = W-1-shift
        cells = ['']*W
        for j,ch in enumerate(reversed(prod_str)):
            pos = W-1-shift-j
            if pos>=0:
                cells[pos]=ch
        partials.append({'shift':shift,'digit':dig,'cells':cells,'value':prod})
        shift+=1
    return {'A':A,'B':B,'W':W,'top_str':top_str,'bottom_str':bottom_str,'partials':partials,'product':A*B}

def render_multiplication():
    st.subheader("Multiplicação longa (armada)")
    def _reset():
        st.session_state["mul_A"]=234
        st.session_state["mul_B"]=56
    A = int(st.number_input("Multiplicando (cima)", value=234, step=1, key="mul_A"))
    B = int(st.number_input("Multiplicador (baixo)", value=56, step=1, key="mul_B"))
    st.button("Mostrar exemplo", key="mul_ex", on_click=_reset)

    d = multiply_armada(A, B)
    W = d['W']
    top_str = d['top_str'].rjust(W)
    bottom_raw = d['bottom_str'].rjust(W)
    prod_str = str(d['product']).rjust(W)
    plus_pos = W - len(d['bottom_str']) -1

    html = _armada_wrapper_start(W, font_size=32)
    # top
    for ch in top_str:
        html+=f'<div>{ch if ch!=" " else ""}</div>'
    # bottom com ×
    for i,ch in enumerate(bottom_raw):
        if i==plus_pos:
            html+=f'<div style="font-size:26px;">×</div>'
        else:
            html+=f'<div>{ch if ch!=" " else ""}</div>'
    html+=f'<div style="grid-column:1 / -1; height:2px; background:#111; margin:4px 0;"></div>'
    # parciais
    for p in reversed(d['partials']):  # mostra do primeiro ao ultimo? manter ordem visual
        pass
    for p in d['partials'][::-1]: # na verdade queremos menor shift primeiro em cima
        # corrigir ordem: primeiro parcial (unidades) em cima
        pass
    # Reordena para exibição tradicional: unidades em cima, dezenas embaixo
    # d['partials'][0] é unidades (shift 0), deve aparecer primeiro após linha
    for p in d['partials']:
        for ch in p['cells']:
            html+=f'<div style="font-size:28px;">{ch}</div>'
    html+=f'<div style="grid-column:1 / -1; height:3px; background:#111; margin:6px 0;"></div>'
    for ch in prod_str:
        html+=f'<div style="color:#dc2626;">{ch if ch!=" " else ""}</div>'
    html+= _armada_wrapper_end()
    html+= f'<div style="margin-top:10px; font-size:18px; font-weight:600;">{A} × {B} = <span style="color:#dc2626">{d["product"]}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("**Passo a passo**")
    lines=[]
    for p in d['partials']:
        lines.append(f"{d['A']} × {p['digit']} = {d['A']*p['digit']} (produto parcial, deslocado {p['shift']} casa(s))")
    lines.append(f"**Soma dos parciais = {A} × {B} = {d['product']}**")
    st.markdown('\n'.join('- '+l for l in lines))

def long_divide(dividend, divisor):
    dividend, divisor = int(dividend), int(divisor)
    if divisor==0:
        return {'error':'Divisão por zero é indefinida.'}
    neg = (dividend<0) ^ (divisor<0)
    dividend, divisor = abs(dividend), abs(divisor)
    digits = list(map(int, str(dividend)))
    N=len(digits)
    quotient_digits=[]
    steps=[]
    cur=0
    working_start=0
    for i in range(len(digits)):
        cur=cur*10+digits[i]
        qd=cur//divisor
        if not steps and qd==0:
            continue
        product=qd*divisor
        rem=cur-product
        steps.append({'working':cur,'qDigit':qd,'product':product,'remainder':rem,'endCol':i,'startCol':working_start})
        quotient_digits.append(qd)
        cur=rem
        working_start=i
    last_nonzero = max((i for i,s in enumerate(steps) if s['product']>0), default=-1)
    for i,s in enumerate(steps):
        s['moreWork']=i<last_nonzero
        s['bringDown']=digits[s['endCol']+1] if s['moreWork'] and s['endCol']+1<N else None
    quotient_str=''.join(map(str, quotient_digits)) or '0'
    quotient=(-1 if neg else 1)*int(quotient_str)
    remainder=cur
    return {'dividend':dividend,'divisor':divisor,'quotient':quotient,'remainder':remainder,'quotient_str':quotient_str,'steps':steps,'neg':neg}

def render_long_division():
    st.subheader("Divisão longa")
    def _reset():
        st.session_state["div_A"]=4356
        st.session_state["div_B"]=12
    dividend=int(st.number_input("Dividendo", value=4356, step=1, key="div_A"))
    divisor=int(st.number_input("Divisor", value=12, step=1, key="div_B"))
    st.button("Mostrar exemplo", key="div_ex", on_click=_reset)
    d=long_divide(dividend, divisor)
    if 'error' in d:
        st.error(d['error'])
        return
    html = f'''
    <div style="display:inline-block; background:#fff; padding:16px 22px; border-radius:12px; border:1px solid #e5e7eb; font-family: ui-monospace, monospace; font-weight:700; font-size:30px;">
      <div style="color:#dc2626; margin-left:{len(str(d["divisor"]))*0.6+1.2}em; margin-bottom:4px;">{d["quotient_str"]}</div>
      <div style="display:flex; align-items:flex-start;">
        <div style="border-top:3px solid #111; border-left:3px solid #111; padding-left:8px; padding-top:2px;">{d["divisor"]}) {d["dividend"]}</div>
      </div>
      <div style="margin-top:10px; font-size:18px;">{d["dividend"]} ÷ {d["divisor"]} = <span style="color:#dc2626">{d["quotient"]}</span> {f"(resto {d['remainder']})" if d["remainder"] else ""}</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("**Passo a passo**")
    lines=[]
    for s in d['steps']:
        line=f"{s['working']} ÷ {d['divisor']} = {s['qDigit']} → {s['qDigit']} × {d['divisor']} = {s['product']}; {s['working']} − {s['product']} = **{s['remainder']}**"
        if s['bringDown'] is not None:
            line+=f"; baixa {s['bringDown']} → {s['remainder']*10+s['bringDown']}"
        lines.append(line)
    lines.append(f"**Quociente: {d['quotient']}**"+(f", resto {d['remainder']}" if d['remainder'] else " (divisão exata)"))
    st.markdown('\n'.join('- '+l for l in lines))

# =============================================================================
#  CÁLCULO (mantido)
# =============================================================================
def solve_limit(expr_str, point):
    f = parse_expr(expr_str)
    x = X
    p = sp.nsimplify(point)
    lim = sp.limit(f, x, p)
    sub = f.subs(x, p)
    steps = [("Enunciado", f"$$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)}$$")]
    steps.append(("Substituição direta", f"$$f({sp.latex(p)}) = {sp.latex(sp.simplify(sub))}$$"))
    if sub == sp.zoo or sub.has(sp.nan) or (getattr(sub, 'is_infinite', None) and sub.is_infinite):
        steps.append(("Forma indeterminada", "A substituição direta dá uma forma infinita/indeterminada; é preciso simplificar algebricamente."))
    steps.append(("Cálculo do limite", f"$$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}$$"))
    try:
        near = [f.subs(x, p + sp.Rational(1, 10**k)) for k in range(1, 4)]
        steps.append(("Verificação numérica", "Valores próximos: " + ", ".join(f"{sp.latex(p + sp.Rational(1,10**k))} → {sp.latex(sp.N(v,5))}" for k, v in enumerate(near, 1))))
    except Exception:
        pass
    final = f"\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}"
    yv = num(lim)
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'}],
            'x_min': num(p) - 3, 'x_max': num(p) + 3,
            'points': [{'x': float(p), 'y': yv, 'label': f'L = {lim}', 'color': 'red'}] if yv is not None else None}
    return steps, final, plot

def render_limit():
    st.subheader("Limites")
    def _reset():
        st.session_state["lim_expr"]="sin(x)/x"
        st.session_state["lim_point"]=0.0
    expr=st.text_input("Função f(x)", value="sin(x)/x", key="lim_expr")
    point=st.number_input("x tende a", value=0.0, key="lim_point")
    st.button("Mostrar exemplo", key="lim_ex", on_click=_reset)
    try:
        steps,final,plot=solve_limit(expr, point)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_derivative_limit(expr_str, point, var_name='x'):
    var=get_var(var_name)
    x=var
    f=parse_expr(expr_str, var_name)
    h=sp.Symbol('h')
    f_xh=sp.simplify(f.subs(x, x+h))
    quotient=sp.simplify((f_xh-f)/h)
    deriv=sp.limit(quotient, h, 0)
    slope=sp.simplify(deriv.subs(x, point))
    f_pt=f.subs(x, point)
    tangent=sp.simplify(f_pt+slope*(x-point))
    steps=[
        ("Definição", f"$$f'({sp.latex(x)}) = \\lim_{{h \\to 0}} \\frac{{f({sp.latex(x)}+h)-f({sp.latex(x)})}}{{h}}$$"),
        ("Calcula f(x+h)", f"$$f({sp.latex(x)}+h) = {sp.latex(f_xh)}$$"),
        ("Quociente das diferenças", f"$$\\frac{{f({sp.latex(x)}+h)-f({sp.latex(x)})}}{{h}} = {sp.latex(quotient)}$$"),
        ("Tomar o limite h→0", f"$$f'({sp.latex(x)}) = \\lim_{{h\\to0}} {sp.latex(quotient)} = {sp.latex(deriv)}$$"),
        ("Inclinação no ponto", f"$$f'({sp.latex(point)}) = {sp.latex(slope)}$$"),
        ("Reta tangente", f"$$y = {sp.latex(tangent)}$$"),
    ]
    final=f"f'({sp.latex(x)}) = {sp.latex(deriv)}, \\quad y = {sp.latex(tangent)}"
    yv=num(f_pt)
    plot={'exprs':[{'expr':for_plot(f,x),'label':'f(x)'},{'expr':for_plot(tangent,x),'label':'tangente','dashed':True,'color':'orange'}],
          'x_min':float(point)-4,'x_max':float(point)+4,'points':[{'x':float(point),'y':yv,'label':f'({point}, {f_pt})'}] if yv is not None else None}
    return steps,final,plot

def render_derivative_limit():
    st.subheader("Derivada — definição por limite")
    def _reset():
        st.session_state["dl_expr"]="x^2"
        st.session_state["dl_point"]=1.0
    expr=st.text_input("f(x)", value="x^2", key="dl_expr")
    point=st.number_input("No ponto x =", value=1.0, key="dl_point")
    st.button("Mostrar exemplo", key="dl_ex", on_click=_reset)
    try:
        steps,final,plot=solve_derivative_limit(expr, point)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_integral_limit(expr_str, a, b, n, var_name='x'):
    var=get_var(var_name)
    x=var
    f=parse_expr(expr_str, var_name)
    a,b,n=float(a),float(b),int(n)
    dx=(b-a)/n
    riemann=sum(float(f.subs(x, a+i*dx))*dx for i in range(1,n+1))
    exact=sp.integrate(f,(x,a,b))
    steps=[
        ("Definição", f"$$\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} {sp.latex(f)}\\,dx = \\lim_{{n\\to\\infty}} \\sum_{{i=1}}^{{n}} f(x_i)\\,\\Delta x$$"),
        ("Largura e pontos", f"$$\\Delta x = \\frac{{{b}-{a}}}{{{n}}} = {dx}, \\quad x_i = {a} + i\\Delta x$$"),
        ("Soma de Riemann (n="+str(n)+")", f"$$S_{{{n}}} = \\sum_{{i=1}}^{{{n}}} f(x_i)\\,\\Delta x = {round(riemann,4)}$$"),
        ("Integral exata", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = {sp.latex(exact)} = {sp.latex(sp.N(exact,5))}$$"),
    ]
    final=f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = {sp.latex(exact)}"
    plot={'exprs':[{'expr':for_plot(f,x),'label':'f(x)'}],'x_min':a-1,'x_max':b+1,'shade':{'expr':for_plot(f,x),'from':a,'to':b}}
    return steps,final,plot

def render_integral_limit():
    st.subheader("Integral — limite das somas de Riemann")
    def _reset():
        st.session_state["il_expr"]="x^2"
        st.session_state["il_a"]=0.0
        st.session_state["il_b"]=2.0
        st.session_state["il_n"]=5
    expr=st.text_input("f(x)", value="x^2", key="il_expr")
    a=st.number_input("Limite inferior a", value=0.0, key="il_a")
    b=st.number_input("Limite superior b", value=2.0, key="il_b")
    n=st.number_input("Retângulos n", value=5, step=1, key="il_n")
    st.button("Mostrar exemplo", key="il_ex", on_click=_reset)
    try:
        steps,final,plot=solve_integral_limit(expr,a,b,n)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_derivative(expr_str, var_name, rule):
    var=get_var(var_name)
    x=var
    f=parse_expr(expr_str, var_name)
    deriv=sp.diff(f,x)
    steps=[("Função", f"$$f({sp.latex(x)}) = {sp.latex(f)}$$")]
    if f.is_Add:
        steps.append(("Regra da soma","Aplique a regra da soma, derivando termo a termo."))
        parts=[]
        for term in sp.Add.make_args(f):
            d=sp.diff(term,x)
            parts.append(f"\\frac{{d}}{{d{sp.latex(x)}}}\\left({sp.latex(term)}\\right) = {sp.latex(d)}")
        steps.append(("Derivando cada termo","$$"+" \\quad ".join(parts)+"$$"))
    else:
        steps.append(("Aplicar regras",f"Aplique a regra **{rule}**."))
    steps.append(("Resultado",f"$$f'({sp.latex(x)}) = {sp.latex(deriv)}$$"))
    final=f"f'({sp.latex(x)}) = {sp.latex(deriv)}"
    plot={'exprs':[{'expr':for_plot(f,x),'label':'f(x)'},{'expr':for_plot(deriv,x),'label':"f'(x)",'dashed':True,'color':'green'}],'x_min':-5,'x_max':5}
    return steps,final,plot

def render_derivative():
    st.subheader("Derivadas — regras")
    def _reset():
        st.session_state["der_expr"]="x^3 + 2*x^2 + sin(x)"
        st.session_state["der_var"]="x"
        st.session_state["der_rule"]="Geral"
    expr=st.text_input("f(variável)", value="x^3 + 2*x^2 + sin(x)", key="der_expr")
    col1,col2=st.columns(2)
    variable=col1.selectbox("Variável", ['x','y','z'], key="der_var")
    rule=col2.selectbox("Regra a demonstrar", ['Geral','Constante','Potência','Soma/Diferença','Produto','Quociente','Cadeia'], key="der_rule")
    st.button("Mostrar exemplo", key="der_ex", on_click=_reset)
    try:
        steps,final,plot=solve_derivative(expr, variable, rule)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_integral(expr_str, var_name, rule, kind, a, b):
    var=get_var(var_name)
    x=var
    f=parse_expr(expr_str, var_name)
    definite=kind=='Definite'
    if definite:
        result=sp.integrate(f,(x,a,b))
        steps=[
            ("Integral", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)}$$"),
            ("Método", f"Regra: **{rule}**."),
            ("Aplicar Teorema Fundamental", f"Encontre a antiderivada F, depois calcule F({b}) − F({a})."),
            ("Resultado", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)}$$"),
        ]
        final=f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)}"
        plot={'exprs':[{'expr':for_plot(f,x),'label':'f(x)'}],'x_min':float(a)-1,'x_max':float(b)+1,'shade':{'expr':for_plot(f,x),'from':float(a),'to':float(b)}}
    else:
        result=sp.integrate(f,x)
        steps=[
            ("Integral", f"$$\\int {sp.latex(f)}\\,d{sp.latex(x)}$$"),
            ("Método", f"Regra: **{rule}**."),
            ("Antiderivada", f"$$\\int {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)} + C$$"),
            ("Verificação", "Derive o resultado para confirmar."),
        ]
        final=f"\\int {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)} + C"
        plot=None
    return steps,final,plot

def render_integral():
    st.subheader("Integrais — regras")
    def _reset():
        st.session_state["int_expr"]="x^2 + 3*x + 2"
        st.session_state["int_var"]="x"
        st.session_state["int_rule"]="Indefinida"
        st.session_state["int_a"]=0.0
        st.session_state["int_b"]=2.0
    expr=st.text_input("Integrando", value="x^2 + 3*x + 2", key="int_expr")
    col1,col2=st.columns(2)
    variable=col1.selectbox("Variável", ['x','y','z'], key="int_var")
    rule=col2.selectbox("Método/regra", ['Primitivas','Substituição','Por partes','Definida','Indefinida','Teorema Fundamental'], key="int_rule")
    definite=rule in ('Definida','Teorema Fundamental')
    a=b=0.0
    if definite:
        a=st.number_input("Limite inferior a", value=0.0, key="int_a")
        b=st.number_input("Limite superior b", value=2.0, key="int_b")
    else:
        a=st.session_state.get("int_a",0.0)
        b=st.session_state.get("int_b",2.0)
    st.button("Mostrar exemplo", key="int_ex", on_click=_reset)
    try:
        steps,final,plot=solve_integral(expr, variable, rule, 'Definite' if definite else 'Indefinite', a, b)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

# Álgebra
def solve_linear(eq_str):
    eq=parse_equation(eq_str)
    x=X
    poly=sp.Poly(eq,x)
    coeffs=poly.all_coeffs()
    if len(coeffs)>2:
        raise ValueError("A equação não é do 1º grau.")
    a=coeffs[0]
    b=coeffs[1] if len(coeffs)==2 else 0
    if a==0:
        raise ValueError("Coeficiente de x é zero — não é equação do 1º grau.")
    root=sp.simplify(-b/a)
    lhs=parse_expr(eq_str.split('=')[0])
    rhs=parse_expr(eq_str.split('=')[1])
    steps=[
        ("Equação original", f"$$ {sp.latex(sp.Eq(lhs, rhs))} $$"),
        ("Forma padrão", f"$$ {sp.latex(a)}\\,x + {sp.latex(b)} = 0 $$"),
        ("Identificar coeficientes", f"$$a = {sp.latex(a)}, \\quad b = {sp.latex(b)}$$"),
        ("Isolar x", f"$$a\\,x = -b \\implies x = \\frac{{-b}}{{a}} = \\frac{{{sp.latex(-b)}}}{{{sp.latex(a)}}}$$"),
        ("Resultado", f"$$x = {sp.latex(root)}$$"),
        ("Verificação", f"Substituindo x = {sp.latex(root)}: {sp.latex(sp.simplify(eq.subs(x, root)))} = 0 ✓"),
    ]
    final=f"x = {sp.latex(root)}"
    rv=num(root)
    plot={'exprs':[{'expr':for_plot(eq,x),'label':'a·x + b'}],'x_min':(rv-5) if rv is not None else -5,'x_max':(rv+5) if rv is not None else 5,'points':[{'x':float(root),'y':0,'label':f'x = {root}','color':'red'}] if rv is not None else None}
    return steps,final,plot

def render_linear():
    st.subheader("Equação linear (1º grau)")
    def _reset():
        st.session_state["lin_eq"]="2*x + 3 = 7"
    eq=st.text_input("Equação", value="2*x + 3 = 7", key="lin_eq")
    st.button("Mostrar exemplo", key="lin_ex", on_click=_reset)
    try:
        steps,final,plot=solve_linear(eq)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_quadratic(eq_str):
    eq=parse_equation(eq_str)
    x=X
    poly=sp.Poly(eq,x)
    coeffs=poly.all_coeffs()
    if len(coeffs)!=3:
        raise ValueError("A equação precisa ser do 2º grau (a·x² + b·x + c).")
    a,b,c=coeffs
    disc=sp.simplify(b**2-4*a*c)
    roots=sp.solve(eq,x)
    lhs=parse_expr(eq_str.split('=')[0])
    rhs=parse_expr(eq_str.split('=')[1])
    steps=[
        ("Equação original", f"$$ {sp.latex(sp.Eq(lhs, rhs))} $$"),
        ("Forma padrão", f"$$ {sp.latex(a)}\\,x^2 + {sp.latex(b)}\\,x + {sp.latex(c)} = 0 $$"),
        ("Coeficientes", f"$$a = {sp.latex(a)}, \\quad b = {sp.latex(b)}, \\quad c = {sp.latex(c)}$$"),
        ("Discriminante", f"$$\\Delta = b^2 - 4ac = {sp.latex(b)}^2 - 4({sp.latex(a)})({sp.latex(c)}) = {sp.latex(disc)}$$"),
        ("Fórmula de Bhaskara", f"$$x = \\frac{{-b \\pm \\sqrt{{\\Delta}}}}{{2a}} = \\frac{{{sp.latex(-b)} \\pm \\sqrt{{{sp.latex(disc)}}}}}{{{sp.latex(2*a)}}}$$"),
        ("Soluções", f"$$x = {sp.latex(roots)}$$"),
    ]
    final="x = "+(", \\quad ".join(sp.latex(r) for r in roots) if isinstance(roots, list) else sp.latex(roots))
    real_roots=[num(r) for r in roots if isinstance(roots, list) and num(r) is not None and abs(num(r).imag)<1e-9]
    pts=[{'x':float(r.real),'y':0.0,'label':f'x={r.real:.3g}'} for r in real_roots] if real_roots else None
    if real_roots:
        cx=sum(r.real for r in real_roots)/len(real_roots)
        span=max(3, max(abs(r.real-cx) for r in real_roots)+2)
        xmin,xmax=cx-span,cx+span
    else:
        xmin,xmax=-5,5
    plot={'exprs':[{'expr':for_plot(eq,x),'label':'a·x² + b·x + c'}],'x_min':xmin,'x_max':xmax,'points':pts}
    return steps,final,plot

def render_quadratic():
    st.subheader("Equação quadrática (2º grau)")
    def _reset():
        st.session_state["quad_eq"]="x^2 - 5*x + 6 = 0"
    eq=st.text_input("Equação", value="x^2 - 5*x + 6 = 0", key="quad_eq")
    st.button("Mostrar exemplo", key="quad_ex", on_click=_reset)
    try:
        steps,final,plot=solve_quadratic(eq)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_system(equations, variables):
    syms=[sp.Symbol(v) for v in variables]
    eqs=[parse_equation(e) for e in equations]
    A,bb=sp.linear_eq_to_matrix(eqs, syms)
    sol=sp.linsolve((A,bb), syms)
    aug=A.row_join(bb)
    rref,pivots=aug.rref()
    cases=[]
    for i in range(A.rows):
        lhs=sp.Add(*[A[i,j]*syms[j] for j in range(len(syms))])
        cases.append(sp.latex(sp.Eq(lhs, bb[i])))
    steps=[
        ("Sistema", "$$\\begin{cases}"+" \\\ ".join(cases)+"\\end{cases}$$"),
        ("Forma matricial", f"$$A = {sp.latex(A)}, \\quad b = {sp.latex(bb)}$$"),
        ("Matriz aumentada [A | b]", f"$$[A \\mid b] = {sp.latex(aug)}$$"),
        ("Forma escalonada (RREF)", f"$$\\text{{RREF}} = {sp.latex(rref)}$$"),
        ("Solução", f"$$({', '.join(str(v) for v in variables)}) = {sp.latex(sol)}$$"),
    ]
    if isinstance(sol, sp.FiniteSet) and sol:
        vals=list(sol)[0]
        verify=[]
        for e in eqs:
            sub=sp.simplify(e.subs(dict(zip(syms, vals))))
            verify.append(f"{sp.latex(e)} → {sp.latex(sub)} = 0"+(" ✓" if sub==0 else ""))
        steps.append(("Verificação","  ".join(verify)))
    final="("+", ".join(str(v) for v in variables)+") = "+sp.latex(sol)
    return steps,final,None

def render_system():
    st.subheader("Sistemas lineares")
    def _reset():
        st.session_state["sys_size"]='2x2'
        st.session_state["sys_e1"]="2*x + 3*y = 5"
        st.session_state["sys_e2"]="x - y = 1"
        st.session_state["sys_e3"]="x + y + z = 6"
    size=st.radio("Tamanho", ['2x2','3x3'], horizontal=True, key="sys_size")
    variables=['x','y'] if size=='2x2' else ['x','y','z']
    eq1=st.text_input("Equação 1", value="2*x + 3*y = 5", key="sys_e1")
    eq2=st.text_input("Equação 2", value="x - y = 1", key="sys_e2")
    eq3=None
    if size=='3x3':
        eq3=st.text_input("Equação 3", value="x + y + z = 6", key="sys_e3")
    st.button("Mostrar exemplo", key="sys_ex", on_click=_reset)
    equations=[eq1,eq2]+([eq3] if size=='3x3' and eq3 else [])
    try:
        steps,final,plot=solve_system(equations, variables)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

# APP PRINCIPAL
st.set_page_config(page_title="CalculusFlow", page_icon="➗", layout="centered")
st.title("CalculusFlow")
st.caption("Companheiro interativo de matemática — aritmética, cálculo e álgebra, passo a passo.")

MODULES={
    "Aritmética":{
        "Adição (vai-um)":render_addition,
        "Subtração (empréstimo)":render_subtraction,
        "Multiplicação longa":render_multiplication,
        "Divisão longa":render_long_division,
    },
    "Cálculo":{
        "Limites":render_limit,
        "Derivada por definição":render_derivative_limit,
        "Integral por somas de Riemann":render_integral_limit,
        "Derivadas (regras)":render_derivative,
        "Integrais (regras)":render_integral,
    },
    "Álgebra":{
        "Equação linear":render_linear,
        "Equação quadrática":render_quadratic,
        "Sistemas lineares":render_system,
    },
}

group=st.sidebar.radio("Área", list(MODULES.keys()))
modules=MODULES[group]
choice=st.sidebar.radio("Módulo", list(modules.keys()))
st.sidebar.markdown("---")
st.sidebar.markdown("Cálculo simbólico com **SymPy** — sem chave de API.")
modules[choice]()
