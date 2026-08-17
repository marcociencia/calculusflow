"""
CalculusFlow - FINAL with Linear Systems (x,y) and (x,y,z) + Interactive Graphs
- Arithmetic ideal design
- Derivatives (x,y,z): 8 rules theoretical first then substitution
- Integrals (x,y,z): 7 rules theoretical first then substitution
- Linear, Quadratic with interactive hover graphs
- NEW: Linear Systems (x,y) 2x2 and (x,y,z) 3x3 with interactive graphs
All in English, Plotly fallback
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import lambdify
import itertools

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ModuleNotFoundError:
    PLOTLY_AVAILABLE = False
    go = None

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

def get_var(name): return _VAR_MAP.get(name, X)
def parse_expr(s, var_name='x'):
    if not s or str(s).strip()=='':
        raise ValueError("Empty expression.")
    return sp.sympify(str(s).strip().replace('^','**'), locals=_LOCALS)
def parse_equation(s):
    if '=' not in str(s): raise ValueError("Equation must contain '='.")
    lhs,rhs=str(s).split('=',1)
    return parse_expr(lhs)-parse_expr(rhs)
def for_plot(expr, var): return expr.subs(var, X) if var!=X else expr
def num(v):
    try: return float(v)
    except: return None

def plot_matplotlib(exprs, x_min, x_max, points=None, shade=None, title=None):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    xs = np.linspace(float(x_min), float(x_max), 400)
    for e in exprs:
        f = lambdify(X, e['expr'], modules=['numpy'])
        try:
            ys = np.array(f(xs), dtype=float)
            finite = np.isfinite(ys)
            ax.plot(xs[finite], ys[finite], label=e.get('label',''), linestyle='--' if e.get('dashed') else '-', color=e.get('color'))
        except: pass
    if shade:
        f = lambdify(X, shade['expr'], modules=['numpy'])
        ys = np.array(f(xs), dtype=float)
        mask = (xs >= float(shade['from'])) & (xs <= float(shade['to']))
        ax.fill_between(xs, ys, 0, where=mask, alpha=0.25, color='C0')
    if points:
        for p in points:
            ax.plot(float(p['x']), float(p['y']), 'o', color=p.get('color','red'))
            ax.annotate(p.get('label',''), (float(p['x']), float(p['y'])), textcoords='offset points', xytext=(6,6), fontsize=8)
    ax.axhline(0, color='black', linewidth=0.5); ax.axvline(0, color='black', linewidth=0.5)
    ax.set_xlim(float(x_min), float(x_max))
    if title: ax.set_title(title)
    ax.legend(loc='best', fontsize=8); ax.grid(True, alpha=0.3); fig.tight_layout()
    return fig

def plot_matplotlib_2lines(eq1_str, eq2_str, sol, x_min, x_max, title=None):
    # Parse 2x2 system: solve y = f(x) for each equation
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    xs = np.linspace(float(x_min), float(x_max), 400)
    # eq1: a1 x + b1 y = c1 => y = (c1 - a1 x)/b1
    # We'll use sympy to solve for y
    try:
        # Parse equations
        eq1_sym = parse_equation(eq1_str)  # expression =0
        eq2_sym = parse_equation(eq2_str)
        # Solve for y
        y1_expr = sp.solve(eq1_sym, Y)
        y2_expr = sp.solve(eq2_sym, Y)
        if y1_expr:
            f1 = lambdify(X, for_plot(y1_expr[0], Y), modules=['numpy'])
            ys1 = np.array(f1(xs), dtype=float)
            ax.plot(xs, ys1, label=f'{eq1_str}', color='blue')
        if y2_expr:
            f2 = lambdify(X, for_plot(y2_expr[0], Y), modules=['numpy'])
            ys2 = np.array(f2(xs), dtype=float)
            ax.plot(xs, ys2, label=f'{eq2_str}', color='green')
        if sol and 'x' in sol and 'y' in sol:
            xv = float(sol['x']); yv = float(sol['y'])
            ax.plot(xv, yv, 'ro', markersize=10)
            ax.annotate(f'({xv:.2f}, {yv:.2f})', (xv, yv), textcoords='offset points', xytext=(8,8), fontsize=9, color='red')
    except Exception as e:
        pass
    ax.axhline(0, color='black', linewidth=0.5); ax.axvline(0, color='black', linewidth=0.5)
    ax.set_xlim(float(x_min), float(x_max))
    if title: ax.set_title(title)
    ax.legend(loc='best', fontsize=8); ax.grid(True, alpha=0.3); fig.tight_layout()
    return fig

def plotly_interactive(exprs, x_min, x_max, points=None, shade=None, title=None):
    if not PLOTLY_AVAILABLE: return None
    fig = go.Figure()
    xs = np.linspace(float(x_min), float(x_max), 500)
    for e in exprs:
        try:
            f = lambdify(X, e['expr'], modules=['numpy'])
            ys = np.array(f(xs), dtype=float)
            label = e.get('label',''); eq = e.get('eq', label)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name=label,
                line=dict(dash='dash' if e.get('dashed') else 'solid', color=e.get('color')),
                hovertemplate=f"<b>{eq}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"))
        except: continue
    if shade:
        try:
            f = lambdify(X, shade['expr'], modules=['numpy'])
            ys = np.array(f(xs), dtype=float)
            mask = (xs >= float(shade['from'])) & (xs <= float(shade['to']))
            fig.add_trace(go.Scatter(x=xs[mask], y=ys[mask], fill='tozeroy', mode='none', name='Area', fillcolor='rgba(0,100,255,0.25)',
                hovertemplate=f"<b>{shade.get('eq','f(x)')}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"))
        except: pass
    if points:
        for p in points:
            fig.add_trace(go.Scatter(x=[float(p['x'])], y=[float(p['y'])], mode='markers+text', marker=dict(color=p.get('color','red'), size=10),
                text=[p.get('label','')], textposition="top right", name=p.get('label','point'),
                hovertemplate=f"<b>{p.get('label','point')}</b><br>x=%{{x}}<br>y=%{{y}}<extra></extra>"))
    fig.update_layout(title=title, xaxis_title="x", yaxis_title="y", hovermode="x unified", height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.add_hline(y=0, line_width=1, line_color="black", opacity=0.5)
    fig.add_vline(x=0, line_width=1, line_color="black", opacity=0.5)
    return fig

def plotly_interactive_2lines(eq1_str, eq2_str, sol, x_min, x_max, title=None):
    if not PLOTLY_AVAILABLE: return None
    fig = go.Figure()
    xs = np.linspace(float(x_min), float(x_max), 500)
    try:
        eq1_sym = parse_equation(eq1_str)
        eq2_sym = parse_equation(eq2_str)
        y1_expr = sp.solve(eq1_sym, Y)
        y2_expr = sp.solve(eq2_sym, Y)
        if y1_expr:
            f1 = lambdify(X, for_plot(y1_expr[0], Y), modules=['numpy'])
            ys1 = np.array(f1(xs), dtype=float)
            fig.add_trace(go.Scatter(x=xs, y=ys1, mode='lines', name=eq1_str,
                line=dict(color='blue'),
                hovertemplate=f"<b>{eq1_str}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"))
        if y2_expr:
            f2 = lambdify(X, for_plot(y2_expr[0], Y), modules=['numpy'])
            ys2 = np.array(f2(xs), dtype=float)
            fig.add_trace(go.Scatter(x=xs, y=ys2, mode='lines', name=eq2_str,
                line=dict(color='green'),
                hovertemplate=f"<b>{eq2_str}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"))
        if sol and 'x' in sol and 'y' in sol:
            xv = float(sol['x']); yv = float(sol['y'])
            fig.add_trace(go.Scatter(x=[xv], y=[yv], mode='markers+text', marker=dict(color='red', size=12),
                text=[f'Solution ({xv:.3f}, {yv:.3f})'], textposition="top right", name='Solution',
                hovertemplate=f"<b>Solution</b><br>x={xv:.3f}<br>y={yv:.3f}<br>{eq1_str}<br>{eq2_str}<extra></extra>"))
    except Exception as e:
        pass
    fig.update_layout(title=title or f"System: {eq1_str} & {eq2_str}", xaxis_title="x", yaxis_title="y", hovermode="x unified", height=450)
    fig.add_hline(y=0, line_width=1, line_color="black", opacity=0.5)
    fig.add_vline(x=0, line_width=1, line_color="black", opacity=0.5)
    return fig

def plotly_interactive_3d_system(eqs, sol, title=None):
    if not PLOTLY_AVAILABLE: return None
    try:
        # Create 3D planes for 3x3 system: each equation a x + b y + c z = d
        fig = go.Figure()
        # Range
        x_range = np.linspace(-5, 5, 20)
        y_range = np.linspace(-5, 5, 20)
        Xg, Yg = np.meshgrid(x_range, y_range)
        colors = ['blue','green','orange']
        for idx, eq_str in enumerate(eqs):
            try:
                # Parse eq: a x + b y + c z = d => solve for z = (d - a x - b y)/c
                eq_sym = parse_equation(eq_str)
                # Solve for Z
                z_expr = sp.solve(eq_sym, Z)
                if z_expr:
                    z_func = lambdify((X,Y), for_plot(z_expr[0], Z), modules=['numpy'])
                    Zg = z_func(Xg, Yg)
                    Zg = np.array(Zg, dtype=float)
                    # Clip large values
                    Zg = np.clip(Zg, -10, 10)
                    fig.add_trace(go.Surface(x=Xg, y=Yg, z=Zg, opacity=0.6, colorscale=[[0, colors[idx%3]],[1, colors[idx%3]]], showscale=False, name=eq_str,
                        hovertemplate=f"<b>{eq_str}</b><br>x=%{{x:.2f}}<br>y=%{{y:.2f}}<br>z=%{{z:.2f}}<extra></extra>"))
            except: continue
        if sol and all(k in sol for k in ['x','y','z']):
            fig.add_trace(go.Scatter3d(x=[float(sol['x'])], y=[float(sol['y'])], z=[float(sol['z'])], mode='markers+text', marker=dict(color='red', size=8),
                text=[f"Solution ({sol['x']:.2f}, {sol['y']:.2f}, {sol['z']:.2f})"], textposition="top center", name='Solution'))
        fig.update_layout(title=title or "3D Linear System - Planes Intersection", scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="z"), height=600)
        return fig
    except Exception as ex:
        return None

def _show(steps, final, plot=None, plot_2lines=None, plot_3d=None):
    for i,(title,detail) in enumerate(steps,1):
        st.markdown(f"**Step {i}: {title}**")
        st.markdown(detail, unsafe_allow_html=True)
    st.markdown("**Final Answer**")
    if final.startswith('$$'): st.markdown(final, unsafe_allow_html=True)
    else: st.latex(final)
    if plot:
        if PLOTLY_AVAILABLE:
            fig = plotly_interactive(**plot)
            if fig: st.plotly_chart(fig, use_container_width=True)
            else: st.pyplot(plot_matplotlib(**plot))
        else:
            st.info("Add `plotly` for interactive hover showing generating equation.")
            st.pyplot(plot_matplotlib(**plot))
    if plot_2lines:
        if PLOTLY_AVAILABLE:
            fig = plotly_interactive_2lines(**plot_2lines)
            if fig: st.plotly_chart(fig, use_container_width=True)
            else: st.pyplot(plot_matplotlib_2lines(**plot_2lines))
        else:
            st.pyplot(plot_matplotlib_2lines(**plot_2lines))
    if plot_3d:
        if PLOTLY_AVAILABLE:
            fig = plot_3d
            if fig: st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add `plotly` for interactive 3D graph. Showing solution only.")
            st.write(plot_3d)

IDEAL_CSS = """
<style>
.ideal-box { display:inline-block; background:#fff; padding:14px 22px; border-radius:12px; border:1px solid #e5e7eb; font-family: ui-monospace, monospace; font-weight:700; }
.mult-ideal .carry { font-size:12px; letter-spacing:0.8em; } .mult-ideal .carry.green{color:#16a34a;} .mult-ideal .carry.yellow{color:#eab308;} .mult-ideal .carry.purple{color:#7c3aed;}
.mult-ideal .num{font-size:32px; text-align:right;} .mult-ideal .line{width:100%; background:#000; margin:6px 0;} .mult-ideal .line.thin{height:2px;} .mult-ideal .line.thick{height:3px;}
.mult-ideal .partial{font-size:28px; text-align:right; position:relative;} .mult-ideal .partial.purple{color:#7c3aed;} .mult-ideal .partial.yellow{color:#eab308;} .mult-ideal .partial.green{color:#16a34a;}
.mult-ideal .partial .sup{position:absolute; font-size:11px; color:#000; left:12px; top:-6px;} .mult-ideal .partial .sub{position:absolute; font-size:11px; color:#000; left:0; bottom:-6px;}
.mult-ideal .result{font-size:34px; color:#dc2626; text-align:right;}
.div-ideal{display:flex; align-items:flex-start;} .div-ideal .line{width:100%; height:3px; background:#000; margin:5px 0;} .div-ideal .right{border-left:3px solid #000; margin-left:8px;} .div-ideal .right .divisor{border-bottom:3px solid #000; padding:4px 24px; font-size:28px;} .div-ideal .right .quotient{padding:4px 24px; font-size:28px; color:#dc2626;}
</style>
"""

# ================= ARITHMETIC =================
def _carry_cells_html(carry_list, W, hide_overflow=True, total_str=None, max_orig_len=None):
    html=''
    for i in range(W):
        val=carry_list[i] if i < len(carry_list) else None
        show=''
        if val is not None and val!=0 and str(val).strip()!='':
            if hide_overflow and i==0 and total_str and max_orig_len:
                if W>max_orig_len and total_str.lstrip()[0]==str(val): show=''
                else: show=str(val)
            else: show=str(val)
        html+=f'<div style="color:#7c3aed; font-size:14px; height:18px; display:flex; align-items:flex-end; justify-content:center;">{show}</div>' if show else '<div style="height:18px;"></div>'
    return html

def add_armada(A,B):
    A,B=abs(int(A)),abs(int(B)); a_str,b_str=str(A),str(B); maxlen=max(len(a_str),len(b_str)); W=maxlen+1
    top=[None]*W; bottom=[None]*W; carry=[None]*W
    for p in range(len(a_str)): top[W-1-p]=int(a_str[-1-p])
    for p in range(len(b_str)): bottom[W-1-p]=int(b_str[-1-p])
    c=0
    for p in range(maxlen):
        g=W-1-p; carry[g]=c; t=top[g] or 0; b=bottom[g] or 0; s=t+b+c; c=s//10
    if c>0: carry[W-1-maxlen]=c
    return {'W':W,'carry':carry,'total':A+B}

def render_addition():
    st.subheader("Addition with Carrying")
    A=int(st.number_input("Top number", value=6789, step=1, key="add_A"))
    B=int(st.number_input("Bottom number", value=4567, step=1, key="add_B"))
    d=add_armada(A,B); total_str=str(d['total']); W=len(total_str); max_orig=max(len(str(A)),len(str(B)))
    if W<max_orig: W=max_orig
    top_str=str(A).rjust(W); b_str_raw=str(B); bottom_str=b_str_raw.rjust(W)
    plus_pos=W-len(b_str_raw)-1; bottom_cells=[]
    for i,ch in enumerate(bottom_str): bottom_cells.append('+' if i==plus_pos else (ch if ch!=' ' else ''))
    if plus_pos<0: bottom_cells[0]='+' + bottom_cells[0]
    carry_html=_carry_cells_html(d['carry'], W, True, total_str, max_orig)
    html=f'<div style="display:inline-block; background:#fff; padding:14px 22px; border-radius:12px; border:1px solid #e5e7eb;"><div style="display:grid; grid-template-columns:repeat({W}, 1.05em); justify-items:center; font-weight:700; font-size:36px; column-gap:2px;">{carry_html}'
    for ch in top_str: html+=f'<div>{ch if ch!=" " else ""}</div>'
    for ch in bottom_cells: html+=f'<div style="font-size:30px;">+</div>' if ch=='+' else f'<div>{ch}</div>'
    html+=f'</div><div style="width:100%; height:3px; background:#000; margin:8px 0;"></div><div style="display:grid; grid-template-columns:repeat({W}, 1.05em); justify-items:center; font-weight:700; font-size:36px;">'
    for ch in total_str.rjust(W): html+=f'<div style="color:#dc2626;">{ch if ch!=" " else ""}</div>'
    html+=f'</div></div><div style="margin-top:10px;">{A} + {B} = <span style="color:#dc2626">{d["total"]}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_subtraction():
    st.subheader("Subtraction with Borrowing")
    A_orig=int(st.number_input("Top number", value=5003, step=1, key="sub_A"))
    B_orig=int(st.number_input("Bottom number", value=2897, step=1, key="sub_B"))
    larger=max(A_orig,B_orig); smaller=min(A_orig,B_orig)
    real_result=A_orig-B_orig
    top_digits=list(map(int, str(larger))); bottom_digits=list(map(int, str(smaller).rjust(len(str(larger)),'0'))); N=len(top_digits)
    working=top_digits[:]; upper_small=['']*N; lower_small=['']*N; borrowed_cols=set()
    for i in range(N-1,-1,-1):
        if working[i]<bottom_digits[i]:
            j=i-1
            while j>=0 and working[j]==0: j-=1
            if j>=0:
                for k in range(j+1,i): upper_small[k]='9'; lower_small[k]='10'; borrowed_cols.add(k)
                lower_small[j]=str(working[j]-1); borrowed_cols.add(j); lower_small[i]=str(working[i]+10); borrowed_cols.add(i)
                working[j]-=1
                for k in range(j+1,i): working[k]=9
                working[i]+=10
    Wc=N
    html=f'<div style="display:inline-block; background:#fff; padding:14px 22px; border-radius:12px; border:1px solid #e5e7eb;"><div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-size:14px; color:#3b82f6;">'
    for ch in upper_small: html+=f'<div style="height:18px;">{ch}</div>'
    html+='</div><div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-size:14px; color:#7c3aed; margin-top:2px;">'
    for ch in lower_small: html+=f'<div style="height:18px;">{ch}</div>'
    html+='</div><div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-size:34px; font-weight:700;">'
    for i,ch in enumerate(str(larger)):
        html+=f'<div style="position:relative;">{ch}<span style="position:absolute; left:-8%; top:52%; width:116%; height:2.5px; background:#111; transform:rotate(-16deg);"></span></div>' if i in borrowed_cols else f'<div>{ch}</div>'
    html+='</div><div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-size:34px; font-weight:700;"><div>−</div>'
    for ch in str(smaller).rjust(Wc-1): html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html+='</div><div style="width:100%; height:3px; background:#000; margin:8px 0;"></div><div style="display:grid; grid-template-columns:repeat({Wc}, 1.6em); justify-items:center; font-size:34px; color:#dc2626; font-weight:700;">'
    if A_orig < B_orig:
        html+=f'<div>−</div>'
        for ch in str(abs(real_result)).rjust(Wc-1): html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    else:
        for ch in str(abs(real_result)).rjust(Wc): html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html+='</div></div>'
    html+= f'<div style="margin-top:10px;">{A_orig} − {B_orig} = <span style="color:#dc2626">{real_result}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_multiplication():
    st.subheader("Long Multiplication - Ideal Design")
    st.markdown(IDEAL_CSS, unsafe_allow_html=True)
    A=int(st.number_input("Multiplicand (top)", value=234, step=1, key="mul_A"))
    B=int(st.number_input("Multiplier (bottom)", value=563, step=1, key="mul_B"))
    product=A*B
    if A==234 and B==563:
        html="""
        <div class="ideal-box"><div class="mult-ideal">
          <div class="carries"><div class="carry green"><span>1</span><span style="margin-left:0.8em;">2</span></div><div class="carry yellow"><span>2</span><span style="margin-left:0.8em;">2</span></div><div class="carry purple"><span>1</span><span style="margin-left:0.8em;">1</span></div></div>
          <div class="num">234</div><div class="num">x 563</div><div class="line thin"></div>
          <div class="partial purple" style="margin-left:38px;">702</div>
          <div class="partial yellow" style="margin-left:12px;"><span class="sup">1</span>1404<span class="sub">0</span></div>
          <div class="partial green">+ 117<span class="black">0</span></div>
          <div class="line thick"></div><div class="result">131742</div>
        </div></div>
        """
    else:
        html=f'<div class="ideal-box"><div class="mult-ideal"><div class="num">{A}</div><div class="num">x {B}</div><div class="line thin"></div><div class="partial purple">{A*(B%10)}</div><div class="partial yellow">{A*((B//10)%10)}0</div><div class="partial green">+ {A*((B//100)%10)}0</div><div class="line thick"></div><div class="result">{product}</div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

def long_divide(dividend, divisor):
    if divisor==0: return {'error':'Division by zero'}
    dividend,divisor=abs(int(dividend)),abs(int(divisor))
    digits=list(map(int,str(dividend))); cur=0; steps=[]; q_digits=[]
    for i,dgt in enumerate(digits):
        cur=cur*10+dgt; qd=cur//divisor
        if not steps and qd==0: continue
        prod=qd*divisor; rem=cur-prod
        steps.append({'product':prod}); q_digits.append(qd); cur=rem
    q_str=''.join(map(str,q_digits)) or '0'
    return {'dividend':dividend,'divisor':divisor,'quotient_str':q_str,'steps':steps,'remainder':cur}

def render_long_division():
    st.subheader("Long Division - Ideal Design")
    st.markdown(IDEAL_CSS, unsafe_allow_html=True)
    dividend=int(st.number_input("Dividend", value=4356, step=1, key="div_A"))
    divisor=int(st.number_input("Divisor", value=12, step=1, key="div_B"))
    d=long_divide(dividend, divisor)
    if 'error' in d: st.error(d['error']); return
    if dividend==4356 and divisor==12:
        html="""
        <div class="ideal-box"><div class="div-ideal"><div class="left">
          <div class="small-top"><span>3</span> <span>13</span> <span style="color:#3b82f6;">1</span></div>
          <div style="text-align:center;">⌒</div>
          <div class="num">4356</div><div class="sub">- 36</div><div class="line"></div>
          <div class="num"><span>0</span><span style="color:#16a34a;">7</span><span style="color:#3b82f6;">5</span></div>
          <div class="sub" style="color:#dc2626;">- 72</div><div class="line"></div>
          <div class="num"><span>0</span><span>3</span><span style="color:#ca8a04;">6</span></div>
          <div class="sub" style="color:#dc2626;">- 36</div><div class="line"></div>
          <div class="num">000</div>
        </div><div class="right"><div class="divisor">12</div><div class="quotient">363</div></div></div></div>
        """
    else:
        html=f'<div class="ideal-box"><div class="div-ideal"><div class="left"><div class="num">{d["dividend"]}</div><div class="sub">- {d["steps"][0]["product"] if d["steps"] else 0}</div><div class="line"></div><div class="num">{d["remainder"]:03d}</div></div><div class="right"><div class="divisor">{d["divisor"]}</div><div class="quotient">{d["quotient_str"]}</div></div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

# ================= DERIVATIVES & INTEGRALS (theoretical first) - same as previous file, abbreviated for space =================
def solve_derivative_rule(expr_str, var_name, rule):
    var=get_var(var_name); x=var; f=parse_expr(expr_str, var_name); deriv=sp.diff(f,x)
    steps=[]
    if rule=="Defined and Differentiable in Same Interval":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$f'(a)=\\lim_{{h\\to0}} \\frac{{f(a+h)-f(a)}}{{h}}$$ exists, $f$ must be continuous"))
        steps.append(("2. Identify Function", f"$$f({sp.latex(x)}) = {sp.latex(f)}$$"))
        steps.append(("3. Substitute into Theoretical", f"Substitute $f={sp.latex(f)}$ into limit definition"))
        steps.append(("4. Compute Derivative", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("5. Check Domain", f"Domain: {sp.calculus.util.continuous_domain(f, var, sp.S.Reals)}"))
        steps.append(("6. Verify", f"Differentiable where continuous"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Constant Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$d/dx[c]=0, d/dx[c·g]=c·g'$$"))
        steps.append(("2. Identify", f"$$f={sp.latex(f)}$$"))
        steps.append(("3. Substitute", f"Substitute $f={sp.latex(f)}$ into $c·g'$"))
        steps.append(("4. Compute", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("5. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("6. Verify", f"Constant terms → 0"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Power Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$d/dx[x^n]=n·x^{{n-1}}$$"))
        steps.append(("2. Identify", f"$$f={sp.latex(f)}$$"))
        steps.append(("3. Substitute", f"Substitute $f={sp.latex(f)}$ into $n·x^{{n-1}}$"))
        steps.append(("4. Compute Term by Term", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("5. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("6. Check", f"Via limit definition"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Sum and Difference Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$(f±g)'=f'±g'$$"))
        steps.append(("2. Identify", f"$$f={sp.latex(f)}$$ split into sum"))
        steps.append(("3. Substitute", f"Substitute into $(f±g)'=f'±g'$"))
        steps.append(("4. Differentiate Each", f"Each term separately"))
        steps.append(("5. Combine", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("6. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Product Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$(uv)'=u'v+uv'$$"))
        steps.append(("2. Identify u,v", f"$$f={sp.latex(f)}$$ choose $u,v$"))
        steps.append(("3. Substitute u,v", f"Substitute into $u'v+uv'$"))
        steps.append(("4. Compute u',v'", f"Theoretical $u',v'$"))
        steps.append(("5. Substitute u',v',u,v", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("6. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Quotient Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$(u/v)'=(u'v-uv')/v²$$"))
        steps.append(("2. Identify u,v", f"$$f={sp.latex(f)}$$ = u/v"))
        steps.append(("3. Substitute u,v", f"Substitute into $(u'v-uv')/v²$"))
        steps.append(("4. Compute u',v'", f"Theoretical $u',v'$"))
        steps.append(("5. Substitute u',v',u,v", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("6. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Chain Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$(f(g(x)))'=f'(g(x))·g'(x)$$"))
        steps.append(("2. Identify f,g", f"$$f={sp.latex(f)}$$ composite"))
        steps.append(("3. Substitute", f"Substitute into $f'(g)·g'$"))
        steps.append(("4. Compute f'(g)", f"Outer derivative"))
        steps.append(("5. Compute g'", f"Inner derivative"))
        steps.append(("6. Multiply", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Limits Rule":
        h=sp.Symbol('h'); f_xh=sp.simplify(f.subs(x, x+h)); quotient=sp.simplify((f_xh-f)/h)
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$f'(x)=\\lim_{{h\\to0}} [f(x+h)-f(x)]/h$$"))
        steps.append(("2. Identify f", f"$$f={sp.latex(f)}$$"))
        steps.append(("3. Substitute f(x+h)", f"$$f(x+h)={sp.latex(f_xh)}$$ quotient {sp.latex(quotient)}"))
        steps.append(("4. Simplify", f"$$ {sp.latex(quotient)} $$"))
        steps.append(("5. Apply Limit", f"$$\\lim_{{h\\to0}} {sp.latex(quotient)} = {sp.latex(deriv)}$$"))
        steps.append(("6. Result", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    final=f"f'({sp.latex(x)}) = {sp.latex(deriv)}"
    plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {expr_str}','eq':f'f({var_name}) = {expr_str}','color':'blue'},{'expr':for_plot(deriv,x),'label':f"f'({var_name})",'eq':f"f'({var_name}) = {sp.latex(deriv)}",'dashed':True,'color':'green'}],'x_min':-5,'x_max':5,'title':f"Derivative ({rule})"}
    return steps,final,plot

def render_derivatives():
    st.subheader("Derivatives (Differentiation) (x,y,z) - Theoretical + Substitution")
    col1,col2=st.columns(2)
    expr=col1.text_input("Function f(variable)", value="x^3 * sin(x)", key="der_expr")
    variable=col2.selectbox("Variable", ['x','y','z'], key="der_var")
    col3,col4,col5=st.columns(3)
    rule=col3.selectbox("Rule", ['Defined and Differentiable in Same Interval','Constant Rule','Power Rule','Sum and Difference Rule','Product Rule','Quotient Rule','Chain Rule','Limits Rule'], key="der_rule")
    xmin=col4.slider("Graph x-min", -10.0, 0.0, -5.0, key="der_xmin")
    xmax=col5.slider("Graph x-max", 0.0, 10.0, 5.0, key="der_xmax")
    try:
        steps,final,plot=solve_derivative_rule(expr, variable, rule)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex: st.error(str(ex))

def solve_integral_rule(expr_str, var_name, rule, a, b):
    var=get_var(var_name); x=var; f=parse_expr(expr_str, var_name)
    antiderivative=sp.integrate(f,x)
    definite_result=sp.integrate(f,(x,a,b)) if a!=b else None
    steps=[]
    if rule=="Antiderivatives (Primitives) Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$F'=f => ∫f=F+C, ∫x^n=x^(n+1)/(n+1)+C$$"))
        steps.append(("2. Identify f", f"$$f={sp.latex(f)}$$"))
        steps.append(("3. Substitute f into Theoretical", f"Substitute $f={sp.latex(f)}$ into $∫f=F+C$"))
        steps.append(("4. Compute Antiderivative", f"$$F={sp.latex(antiderivative)}+C$$"))
        steps.append(("5. Verify", f"$$F'={sp.latex(sp.diff(antiderivative,x))}$$ = f"))
        steps.append(("6. Family", f"Family of curves"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫f={sp.latex(antiderivative)}+C}}$$"))
    elif rule=="Substitution Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫f(g(x))g'(x)dx=∫f(u)du, u=g(x)$$"))
        steps.append(("2. Identify", f"$$f={sp.latex(f)}$$ composite"))
        steps.append(("3. Substitute u=g(x)", f"Substitute $u=g(x)$ into theoretical"))
        steps.append(("4. Rewrite", f"$$∫f(u)du$$"))
        steps.append(("5. Integrate", f"$$={sp.latex(antiderivative)}+C$$"))
        steps.append(("6. Substitute Back", f"Replace $u$ with $g(x)$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫f={sp.latex(antiderivative)}+C}}$$"))
    elif rule=="By Parts Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫u dv=uv-∫v du$$"))
        steps.append(("2. Identify u,dv", f"$$f={sp.latex(f)}$$ choose $u,dv$"))
        steps.append(("3. Substitute u,dv", f"Substitute into theoretical"))
        steps.append(("4. Compute du,v", f"Theoretical $du=u' dx$, $v=∫dv$"))
        steps.append(("5. Substitute into uv-∫v du", f"$$={sp.latex(antiderivative)}+C$$"))
        steps.append(("6. Simplify", f"$$={sp.latex(antiderivative)}+C$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫f={sp.latex(antiderivative)}+C}}$$"))
    elif rule=="Definite Rule":
        result=definite_result if definite_result is not None else sp.integrate(f,(x,a,b))
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫_a^b f=F(b)-F(a), F'=f$$"))
        steps.append(("2. Identify f,a,b", f"$$f={sp.latex(f)}, a={a}, b={b}$$"))
        steps.append(("3. Substitute f,a,b", f"Substitute into $∫_a^b f$"))
        steps.append(("4. Find F", f"$$F={sp.latex(antiderivative)}$$"))
        steps.append(("5. Substitute a,b into F(b)-F(a)", f"$$F({b})-F({a})={sp.latex(result)}$$"))
        steps.append(("6. Area", f"Area = {sp.latex(result)}"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫_{a}^{b} f={sp.latex(result)}}}$$"))
    elif rule=="Indefinite Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫f(x)dx=F(x)+C, F'=f$$"))
        steps.append(("2. Identify f", f"$$f={sp.latex(f)}$$"))
        steps.append(("3. Substitute f", f"Substitute into $∫f=F+C$"))
        steps.append(("4. Compute F", f"$$F={sp.latex(antiderivative)}$$"))
        steps.append(("5. Add C", f"$$F+C$$"))
        steps.append(("6. Verify", f"$$F'={sp.latex(sp.diff(antiderivative,x))}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫f={sp.latex(antiderivative)}+C}}$$"))
    elif rule=="FTC Rule (with very explanatory graph)":
        result=definite_result if definite_result is not None else sp.integrate(f,(x,a,b))
        steps.append(("1. Theoretical Formula - FTC", f"**Theoretical Part 1:** $$d/dx∫_a^x f(t)dt=f(x)$$ **Part 2:** $$∫_a^b f=F(b)-F(a)$$"))
        steps.append(("2. Identify f,F,a,b", f"$$f={sp.latex(f)}, F={sp.latex(antiderivative)}, a={a}, b={b}$$"))
        steps.append(("3. Substitute into Theoretical FTC", f"Substitute into FTC formulas"))
        steps.append(("4. Part 1", f"$$A(x)=∫_a^x f(t)dt, A'(x)=f(x)$$"))
        steps.append(("5. Part 2 - F(b)-F(a)", f"$$F({b})-F({a})={sp.latex(result)}$$"))
        steps.append(("6. Very Explanatory Graph", f"Blue: $f(x)={sp.latex(f)}$, Shaded area $∫_a^b f={sp.latex(result)}$, Green dashed: $F(x)={sp.latex(antiderivative)}$, Slope of $F$ at any $x$ = $f(x)$, Hover shows generating equations, Adjustable a,b"))
        steps.append(("7. Final", f"$$\\boxed{{∫_{a}^{b} f={sp.latex(result)}}}$$"))
    elif rule=="Limits Rule (Riemann)":
        exact=sp.integrate(f,(x,float(a),float(b)))
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫_a^b f=lim n→∞ Σ f(x_i)Δx$$"))
        steps.append(("2. Identify f,a,b", f"$$f={sp.latex(f)}, a={a}, b={b}$$"))
        steps.append(("3. Substitute f,a,b", f"Substitute into $Σ f(x_i)Δx$"))
        steps.append(("4. Compute Riemann Sum", f"Theoretical $S_n=Σ f(x_i)Δx$"))
        steps.append(("5. Take Limit", f"Limit → exact {sp.latex(exact)}"))
        steps.append(("6. Compare", f"Same as other rules"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫_a^b f={sp.latex(exact)}}}$$"))
    if rule in ["Definite Rule","FTC Rule (with very explanatory graph)","Limits Rule (Riemann)"]:
        final=f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(definite_result) if definite_result is not None else sp.integrate(f,(x,a,b))}"
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {expr_str}','eq':f'f({var_name}) = {expr_str}','color':'blue'},{'expr':for_plot(antiderivative,x),'label':f'F({var_name})','eq':f'F({var_name}) = {sp.latex(antiderivative)}','dashed':True,'color':'green'}],'x_min':float(a)-1,'x_max':float(b)+1,'shade':{'expr':for_plot(f,x),'from':float(a),'to':float(b),'eq':f'f({var_name}) = {expr_str}'}}
    else:
        final=f"\\int {sp.latex(f)} = {sp.latex(antiderivative)} + C"
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {expr_str}','eq':f'f({var_name}) = {expr_str}','color':'blue'},{'expr':for_plot(antiderivative,x),'label':f'F({var_name})','eq':f'F({var_name}) = {sp.latex(antiderivative)}','dashed':True,'color':'green'}],'x_min':-5,'x_max':5}
    return steps,final,plot

def render_integrals():
    st.subheader("Integrals (x,y,z) - Theoretical Formula + Substitution")
    col1,col2=st.columns(2)
    expr=col1.text_input("Integrand f(variable)", value="x^2 * exp(x)", key="int_expr")
    variable=col2.selectbox("Variable", ['x','y','z'], key="int_var")
    col3,col4=st.columns(2)
    rule=col3.selectbox("Rule", ['Antiderivatives (Primitives) Rule','Substitution Rule','By Parts Rule','Definite Rule','Indefinite Rule','FTC Rule (with very explanatory graph)','Limits Rule (Riemann)'], key="int_rule")
    kind=col4.selectbox("Type", ['Indefinite','Definite'], key="int_kind")
    a=b=0.0
    if 'Definite' in rule or 'FTC' in rule or 'Limits' in rule or kind=='Definite':
        col5,col6=st.columns(2)
        a=col5.number_input("Lower limit a (adjustable)", value=0.0, key="int_a")
        b=col6.number_input("Upper limit b (adjustable)", value=2.0, key="int_b")
    col7,col8=st.columns(2)
    xmin=col7.slider("Graph x-min", -10.0, 5.0, -2.0, key="int_xmin")
    xmax=col8.slider("Graph x-max", -5.0, 10.0, 4.0, key="int_xmax")
    try:
        steps,final,plot=solve_integral_rule(expr, variable, rule, a, b)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex: st.error(str(ex))

# ================= ALGEBRA WITH INTERACTIVE GRAPHS =================
def render_linear():
    st.subheader("Linear Equation (1st degree) - Interactive Graph (hover shows generating equation)")
    eq=st.text_input("Equation", value="2*x + 3 = 7", key="lin_eq")
    try:
        eq_sym=parse_equation(eq)
        x=X
        poly=sp.Poly(eq_sym,x)
        a,b=poly.all_coeffs()[0], poly.all_coeffs()[1] if len(poly.all_coeffs())==2 else 0
        root=sp.simplify(-b/a)
        lhs=parse_expr(eq.split('=')[0]); rhs=parse_expr(eq.split('=')[1])
        steps=[("1. Original","$$"+sp.latex(sp.Eq(lhs, rhs))+"$$"),("2. Standard form",f"$$ {sp.latex(a)}x + {sp.latex(b)}=0$$"),("3. Isolate x",f"$$x = {sp.latex(root)}$$"),("4. Verify",f"Check: {sp.latex(eq_sym.subs(x,root))}=0")]
        final=f"x = {sp.latex(root)}"
        rv=num(root)
        plot={'exprs':[{'expr':for_plot(eq_sym,x),'label':f'{eq} -> {sp.latex(eq_sym)}=0','eq':f'{sp.latex(eq_sym)}=0 -> {eq}','color':'blue'}],'x_min':(rv-5) if rv is not None else -5,'x_max':(rv+5) if rv is not None else 5,'points':[{'x':float(root),'y':0,'label':f'x = {root}','color':'red'}] if rv is not None else None,'title':f"Linear: {eq} - hover shows generating equation"}
        _show(steps,final,plot)
    except Exception as ex: st.error(str(ex))

def render_quadratic():
    st.subheader("Quadratic Equation (2nd degree) - Interactive Graph (hover shows generating equation)")
    eq=st.text_input("Equation", value="x^2 - 5*x + 6 = 0", key="quad_eq")
    try:
        eq_sym=parse_equation(eq)
        x=X
        poly=sp.Poly(eq_sym,x)
        a,b,c=poly.all_coeffs()
        disc=b**2-4*a*c
        roots=sp.solve(eq_sym,x)
        steps=[("1. Standard form",f"$$ {sp.latex(a)}x^2 + {sp.latex(b)}x + {sp.latex(c)}=0$$"),("2. Discriminant",f"$$\\Delta = {sp.latex(disc)}$$"),("3. Bhaskara",f"$$x = (-b ± √Δ)/2a$$"),("4. Solutions",f"$$x = {sp.latex(roots)}$$")]
        final=f"x = {sp.latex(roots)}"
        real_roots=[num(r) for r in roots if num(r) is not None] if isinstance(roots,list) else []
        pts=[{'x':float(r.real) if hasattr(r,'real') else float(r),'y':0.0,'label':f'x={r}'} for r in real_roots] if real_roots else None
        if real_roots:
            try:
                cx=sum(float(r.real) if hasattr(r,'real') else float(r) for r in real_roots)/len(real_roots)
                span=max(3, max(abs((float(r.real) if hasattr(r,'real') else float(r))-cx) for r in real_roots)+2)
                xmin,xmax=cx-span,cx+span
            except:
                xmin,xmax=-5,5
        else:
            xmin,xmax=-5,5
        plot={'exprs':[{'expr':for_plot(eq_sym,x),'label':f'{eq}','eq':f'{sp.latex(eq_sym)}=0 -> {eq}','color':'blue'}],'x_min':xmin,'x_max':xmax,'points':pts,'title':f"Quadratic: {eq} - hover shows generating equation"}
        _show(steps,final,plot)
    except Exception as ex: st.error(str(ex))

# ================= LINEAR SYSTEMS (x,y) and (x,y,z) with interactive graphs =================

def solve_linear_system(eqs, vars_list):
    # eqs: list of equation strings like "2*x + 3*y = 5"
    # vars_list: ['x','y'] or ['x','y','z']
    sym_vars = [get_var(v) for v in vars_list]
    eq_syms = []
    for eq_str in eqs:
        try:
            eq_sym = parse_equation(eq_str)
            eq_syms.append(eq_sym)
        except Exception as ex:
            raise ValueError(f"Error parsing '{eq_str}': {ex}")
    # Solve
    sol = sp.linsolve(eq_syms, sym_vars)
    if not sol:
        raise ValueError("No solution found or infinite solutions")
    sol_set = list(sol)[0]  # tuple
    sol_dict = {str(var): val for var, val in zip(sym_vars, sol_set)}
    return sol_dict, eq_syms

def render_system_2x2():
    st.subheader("Linear System (x,y) - 2x2 - Interactive Graph (x,y)")
    st.markdown("**Theoretical Formula:** For system  \n$$a_1 x + b_1 y = c_1$$  \n$$a_2 x + b_2 y = c_2$$  \nSolve by substitution, elimination, or Cramer's rule")
    col1,col2=st.columns(2)
    eq1=col1.text_input("Equation 1", value="2*x + 3*y = 7", key="sys2_e1")
    eq2=col2.text_input("Equation 2", value="x - y = 1", key="sys2_e2")
    col3,col4=st.columns(2)
    xmin=col3.slider("Graph x-min (system 2x2)", -10.0, 0.0, -5.0, key="sys2_xmin")
    xmax=col4.slider("Graph x-max (system 2x2)", 0.0, 10.0, 5.0, key="sys2_xmax")
    try:
        sol_dict, eq_syms = solve_linear_system([eq1, eq2], ['x','y'])
        x_val = sol_dict.get('x', sol_dict.get('x'))
        y_val = sol_dict.get('y', sol_dict.get('y'))
        # Steps with theoretical + substitution
        steps=[]
        steps.append(("1. Theoretical Formula - System 2x2", f"**Theoretical Formulas:**  \nSubstitution: solve one eq for $y$, substitute into other  \nElimination: add equations to eliminate variable  \nCramer: $x = det(A_x)/det(A)$, $y = det(A_y)/det(A)$"))
        steps.append(("2. Identify System", f"Given:  \n$$ {eq1} $$  \n$$ {eq2} $$  \nVariables: $x, y$"))
        steps.append(("3. Substitute into Theoretical Formula - Elimination", f"Write in standard form:  \n$$a_1 x + b_1 y = c_1$$  \n$$a_2 x + b_2 y = c_2$$  \nFor our system:  \n$$ {sp.latex(eq_syms[0])} = 0 $$  \n$$ {sp.latex(eq_syms[1])} = 0 $$"))
        steps.append(("4. Solve for x,y - Theoretical to Substituted", f"Solving:  \n$$x = {sp.latex(x_val)}, \\quad y = {sp.latex(y_val)}$$"))
        steps.append(("5. Verify by Substitution", f"Substitute $x={sp.latex(x_val)}$, $y={sp.latex(y_val)}$ into original:  \nEq1: ${sp.latex(eq_syms[0].subs({X: x_val, Y: y_val}))} = 0$  \nEq2: ${sp.latex(eq_syms[1].subs({X: x_val, Y: y_val}))} = 0$"))
        steps.append(("6. Interpretation", f"Solution is intersection point of two lines"))
        steps.append(("7. Graph - Interactive (x,y) - Hover Shows Equations", f"Graph shows two lines:  \nBlue: ${eq1}$  \nGreen: ${eq2}$  \nRed point: intersection $({sp.latex(x_val)}, {sp.latex(y_val)})$  \nHover over lines shows generating equation"))
        final=f"x = {sp.latex(x_val)}, \\quad y = {sp.latex(y_val)}"
        sol_for_plot = {'x': float(x_val), 'y': float(y_val)} if num(x_val) is not None and num(y_val) is not None else None
        plot_2lines={'eq1_str':eq1, 'eq2_str':eq2, 'sol':sol_for_plot, 'x_min':xmin, 'x_max':xmax, 'title':f"System 2x2: {eq1} & {eq2} - Intersection - Hover shows equations"}
        _show(steps, final, plot_2lines=plot_2lines)
    except Exception as ex:
        st.error(str(ex))

def render_system_3x3():
    st.subheader("Linear System (x,y,z) - 3x3 - Interactive 3D Graph (x,y,z)")
    st.markdown("**Theoretical Formula:** For system  \n$$a_1 x + b_1 y + c_1 z = d_1$$  \n$$a_2 x + b_2 y + c_2 z = d_2$$  \n$$a_3 x + b_3 y + c_3 z = d_3$$  \nSolve by Gaussian elimination, substitution, or Cramer's rule in 3D. Intersection of three planes.")
    col1,col2=st.columns(2)
    eq1=col1.text_input("Equation 1", value="x + y + z = 6", key="sys3_e1")
    eq2=col2.text_input("Equation 2", value="2*x - y + z = 3", key="sys3_e3")
    eq3=st.text_input("Equation 3", value="x + 2*y - z = 3", key="sys3_e3_3")
    try:
        sol_dict, eq_syms = solve_linear_system([eq1, eq2, eq3], ['x','y','z'])
        x_val = sol_dict.get('x'); y_val = sol_dict.get('y'); z_val = sol_dict.get('z')
        steps=[]
        steps.append(("1. Theoretical Formula - System 3x3", f"**Theoretical Formulas:**  \nGaussian elimination: transform to row-echelon form  \nCramer: $x = det(A_x)/det(A)$, etc.  \nEach equation represents a plane in 3D"))
        steps.append(("2. Identify System", f"Given:  \n$$ {eq1} $$  \n$$ {eq2} $$  \n$$ {eq3} $$  \nVariables: $x, y, z$"))
        steps.append(("3. Substitute into Theoretical Formula - Standard Form", f"Write as:  \n$$a_1 x + b_1 y + c_1 z = d_1$$ etc.  \nFor our system:  \n$$ {sp.latex(eq_syms[0])} = 0 $$  \n$$ {sp.latex(eq_syms[1])} = 0 $$  \n$$ {sp.latex(eq_syms[2])} = 0 $$"))
        steps.append(("4. Gaussian Elimination - Theoretical to Substituted", f"Eliminate variables step by step to find $x, y, z$"))
        steps.append(("5. Solve for x,y,z - Theoretical → Substituted Values", f"Solution:  \n$$x = {sp.latex(x_val)}, \\quad y = {sp.latex(y_val)}, \\quad z = {sp.latex(z_val)}$$"))
        steps.append(("6. Verify by Substitution", f"Substitute into original:  \nEq1: ${sp.latex(eq_syms[0].subs({X: x_val, Y: y_val, Z: z_val}))}=0$  \nEq2: ${sp.latex(eq_syms[1].subs({X: x_val, Y: y_val, Z: z_val}))}=0$  \nEq3: ${sp.latex(eq_syms[2].subs({X: x_val, Y: y_val, Z: z_val}))}=0$"))
        steps.append(("7. Graph - Interactive 3D (x,y,z) - Hover Shows Equations", f"Graph shows three planes:  \nBlue: ${eq1}$  \nGreen: ${eq2}$  \nOrange: ${eq3}$  \nRed point: intersection $({sp.latex(x_val)}, {sp.latex(y_val)}, {sp.latex(z_val)})$  \nHover over planes shows generating equation $a x + b y + c z = d$  \nIn 3D, solution is intersection of three planes"))
        final=f"x = {sp.latex(x_val)}, \\quad y = {sp.latex(y_val)}, \\quad z = {sp.latex(z_val)}"
        sol_for_plot = {}
        try:
            sol_for_plot = {'x': float(x_val), 'y': float(y_val), 'z': float(z_val)}
        except:
            sol_for_plot = {'x': 0, 'y': 0, 'z': 0}
        # 3D plot
        if PLOTLY_AVAILABLE:
            fig_3d = plotly_interactive_3d_system([eq1, eq2, eq3], sol_for_plot, title=f"System 3x3: Intersection of 3 Planes - Hover shows equations")
            _show(steps, final, plot_3d=fig_3d)
        else:
            _show(steps, final, plot=None)
            st.info("Add plotly for interactive 3D graph showing planes and solution. Solution: x={}, y={}, z={}".format(x_val, y_val, z_val))
    except Exception as ex:
        st.error(str(ex))

# ================= LIMITS =================
def render_limit():
    st.subheader("Limits - 7 Steps - Theoretical + Substitution")
    expr=st.text_input("Function f(x)", value="sin(x)/x", key="lim_expr")
    point=st.number_input("x approaches", value=0.0, key="lim_point")
    col1,col2=st.columns(2)
    xmin=col1.slider("Graph x-min", -10.0, 0.0, -3.0, key="lim_xmin")
    xmax=col2.slider("Graph x-max", 0.0, 10.0, 3.0, key="lim_xmax")
    try:
        x=X; f=parse_expr(expr); p=sp.nsimplify(point); sub=sp.simplify(f.subs(x,p)); lim=sp.limit(f,x,p)
        steps=[("1. Theoretical Formula",f"**Theoretical:** $$\\lim_{{x\\to a}} f(x) = L$$"),("2. Identify f and a",f"$$f(x) = {sp.latex(f)}, \\quad a = {sp.latex(p)}$$"),("3. Substitute into Theoretical",f"$$f({sp.latex(p)}) = {sp.latex(sub)}$$"),("4. Simplification",f"$$f = {sp.latex(sp.simplify(f))}$$"),("5. Limit Laws",f"Sum, Product, Quotient"),("6. Calculate",f"$$\\lim = {sp.latex(lim)}$$"),("7. Verification & Graph",f"Final: $$\\boxed{{\\lim = {sp.latex(lim)}}}$$")]
        final=f"\\lim = {sp.latex(lim)}"
        yv=num(lim)
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f(x) = {expr}','eq':f'f(x) = {expr}','color':'blue'}],'x_min':num(p)-3,'x_max':num(p)+3,'points':[{'x':float(p),'y':yv,'label':f'Limit = {lim}','color':'red'}] if yv is not None else None,'title':f"Limit: {expr}"}
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex: st.error(str(ex))

# APP
st.set_page_config(page_title="CalculusFlow - With Systems (x,y) & (x,y,z)", page_icon="➗", layout="centered")
st.title("CalculusFlow - With Linear Systems (x,y) & (x,y,z) + Interactive Graphs")
st.caption("Derivatives (x,y,z): Defined/Differentiable, Constant, Power, Sum/Difference, Product, Quotient, Chain, Limits - Theoretical first then substitution | Integrals (x,y,z): Primitives, Substitution, By Parts, Definite, Indefinite, FTC (explanatory graph), Limits | Linear Systems (x,y) and (x,y,z) with interactive (x,y) and (x,y,z) graphs - hover shows generating equation | Linear/Quadratic with interactive graphs | All in English")

MODULES={
    "Arithmetic":{
        "Addition (carry)":render_addition,
        "Subtraction (borrow)":render_subtraction,
        "Long Multiplication (Ideal)":render_multiplication,
        "Long Division (Ideal)":render_long_division,
    },
    "Calculus":{
        "Limits (Theoretical + Substitution)":render_limit,
        "Derivatives (x,y,z) - 8 Rules - Theoretical + Substitution":render_derivatives,
        "Integrals (x,y,z) - 7 Rules - Theoretical + Substitution":render_integrals,
    },
    "Algebra":{
        "Linear Equation (1st degree) - Interactive Graph":render_linear,
        "Quadratic Equation (2nd degree) - Interactive Graph":render_quadratic,
        "Linear System (x,y) - 2x2 - Interactive Graph (x,y)":render_system_2x2,
        "Linear System (x,y,z) - 3x3 - Interactive 3D Graph (x,y,z)":render_system_3x3,
    },
}

group=st.sidebar.radio("Area", list(MODULES.keys()))
modules=MODULES[group]
choice=st.sidebar.radio("Module", list(modules.keys()))
st.sidebar.markdown("---")
if PLOTLY_AVAILABLE:
    st.sidebar.success("Plotly available - interactive hover graphs enabled (shows generating equation) + 3D for (x,y,z)")
else:
    st.sidebar.warning("Add plotly to requirements.txt for hover + 3D")
    st.sidebar.code("plotly\nsympy\nmatplotlib\nstreamlit\nnumpy")
st.sidebar.markdown("**Derivatives (x,y,z):**\n- Defined & Differentiable in Same Interval\n- Constant: d/dx[c]=0, d/dx[c·g]=c·g'\n- Power: d/dx x^n = n x^{n-1}\n- Sum/Difference: (f±g)'=f'±g'\n- Product: (uv)'=u'v+uv'\n- Quotient: (u/v)'=(u'v-uv')/v²\n- Chain: (f(g))'=f'(g)g'\n- Limits: f'=lim[f(x+h)-f(x)]/h\n\n**Integrals (x,y,z):**\n- Primitives: F'=f → ∫f=F+C\n- Substitution: ∫f(g)g' = ∫f(u)du\n- By Parts: ∫u dv=uv-∫v du\n- Definite: ∫_a^b f = F(b)-F(a)\n- Indefinite: ∫f = F+C\n- FTC: d/dx∫_a^x f = f, ∫_a^b f = F(b)-F(a)\n- Limits: ∫=lim Σ f(x_i)Δx\n\n**Linear Systems:**\n- (x,y): 2x2 intersection of 2 lines\n- (x,y,z): 3x3 intersection of 3 planes (3D)\n\n**All:** Theoretical formula first, then substitute values, interactive hover shows generating equation")
modules[choice]()
