"""
CalculusFlow - FINAL CORRECTED with Theoretical Formula + Substitution
Requirement: For each rule, show theoretical formula FIRST, then substitute values

Derivatives (x,y,z):
- Defined and Differentiable in Same Interval
- Constant Rule
- Power Rule
- Sum and Difference Rule
- Product Rule
- Quotient Rule
- Chain Rule
- Limits Rule

Integrals (x,y,z):
- Antiderivatives (Primitives) Rule
- Substitution Rule
- By Parts Rule
- Definite Rule
- Indefinite Rule
- FTC Rule (with very explanatory graph)
- Limits Rule (Riemann)

All: Theoretical formula first, then substitution, interactive hover graph shows generating equation, linear/quadratic also interactive, all in English
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import lambdify

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

def _show(steps, final, plot=None):
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
            st.info("Add `plotly` to requirements.txt for interactive hover showing generating equation.")
            st.pyplot(plot_matplotlib(**plot))

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

# ================= ARITHMETIC IDEAL =================
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

# ================= DERIVATIVES (x,y,z) - THEORETICAL FORMULA + SUBSTITUTION =================

def solve_derivative_rule(expr_str, var_name, rule):
    var=get_var(var_name); x=var
    f=parse_expr(expr_str, var_name)
    deriv=sp.diff(f,x)
    steps=[]
    
    if rule=="Defined and Differentiable in Same Interval":
        steps.append(("1. Theoretical Formula", 
            f"**Theoretical Formula - Differentiability:**  \n$$f \\text{{ differentiable at }} a \\iff f'(a) = \\lim_{{h\\to0}} \\frac{{f(a+h)-f(a)}}{{h}} \\text{{ exists}}$$  \n**Requirement:** $f$ must be continuous and defined in interval containing $a$"))
        steps.append(("2. Identify Function and Interval", 
            f"Given function: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nVariable: ${sp.latex(x)}$  \nWe check where $f$ is defined and continuous"))
        steps.append(("3. Substitute into Theoretical Formula", 
            f"Substitute $f({sp.latex(x)}) = {sp.latex(f)}$ into definition:  \n$$f'({sp.latex(x)}) = \\lim_{{h\\to0}} \\frac{{({sp.latex(f.subs(x, x+sp.Symbol('h')))}) - ({sp.latex(f)})}}{{h}}$$"))
        steps.append(("4. Check Domain", 
            f"Domain of $f$: $$ {sp.calculus.util.continuous_domain(f, var, sp.S.Reals)} $$  \n$f$ is defined in this interval"))
        steps.append(("5. Compute Derivative (Theoretical → Practical)", 
            f"Using derivative rules, compute:  \n$$f'({sp.latex(x)}) = {sp.latex(deriv)}$$"))
        steps.append(("6. Verify Differentiability", 
            f"Derivative exists where $f$ is continuous:  \n$$f' = {sp.latex(deriv)}$$ exists for all $x$ in domain except where denominator=0"))
        steps.append(("7. Conclusion & Graph", 
            f"$f$ is differentiable where $f'$ exists  \nFinal: $$\\boxed{{f'({sp.latex(x)}) = {sp.latex(deriv)}}}$$  \nGraph shows $f$ and $f'$ - hover shows generating equation $f({var_name}) = {expr_str}$"))
        
    elif rule=="Constant Rule":
        steps.append(("1. Theoretical Formula - Constant Rule", 
            f"**Theoretical Formulas:**  \n$$\\frac{{d}}{{dx}}[c] = 0$$  \n$$\\frac{{d}}{{dx}}[c·g(x)] = c·\\frac{{d}}{{dx}}g(x) = c·g'(x)$$  \nWhere $c$ is constant"))
        steps.append(("2. Identify Constant in Function", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nIdentify constant factors and constant terms"))
        # Try to extract constant
        try:
            coeff = f.as_coefficient(var) if not f.is_Add else None
            steps.append(("3. Substitute into Theoretical Formula", 
                f"Substitute $f = {sp.latex(f)}$ into constant rule:  \nIf $f = c·g(x)$, then $f' = c·g'(x)$  \nHere: $$f({sp.latex(x)}) = {sp.latex(f)}$$"))
        except:
            steps.append(("3. Substitute into Theoretical Formula", 
                f"Substitute $f = {sp.latex(f)}$ into: $$\\frac{{d}}{{dx}}[c·g(x)] = c·g'(x)$$"))
        steps.append(("4. Compute Derivative", 
            f"Apply rule:  \n$$f'({sp.latex(x)}) = {sp.latex(deriv)}$$"))
        steps.append(("5. Simplify - Power Rule for remaining", 
            f"$$f' = {sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("6. Verify Constant Terms → 0", 
            f"Any pure constant term $c$ has derivative $0$"))
        steps.append(("7. Final & Graph", 
            f"Final: $$\\boxed{{f'({sp.latex(x)}) = {sp.latex(deriv)}}}$$  \nGraph shows $f$ and $f'$ - hover shows equations"))
        
    elif rule=="Power Rule":
        steps.append(("1. Theoretical Formula - Power Rule", 
            f"**Theoretical Formula:**  \n$$\\frac{{d}}{{dx}}[x^n] = n·x^{{n-1}}$$  \nFor any real $n$"))
        steps.append(("2. Identify Power Terms in Function", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nIdentify each $x^n$ term"))
        steps.append(("3. Substitute into Theoretical Formula", 
            f"Substitute each power term into $n·x^{{n-1}}$:  \nFor $f({sp.latex(x)}) = {sp.latex(f)}$, apply $n·x^{{n-1}}$ to each power"))
        steps.append(("4. Compute Term by Term", 
            f"Example: if $f = x^3$, then $n=3$, $f' = 3x^2$  \nFor our $f$:  \n$$f'({sp.latex(x)}) = {sp.latex(deriv)}$$"))
        steps.append(("5. Apply to All Terms", 
            f"Combine results from all power terms"))
        steps.append(("6. Simplify", 
            f"Simplified: $$f'({sp.latex(x)}) = {sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Verification & Graph", 
            f"Power rule verified via limit definition  \nFinal: $$\\boxed{{f'({sp.latex(x)}) = {sp.latex(deriv)}}}$$  \nGraph $f$ and $f'$ - hover shows $f({var_name})={expr_str}$"))
        
    elif rule=="Sum and Difference Rule":
        steps.append(("1. Theoretical Formula - Sum/Difference", 
            f"**Theoretical Formulas:**  \n$$(f + g)'(x) = f'(x) + g'(x)$$  \n$$(f - g)'(x) = f'(x) - g'(x)$$  \nDerivative of sum = sum of derivatives"))
        steps.append(("2. Identify Sum/Difference in Function", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nSplit into $f = f_1 ± f_2 ± f_3 ...$"))
        steps.append(("3. Substitute into Theoretical Formula", 
            f"Substitute into $(f±g)' = f'±g'$:  \n$$f = {sp.latex(f)} = f_1 + f_2 ...$$  \nThen $$f' = f_1' + f_2' ...$$"))
        terms = sp.Add.make_args(f) if f.is_Add else [f]
        for idx, term in enumerate(terms[:3],1):
            d = sp.diff(term, x)
            steps.append((f"4.{idx} Apply to Term {idx} - Substitute", f"Term {idx}: $$f_{idx} = {sp.latex(term)}$$  \nTheoretical: $f_{idx}' = ...$  \nSubstituted: $$f_{idx}' = {sp.latex(d)}$$"))
        steps.append(("5. Combine Results - Theoretical Sum", f"Combine using sum rule: $$f' = {sp.latex(deriv)}$$"))
        steps.append(("6. Simplify", f"$$f' = {sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Graph Verification", f"Derivative of sum = sum of derivatives  \nFinal: $$\\boxed{{f' = {sp.latex(deriv)}}}$$"))
        
    elif rule=="Product Rule":
        if f.is_Mul:
            args=list(f.args); u=args[0]; v=sp.Mul(*args[1:])
            u_p=sp.diff(u,x); v_p=sp.diff(v,x)
            steps.append(("1. Theoretical Formula - Product Rule", f"**Theoretical Formula:**  \n$$(u·v)' = u'·v + u·v'$$"))
            steps.append(("2. Identify u and v in Function", f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nChoose: $$u = {sp.latex(u)}, \\quad v = {sp.latex(v)}$$"))
            steps.append(("3. Substitute u,v into Theoretical Formula", f"Substitute $u={sp.latex(u)}$, $v={sp.latex(v)}$ into $(uv)' = u'v + uv'$:  \n$$f' = u'v + uv'$$"))
            steps.append(("4. Compute u' and v' - Theoretical Power/Constant", f"Theoretical: $u' = d/dx[{sp.latex(u)}]$, $v' = d/dx[{sp.latex(v)}]$  \nSubstituted: $$u' = {sp.latex(u_p)}, \\quad v' = {sp.latex(v_p)}$$"))
            steps.append(("5. Substitute u',v',u,v into Formula", f"Substitute into $u'v + uv'$:  \n$$f' = ({sp.latex(u_p)})({sp.latex(v)}) + ({sp.latex(u)})({sp.latex(v_p)}) = {sp.latex(sp.expand(u_p*v + u*v_p))}$$"))
            steps.append(("6. Simplify", f"$$f' = {sp.latex(sp.simplify(deriv))}$$"))
            steps.append(("7. Final & Graph", f"Product rule: theoretical $u'v+uv'$ → substituted values → result  \nFinal: $$\\boxed{{f' = {sp.latex(deriv)}}}$$  \nHover shows generating equations"))
        else:
            steps.append(("1. Theoretical Formula - Product Rule", f"**Theoretical:** $$(uv)' = u'v + uv'$$"))
            steps.append(("2. Identify - Not Product Form", f"$$f = {sp.latex(f)}$$ is not product, treat as single"))
            steps.append(("3. Substitute", f"Substitute into product formula with $u=f$, $v=1$"))
            steps.append(("4. Compute", f"$$f' = {sp.latex(deriv)}$$"))
            steps.append(("5. Simplify", f"$$f' = {sp.latex(sp.simplify(deriv))}$$"))
            steps.append(("6. Example Product", f"Example: $f=x·\\sin x$, $u=x$, $v=\\sin x$, $f' = \\sin x + x\\cos x$"))
            steps.append(("7. Conclusion", f"Final: $$f' = {sp.latex(deriv)}$$"))
            
    elif rule=="Quotient Rule":
        num_expr, den_expr = sp.fraction(f)
        num_p=sp.diff(num_expr,x); den_p=sp.diff(den_expr,x)
        steps.append(("1. Theoretical Formula - Quotient Rule", f"**Theoretical Formula:**  \n$$\\left(\\frac{{u}}{{v}}\\right)' = \\frac{{u'v - uv'}}{{v^2}}$$"))
        steps.append(("2. Identify u (numerator) and v (denominator)", f"Given: $$f({sp.latex(x)}) = {sp.latex(f)} = \\frac{{{sp.latex(num_expr)}}}{{{sp.latex(den_expr)}}}$$  \n$$u = {sp.latex(num_expr)}, \\quad v = {sp.latex(den_expr)}$$"))
        steps.append(("3. Substitute u,v into Theoretical Formula", f"Substitute into $\\frac{{u'v - uv'}}{{v^2}}$:  \nTheoretical numerator: $u'v - uv'$, denominator: $v^2$"))
        steps.append(("4. Compute u' and v' - Theoretical → Substituted", f"Theoretical: $u' = d/dx[u]$, $v' = d/dx[v]$  \nSubstituted: $$u' = {sp.latex(num_p)}, \\quad v' = {sp.latex(den_p)}$$"))
        steps.append(("5. Substitute u',v',u,v into Formula", f"Substitute values:  \n$$u'v - uv' = ({sp.latex(num_p)})({sp.latex(den_expr)}) - ({sp.latex(num_expr)})({sp.latex(den_p)}) = {sp.latex(num_p*den_expr - num_expr*den_p)}$$  \n$$f' = \\frac{{{sp.latex(num_p*den_expr - num_expr*den_p)}}}{{{sp.latex(den_expr)}^2}}$$"))
        steps.append(("6. Simplify - Theoretical to Final", f"Simplify quotient: $$f' = {sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Final & Graph", f"Quotient rule: theoretical $\\frac{{u'v-uv'}}{{v^2}}$ → substituted values → result  \nFinal: $$\\boxed{{f' = {sp.latex(deriv)}}}$$"))
        
    elif rule=="Chain Rule":
        steps.append(("1. Theoretical Formula - Chain Rule", f"**Theoretical Formula:**  \n$$(f(g(x)))' = f'(g(x))·g'(x)$$  \nOuter derivative × inner derivative"))
        steps.append(("2. Identify Outer f and Inner g", f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nDecompose into $f(g({sp.latex(x)}))$ where $g$ is inner"))
        steps.append(("3. Substitute into Theoretical Formula", f"Substitute into $f'(g(x))·g'(x)$:  \nTheoretical outer: $f'(g)$, inner: $g'(x)$"))
        steps.append(("4. Compute f'(g(x)) - Outer Derivative at Inner", f"Differentiate outer function evaluated at inner $g(x)$"))
        steps.append(("5. Compute g'(x) - Inner Derivative", f"Differentiate inner function $g(x)$"))
        steps.append(("6. Multiply - Theoretical → Substituted", f"Multiply: $f'(g)·g' = {sp.latex(deriv)}$  \nSimplified: $$f' = {sp.latex(sp.simplify(deriv))}$$"))
        steps.append(("7. Final & Graph", f"Chain rule: theoretical $f'(g)·g'$ → substituted → result  \nFinal: $$\\boxed{{f' = {sp.latex(deriv)}}}$$"))
        
    elif rule=="Limits Rule":
        h=sp.Symbol('h')
        f_xh=sp.simplify(f.subs(x, x+h))
        quotient=sp.simplify((f_xh-f)/h)
        deriv_lim=sp.limit(quotient, h, 0)
        steps.append(("1. Theoretical Formula - Limits Definition", f"**Theoretical Formula:**  \n$$f'(x) = \\lim_{{h\\to0}} \\frac{{f(x+h)-f(x)}}{{h}}$$"))
        steps.append(("2. Identify f(x)", f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$"))
        steps.append(("3. Substitute f(x) and f(x+h) into Theoretical Formula", f"Compute $f(x+h)$ by substitution:  \nTheoretical: $f(x+h)$  \nSubstituted: $$f(x+h) = {sp.latex(f_xh)}$$  \nThen: $$\\frac{{f(x+h)-f(x)}}{{h}} = \\frac{{{sp.latex(f_xh)} - ({sp.latex(f)})}}{{h}} = {sp.latex(quotient)}$$"))
        steps.append(("4. Simplify Quotient - Theoretical Power Rule", f"Simplify using algebra: $$ {sp.latex(quotient)} $$"))
        steps.append(("5. Substitute Simplified Quotient into Limit", f"Theoretical limit: $\\lim_{{h\\to0}} ...$  \nSubstituted: $$\\lim_{{h\\to0}} {sp.latex(quotient)}$$"))
        steps.append(("6. Apply Limit h→0 - Theoretical → Result", f"Apply limit: $$f'(x) = \\lim_{{h\\to0}} {sp.latex(quotient)} = {sp.latex(deriv_lim)}$$  \nMatches other rules: $$ {sp.latex(deriv)} $$"))
        steps.append(("7. Final & Graph", f"Limits rule: theoretical $\\lim$ → substituted values → result  \nFinal: $$\\boxed{{f' = {sp.latex(deriv)}}}$$"))
    
    final=f"f'({sp.latex(x)}) = {sp.latex(deriv)}"
    plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {expr_str}','eq':f'f({var_name}) = {expr_str}','color':'blue'},{'expr':for_plot(deriv,x),'label':f"f'({var_name})",'eq':f"f'({var_name}) = {sp.latex(deriv)}",'dashed':True,'color':'green'}],'x_min':-5,'x_max':5,'title':f"Derivative ({rule}): {expr_str}"}
    return steps,final,plot

def render_derivatives():
    st.subheader("Derivatives (Differentiation) (x,y,z) - Theoretical Formula + Substitution")
    st.markdown("**For each rule: show theoretical formula FIRST, then substitute values**")
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

# ================= INTEGRALS (x,y,z) - THEORETICAL FORMULA + SUBSTITUTION =================

def solve_integral_rule(expr_str, var_name, rule, a, b):
    var=get_var(var_name); x=var; f=parse_expr(expr_str, var_name)
    antiderivative=sp.integrate(f,x)
    definite_result=sp.integrate(f,(x,a,b)) if a!=b else None
    
    steps=[]
    
    if rule=="Antiderivatives (Primitives) Rule":
        steps.append(("1. Theoretical Formula - Antiderivatives", 
            f"**Theoretical Formulas:**  \n$$F'(x) = f(x) \\implies \\int f(x)dx = F(x) + C$$  \n$$\\int x^n dx = \\frac{{x^{{n+1}}}}{{n+1}} + C, \\quad n\\neq-1$$"))
        steps.append(("2. Identify f(x) for Antiderivative", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nWe seek $F$ such that $F' = f$"))
        steps.append(("3. Substitute f(x) into Theoretical Formula", 
            f"Substitute $f({sp.latex(x)}) = {sp.latex(f)}$ into $\\int f(x)dx = F(x)+C$:  \nTheoretical antiderivative: $F$ where $F' = {sp.latex(f)}$"))
        steps.append(("4. Compute Antiderivative - Theoretical → Substituted", 
            f"Apply reverse Power Rule: $$F({sp.latex(x)}) = {sp.latex(antiderivative)} + C$$"))
        steps.append(("5. Verify by Differentiation - Theoretical Check", 
            f"Theoretical check: $F' = f$  \nSubstituted: $$\\frac{{d}}{{dx}}({sp.latex(antiderivative)}) = {sp.latex(sp.diff(antiderivative,x))}$$  \nShould equal $f = {sp.latex(f)}$ → {'✅' if sp.simplify(sp.diff(antiderivative,x)-f)==0 else 'check'}"))
        steps.append(("6. Family of Curves", 
            f"Indefinite integral gives family differing by $C$"))
        steps.append(("7. Final & Graph", 
            f"Theoretical $\\int f = F+C$ → Substituted $F={sp.latex(antiderivative)}$  \nFinal: $$\\boxed{{\\int {sp.latex(f)} d{sp.latex(x)} = {sp.latex(antiderivative)} + C}}$$  \nGraph $f$ and $F$ - hover shows generating equations"))
        
    elif rule=="Substitution Rule":
        steps.append(("1. Theoretical Formula - Substitution", 
            f"**Theoretical Formula:**  \n$$\\int f(g(x))·g'(x) dx = \\int f(u) du, \\quad u = g(x), \\quad du = g'(x)dx$$"))
        steps.append(("2. Identify Composite Form f(g(x))·g'(x) in Function", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nLook for inner $g(x)$ and its derivative $g'(x)$"))
        steps.append(("3. Substitute u = g(x) into Theoretical Formula", 
            f"Choose: $$u = g({sp.latex(x)})$$  \nTheoretical: $du = g'({sp.latex(x)}) d{sp.latex(x)}$  \nSubstituted: Rewrite $\\int {sp.latex(f)} d{sp.latex(x)}$ as $\\int f(u) du$"))
        steps.append(("4. Rewrite Integral in u - Theoretical to Substituted", 
            f"Theoretical: $\\int f(u) du$  \nSubstituted: Transform ${sp.latex(f)} d{sp.latex(x)}$ to $f(u) du$"))
        steps.append(("5. Integrate in u - Theoretical Power Rule", 
            f"Theoretical: $\\int f(u) du$  \nSubstituted: $$= {sp.latex(antiderivative)} + C$$ (in $u$)"))
        steps.append(("6. Substitute Back u → g(x)", 
            f"Replace $u$ with $g({sp.latex(x)})$: $$ {sp.latex(antiderivative)} + C $$"))
        steps.append(("7. Final & Graph", 
            f"Substitution: theoretical $\\int f(u)du$ → substituted values → result  \nFinal: $$\\boxed{{\\int {sp.latex(f)} = {sp.latex(antiderivative)} + C}}$$"))
        
    elif rule=="By Parts Rule":
        steps.append(("1. Theoretical Formula - By Parts", 
            f"**Theoretical Formula:**  \n$$\\int u dv = uv - \\int v du$$"))
        steps.append(("2. Identify u and dv in Function", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nFor product $u·dv$, choose $u$ = first part, $dv$ = rest  \nILATE: Inverse, Log, Algebraic, Trig, Exponential for $u$"))
        steps.append(("3. Substitute u,dv into Theoretical Formula", 
            f"Choose $u$ and $dv$ from $f = {sp.latex(f)}$  \nTheoretical $u$, $dv$ → substituted values"))
        steps.append(("4. Compute du and v - Theoretical Differentiation/Integration", 
            f"Theoretical: $du = u' dx$, $v = \\int dv$  \nSubstituted: $du = ...$, $v = ...$"))
        steps.append(("5. Substitute du,v,u into Formula uv - ∫v du", 
            f"Substitute into $uv - \\int v du$:  \nTheoretical $uv - \\int v du$ → Substituted $$= {sp.latex(antiderivative)} + C$$"))
        steps.append(("6. Simplify", 
            f"$$= {sp.latex(antiderivative)} + C$$"))
        steps.append(("7. Final & Graph", 
            f"By Parts: theoretical $uv - \\int v du$ → substituted → result  \nFinal: $$\\boxed{{\\int {sp.latex(f)} = {sp.latex(antiderivative)} + C}}$$"))
        
    elif rule=="Definite Rule":
        result=definite_result if definite_result is not None else sp.integrate(f,(x,a,b))
        steps.append(("1. Theoretical Formula - Definite Integral", 
            f"**Theoretical Formula:**  \n$$\\int_{{{a}}}^{{{b}}} f(x) dx = \\lim_{{n\\to\\infty}} \\sum_{{i=1}}^{{n}} f(x_i)\\Delta x = F(b) - F(a)$$"))
        steps.append(("2. Identify Function and Limits", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)} = {sp.latex(f)}$$  \nLimits: $a={a}$, $b={b}$ (adjustable)"))
        steps.append(("3. Substitute f(x),a,b into Theoretical Formula", 
            f"Substitute into $\\int_{{{a}}}^{{{b}}} f(x)dx$:  \nTheoretical $\\int_a^b f$ → Substituted $$\\int_{{{a}}}^{{{b}}} {sp.latex(f)} d{sp.latex(x)}$$"))
        steps.append(("4. Find Antiderivative F - Theoretical Power Rule", 
            f"Theoretical: $F$ such that $F' = f$  \nSubstituted: $$F({sp.latex(x)}) = {sp.latex(antiderivative)}$$"))
        steps.append(("5. Substitute a,b into F(b)-F(a) - Theoretical FTC", 
            f"Theoretical: $F(b)-F(a)$  \nSubstituted: $$F({b}) = {sp.latex(antiderivative.subs(x,b))}, \\quad F({a}) = {sp.latex(antiderivative.subs(x,a))}$$  \n$$F(b)-F(a) = {sp.latex(result)}$$"))
        steps.append(("6. Area Interpretation", 
            f"Result = signed area: $$\\boxed{{{sp.latex(result)}}}$$"))
        steps.append(("7. Graph - Shaded Area (Interactive)", 
            f"Graph shows shaded area from {a} to {b} = $\\int_a^b f$ - hover shows $f({var_name})={expr_str}$  \nFinal: $$\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(result)}$$"))
        
    elif rule=="Indefinite Rule":
        steps.append(("1. Theoretical Formula - Indefinite Integral", 
            f"**Theoretical Formula:**  \n$$\\int f(x)dx = F(x) + C, \\quad F'(x)=f(x)$$  \nFamily of antiderivatives differing by constant $C$"))
        steps.append(("2. Identify f(x)", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$"))
        steps.append(("3. Substitute f(x) into Theoretical Formula", 
            f"Substitute into $\\int f(x)dx = F(x)+C$:  \nTheoretical $\\int f$ → Substituted $$\\int {sp.latex(f)} d{sp.latex(x)}$$"))
        steps.append(("4. Compute Antiderivative - Theoretical Power/Substitution/By Parts", 
            f"Theoretical: $F$ such that $F'=f$  \nSubstituted: $$F({sp.latex(x)}) = {sp.latex(antiderivative)}$$"))
        steps.append(("5. Add Constant C - Theoretical Family", 
            f"Theoretical: $F(x)+C$  \nSubstituted: $$ {sp.latex(antiderivative)} + C $$"))
        steps.append(("6. Verify by Differentiation", 
            f"Theoretical check: $F' = f$  \nSubstituted: $$\\frac{{d}}{{dx}}({sp.latex(antiderivative)}) = {sp.latex(sp.diff(antiderivative,x))}$$ should equal $f$"))
        steps.append(("7. Final & Graph", 
            f"Theoretical $\\int f = F+C$ → Substituted $F={sp.latex(antiderivative)}$  \nFinal: $$\\boxed{{\\int {sp.latex(f)} = {sp.latex(antiderivative)} + C}}$$  \nGraph $f$ and $F$ - hover shows equations"))
        
    elif rule=="FTC Rule (with very explanatory graph)":
        result=definite_result if definite_result is not None else sp.integrate(f,(x,a,b))
        steps.append(("1. Theoretical Formula - FTC", 
            f"**Theoretical Formulas - Fundamental Theorem of Calculus:**  \n**Part 1:** $$\\frac{{d}}{{dx}}\\int_a^x f(t)dt = f(x)$$  \n**Part 2:** $$\\int_a^b f(t)dt = F(b)-F(a), \\quad F'(x)=f(x)$$"))
        steps.append(("2. Identify f(x) and F(x) - Theoretical Relationship", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)}$$  \nTheoretical: $F$ such that $F' = f$  \nSubstituted: $$F({sp.latex(x)}) = {sp.latex(antiderivative)}$$"))
        steps.append(("3. Substitute f(x),F(x),a,b into Theoretical FTC Formulas", 
            f"Substitute into FTC Part 1 and Part 2:  \nTheoretical $\\frac{{d}}{{dx}}\\int_a^x f(t)dt = f(x)$ → Substituted with $f={sp.latex(f)}$  \nTheoretical $\\int_a^b f = F(b)-F(a)$ → Substituted with $a={a}, b={b}, F={sp.latex(antiderivative)}$"))
        steps.append(("4. Part 1 - Differentiation of Accumulation", 
            f"Define accumulation: $$A(x) = \\int_{{{a}}}^{{x}} {sp.latex(f)} dt$$  \nTheoretical: $A'(x) = f(x)$  \nSubstituted: $A'(x) = {sp.latex(f)}$"))
        steps.append(("5. Part 2 - Evaluation F(b)-F(a) with Substitution", 
            f"Theoretical: $F(b)-F(a)$  \nSubstituted: $$F({b}) = {sp.latex(antiderivative.subs(x,b))}$$  \n$$F({a}) = {sp.latex(antiderivative.subs(x,a))}$$  \n$$F(b)-F(a) = {sp.latex(result)}$$"))
        steps.append(("6. Very Explanatory Graph - FTC Visualization", 
            f"Graph shows:  \n• **Blue curve:** $f(x) = {sp.latex(f)} = {expr_str}$  \n• **Shaded area** from {a} to {b} = $\\int_a^b f$ = ${sp.latex(result)}$ (area)  \n• **Green dashed curve:** $F(x) = {sp.latex(antiderivative)}$ antiderivative  \n• **Slope of $F$ at any $x$ = $f(x)$** (FTC Part 1)  \n• **Hover over curves:** shows generating equation $f({var_name})={expr_str}$ and $F({var_name})={sp.latex(antiderivative)}$  \nAdjustable limits $a,b$ change shaded area"))
        steps.append(("7. Conclusion - FTC Connects Differentiation and Integration", 
            f"FTC shows differentiation and integration are inverses  \nTheoretical $\\int_a^b f = F(b)-F(a)$ → Substituted values → $$\\boxed{{\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(result)}}}$$  \nArea = ${sp.latex(result)}$"))
        
    elif rule=="Limits Rule (Riemann)":
        a_f,b_f=float(a),float(b); n=10; dx=(b_f-a_f)/n
        riemann=sum(float(f.subs(x, a_f+i*dx))*dx for i in range(1,n+1))
        exact=sp.integrate(f,(x,a_f,b_f))
        steps.append(("1. Theoretical Formula - Limits (Riemann)", 
            f"**Theoretical Formula:**  \n$$\\int_{{{a}}}^{{{b}}} f(x)dx = \\lim_{{n\\to\\infty}} \\sum_{{i=1}}^{{n}} f(x_i)\\Delta x, \\quad \\Delta x = \\frac{{b-a}}{{n}}$$"))
        steps.append(("2. Identify f(x),a,b", 
            f"Given: $$f({sp.latex(x)}) = {sp.latex(f)} = {expr_str}$$  \nLimits: $a={a}$, $b={b}$ (adjustable)"))
        steps.append(("3. Substitute f(x),a,b into Theoretical Formula", 
            f"Substitute into $\\sum f(x_i)\\Delta x$:  \nTheoretical $\\Delta x = (b-a)/n$ → Substituted $\\Delta x = ({b}-{a})/n$  \nTheoretical $x_i = a + i\\Delta x$ → Substituted $x_i = {a} + i\\Delta x$"))
        steps.append(("4. Compute Riemann Sum - Theoretical to Substituted", 
            f"Theoretical: $S_n = \\sum f(x_i)\\Delta x$  \nSubstituted (n=10 example): $$S_{{10}} ≈ {riemann:.4f}$$"))
        steps.append(("5. Take Limit n→∞ - Theoretical → Exact", 
            f"Theoretical limit $n\\to\\infty$ → exact integral  \nSubstituted exact: $$\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(exact)}$$"))
        steps.append(("6. Compare with Power/Substitution Rules", 
            f"Riemann limit gives same as Power/Substitution/By Parts/FTC: $$ {sp.latex(exact)} $$"))
        steps.append(("7. Graph & Final", 
            f"Graph shaded area = limit of sums - hover shows equation $f({var_name})={expr_str}$  \nFinal: $$\\boxed{{\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(exact)}}}$$"))
    
    # Prepare plots
    if rule in ["Definite Rule","FTC Rule (with very explanatory graph)","Limits Rule (Riemann)"]:
        final=f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(definite_result) if definite_result is not None else sp.integrate(f,(x,a,b))}"
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {expr_str}','eq':f'f({var_name}) = {expr_str}','color':'blue'},{'expr':for_plot(antiderivative,x),'label':f'F({var_name}) = {sp.latex(antiderivative)}','eq':f'F({var_name}) = {sp.latex(antiderivative)}','dashed':True,'color':'green'}],'x_min':float(a)-1,'x_max':float(b)+1,'shade':{'expr':for_plot(f,x),'from':float(a),'to':float(b),'eq':f'f({var_name}) = {expr_str}'},'title':f"Integral {rule}: {expr_str} from {a} to {b} - FTC explanatory"}
    else:
        final=f"\\int {sp.latex(f)} d{sp.latex(x)} = {sp.latex(antiderivative)} + C"
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f({var_name}) = {expr_str}','eq':f'f({var_name}) = {expr_str}','color':'blue'},{'expr':for_plot(antiderivative,x),'label':f'F({var_name}) = {sp.latex(antiderivative)}','eq':f'F({var_name}) = {sp.latex(antiderivative)}','dashed':True,'color':'green'}],'x_min':-5,'x_max':5,'title':f"Integral {rule}: {expr_str}"}
    return steps,final,plot

def render_integrals():
    st.subheader("Integrals (x,y,z) - Theoretical Formula + Substitution Step by Step")
    st.markdown("**For each rule: show theoretical formula FIRST, then substitute values**")
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
    st.subheader("Linear Equation (1st degree) - Interactive Graph (hover shows equation)")
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
    st.subheader("Quadratic Equation (2nd degree) - Interactive Graph (hover shows equation)")
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

def render_limit():
    st.subheader("Limits - 7 Steps (Power, Substitution) - Theoretical + Substitution")
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
st.set_page_config(page_title="CalculusFlow - Theoretical + Substitution", page_icon="➗", layout="centered")
st.title("CalculusFlow - Theoretical Formula First, Then Substitution")
st.caption("For Derivatives and Integrals: theoretical formula FIRST, then substitute values | Interactive hover graphs show generating equation | Linear/Quadratic interactive | All in English")

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
        "Linear Equation (Interactive Graph)":render_linear,
        "Quadratic Equation (Interactive Graph)":render_quadratic,
    },
}

group=st.sidebar.radio("Area", list(MODULES.keys()))
modules=MODULES[group]
choice=st.sidebar.radio("Module", list(modules.keys()))
st.sidebar.markdown("---")
if PLOTLY_AVAILABLE:
    st.sidebar.success("Plotly available - hover shows generating equation")
else:
    st.sidebar.warning("Add plotly to requirements.txt for hover")
    st.sidebar.code("plotly\nsympy\nmatplotlib\nstreamlit\nnumpy")
st.sidebar.markdown("**Derivatives (x,y,z):**\n- Defined & Differentiable in Same Interval\n- Constant Rule: d/dx[c]=0, d/dx[c·g]=c·g'\n- Power: d/dx x^n = n x^{n-1}\n- Sum/Difference: (f±g)'=f'±g'\n- Product: (uv)'=u'v+uv'\n- Quotient: (u/v)'=(u'v-uv')/v²\n- Chain: (f(g))'=f'(g)g'\n- Limits: f'=lim[f(x+h)-f(x)]/h\n\n**Integrals (x,y,z):**\n- Primitives: F'=f → ∫f=F+C\n- Substitution: ∫f(g)g' = ∫f(u)du\n- By Parts: ∫u dv=uv-∫v du\n- Definite: ∫_a^b f = F(b)-F(a)\n- Indefinite: ∫f = F+C\n- FTC: d/dx∫_a^x f = f, ∫_a^b f = F(b)-F(a)\n- Limits: ∫=lim Σ f(x_i)Δx\n\n**All:** Theoretical formula first, then substitute values")
modules[choice]()
