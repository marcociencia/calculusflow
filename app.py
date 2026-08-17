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

    # GRID 1 = vai-um + operação (sem linha)
    html = f'''
    <div style="display:inline-block; background:#ffffff; padding:14px 22px 10px 22px; border-radius:12px; border:1px solid #e5e7eb;">
      <div style="display:grid; grid-template-columns:repeat({W}, 1.05em); justify-items:center; align-items:end; font-family: ui-monospace, monospace; font-weight:700; font-size:36px; line-height:1.05; column-gap:2px; row-gap:1px;">
        {carry_html}
    '''
    for ch in top_str:
        html+=f'<div>{ch if ch!=" " else ""}</div>'
    for ch in bottom_cells:
        if ch=='+':
            html+=f'<div style="font-size:30px; line-height:1;">+</div>'
        else:
            html+=f'<div>{ch}</div>'
    html+=f'</div>'

    # LINHA SÓLIDA - separação operação / resultado - SÓLIDA PRETA
    html+=f'<div style="width:100%; height:3px; background:#000000; margin:8px 0; border:none; border-radius:0;"></div>'

    # GRID 2 = resultado sólido vermelho
    html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.05em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:36px; line-height:1.05; column-gap:2px;">'
    for ch in total_str.rjust(W):
        html+=f'<div style="color:#dc2626;">{ch if ch!=" " else ""}</div>'
    html+=f'</div></div>'
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
    A_orig = int(st.number_input("Número de cima", value=5003, step=1, key="sub_A"))
    B_orig = int(st.number_input("Número de baixo", value=2897, step=1, key="sub_B"))
    st.button("Mostrar exemplo", key="sub_ex", on_click=_reset)

    # Usa valores originais para saber se é negativo
    is_negative = A_orig < B_orig
    # Para visualização, sempre usa maior em cima para mostrar empréstimo
    larger = max(A_orig, B_orig)
    smaller = min(A_orig, B_orig)

    d = subtract_armada(larger, smaller)  # d['larger'] = larger, d['smaller']=smaller, result = larger-smaller
    # Resultado real com sinal
    real_result = A_orig - B_orig

    W = len(str(larger))
    # Se negativo, precisa de 1 coluna extra para o sinal -
    if is_negative:
        W_display = W + 1
    else:
        W_display = W

    top_digits = list(map(int, str(larger)))
    bottom_digits = list(map(int, str(smaller).rjust(len(str(larger)), '0')))
    N = len(top_digits)

    # Calcula as duas linhas pequenas de empréstimo (9 9 e 1 10 10 13) como na imagem ideal
    working = top_digits[:]
    upper_small = ['']*N  # 9 9
    lower_small = ['']*N  # 4 10 10 13
    # Para rastrear quais colunas foram emprestadas
    borrowed_cols = set()

    for i in range(N-1, -1, -1):
        if working[i] < bottom_digits[i]:
            j = i-1
            while j >=0 and working[j]==0:
                j-=1
            if j>=0:
                # marca 9s intermediários
                for k in range(j+1, i):
                    upper_small[k]='9'
                    lower_small[k]='10'
                    borrowed_cols.add(k)
                # j vira working[j]-1
                lower_small[j]=str(working[j]-1)
                borrowed_cols.add(j)
                # i vira +10
                lower_small[i]=str(working[i]+10)
                borrowed_cols.add(i)

                working[j]-=1
                for k in range(j+1, i):
                    working[k]=9
                working[i]+=10

    # Se não houve empréstimo em cadeia de zeros, preenche lower com valores finais onde houve empréstimo simples
    # (caso 5003 já foi tratado acima)
    # Garante que colunas com empréstimo simples também mostrem valor final
    for idx in range(N):
        if idx in borrowed_cols and lower_small[idx]=='':
            # se foi doador mas não preenchido
            if idx in d['lent_by']:
                lower_small[idx]=str(d['lent_by'][idx]['newValue'])
        if d['columns'][idx]['borrowedFrom'] is not None and lower_small[idx]=='':
            lower_small[idx]=str(d['columns'][idx]['displayedTop'])

    # HTML com linhas sólidas
    # Usa W_display para acomodar sinal negativo
    offset = W_display - N  # deslocamento para alinhar à direita quando tem coluna extra

    html = f'''
    <div style="display:inline-block; background:#ffffff; padding:14px 22px 10px 22px; border-radius:12px; border:1px solid #e5e7eb;">
      <div style="display:grid; grid-template-columns:repeat({W_display}, 1.6em); justify-items:center; align-items:end; font-family: ui-monospace, monospace; font-weight:700; font-size:15px; line-height:1.0; column-gap:1px;">
    '''
    # linha 9 9 (superior)
    for i in range(W_display):
        if i < offset:
            html+=f'<div style="height:18px;"></div>'
        else:
            idx = i - offset
            ch = upper_small[idx]
            if ch:
                html+=f'<div style="color:#3b82f6; height:18px; display:flex; align-items:flex-end; justify-content:center;">{ch}</div>'
            else:
                html+=f'<div style="height:18px;"></div>'
    html+='</div>'

    # linha 4 10 10 13
    html+=f'<div style="display:grid; grid-template-columns:repeat({W_display}, 1.6em); justify-items:center; align-items:end; font-family: ui-monospace, monospace; font-weight:700; font-size:15px; line-height:1.0; column-gap:1px; margin-top:2px;">'
    for i in range(W_display):
        if i < offset:
            html+=f'<div style="height:18px;"></div>'
        else:
            idx = i - offset
            ch = lower_small[idx]
            if ch:
                # cor roxa para 10,13 e azul para 4? usa roxo como na imagem ideal
                color = "#7c3aed" if ch in ("10","13","10") else "#7c3aed"
                html+=f'<div style="color:{color}; height:18px; display:flex; align-items:flex-end; justify-content:center;">{ch}</div>'
            else:
                html+=f'<div style="height:18px;"></div>'
    html+='</div>'

    # linha do número original riscado
    html+=f'<div style="display:grid; grid-template-columns:repeat({W_display}, 1.6em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:34px; line-height:1.05; column-gap:1px; margin-top:2px;">'
    for i in range(W_display):
        if i < offset:
            # coluna extra para sinal negativo no topo? deixa vazia
            if is_negative and i==0:
                html+=f'<div></div>'
            else:
                html+=f'<div></div>'
        else:
            idx = i - offset
            ch = str(larger)[idx] if idx < len(str(larger)) else ''
            # riscado se houve empréstimo nessa coluna
            if idx in borrowed_cols:
                html+=f'<div style="position:relative;">{ch}<span style="position:absolute; left:-10%; top:52%; width:120%; height:2.5px; background:#111; transform:rotate(-16deg);"></span></div>'
            else:
                html+=f'<div>{ch}</div>'
    html+='</div>'

    # linha de baixo - 2897 com -
    html+=f'<div style="display:grid; grid-template-columns:repeat({W_display}, 1.6em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:34px; line-height:1.05; column-gap:1px;">'
    for i in range(W_display):
        if i < offset:
            if i==offset-1:  # posição do sinal - da operação
                html+=f'<div style="font-size:28px;">−</div>'
            else:
                html+=f'<div></div>'
        else:
            idx = i - offset
            # bottom com - na primeira coluna do número
            if idx==0 and offset>0:
                # já mostramos - acima, mas para W sem offset, mostra - na coluna 0
                pass
            # para caso sem offset, mostra - na coluna 0
            if W_display==N and i==0:
                # precisa mostrar - e primeiro dígito? Na imagem ideal - está antes do número
                # Vamos mostrar - na coluna 0 e número deslocado? Simplifica: mostra - na coluna 0 se for a primeira
                # Na verdade para W==N, queremos "- 2897" com - na coluna 0
                if i==0:
                    html+=f'<div style="font-size:28px;">−</div>'
                else:
                    b_ch = str(smaller).rjust(N)[idx]
                    html+=f'<div>{b_ch if b_ch.strip()!="" else ""}</div>'
            else:
                if i==offset: # quando tem coluna extra, o - já foi no offset-1, agora mostra dígitos
                    b_ch = str(smaller).rjust(N)[idx] if idx < N else ''
                    html+=f'<div>{b_ch if b_ch.strip()!="" else ""}</div>'
                else:
                    b_ch = str(smaller).rjust(N)[idx] if idx < N else ''
                    if offset==0 and i==0:
                        # sem coluna extra, já mostramos - acima? para evitar duplicar, mostra dígito a partir de i=1
                        # Mas vamos refazer lógica simples:
                        html+=f'<div>{b_ch if b_ch.strip()!="" else ""}</div>'
                    else:
                        html+=f'<div>{b_ch if b_ch.strip()!="" else ""}</div>'
    # corrige bottom row quando offset==0 (caso sem negativo): precisa - na coluna 0
    # Vamos reconstruir bottom de forma simples para evitar confusão:
    html+='</div>'
    # Se offset==0, o grid acima não mostrou - corretamente, refaz bottom simples:
    if W_display==N:
        # recria bottom row correta com - no início
        html = html[:-6]  # remove fechamento anterior? melhor recriar tudo de forma mais simples
        # Na verdade vamos ignorar e criar novo HTML final para bottom
        pass

    # Para simplificar e garantir visual idêntico à imagem ideal, reconstrói bottom e linha final de forma limpa:
    # Vamos fechar e reabrir com lógica limpa para bottom:
    # O código acima já fechou, vamos continuar com linha sólida

    # LINHA SÓLIDA
    html+=f'<div style="width:100%; height:3px; background:#000000; margin:8px 0; border:none;"></div>'

    # Resultado com sinal negativo se necessário
    html+=f'<div style="display:grid; grid-template-columns:repeat({W_display}, 1.6em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:34px; line-height:1.05;">'
    result_str_display = (f"-{abs(real_result)}" if is_negative else str(abs(real_result))).rjust(W_display)
    for ch in result_str_display:
        if ch.strip()=='':
            html+=f'<div></div>'
        elif ch=='-':
            html+=f'<div style="color:#dc2626;">−</div>'
        else:
            html+=f'<div style="color:#dc2626;">{ch}</div>'
    html+='</div></div>'

    # Corrige bottom row visual para caso simples (sem offset) - re-renderiza tudo de forma correta para o caso mais comum 5003-2897
    # Para não complicar, se W_display==N (sem negativo), vamos gerar HTML final limpo e sobrescrever
    if not is_negative:
        # Recria HTML limpo para o caso positivo (igual imagem ideal)
        Wc = N
        top_clean = str(larger)
        bottom_clean = str(smaller)
        # upper e lower já calculados
        html_clean = f'''
        <div style="display:inline-block; background:#ffffff; padding:14px 22px 10px 22px; border-radius:12px; border:1px solid #e5e7eb;">
          <div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:14px; color:#3b82f6;">
        '''
        for ch in upper_small:
            html_clean+=f'<div style="height:18px;">{ch}</div>'
        html_clean+='</div>'
        html_clean+=f'<div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:14px; color:#7c3aed; margin-top:2px;">'
        for ch in lower_small:
            html_clean+=f'<div style="height:18px;">{ch}</div>'
        html_clean+='</div>'
        html_clean+=f'<div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:34px;">'
        for i,ch in enumerate(top_clean):
            if i in borrowed_cols:
                html_clean+=f'<div style="position:relative;">{ch}<span style="position:absolute; left:-8%; top:52%; width:116%; height:2.5px; background:#111; transform:rotate(-16deg);"></span></div>'
            else:
                html_clean+=f'<div>{ch}</div>'
        html_clean+='</div>'
        html_clean+=f'<div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:34px;">'
        # linha com - 2897
        html_clean+=f'<div style="font-size:28px;">−</div>'
        for i,ch in enumerate(bottom_clean.rjust(Wc-1)):
            html_clean+=f'<div>{ch if ch.strip()!="" else ""}</div>'
        html_clean+='</div>'
        html_clean+=f'<div style="width:100%; height:3px; background:#000; margin:8px 0;"></div>'
        html_clean+=f'<div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:34px; color:#dc2626;">'
        for ch in str(abs(real_result)).rjust(Wc):
            html_clean+=f'<div>{ch if ch.strip()!="" else ""}</div>'
        html_clean+='</div></div>'
        html = html_clean

    html+= f'<div style="margin-top:10px; font-size:18px; font-weight:600;">{A_orig} − {B_orig} = <span style="color:#dc2626">{real_result}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("**Passo a passo — cada coluna**")
    lines=[]
    for c in d['columns']:
        if c['borrowedFrom'] is not None:
            lines.append(f"Empresta 1 da coluna {c['borrowedFrom']+1}: {c['originalTop']} → {c['displayedTop']}, então {c['displayedTop']} − {c['bottom']} = **{c['result']}**")
        else:
            lines.append(f"Coluna {c['index']+1}: {c['originalTop']} − {c['bottom']} = **{c['result']}**")
    if is_negative:
        lines.append(f"Como {A_orig} < {B_orig}, o resultado é negativo: **{real_result}**")
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
        st.session_state["mul_B"]=563
    A = int(st.number_input("Multiplicando (cima)", value=234, step=1, key="mul_A"))
    B = int(st.number_input("Multiplicador (baixo)", value=563, step=1, key="mul_B"))
    st.button("Mostrar exemplo", key="mul_ex", on_click=_reset)

    # Calcula produto
    product = A * B
    top_str_raw = str(A)
    bottom_str_raw = str(B)
    prod_str_raw = str(product)

    # W para acomodar parciais deslocadas + sinal +
    W = len(prod_str_raw) + 1
    W = max(W, len(top_str_raw)+1, len(bottom_str_raw)+1)
    # Garante espaço para deslocamento máximo
    W = max(W, len(top_str_raw) + len(bottom_str_raw))

    # Cores por dígito do multiplicador (da direita para esquerda)
    colors = ["#7c3aed", "#ca8a04", "#16a34a", "#2563eb", "#db2777"]  # roxo, amarelo, verde, azul, rosa

    # Calcula carries por dígito do multiplicador
    bottom_digits = list(map(int, bottom_str_raw))
    top_digits = list(map(int, top_str_raw))
    L = len(top_str_raw)

    carry_rows = []  # lista de dict {digit, color, carry_display list len L}
    partials = []   # lista de {digit, color, cells W, value}

    for idx_b in range(len(bottom_digits)-1, -1, -1):  # da direita para esquerda
        dgt = bottom_digits[idx_b]
        color = colors[(len(bottom_digits)-1 - idx_b) % len(colors)]

        # carries para este dígito
        carry = 0
        carry_display = ['']*L
        for i in range(L-1, -1, -1):
            prod = top_digits[i]*dgt + carry
            carry = prod // 10
            if i>0:
                if carry>0:
                    carry_display[i-1]=str(carry)
            # se i==0, carry extra vira parte do parcial, não é mostrado como vai-um
        carry_rows.append({'digit':dgt, 'color':color, 'display':carry_display})

        # parcial
        partial_val = A * dgt
        partial_str = str(partial_val)
        shift = (len(bottom_digits)-1 - idx_b)
        cells = ['']*W
        # posiciona partial_str com deslocamento
        # rightmost = W-1-shift
        for j,ch in enumerate(reversed(partial_str)):
            pos = W-1-shift-j
            if pos>=0:
                cells[pos]=ch
        partials.append({'digit':dgt, 'color':color, 'cells':cells, 'value':partial_val, 'shift':shift})

    # Inverte carry_rows para exibir do mais significativo no topo (como na imagem)
    carry_rows_display = list(reversed(carry_rows))

    # HTML
    html = f'''
    <div style="display:inline-block; background:#ffffff; padding:14px 22px 10px 22px; border-radius:12px; border:1px solid #e5e7eb;">
    '''

    # Carries - cada linha com sua cor
    for cr in carry_rows_display:
        html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:13px; color:{cr["color"]}; line-height:1.0;">'
        # deslocamento para alinhar à direita com top
        offset = W - L
        for i in range(W):
            if i < offset:
                html+=f'<div style="height:16px;"></div>'
            else:
                idx = i - offset
                ch = cr["display"][idx] if idx < len(cr["display"]) else ''
                html+=f'<div style="height:16px;">{ch}</div>'
        html+='</div>'

    # Top e bottom
    html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:32px; line-height:1.05; margin-top:4px;">'
    for ch in top_str_raw.rjust(W):
        html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html+='</div>'
    html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:32px; line-height:1.05;">'
    # linha com x
    bottom_padded = bottom_str_raw.rjust(W)
    x_pos = W - len(bottom_str_raw) -1
    for i,ch in enumerate(bottom_padded):
        if i==x_pos:
            html+=f'<div style="font-size:26px;">×</div>'
        else:
            html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html+='</div>'

    # Linha sólida 1
    html+=f'<div style="width:100%; height:2px; background:#000; margin:6px 0;"></div>'

    # Parciais com cores
    html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:28px; line-height:1.1; row-gap:2px;">'
    # Primeiro parcial sem +, segundo com 0 pequeno, terceiro com + etc - para simplificar, todos com cor, último com +
    for p_idx, p in enumerate(partials):
        # para o último parcial (mais significativo), adiciona + antes
        is_last = (p_idx == len(partials)-1)
        for i,ch in enumerate(p['cells']):
            if ch=='':
                # se é último e é a posição antes do primeiro dígito, mostra + ?
                if is_last and i==0:
                    # procura primeiro dígito não vazio
                    first_non_empty = next((j for j,c in enumerate(p['cells']) if c!=''), None)
                    if first_non_empty is not None and i==first_non_empty-1 and first_non_empty>0:
                        html+=f'<div style="color:{p["color"]}; font-size:24px;">+</div>'
                    else:
                        html+=f'<div></div>'
                else:
                    # para segunda parcial, mostra 0 pequeno como na imagem?
                    # se shift>0 e i == W-1 (última coluna vazia por shift), mostra 0 cinza pequeno
                    if p['shift']>0 and i==W-1:
                        html+=f'<div style="color:#9ca3af; font-size:18px;">0</div>' if p['shift']==1 else f'<div></div>'
                    else:
                        html+=f'<div></div>'
            else:
                if is_last:
                    # último parcial com +? já tratamos, agora mostra dígito verde com +
                    # se for a primeira coluna do parcial e é último, mostra com + antes? Simplifica: mostra dígito normal, mas adiciona + na coluna anterior já feito
                    html+=f'<div style="color:{p["color"]};">{ch}</div>'
                else:
                    html+=f'<div style="color:{p["color"]};">{ch}</div>'
        # quebra de linha automática pelo grid? Na verdade estamos em um único grid com W colunas, mas precisamos de nova linha a cada W células
        # Como estamos usando um único grid para todos parciais, precisamos garantir que a cada W células quebra
        # O grid com repeat(W, ...) já quebra automaticamente a cada W itens
    html+='</div>'

    # Ajuste visual para + no último parcial - recria de forma mais fiel à imagem
    # Vamos recriar a seção de parciais de forma separada por linhas para ter + e 0
    # Para ficar idêntico à imagem 234x563, vamos fazer HTML custom:
    html_partials_custom = ''
    # Para o exemplo 234x563, queremos:
    # 702 roxo
    # 0 1404 amarelo com 1 pequeno
    # + 1170 verde
    # Vamos implementar lógica geral:
    html_partials_custom += f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:28px;">'
    # Parcial 1 (unidades)
    p0 = partials[0]
    for ch in p0['cells']:
        if ch=='':
            html_partials_custom+=f'<div></div>'
        else:
            html_partials_custom+=f'<div style="color:{p0["color"]};">{ch}</div>'
    html_partials_custom+='</div>'

    if len(partials)>=2:
        p1 = partials[1]
        # segunda linha com um pequeno 1 acima e 0 no final como na imagem?
        # Mostra "1" pequeno no canto esquerdo da parcial?
        html_partials_custom+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:28px; position:relative;">'
        for i,ch in enumerate(p1['cells']):
            if ch=='' and i==W-1:
                html_partials_custom+=f'<div style="color:#111; font-size:16px; opacity:0.7;">0</div>'
            elif ch=='':
                if i==W-p1["shift"]-len(str(p1["value"]))-1:
                    html_partials_custom+=f'<div style="font-size:14px; color:#111;">1</div>'
                else:
                    html_partials_custom+=f'<div></div>'
            else:
                html_partials_custom+=f'<div style="color:{p1["color"]};">{ch}</div>'
        html_partials_custom+='</div>'

    if len(partials)>=3:
        p2 = partials[2]
        html_partials_custom+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:28px;">'
        # + na primeira coluna
        first_idx = next((i for i,c in enumerate(p2['cells']) if c!=''), 0)
        for i,ch in enumerate(p2['cells']):
            if i==first_idx-1 and first_idx>0:
                html_partials_custom+=f'<div style="color:{p2["color"]}; font-size:24px;">+</div>'
            elif ch=='':
                html_partials_custom+=f'<div></div>'
            else:
                html_partials_custom+=f'<div style="color:{p2["color"]};">{ch}</div>'
        html_partials_custom+='</div>'

    # Se tiver mais de 3 parciais, mostra genérico
    if len(partials)>3:
        for p in partials[3:]:
            html_partials_custom+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:28px;">'
            for ch in p['cells']:
                html_partials_custom+=f'<div style="color:{p["color"]};">{ch}</div>' if ch!='' else '<div></div>'
            html_partials_custom+='</div>'

    # Substitui a seção de parciais anterior pelo custom
    # Para isso, vamos fechar o html anterior e usar o custom
    html = f'''
    <div style="display:inline-block; background:#ffffff; padding:14px 22px 10px 22px; border-radius:12px; border:1px solid #e5e7eb;">
    '''
    for cr in carry_rows_display:
        html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:13px; color:{cr["color"]};">'
        offset = W - L
        for i in range(W):
            if i < offset:
                html+=f'<div style="height:16px;"></div>'
            else:
                idx = i - offset
                ch = cr["display"][idx] if idx < len(cr["display"]) else ''
                html+=f'<div style="height:16px;">{ch}</div>'
        html+='</div>'
    html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:32px; margin-top:4px;">'
    for ch in top_str_raw.rjust(W):
        html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html+='</div>'
    html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:32px;">'
    for i,ch in enumerate(bottom_str_raw.rjust(W)):
        if i==W-len(bottom_str_raw)-1:
            html+=f'<div style="font-size:26px;">×</div>'
        else:
            html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html+='</div>'
    html+=f'<div style="width:100%; height:2px; background:#000; margin:6px 0;"></div>'
    html+= html_partials_custom
    html+=f'<div style="width:100%; height:3px; background:#000; margin:8px 0;"></div>'
    html+=f'<div style="display:grid; grid-template-columns:repeat({W}, 1.3em); justify-items:center; font-family: ui-monospace, monospace; font-weight:700; font-size:34px; color:#dc2626;">'
    for ch in prod_str_raw.rjust(W):
        html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html+='</div></div>'

    html+= f'<div style="margin-top:10px; font-size:18px; font-weight:600;">{A} × {B} = <span style="color:#dc2626">{product}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("**Passo a passo**")
    lines=[]
    for p in partials:
        lines.append(f"{A} × {p['digit']} = {A*p['digit']} (parcial, deslocado {p['shift']} casa(s)) - cor {p['color']}")
    lines.append(f"**Produto final = {product}**")
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
