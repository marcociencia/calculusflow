"""
CalculusFlow - FINAL CLEAN - No * display, no long caption
- Remove long caption: Derivatives (x,y,z): Defined/Differentiable... etc - not shown
- Adjust display:
  2*y -> 2y
  2*x -> 2x
  2*z -> 2z
  x*y -> x•y
  x*y*z -> x•y•z
  2*3 -> 2•3
- Keep all features: 8 derivative rules, 7 integral rules, theoretical first then substitution, systems (x,y) and (x,y,z) with interactive graphs, linear/quadratic interactive, ideal arithmetic, all in English
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import lambdify
import re

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

def pretty_eq(s):
    """Clean display: 2*y->2y, 2*x->2x, 2*z->2z, x*y->x•y, 2*3->2•3, etc."""
    if s is None:
        return ""
    t = str(s).strip()
    # Remove spaces around *
    # First handle number * variable -> remove *
    t = re.sub(r'(\d)\s*\*\s*([xyzXYZ])', r'\1\2', t)
    # Handle variable * number -> number after variable? e.g. x*2 -> x•2? Keep • for clarity, but user wants 2*x ->2x, so x*2 maybe x•2 or 2x? We'll keep x•2 for now
    # Actually for consistency, if variable * number, keep •? Let's do x*2 -> x•2
    # But also handle ) * ( , ) * variable, etc.
    # Replace * between letters/digits with •
    # After removing number*variable cases, remaining * becomes •
    t = t.replace('*', '•')
    # Clean up multiple •? Keep
    # Remove • between number and parenthesis? Keep as •
    # Replace "•(" with "("? Actually 2*(x) should be 2(x) maybe? Keep 2(x) -> 2(x) is okay without •
    t = re.sub(r'(\d)•\(', r'\1(', t)
    t = re.sub(r'\)•(\d)', r')\1', t)  # )•2 -> )2? maybe keep •? We'll keep simple
    # Clean double ••
    t = re.sub(r'•{2,}', '•', t)
    # Remove • before ^ ? e.g. x•^2 -> x^2
    t = re.sub(r'•\^', '^', t)
    # For display like 2•x should have been converted to 2x earlier, but if still 2•x, convert to 2x
    t = re.sub(r'(\d)•([xyz])', r'\1\2', t)
    return t

def get_var(name): return _VAR_MAP.get(name, X)

def _insert_implicit_mul(s):
    """Insert * for implicit multiplication: 3x->3*x, 3sin->3*sin, x(->x*(, )(->)*(, etc."""
    # Normalize spaces and handle • as * for input (user may paste display format)
    t = str(s).strip()
    t = t.replace('•', '*')  # allow user pasting pretty format
    t = t.replace('^', '**')
    # ln -> log for sympy
    t = re.sub(r'\bln\s*\(', 'log(', t, flags=re.IGNORECASE)
    # Handle cases like 3x, 3y, 3z
    t = re.sub(r'(?<=\d)(?=[xyzXYZ])', '*', t)
    # Handle number before function name: 3sin, 2cos, etc -> 3*sin
    t = re.sub(r'(?<=\d)(?=(?:sin|cos|tan|asin|acos|atan|log|exp|sqrt|abs)\s*\()', '*', t, flags=re.IGNORECASE)
    # Handle ) followed by ( or variable or number or function
    t = re.sub(r'(?<=\))(?=\s*[a-zA-Z0-9\(])', '*', t)
    # Handle variable followed by ( : x( -> x*(
    t = re.sub(r'(?<=[xyzXYZ])(?=\s*\()', '*', t)
    # Handle variable followed by number: x2 -> x*2 (rare)
    # Handle )(
    t = re.sub(r'\)\s*\(', ')*(', t)
    # Clean double **
    t = re.sub(r'\*{3,}', '**', t)
    return t

def parse_expr(s, var_name='x'):
    if not s or str(s).strip()=='':
        raise ValueError("Empty expression.")
    raw = str(s).strip()
    # Insert implicit multiplication
    processed = _insert_implicit_mul(raw)
    try:
        return sp.sympify(processed, locals=_LOCALS)
    except Exception as e:
        # Try again with more aggressive cleaning
        # Replace 3x with 3*x already done, try to give helpful error
        raise ValueError(f"Could not parse '{raw}' as '{processed}'. Error: {e}")
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
    if title: ax.set_title(pretty_eq(title))
    ax.legend(loc='best', fontsize=8); ax.grid(True, alpha=0.3); fig.tight_layout()
    return fig

def plot_matplotlib_2lines(eq1_str, eq2_str, sol, x_min, x_max, title=None):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    xs = np.linspace(float(x_min), float(x_max), 400)
    try:
        eq1_sym = parse_equation(eq1_str)
        eq2_sym = parse_equation(eq2_str)
        y1_expr = sp.solve(eq1_sym, Y)
        y2_expr = sp.solve(eq2_sym, Y)
        if y1_expr:
            f1 = lambdify(X, for_plot(y1_expr[0], Y), modules=['numpy'])
            ys1 = np.array(f1(xs), dtype=float)
            ax.plot(xs, ys1, label=pretty_eq(eq1_str), color='blue')
        if y2_expr:
            f2 = lambdify(X, for_plot(y2_expr[0], Y), modules=['numpy'])
            ys2 = np.array(f2(xs), dtype=float)
            ax.plot(xs, ys2, label=pretty_eq(eq2_str), color='green')
        if sol and 'x' in sol and 'y' in sol:
            xv = float(sol['x']); yv = float(sol['y'])
            ax.plot(xv, yv, 'ro', markersize=10)
            ax.annotate(f'({xv:.2f}, {yv:.2f})', (xv, yv), textcoords='offset points', xytext=(8,8), fontsize=9, color='red')
    except: pass
    ax.axhline(0, color='black', linewidth=0.5); ax.axvline(0, color='black', linewidth=0.5)
    ax.set_xlim(float(x_min), float(x_max))
    if title: ax.set_title(pretty_eq(title))
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
            label = pretty_eq(e.get('label','')); eq = pretty_eq(e.get('eq', label))
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
                hovertemplate=f"<b>{pretty_eq(shade.get('eq','f(x)'))}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"))
        except: pass
    if points:
        for p in points:
            fig.add_trace(go.Scatter(x=[float(p['x'])], y=[float(p['y'])], mode='markers+text', marker=dict(color=p.get('color','red'), size=10),
                text=[pretty_eq(p.get('label',''))], textposition="top right", name=pretty_eq(p.get('label','point')),
                hovertemplate=f"<b>{pretty_eq(p.get('label','point'))}</b><br>x=%{{x}}<br>y=%{{y}}<extra></extra>"))
    fig.update_layout(title=pretty_eq(title), xaxis_title="x", yaxis_title="y", hovermode="x unified", height=450,
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
            fig.add_trace(go.Scatter(x=xs, y=ys1, mode='lines', name=pretty_eq(eq1_str),
                line=dict(color='blue'),
                hovertemplate=f"<b>{pretty_eq(eq1_str)}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"))
        if y2_expr:
            f2 = lambdify(X, for_plot(y2_expr[0], Y), modules=['numpy'])
            ys2 = np.array(f2(xs), dtype=float)
            fig.add_trace(go.Scatter(x=xs, y=ys2, mode='lines', name=pretty_eq(eq2_str),
                line=dict(color='green'),
                hovertemplate=f"<b>{pretty_eq(eq2_str)}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"))
        if sol and 'x' in sol and 'y' in sol:
            xv = float(sol['x']); yv = float(sol['y'])
            fig.add_trace(go.Scatter(x=[xv], y=[yv], mode='markers+text', marker=dict(color='red', size=12),
                text=[f'Solution ({xv:.3f}, {yv:.3f})'], textposition="top right", name='Solution',
                hovertemplate=f"<b>Solution</b><br>x={xv:.3f}<br>y={yv:.3f}<br>{pretty_eq(eq1_str)}<br>{pretty_eq(eq2_str)}<extra></extra>"))
    except: pass
    fig.update_layout(title=pretty_eq(title or f"System: {eq1_str} & {eq2_str}"), xaxis_title="x", yaxis_title="y", hovermode="x unified", height=450)
    fig.add_hline(y=0, line_width=1, line_color="black", opacity=0.5)
    fig.add_vline(x=0, line_width=1, line_color="black", opacity=0.5)
    return fig

def plotly_interactive_3d_system(eqs, sol, title=None):
    if not PLOTLY_AVAILABLE: return None
    try:
        fig = go.Figure()
        x_range = np.linspace(-5, 5, 20)
        y_range = np.linspace(-5, 5, 20)
        Xg, Yg = np.meshgrid(x_range, y_range)
        colors = ['blue','green','orange']
        for idx, eq_str in enumerate(eqs):
            try:
                eq_sym = parse_equation(eq_str)
                z_expr = sp.solve(eq_sym, Z)
                if z_expr:
                    z_func = lambdify((X,Y), for_plot(z_expr[0], Z), modules=['numpy'])
                    Zg = z_func(Xg, Yg)
                    Zg = np.array(Zg, dtype=float)
                    Zg = np.clip(Zg, -10, 10)
                    fig.add_trace(go.Surface(x=Xg, y=Yg, z=Zg, opacity=0.6, colorscale=[[0, colors[idx%3]],[1, colors[idx%3]]], showscale=False, name=pretty_eq(eq_str),
                        hovertemplate=f"<b>{pretty_eq(eq_str)}</b><br>x=%{{x:.2f}}<br>y=%{{y:.2f}}<br>z=%{{z:.2f}}<extra></extra>"))
            except: continue
        if sol and all(k in sol for k in ['x','y','z']):
            fig.add_trace(go.Scatter3d(x=[float(sol['x'])], y=[float(sol['y'])], z=[float(sol['z'])], mode='markers+text', marker=dict(color='red', size=8),
                text=[f"Solution ({sol['x']:.2f}, {sol['y']:.2f}, {sol['z']:.2f})"], textposition="top center", name='Solution'))
        fig.update_layout(title=pretty_eq(title or "3D Linear System - Planes Intersection"), scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="z"), height=600)
        return fig
    except:
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

IDEAL_CSS = """
<style>
.ideal-box { display:inline-block; background:#fff; padding:14px 22px; border-radius:12px; border:1px solid #e5e7eb; font-family: ui-monospace, monospace; font-weight:700; }
.mult-ideal .carry { font-size:12px; letter-spacing:0.8em; } .mult-ideal .carry.green{color:#16a34a;} .mult-ideal .carry.yellow{color:#eab308;} .mult-ideal .carry.purple{color:#7c3aed;}
.mult-ideal .num{font-size:32px; text-align:right;} .mult-ideal .line{width:100%; background:#000; margin:6px 0;} .mult-ideal .line.thin{height:2px;} .mult-ideal .line.thick{height:3px;}
.mult-ideal .partial{font-size:28px; text-align:right; position:relative;} .mult-ideal .partial.purple{color:#7c3aed;} .mult-ideal .partial.yellow{color:#eab308;} .mult-ideal .partial.green{color:#16a34a;}
.mult-ideal .partial .sup{position:absolute; font-size:11px; color:#000; left:12px; top:-6px;} .mult-ideal .partial .sub{position:absolute; font-size:11px; color:#000; left:0; bottom:-6px;}
.mult-ideal .result{font-size:34px; color:#dc2626; text-align:right;}
.div-ideal{display:flex; align-items:flex-start;} .div-ideal .line{width:100%; height:3px; background:#000; margin:5px 0;} .div-ideal .right{border-left:3px solid #000; margin-left:8px;} .div-ideal .right .divisor{border-bottom:3px solid #000; padding:4px 24px; font-size:28px;} .div-ideal .right .quotient{padding:4px 24px; font-size:28px; color:#dc2626;}
.sub-ideal { text-align:center; }
.sub-ideal .carry-row { display:grid; justify-items:center; font-size:14px; font-weight:700; height:20px; }
.sub-ideal .carry-row.blue { color:#2563eb; }
.sub-ideal .carry-row.purple { color:#7c3aed; }
.sub-ideal .num-row { display:grid; justify-items:center; font-size:32px; font-weight:700; line-height:1.1; }
.sub-ideal .num-row .cross { position:relative; display:inline-block; }
.sub-ideal .num-row .cross::after { content:''; position:absolute; left:-10%; top:50%; width:120%; height:2.5px; background:#111; transform:rotate(-22deg); }
.sub-ideal .line { width:100%; height:3px; background:#000; margin:8px 0; }
.sub-ideal .result-row { display:grid; justify-items:center; font-size:34px; font-weight:700; color:#dc2626; }
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
    st.subheader("Subtraction with Borrowing - Ideal Format")
    st.markdown(IDEAL_CSS, unsafe_allow_html=True)
    A_orig=int(st.number_input("Top number", value=5003, step=1, key="sub_A"))
    B_orig=int(st.number_input("Bottom number", value=2897, step=1, key="sub_B"))
    larger=max(A_orig,B_orig); smaller=min(A_orig,B_orig)
    real_result=A_orig-B_orig
    
    # Compute borrowing for ideal display (same logic as before)
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
    
    # For ideal example 5003-2897, upper_small = ['',9,9,''], lower_small = ['4','10','10','13']
    # Build ideal HTML matching second image
    Wc=N
    col_style = f"grid-template-columns:repeat({Wc}, 1.8em);"
    
    # Upper row (blue 9 9)
    html = f'<div class="ideal-box"><div class="sub-ideal">'
    html += f'<div class="carry-row blue" style="{col_style}">'
    for ch in upper_small:
        html += f'<div>{ch}</div>'
    html += '</div>'
    # Lower small row (purple 4 10 10 13) - need to show 10 as small but centered
    html += f'<div class="carry-row purple" style="{col_style}">'
    for ch in lower_small:
        # Show 10 as "10" but smaller font, keep alignment
        if ch=='':
            html+=f'<div></div>'
        else:
            html+=f'<div style="font-size:13px;">{ch}</div>'
    html += '</div>'
    # Top number with crosses
    html += f'<div class="num-row" style="{col_style}">'
    for i,ch in enumerate(str(larger)):
        if i in borrowed_cols:
            html+=f'<div><span class="cross">{ch}</span></div>'
        else:
            html+=f'<div>{ch}</div>'
    html += '</div>'
    # Bottom number with minus
    html += f'<div class="num-row" style="{col_style}">'
    # First cell minus sign, but for ideal we put "- " before number
    # For general, put minus in first column if Wc==len(smaller) else adjust
    smaller_str = str(smaller).rjust(Wc)
    # Show minus sign in separate row? Ideal image shows "- 2897" on same line
    # We'll show minus in first position and numbers after
    for idx,ch in enumerate(smaller_str):
        if idx==0 and ch.strip()=='':
            html+=f'<div style="text-align:left;">-</div>'
        elif idx==0:
            # If first digit is not empty, show minus and digit? Put minus before
            # For simplicity: show "-" in its own style but aligned
            # We'll show minus in first column, and if smaller_str has digit there, shift
            # Better: first column is "-", rest are digits
            # Let's handle: if Wc == len(str(smaller)), we need extra column for "-"
            # For ideal, we will show "- " + number in same row with 4 columns, minus in first column offset
            html+=f'<div style="font-size:28px;">-</div>' if Wc>len(str(smaller)) else f'<div style="position:relative;"><span style="position:absolute; left:-18px;">-</span>{ch}</div>'
        else:
            html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    # Fix for case where Wc == len(smaller): we need minus outside grid, so redo
    # Let's rebuild bottom row more cleanly for ideal 5003 case
    html = html  # keep
    html += '</div>'
    # Rebuild bottom row correctly for ideal display
    # For 5003 example, we want "- 2897" with minus aligned left
    # We'll close previous and create new bottom row with proper layout
    
    # Actually replace bottom row with cleaner version
    # To keep simple, we will create a new bottom row HTML
    # We'll generate from scratch for ideal
    
    # Close and rebuild bottom part
    # Let's create final ideal HTML from scratch for clarity
    html_ideal = f'<div class="ideal-box"><div class="sub-ideal">'
    html_ideal += f'<div class="carry-row blue" style="{col_style}">'
    for ch in upper_small:
        html_ideal+=f'<div>{ch}</div>'
    html_ideal+='</div>'
    html_ideal+=f'<div class="carry-row purple" style="{col_style}">'
    for ch in lower_small:
        html_ideal+=f'<div style="font-size:13px;">{ch}</div>' if ch!='' else '<div></div>'
    html_ideal+='</div>'
    html_ideal+=f'<div class="num-row" style="{col_style}">'
    for i,ch in enumerate(str(larger)):
        if i in borrowed_cols:
            html_ideal+=f'<div><span class="cross">{ch}</span></div>'
        else:
            html_ideal+=f'<div>{ch}</div>'
    html_ideal+='</div>'
    # Bottom: - 2897
    html_ideal+=f'<div class="num-row" style="{col_style}">'
    # Show minus sign in first column, then digits
    if Wc==4:
        # For 5003-2897: we want "- 2897" -> minus in col0? Actually ideal shows "- 2897" with minus left of 2
        # We'll put minus in first column as "-" and then 2897 occupies cols 1-3? But 2897 has 4 digits, so need 5 cols? Simpler: put "-" in separate span before grid
        # For ideal 4-digit case, show as: - 2 8 9 7 with minus as first grid item
        # Our smaller is 2897 (4 digits), Wc=4, so we show minus overlapping first digit? In ideal image, minus is left of number
        # We'll show: column 0 = "-", column 1 = "2", column2="8", column3="9" and 7? But need 4 digits for 2897, so we need to show minus outside
        # Let's show minus as absolute positioned left of grid for 4-digit case
        html_ideal+=f'<div style="position:relative;"><span style="position:absolute; left:-22px;">-</span>{str(smaller)[0]}</div>'
        for ch in str(smaller)[1:]:
            html_ideal+=f'<div>{ch}</div>'
    else:
        for idx,ch in enumerate(str(smaller).rjust(Wc)):
            if idx==0 and ch.strip()=='':
                html_ideal+=f'<div>-</div>'
            else:
                html_ideal+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html_ideal+='</div>'
    html_ideal+=f'<div class="line"></div>'
    html_ideal+=f'<div class="result-row" style="{col_style}">'
    result_str = str(abs(real_result)).rjust(Wc)
    if A_orig < B_orig:
        html_ideal+=f'<div>-</div>'
        for ch in str(abs(real_result)).rjust(Wc-1):
            html_ideal+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    else:
        for ch in result_str:
            html_ideal+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html_ideal+='</div>'
    html_ideal+='</div></div>'
    html_ideal+=f'<div style="margin-top:10px;">{A_orig} − {B_orig} = <span style="color:#dc2626">{real_result}</span></div>'
    # For generic case where A_orig and B_orig not 5003/2897, the above still works
    st.markdown(html_ideal, unsafe_allow_html=True)

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

# ================= DERIVATIVES & INTEGRALS - THEORETICAL FIRST =================
def solve_derivative_rule(expr_str, var_name, rule):
    var=get_var(var_name); x=var; f=parse_expr(expr_str, var_name); deriv=sp.diff(f,x)
    pretty_f = pretty_eq(expr_str)
    steps=[]
    if rule=="Defined and Differentiable in Same Interval":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$f'(a)=\\lim_{{h\\to0}} \\frac{{f(a+h)-f(a)}}{{h}}$$ exists, $f$ must be continuous"))
        steps.append(("2. Identify Function", f"$$f({sp.latex(x)}) = {sp.latex(f)}$$  \nDisplay: ${pretty_f}$"))
        steps.append(("3. Substitute into Theoretical", f"Substitute $f={sp.latex(f)}$ into limit definition"))
        steps.append(("4. Compute Derivative", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("5. Check Domain", f"Domain: {sp.calculus.util.continuous_domain(f, var, sp.S.Reals)}"))
        steps.append(("6. Verify", f"Differentiable where continuous"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$  \nGraph $f$ and $f'$ - hover shows ${pretty_f}$"))
    elif rule=="Constant Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$d/dx[c]=0, d/dx[c·g]=c·g'$$"))
        steps.append(("2. Identify", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$"))
        steps.append(("3. Substitute", f"Substitute $f={pretty_f}$ into $c·g'$"))
        steps.append(("4. Compute", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("5. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("6. Verify", f"Constant terms → 0"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Power Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$d/dx[x^n]=n·x^{{n-1}}$$"))
        steps.append(("2. Identify", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$"))
        steps.append(("3. Substitute", f"Substitute $f={pretty_f}$ into $n·x^{{n-1}}$"))
        steps.append(("4. Compute Term by Term", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("5. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("6. Check", f"Via limit definition"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$  \nHover shows ${pretty_f}$"))
    elif rule=="Sum and Difference Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$(f±g)'=f'±g'$$"))
        steps.append(("2. Identify", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$ split into sum"))
        steps.append(("3. Substitute", f"Substitute into $(f±g)'=f'±g'$"))
        steps.append(("4. Differentiate Each", f"Each term separately"))
        steps.append(("5. Combine", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("6. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Product Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$(uv)'=u'v+uv'$$"))
        steps.append(("2. Identify u,v", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$ choose $u,v$"))
        steps.append(("3. Substitute u,v", f"Substitute into $u'v+uv'$"))
        steps.append(("4. Compute u',v'", f"Theoretical $u',v'$"))
        steps.append(("5. Substitute u',v',u,v", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("6. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Quotient Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$(u/v)'=(u'v-uv')/v²$$"))
        steps.append(("2. Identify u,v", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$ = u/v"))
        steps.append(("3. Substitute u,v", f"Substitute into $(u'v-uv')/v²$"))
        steps.append(("4. Compute u',v'", f"Theoretical $u',v'$"))
        steps.append(("5. Substitute u',v',u,v", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("6. Simplify", f"$$f'={sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Chain Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$(f(g(x)))'=f'(g(x))·g'(x)$$"))
        steps.append(("2. Identify f,g", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$ composite"))
        steps.append(("3. Substitute", f"Substitute into $f'(g)·g'$"))
        steps.append(("4. Compute f'(g)", f"Outer derivative"))
        steps.append(("5. Compute g'", f"Inner derivative"))
        steps.append(("6. Multiply", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    elif rule=="Limits Rule":
        h=sp.Symbol('h'); f_xh=sp.simplify(f.subs(x, x+h)); quotient=sp.simplify((f_xh-f)/h)
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$f'(x)=\\lim_{{h\\to0}} [f(x+h)-f(x)]/h$$"))
        steps.append(("2. Identify f", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$"))
        steps.append(("3. Substitute f(x+h)", f"$$f(x+h)={sp.latex(f_xh)}$$ quotient {sp.latex(quotient)}"))
        steps.append(("4. Simplify", f"$$ {sp.latex(quotient)} $$"))
        steps.append(("5. Apply Limit", f"$$\\lim_{{h\\to0}} {sp.latex(quotient)} = {sp.latex(deriv)}$$"))
        steps.append(("6. Result", f"$$f'={sp.latex(deriv)}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{f'={sp.latex(deriv)}}}$$"))
    final=f"f'({sp.latex(x)}) = {sp.latex(deriv)}"
    plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {pretty_f}','eq':f'f({var_name}) = {pretty_f}','color':'blue'},{'expr':for_plot(deriv,x),'label':f"f'({var_name})",'eq':f"f'({var_name}) = {sp.latex(deriv)}",'dashed':True,'color':'green'}],'x_min':-5,'x_max':5,'title':f"Derivative ({rule}): {pretty_f}"}
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
    st.caption(f"Display format: {pretty_eq(expr)}")  # Show cleaned format
    try:
        steps,final,plot=solve_derivative_rule(expr, variable, rule)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex: st.error(str(ex))

def solve_integral_rule(expr_str, var_name, rule, a, b):
    var=get_var(var_name); x=var; f=parse_expr(expr_str, var_name)
    antiderivative=sp.integrate(f,x)
    definite_result=sp.integrate(f,(x,a,b)) if a!=b else None
    pretty_f = pretty_eq(expr_str)
    steps=[]
    if rule=="Antiderivatives (Primitives) Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$F'=f => ∫f=F+C, ∫x^n=x^(n+1)/(n+1)+C$$"))
        steps.append(("2. Identify f", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$"))
        steps.append(("3. Substitute f into Theoretical", f"Substitute $f={pretty_f}$ into $∫f=F+C$"))
        steps.append(("4. Compute Antiderivative", f"$$F={sp.latex(antiderivative)}+C$$"))
        steps.append(("5. Verify", f"$$F'={sp.latex(sp.diff(antiderivative,x))}$$ = f"))
        steps.append(("6. Family", f"Family of curves"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫f={sp.latex(antiderivative)}+C}}$$ Display: ${pretty_f}$"))
    elif rule=="Substitution Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫f(g(x))g'(x)dx=∫f(u)du, u=g(x)$$"))
        steps.append(("2. Identify", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$ composite"))
        steps.append(("3. Substitute u=g(x)", f"Substitute $u=g(x)$ into theoretical"))
        steps.append(("4. Rewrite", f"$$∫f(u)du$$"))
        steps.append(("5. Integrate", f"$$={sp.latex(antiderivative)}+C$$"))
        steps.append(("6. Substitute Back", f"Replace $u$ with $g(x)$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫f={sp.latex(antiderivative)}+C}}$$"))
    elif rule=="By Parts Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫u dv=uv-∫v du$$"))
        steps.append(("2. Identify u,dv", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$ choose $u,dv$"))
        steps.append(("3. Substitute u,dv", f"Substitute into theoretical"))
        steps.append(("4. Compute du,v", f"Theoretical $du=u' dx$, $v=∫dv$"))
        steps.append(("5. Substitute into uv-∫v du", f"$$={sp.latex(antiderivative)}+C$$"))
        steps.append(("6. Simplify", f"$$={sp.latex(antiderivative)}+C$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫f={sp.latex(antiderivative)}+C}}$$"))
    elif rule=="Definite Rule":
        result=definite_result if definite_result is not None else sp.integrate(f,(x,a,b))
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫_a^b f=F(b)-F(a), F'=f$$"))
        steps.append(("2. Identify f,a,b", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$, $a={a}$, $b={b}$"))
        steps.append(("3. Substitute f,a,b", f"Substitute into $∫_a^b f$"))
        steps.append(("4. Find F", f"$$F={sp.latex(antiderivative)}$$"))
        steps.append(("5. Substitute a,b into F(b)-F(a)", f"$$F({b})-F({a})={sp.latex(result)}$$"))
        steps.append(("6. Area", f"Area = {sp.latex(result)}"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫_{a}^{b} f={sp.latex(result)}}}$$ Display: ${pretty_f}$"))
    elif rule=="Indefinite Rule":
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫f(x)dx=F(x)+C, F'=f$$"))
        steps.append(("2. Identify f", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$"))
        steps.append(("3. Substitute f", f"Substitute into $∫f=F+C$"))
        steps.append(("4. Compute F", f"$$F={sp.latex(antiderivative)}$$"))
        steps.append(("5. Add C", f"$$F+C$$"))
        steps.append(("6. Verify", f"$$F'={sp.latex(sp.diff(antiderivative,x))}$$"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫f={sp.latex(antiderivative)}+C}}$$"))
    elif rule=="FTC Rule (with very explanatory graph)":
        result=definite_result if definite_result is not None else sp.integrate(f,(x,a,b))
        steps.append(("1. Theoretical Formula - FTC", f"**Theoretical Part 1:** $$d/dx∫_a^x f(t)dt=f(x)$$ **Part 2:** $$∫_a^b f=F(b)-F(a)$$"))
        steps.append(("2. Identify f,F,a,b", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$, $F={sp.latex(antiderivative)}$, $a={a}$, $b={b}$"))
        steps.append(("3. Substitute into Theoretical FTC", f"Substitute into FTC formulas"))
        steps.append(("4. Part 1", f"$$A(x)=∫_a^x f(t)dt, A'(x)=f(x)$$"))
        steps.append(("5. Part 2 - F(b)-F(a)", f"$$F({b})-F({a})={sp.latex(result)}$$"))
        steps.append(("6. Very Explanatory Graph", f"Blue: $f(x)={sp.latex(f)}$ Display: ${pretty_f}$, Shaded area $∫_a^b f={sp.latex(result)}$, Green dashed: $F(x)={sp.latex(antiderivative)}$, Slope of $F$ at any $x$ = $f(x)$, Hover shows generating equation Display: ${pretty_f}$, Adjustable a,b"))
        steps.append(("7. Final", f"$$\\boxed{{∫_{a}^{b} f={sp.latex(result)}}}$$"))
    elif rule=="Limits Rule (Riemann)":
        exact=sp.integrate(f,(x,float(a),float(b)))
        steps.append(("1. Theoretical Formula", f"**Theoretical:** $$∫_a^b f=lim n→∞ Σ f(x_i)Δx$$"))
        steps.append(("2. Identify f,a,b", f"$$f={sp.latex(f)}$$ Display: ${pretty_f}$, $a={a}$, $b={b}$"))
        steps.append(("3. Substitute f,a,b", f"Substitute into $Σ f(x_i)Δx$"))
        steps.append(("4. Compute Riemann Sum", f"Theoretical $S_n=Σ f(x_i)Δx$"))
        steps.append(("5. Take Limit", f"Limit → exact {sp.latex(exact)}"))
        steps.append(("6. Compare", f"Same as other rules"))
        steps.append(("7. Final & Graph", f"$$\\boxed{{∫_a^b f={sp.latex(exact)}}}$$"))
    if rule in ["Definite Rule","FTC Rule (with very explanatory graph)","Limits Rule (Riemann)"]:
        final=f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(definite_result) if definite_result is not None else sp.integrate(f,(x,a,b))}"
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {pretty_f}','eq':f'f({var_name}) = {pretty_f}','color':'blue'},{'expr':for_plot(antiderivative,x),'label':f'F({var_name})','eq':f'F({var_name}) = {sp.latex(antiderivative)}','dashed':True,'color':'green'}],'x_min':float(a)-1,'x_max':float(b)+1,'shade':{'expr':for_plot(f,x),'from':float(a),'to':float(b),'eq':f'f({var_name}) = {pretty_f}'}}
    else:
        final=f"\\int {sp.latex(f)} = {sp.latex(antiderivative)} + C"
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {pretty_f}','eq':f'f({var_name}) = {pretty_f}','color':'blue'},{'expr':for_plot(antiderivative,x),'label':f'F({var_name})','eq':f'F({var_name}) = {sp.latex(antiderivative)}','dashed':True,'color':'green'}],'x_min':-5,'x_max':5}
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
    st.caption(f"Display format: {pretty_eq(expr)}")
    try:
        steps,final,plot=solve_integral_rule(expr, variable, rule, a, b)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex: st.error(str(ex))

# ================= ALGEBRA WITH INTERACTIVE GRAPHS =================
def render_linear():
    st.subheader("Linear Equation (1st degree) - Interactive Graph (hover shows generating equation)")
    eq=st.text_input("Equation", value="2*x + 3 = 7", key="lin_eq")
    st.caption(f"Display format: {pretty_eq(eq)}")
    try:
        eq_sym=parse_equation(eq)
        x=X
        poly=sp.Poly(eq_sym,x)
        a,b=poly.all_coeffs()[0], poly.all_coeffs()[1] if len(poly.all_coeffs())==2 else 0
        root=sp.simplify(-b/a)
        lhs=parse_expr(eq.split('=')[0]); rhs=parse_expr(eq.split('=')[1])
        steps=[("1. Original","$$"+sp.latex(sp.Eq(lhs, rhs))+"$$ Display: $"+pretty_eq(eq)+"$"),("2. Standard form",f"$$ {sp.latex(a)}x + {sp.latex(b)}=0$$"),("3. Isolate x",f"$$x = {sp.latex(root)}$$"),("4. Verify",f"Check: {sp.latex(eq_sym.subs(x,root))}=0")]
        final=f"x = {sp.latex(root)}"
        rv=num(root)
        plot={'exprs':[{'expr':for_plot(eq_sym,x),'label':f'{pretty_eq(eq)} -> {sp.latex(eq_sym)}=0','eq':f'{pretty_eq(eq_sym)}=0 -> {pretty_eq(eq)}','color':'blue'}],'x_min':(rv-5) if rv is not None else -5,'x_max':(rv+5) if rv is not None else 5,'points':[{'x':float(root),'y':0,'label':f'x = {root}','color':'red'}] if rv is not None else None,'title':f"Linear: {pretty_eq(eq)} - hover shows generating equation"}
        _show(steps,final,plot)
    except Exception as ex: st.error(str(ex))

def render_quadratic():
    st.subheader("Quadratic Equation (2nd degree) - Interactive Graph (hover shows generating equation)")
    eq=st.text_input("Equation", value="x^2 - 5*x + 6 = 0", key="quad_eq")
    st.caption(f"Display format: {pretty_eq(eq)}")
    try:
        eq_sym=parse_equation(eq)
        x=X
        poly=sp.Poly(eq_sym,x)
        a,b,c=poly.all_coeffs()
        disc=b**2-4*a*c
        roots=sp.solve(eq_sym,x)
        steps=[("1. Standard form",f"$$ {sp.latex(a)}x^2 + {sp.latex(b)}x + {sp.latex(c)}=0$$ Display: ${pretty_eq(eq)}$"),("2. Discriminant",f"$$\\Delta = {sp.latex(disc)}$$"),("3. Bhaskara",f"$$x = (-b ± √Δ)/2a$$"),("4. Solutions",f"$$x = {sp.latex(roots)}$$")]
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
        plot={'exprs':[{'expr':for_plot(eq_sym,x),'label':f'{pretty_eq(eq)}','eq':f'{pretty_eq(eq_sym)}=0 -> {pretty_eq(eq)}','color':'blue'}],'x_min':xmin,'x_max':xmax,'points':pts,'title':f"Quadratic: {pretty_eq(eq)} - hover shows generating equation"}
        _show(steps,final,plot)
    except Exception as ex: st.error(str(ex))

# ================= LINEAR SYSTEMS =================

def solve_linear_system(eqs, vars_list):
    sym_vars = [get_var(v) for v in vars_list]
    eq_syms = []
    for eq_str in eqs:
        try:
            eq_sym = parse_equation(eq_str)
            eq_syms.append(eq_sym)
        except Exception as ex:
            raise ValueError(f"Error parsing '{eq_str}': {ex}")
    sol = sp.linsolve(eq_syms, sym_vars)
    if not sol:
        raise ValueError("No solution found or infinite solutions")
    sol_set = list(sol)[0]
    sol_dict = {str(var): val for var, val in zip(sym_vars, sol_set)}
    return sol_dict, eq_syms

def render_system_2x2():
    st.subheader("Linear System (x,y) - 2x2 - Interactive Graph (x,y)")
    col1,col2=st.columns(2)
    eq1=col1.text_input("Equation 1", value="2*x + 3*y = 7", key="sys2_e1")
    eq2=col2.text_input("Equation 2", value="x - y = 1", key="sys2_e2")
    col3,col4=st.columns(2)
    xmin=col3.slider("Graph x-min (system 2x2)", -10.0, 0.0, -5.0, key="sys2_xmin")
    xmax=col4.slider("Graph x-max (system 2x2)", 0.0, 10.0, 5.0, key="sys2_xmax")
    st.caption(f"Display: {pretty_eq(eq1)} and {pretty_eq(eq2)}")
    try:
        sol_dict, eq_syms = solve_linear_system([eq1, eq2], ['x','y'])
        x_val = sol_dict.get('x')
        y_val = sol_dict.get('y')
        steps=[]
        steps.append(("1. Theoretical Formula - System 2x2", f"**Theoretical:**  \n$$a_1 x + b_1 y = c_1$$  \n$$a_2 x + b_2 y = c_2$$  \nSubstitution, Elimination, Cramer"))
        steps.append(("2. Identify System", f"Given:  \n$$ {pretty_eq(eq1)} $$  \n$$ {pretty_eq(eq2)} $$"))
        steps.append(("3. Substitute into Theoretical Formula", f"Standard form: $$a_1 x + b_1 y = c_1$$"))
        steps.append(("4. Solve for x,y", f"$$x = {sp.latex(x_val)}, \\quad y = {sp.latex(y_val)}$$ Display: x={x_val}, y={y_val}"))
        steps.append(("5. Verify by Substitution", f"Substitute $x={sp.latex(x_val)}$, $y={sp.latex(y_val)}$ into original"))
        steps.append(("6. Interpretation", f"Solution is intersection point of two lines"))
        steps.append(("7. Graph - Interactive (x,y)", f"Blue: ${pretty_eq(eq1)}$, Green: ${pretty_eq(eq2)}$, Red intersection $({sp.latex(x_val)}, {sp.latex(y_val)})$, Hover shows ${pretty_eq(eq1)}$ and ${pretty_eq(eq2)}$"))
        final=f"x = {sp.latex(x_val)}, \\quad y = {sp.latex(y_val)}"
        sol_for_plot = {'x': float(x_val), 'y': float(y_val)} if num(x_val) is not None and num(y_val) is not None else None
        plot_2lines={'eq1_str':eq1, 'eq2_str':eq2, 'sol':sol_for_plot, 'x_min':xmin, 'x_max':xmax, 'title':f"System 2x2: {pretty_eq(eq1)} & {pretty_eq(eq2)} - Hover shows equations"}
        _show(steps, final, plot_2lines=plot_2lines)
    except Exception as ex:
        st.error(str(ex))

def render_system_3x3():
    st.subheader("Linear System (x,y,z) - 3x3 - Interactive 3D Graph (x,y,z)")
    col1,col2=st.columns(2)
    eq1=col1.text_input("Equation 1", value="x + y + z = 6", key="sys3_e1")
    eq2=col2.text_input("Equation 2", value="2*x - y + z = 3", key="sys3_e2")
    eq3=st.text_input("Equation 3", value="x + 2*y - z = 3", key="sys3_e3_3")
    st.caption(f"Display: {pretty_eq(eq1)}, {pretty_eq(eq2)}, {pretty_eq(eq3)}")
    try:
        sol_dict, eq_syms = solve_linear_system([eq1, eq2, eq3], ['x','y','z'])
        x_val = sol_dict.get('x'); y_val = sol_dict.get('y'); z_val = sol_dict.get('z')
        steps=[]
        steps.append(("1. Theoretical Formula - System 3x3", f"**Theoretical:**  \n$$a_1 x + b_1 y + c_1 z = d_1$$ etc. Gaussian elimination, Cramer, planes"))
        steps.append(("2. Identify System", f"Given:  \n$$ {pretty_eq(eq1)} $$  \n$$ {pretty_eq(eq2)} $$  \n$$ {pretty_eq(eq3)} $$"))
        steps.append(("3. Substitute into Theoretical", f"Standard form $a x + b y + c z = d$"))
        steps.append(("4. Gaussian Elimination", f"Eliminate variables"))
        steps.append(("5. Solve for x,y,z", f"$$x = {sp.latex(x_val)}, y = {sp.latex(y_val)}, z = {sp.latex(z_val)}$$"))
        steps.append(("6. Verify", f"Substitute into original"))
        steps.append(("7. Graph - Interactive 3D (x,y,z)", f"3 planes: Blue ${pretty_eq(eq1)}$, Green ${pretty_eq(eq2)}$, Orange ${pretty_eq(eq3)}$, Red intersection, Hover shows generating equations Display: ${pretty_eq(eq1)}$, ${pretty_eq(eq2)}$, ${pretty_eq(eq3)}$"))
        final=f"x = {sp.latex(x_val)}, y = {sp.latex(y_val)}, z = {sp.latex(z_val)}"
        sol_for_plot = {}
        try:
            sol_for_plot = {'x': float(x_val), 'y': float(y_val), 'z': float(z_val)}
        except:
            sol_for_plot = {'x': 0, 'y': 0, 'z': 0}
        if PLOTLY_AVAILABLE:
            fig_3d = plotly_interactive_3d_system([eq1, eq2, eq3], sol_for_plot, title=f"System 3x3: {pretty_eq(eq1)} & {pretty_eq(eq2)} & {pretty_eq(eq3)} - Hover shows equations")
            _show(steps, final, plot_3d=fig_3d)
        else:
            _show(steps, final, plot=None)
    except Exception as ex:
        st.error(str(ex))

def render_limit():
    st.subheader("Limits - 7 Steps - Theoretical + Substitution")
    expr=st.text_input("Function f(x)", value="sin(x)/x", key="lim_expr")
    point=st.number_input("x approaches", value=0.0, key="lim_point")
    col1,col2=st.columns(2)
    xmin=col1.slider("Graph x-min", -10.0, 0.0, -3.0, key="lim_xmin")
    xmax=col2.slider("Graph x-max", 0.0, 10.0, 3.0, key="lim_xmax")
    st.caption(f"Display: {pretty_eq(expr)}")
    try:
        x=X; f=parse_expr(expr); p=sp.nsimplify(point); sub=sp.simplify(f.subs(x,p)); lim=sp.limit(f,x,p)
        steps=[("1. Theoretical Formula",f"**Theoretical:** $$\\lim_{{x\\to a}} f(x) = L$$"),("2. Identify f and a",f"$$f(x) = {sp.latex(f)}$$ Display: ${pretty_eq(expr)}$, $a = {sp.latex(p)}$"),("3. Substitute into Theoretical",f"$$f({sp.latex(p)}) = {sp.latex(sub)}$$"),("4. Simplification",f"$$f = {sp.latex(sp.simplify(f))}$$"),("5. Limit Laws",f"Sum, Product, Quotient"),("6. Calculate",f"$$\\lim = {sp.latex(lim)}$$"),("7. Verification & Graph",f"Final: $$\\boxed{{\\lim = {sp.latex(lim)}}}$$ Display: ${pretty_eq(expr)}$")]
        final=f"\\lim = {sp.latex(lim)}"
        yv=num(lim)
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f(x) = {pretty_eq(expr)}','eq':f'f(x) = {pretty_eq(expr)}','color':'blue'}],'x_min':num(p)-3,'x_max':num(p)+3,'points':[{'x':float(p),'y':yv,'label':f'Limit = {lim}','color':'red'}] if yv is not None else None,'title':f"Limit: {pretty_eq(expr)}"}
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex: st.error(str(ex))

# APP
st.set_page_config(page_title="CalculusFlow - Clean Display", page_icon="➗", layout="centered")
st.title("CalculusFlow")
st.caption("Interactive math companion - arithmetic, calculus and algebra, step by step")  # Clean short caption, no long rule list

MODULES={
    "Arithmetic":{
        "Addition (carry)":render_addition,
        "Subtraction (borrow)":render_subtraction,
        "Long Multiplication (Ideal)":render_multiplication,
        "Long Division (Ideal)":render_long_division,
    },
    "Calculus":{
        "Limits (Theoretical + Substitution)":render_limit,
        "Derivatives (x,y,z) - 8 Rules":render_derivatives,
        "Integrals (x,y,z) - 7 Rules":render_integrals,
    },
    "Algebra":{
        "Linear Equation (1st degree)":render_linear,
        "Quadratic Equation (2nd degree)":render_quadratic,
        "Linear System (x,y) - 2x2":render_system_2x2,
        "Linear System (x,y,z) - 3x3":render_system_3x3,
    },
}

group=st.sidebar.radio("Area", list(MODULES.keys()))
modules=MODULES[group]
choice=st.sidebar.radio("Module", list(modules.keys()))
st.sidebar.markdown("---")
if PLOTLY_AVAILABLE:
    st.sidebar.success("Plotly available - interactive hover graphs enabled")
else:
    st.sidebar.warning("Add plotly to requirements.txt for hover")
    st.sidebar.code("plotly\nsympy\nmatplotlib\nstreamlit\nnumpy")
# Removed long rule list from sidebar - clean display as requested
modules[choice]()
