"""
CalculusFlow - ENGLISH - Enhanced Calculus with 6-7 steps + interactive graphs
Fixed: No ModuleNotFoundError for plotly - falls back to matplotlib if plotly not installed
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import lambdify

# Try plotly, fallback to matplotlib if not available (Streamlit Cloud)
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

def get_var(name):
    return _VAR_MAP.get(name, X)

def parse_expr(s, var_name='x'):
    if not s or str(s).strip()=='':
        raise ValueError("Empty expression.")
    expr_str = str(s).strip().replace('^','**')
    return sp.sympify(expr_str, locals=_LOCALS)

def parse_equation(s):
    if '=' not in str(s):
        raise ValueError("Equation must contain '='.")
    lhs,rhs=str(s).split('=',1)
    return parse_expr(lhs)-parse_expr(rhs)

def for_plot(expr, var):
    return expr.subs(var, X) if var!=X else expr

def num(v):
    try:
        return float(v)
    except:
        return None

def plot_functions_matplotlib(exprs, x_min, x_max, points=None, shade=None, title=None):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    xs = np.linspace(float(x_min), float(x_max), 400)
    for e in exprs:
        f = lambdify(X, e['expr'], modules=['numpy'])
        try:
            ys = np.array(f(xs), dtype=float)
            finite = np.isfinite(ys)
            ax.plot(xs[finite], ys[finite], label=e.get('label',''), linestyle='--' if e.get('dashed') else '-', color=e.get('color'))
        except:
            pass
    if shade:
        f = lambdify(X, shade['expr'], modules=['numpy'])
        ys = np.array(f(xs), dtype=float)
        mask = (xs >= float(shade['from'])) & (xs <= float(shade['to']))
        ax.fill_between(xs, ys, 0, where=mask, alpha=0.25, color='C0')
    if points:
        for p in points:
            ax.plot(float(p['x']), float(p['y']), 'o', color=p.get('color','red'))
            ax.annotate(p.get('label',''), (float(p['x']), float(p['y'])), textcoords='offset points', xytext=(6,6), fontsize=8)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.set_xlim(float(x_min), float(x_max))
    if title:
        ax.set_title(title)
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

def plotly_interactive(exprs, x_min, x_max, points=None, shade=None, title=None):
    if not PLOTLY_AVAILABLE:
        # fallback to matplotlib handled outside
        return None
    fig = go.Figure()
    xs = np.linspace(float(x_min), float(x_max), 500)
    for e in exprs:
        try:
            f = lambdify(X, e['expr'], modules=['numpy'])
            ys = np.array(f(xs), dtype=float)
            label = e.get('label','')
            eq = e.get('eq', label)
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode='lines', name=label,
                line=dict(dash='dash' if e.get('dashed') else 'solid', color=e.get('color')),
                hovertemplate=f"<b>{eq}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"
            ))
        except Exception:
            continue
    if shade:
        try:
            f = lambdify(X, shade['expr'], modules=['numpy'])
            ys = np.array(f(xs), dtype=float)
            mask = (xs >= float(shade['from'])) & (xs <= float(shade['to']))
            fig.add_trace(go.Scatter(
                x=xs[mask], y=ys[mask], fill='tozeroy', mode='none',
                name='Area', fillcolor='rgba(0,100,255,0.2)',
                hovertemplate=f"<b>{shade.get('eq','f(x)')}</b><br>x=%{{x:.3f}}<br>y=%{{y:.3f}}<extra></extra>"
            ))
        except:
            pass
    if points:
        for p in points:
            fig.add_trace(go.Scatter(
                x=[float(p['x'])], y=[float(p['y'])], mode='markers+text',
                marker=dict(color=p.get('color','red'), size=10),
                text=[p.get('label','')], textposition="top right",
                name=p.get('label','point'),
                hovertemplate=f"<b>{p.get('label','point')}</b><br>x=%{{x}}<br>y=%{{y}}<extra></extra>"
            ))
    fig.update_layout(
        title=title, xaxis_title="x", yaxis_title="y",
        hovermode="x unified", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.add_hline(y=0, line_width=1, line_color="black", opacity=0.5)
    fig.add_vline(x=0, line_width=1, line_color="black", opacity=0.5)
    return fig

def _show(steps, final, plot=None):
    for i,(title,detail) in enumerate(steps,1):
        st.markdown(f"**Step {i}: {title}**")
        st.markdown(detail)
    st.markdown("**Final Answer**")
    if final.startswith('$$'):
        st.markdown(final)
    else:
        st.latex(final)
    if plot:
        if PLOTLY_AVAILABLE:
            fig = plotly_interactive(**plot)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.pyplot(plot_functions_matplotlib(**plot))
        else:
            # Fallback to matplotlib when plotly not installed
            st.info("Plotly not installed - using matplotlib fallback. Add `plotly` to requirements.txt for interactive hover graphs.")
            st.pyplot(plot_functions_matplotlib(**plot))

IDEAL_CSS = """
<style>
.ideal-box { display:inline-block; background:#fff; padding:14px 22px; border-radius:12px; border:1px solid #e5e7eb; font-family: ui-monospace, monospace; font-weight:700; }
.mult-ideal .carry { font-size:12px; letter-spacing:0.8em; }
.mult-ideal .carry.green { color:#16a34a; } .mult-ideal .carry.yellow { color:#eab308; } .mult-ideal .carry.purple { color:#7c3aed; }
.mult-ideal .num { font-size:32px; text-align:right; } .mult-ideal .line { width:100%; background:#000; margin:6px 0; } .mult-ideal .line.thin{height:2px;} .mult-ideal .line.thick{height:3px;}
.mult-ideal .partial { font-size:28px; text-align:right; position:relative; } .mult-ideal .partial.purple{color:#7c3aed;} .mult-ideal .partial.yellow{color:#eab308;} .mult-ideal .partial.green{color:#16a34a;}
.mult-ideal .partial .sup{position:absolute; font-size:11px; color:#000; left:12px; top:-6px;} .mult-ideal .partial .sub{position:absolute; font-size:11px; color:#000; left:0; bottom:-6px;}
.mult-ideal .result{font-size:34px; color:#dc2626; text-align:right;}
.div-ideal{display:flex; align-items:flex-start;} .div-ideal .small-top{font-size:11px; color:#16a34a; letter-spacing:0.2em;} .div-ideal .line{width:100%; height:3px; background:#000; margin:5px 0;} .div-ideal .right{border-left:3px solid #000; margin-left:8px;} .div-ideal .right .divisor{border-bottom:3px solid #000; padding:4px 24px; font-size:28px;} .div-ideal .right .quotient{padding:4px 24px; font-size:28px; color:#dc2626;}
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
                if W>max_orig_len and total_str.lstrip()[0]==str(val):
                    show=''
                else:
                    show=str(val)
            else:
                show=str(val)
        html+=f'<div style="color:#7c3aed; font-size:14px; height:18px; display:flex; align-items:flex-end; justify-content:center;">{show}</div>' if show else '<div style="height:18px;"></div>'
    return html

def add_armada(A,B):
    A,B=abs(int(A)),abs(int(B))
    a_str,b_str=str(A),str(B)
    maxlen=max(len(a_str),len(b_str))
    W=maxlen+1
    top=[None]*W; bottom=[None]*W; carry=[None]*W; result=[None]*W
    for p in range(len(a_str)): top[W-1-p]=int(a_str[-1-p])
    for p in range(len(b_str)): bottom[W-1-p]=int(b_str[-1-p])
    c=0; cols=[]
    for p in range(maxlen):
        g=W-1-p; carry[g]=c; t=top[g] or 0; b=bottom[g] or 0; s=t+b+c; result[g]=s%10; c=s//10
        cols.insert(0,{'top':t,'bottom':b,'carryIn':carry[g],'sum':s,'digit':result[g]})
    if c>0: result[W-1-maxlen]=c; carry[W-1-maxlen]=c
    return {'A':A,'B':B,'W':W,'top':top,'bottom':bottom,'carry':carry,'result':result,'cols':cols,'total':A+B}

def render_addition():
    st.subheader("Addition with Carrying")
    def _reset():
        st.session_state["add_A"]=6789; st.session_state["add_B"]=4567
    A=int(st.number_input("Top number", value=6789, step=1, key="add_A"))
    B=int(st.number_input("Bottom number", value=4567, step=1, key="add_B"))
    st.button("Show example", key="add_ex", on_click=_reset)
    d=add_armada(A,B)
    total_str=str(d['total']); W=len(total_str); max_orig=max(len(str(A)),len(str(B)))
    if W<max_orig: W=max_orig
    top_str=str(A).rjust(W); b_str_raw=str(B); bottom_str=b_str_raw.rjust(W)
    plus_pos=W-len(b_str_raw)-1
    bottom_cells=[]
    for i,ch in enumerate(bottom_str):
        bottom_cells.append('+' if i==plus_pos else (ch if ch!=' ' else ''))
    if plus_pos<0: bottom_cells[0]='+' + bottom_cells[0]
    carry_html=_carry_cells_html(d['carry'], W, True, total_str, max_orig)
    html=f'<div style="display:inline-block; background:#fff; padding:14px 22px; border-radius:12px; border:1px solid #e5e7eb;"><div style="display:grid; grid-template-columns:repeat({W}, 1.05em); justify-items:center; font-weight:700; font-size:36px; column-gap:2px;">{carry_html}'
    for ch in top_str: html+=f'<div>{ch if ch!=" " else ""}</div>'
    for ch in bottom_cells: html+=f'<div style="font-size:30px;">+</div>' if ch=='+' else f'<div>{ch}</div>'
    html+=f'</div><div style="width:100%; height:3px; background:#000; margin:8px 0;"></div><div style="display:grid; grid-template-columns:repeat({W}, 1.05em); justify-items:center; font-weight:700; font-size:36px;">'
    for ch in total_str.rjust(W): html+=f'<div style="color:#dc2626;">{ch if ch!=" " else ""}</div>'
    html+=f'</div></div><div style="margin-top:10px;">{A} + {B} = <span style="color:#dc2626">{d["total"]}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

def subtract_armada(A,B):
    A,B=int(A),int(B)
    larger,smaller=max(A,B),min(A,B)
    top_str=str(larger); bottom_str=str(smaller).rjust(len(top_str),'0')
    top_arr=list(map(int, top_str)); bottom_arr=list(map(int, bottom_str))
    working=top_arr[:]; lent_by={}; columns=[]
    for i in range(len(top_str)-1,-1,-1):
        t=working[i]; b=bottom_arr[i]; borrowed=None
        if t<b:
            j=i-1
            while j>=0 and working[j]==0: j-=1
            if j>=0:
                old=working[j]; working[j]-=1
                for k in range(j+1,i): working[k]=9
                t=working[i]+10; borrowed=j; lent_by[j]={'newValue':working[j],'oldValue':old}
        columns.insert(0,{'index':i,'originalTop':top_arr[i],'displayedTop':t,'bottom':b,'result':t-b,'borrowedFrom':borrowed})
    magnitude=int(''.join(str(c['result']) for c in columns))
    result=-magnitude if A<B else magnitude
    return {'larger':larger,'smaller':smaller,'columns':columns,'lent_by':lent_by,'result':result}

def render_subtraction():
    st.subheader("Subtraction with Borrowing")
    def _reset():
        st.session_state["sub_A"]=5003; st.session_state["sub_B"]=2897
    A_orig=int(st.number_input("Top number", value=5003, step=1, key="sub_A"))
    B_orig=int(st.number_input("Bottom number", value=2897, step=1, key="sub_B"))
    st.button("Show example", key="sub_ex", on_click=_reset)
    larger=max(A_orig,B_orig); smaller=min(A_orig,B_orig)
    d=subtract_armada(larger, smaller); real_result=A_orig-B_orig
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
    for ch in str(abs(real_result)).rjust(Wc): html+=f'<div>{ch if ch.strip()!="" else ""}</div>'
    html+='</div></div>'
    if A_orig<B_orig:
        html = html.replace(f'<div>{str(abs(real_result)).rjust(Wc)[0]}', f'<div>−</div><div>{str(abs(real_result))}')  # simple handling, will show negative in text below
        html += f'<div style="margin-top:10px; color:#dc2626;">Negative result: {real_result}</div>'
    html+= f'<div style="margin-top:10px;">{A_orig} − {B_orig} = <span style="color:#dc2626">{real_result}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_multiplication():
    st.subheader("Long Multiplication - Ideal Design")
    st.markdown(IDEAL_CSS, unsafe_allow_html=True)
    def _reset():
        st.session_state["mul_A"]=234; st.session_state["mul_B"]=563
    A=int(st.number_input("Multiplicand (top)", value=234, step=1, key="mul_A"))
    B=int(st.number_input("Multiplier (bottom)", value=563, step=1, key="mul_B"))
    st.button("Show example", key="mul_ex", on_click=_reset)
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
        W=len(str(product))+1
        html=f'<div class="ideal-box"><div class="mult-ideal"><div class="num">{A}</div><div class="num">x {B}</div><div class="line thin"></div><div class="partial purple">{A*(B%10)}</div><div class="partial yellow">{A*((B//10)%10)}0</div><div class="partial green">+ {A*((B//100)%10)}0</div><div class="line thick"></div><div class="result">{product}</div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

def long_divide(dividend, divisor):
    if divisor==0: return {'error':'Division by zero'}
    dividend,divisor=abs(int(dividend)),abs(int(divisor))
    digits=list(map(int,str(dividend)))
    cur=0; steps=[]; q_digits=[]
    for i,dgt in enumerate(digits):
        cur=cur*10+dgt
        qd=cur//divisor
        if not steps and qd==0: continue
        prod=qd*divisor; rem=cur-prod
        steps.append({'working':cur,'qDigit':qd,'product':prod,'remainder':rem,'endCol':i})
        q_digits.append(qd); cur=rem
    q_str=''.join(map(str,q_digits)) or '0'
    return {'dividend':dividend,'divisor':divisor,'quotient':int(q_str),'quotient_str':q_str,'steps':steps,'remainder':cur}

def render_long_division():
    st.subheader("Long Division - Ideal Design")
    st.markdown(IDEAL_CSS, unsafe_allow_html=True)
    def _reset():
        st.session_state["div_A"]=4356; st.session_state["div_B"]=12
    dividend=int(st.number_input("Dividend", value=4356, step=1, key="div_A"))
    divisor=int(st.number_input("Divisor", value=12, step=1, key="div_B"))
    st.button("Show example", key="div_ex", on_click=_reset)
    d=long_divide(dividend, divisor)
    if 'error' in d:
        st.error(d['error']); return
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

# ================= ENHANCED CALCULUS =================

def solve_limit_enhanced(expr_str, point):
    x=X
    f=parse_expr(expr_str)
    p=sp.nsimplify(point)
    sub=sp.simplify(f.subs(x,p))
    lim=sp.limit(f,x,p)
    steps=[]
    steps.append(("1. Statement", f"$$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)}$$"))
    steps.append(("2. Domain Analysis", f"Function: $$f(x) = {sp.latex(f)}$$<br>Point: $$x \\to {sp.latex(p)}$$"))
    steps.append(("3. Direct Substitution", f"$$f({sp.latex(p)}) = {sp.latex(sub)}$$"))
    try:
        factored=sp.factor(f)
        if factored!=f:
            steps.append(("4. Algebraic Simplification - Factoring", f"$$f(x) = {sp.latex(factored)}$$"))
        else:
            steps.append(("4. Algebraic Simplification", f"$$f(x) = {sp.latex(sp.simplify(f))}$$"))
    except:
        steps.append(("4. Algebraic Simplification", f"$$f(x) = {sp.latex(f)}$$"))
    steps.append(("5. Apply Limit Laws", f"Use limit laws<br>$$\\lim f(x) = {sp.latex(lim)}$$"))
    steps.append(("6. Calculate Limit", f"$$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}$$"))
    steps.append(("7. Numerical Verification & Graph", f"Graph shows behavior near point. Hover to see equation (if Plotly available)."))
    final=f"\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}"
    yv=num(lim)
    plot={
        'exprs':[{'expr':for_plot(f,x),'label':f'f(x) = {expr_str}','eq':f'f(x) = {expr_str}','color':'blue'}],
        'x_min': num(p)-3, 'x_max': num(p)+3,
        'points':[{'x':float(p),'y':yv,'label':f'Limit = {lim}','color':'red'}] if yv is not None else None,
        'title':f"Limit: {expr_str} as x→{point}"
    }
    return steps,final,plot

def render_limit():
    st.subheader("Limits - 7 Step Solution with Interactive Graph")
    def _reset():
        st.session_state["lim_expr"]="sin(x)/x"
        st.session_state["lim_point"]=0.0
        st.session_state["lim_xmin"]=-3.0
        st.session_state["lim_xmax"]=3.0
    col1,col2=st.columns(2)
    expr=col1.text_input("Function f(x)", value="sin(x)/x", key="lim_expr")
    point=col2.number_input("x approaches", value=0.0, key="lim_point")
    col3,col4=st.columns(2)
    xmin=col3.slider("Graph x-min", -10.0, 0.0, -3.0, key="lim_xmin")
    xmax=col4.slider("Graph x-max", 0.0, 10.0, 3.0, key="lim_xmax")
    st.button("Show example", key="lim_ex", on_click=_reset)
    try:
        steps,final,plot=solve_limit_enhanced(expr, point)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_derivative_limit_enhanced(expr_str, point, var_name='x'):
    var=get_var(var_name); x=var
    f=parse_expr(expr_str, var_name)
    h=sp.Symbol('h')
    f_xh=sp.simplify(f.subs(x, x+h))
    quotient=sp.simplify((f_xh-f)/h)
    deriv=sp.limit(quotient, h, 0)
    deriv_simplified=sp.simplify(deriv)
    slope=sp.simplify(deriv_simplified.subs(x, point))
    f_pt=f.subs(x, point)
    tangent=sp.simplify(f_pt+slope*(x-point))
    steps=[]
    steps.append(("1. Definition", f"$$f'(x) = \\lim_{{h \\to 0}} \\frac{{f(x+h)-f(x)}}{{h}}$$"))
    steps.append(("2. Identify f(x)", f"$$f(x) = {sp.latex(f)}$$ at $$x={sp.latex(point)}$$"))
    steps.append(("3. Compute f(x+h)", f"$$f(x+h) = {sp.latex(f_xh)}$$"))
    steps.append(("4. Difference Quotient", f"$$\\frac{{f(x+h)-f(x)}}{{h}} = {sp.latex(quotient)}$$"))
    steps.append(("5. Simplify Quotient", f"$$ {sp.latex(quotient)} $$"))
    steps.append(("6. Take Limit h→0", f"$$f'(x) = {sp.latex(deriv_simplified)}$$"))
    steps.append(("7. Slope & Tangent at Point", f"$$f'({sp.latex(point)}) = {sp.latex(slope)}$$<br>$$y = {sp.latex(tangent)}$$"))
    final=f"f'({sp.latex(x)}) = {sp.latex(deriv_simplified)}, \\quad f'({sp.latex(point)}) = {sp.latex(slope)}"
    yv=num(f_pt)
    plot={
        'exprs':[
            {'expr':for_plot(f,x),'label':f'f(x) = {expr_str}','eq':f'f(x) = {expr_str}','color':'blue'},
            {'expr':for_plot(tangent,x),'label':f'tangent at x={point}','eq':f'y = {sp.latex(tangent)}','dashed':True,'color':'orange'}
        ],
        'x_min': float(point)-4, 'x_max': float(point)+4,
        'points':[{'x':float(point),'y':yv,'label':f'({point}, {f_pt})','color':'red'}] if yv is not None else None,
        'title': f"Derivative by definition: {expr_str}"
    }
    return steps,final,plot

def render_derivative_limit():
    st.subheader("Derivative by Definition - 7 Steps + Interactive Graph")
    def _reset():
        st.session_state["dl_expr"]="x^2"
        st.session_state["dl_point"]=1.0
        st.session_state["dl_xmin"]=-3.0
        st.session_state["dl_xmax"]=5.0
    col1,col2=st.columns(2)
    expr=col1.text_input("f(x)", value="x^2", key="dl_expr")
    point=col2.number_input("At x =", value=1.0, key="dl_point")
    col3,col4=st.columns(2)
    xmin=col3.slider("Graph x-min (derivative)", -10.0, 0.0, -3.0, key="dl_xmin")
    xmax=col4.slider("Graph x-max (derivative)", 0.0, 10.0, 5.0, key="dl_xmax")
    st.button("Show example", key="dl_ex", on_click=_reset)
    try:
        steps,final,plot=solve_derivative_limit_enhanced(expr, point)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_integral_limit_enhanced(expr_str, a, b, n, var_name='x'):
    var=get_var(var_name); x=var
    f=parse_expr(expr_str, var_name)
    a,b,n=float(a),float(b),int(n)
    dx=(b-a)/n
    riemann_right=sum(float(f.subs(x, a+i*dx))*dx for i in range(1,n+1))
    exact=sp.integrate(f,(x,a,b))
    steps=[]
    steps.append(("1. Definition", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = \\lim_{{n\\to\\infty}} \\sum f(x_i)\\Delta x$$"))
    steps.append(("2. Partition Interval", f"$$\\Delta x = {dx:.4f}$$"))
    steps.append(("3. Sample Points", f"$x_i = a + i\\Delta x$"))
    steps.append(("4. Riemann Sum Formula", f"$$S_n = \\sum f(x_i)\\Delta x$$"))
    steps.append(("5. Compute Sum (n={})".format(n), f"Right sum: {riemann_right:.6f}"))
    steps.append(("6. Exact Integral", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(exact)}$$"))
    steps.append(("7. Error & Convergence", f"Exact = {sp.N(exact,6)}, Error = {abs(float(sp.N(exact,6))-riemann_right):.6f}"))
    final=f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(exact)}"
    plot={
        'exprs':[{'expr':for_plot(f,x),'label':f'f(x) = {expr_str}','eq':f'f(x) = {expr_str}','color':'blue'}],
        'x_min': a-1, 'x_max': b+1,
        'shade':{'expr':for_plot(f,x),'from':a,'to':b,'eq':f'f(x) = {expr_str}'},
        'title': f"Riemann Sum n={n}"
    }
    return steps,final,plot

def render_integral_limit():
    st.subheader("Integral by Riemann Sums - 7 Steps + Adjustable Limits")
    def _reset():
        st.session_state["il_expr"]="x^2"
        st.session_state["il_a"]=0.0
        st.session_state["il_b"]=2.0
        st.session_state["il_n"]=5
        st.session_state["il_xmin"]=-1.0
        st.session_state["il_xmax"]=3.0
    col1,col2,col3=st.columns(3)
    expr=col1.text_input("f(x)", value="x^2", key="il_expr")
    a=col2.number_input("Lower limit a", value=0.0, key="il_a")
    b=col3.number_input("Upper limit b", value=2.0, key="il_b")
    col4,col5=st.columns(2)
    n=col4.slider("Rectangles n", 1, 100, 5, key="il_n")
    col6,col7=st.columns(2)
    xmin=col6.slider("Graph x-min", -5.0, 5.0, -1.0, key="il_xmin")
    xmax=col7.slider("Graph x-max", -5.0, 10.0, 3.0, key="il_xmax")
    st.button("Show example", key="il_ex", on_click=_reset)
    try:
        steps,final,plot=solve_integral_limit_enhanced(expr,a,b,n)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_derivative_rules(expr_str, var_name, rule):
    var=get_var(var_name); x=var
    f=parse_expr(expr_str, var_name)
    deriv=sp.diff(f,x)
    steps=[]
    steps.append(("1. Identify Function", f"$$f({sp.latex(x)}) = {sp.latex(f)}$$"))
    steps.append(("2. Choose Rule", f"Rule: **{rule}**"))
    steps.append(("3. Apply Rule", f"Apply {rule}"))
    steps.append(("4. Compute Derivative", f"$$f' = {sp.latex(deriv)}$$"))
    steps.append(("5. Simplify", f"$$f' = {sp.latex(sp.simplify(deriv))}$$"))
    steps.append(("6. Verification & Graph", f"Final: $$f' = {sp.latex(deriv)}$$"))
    final=f"f'({sp.latex(x)}) = {sp.latex(deriv)}"
    plot={
        'exprs':[
            {'expr':for_plot(f,x),'label':f'f(x) = {expr_str}','eq':f'f(x) = {expr_str}','color':'blue'},
            {'expr':for_plot(deriv,x),'label':f"f'(x)",'eq':f"f'(x) = {sp.latex(deriv)}",'dashed':True,'color':'green'}
        ],
        'x_min': -5, 'x_max': 5,
        'title': f"Derivative: {expr_str}"
    }
    return steps,final,plot

def render_derivative():
    st.subheader("Derivatives (Rules) - 6 Steps + Interactive Graph")
    def _reset():
        st.session_state["der_expr"]="x^3 + 2*x^2 + sin(x)"
        st.session_state["der_var"]="x"
        st.session_state["der_rule"]="Power"
        st.session_state["der_xmin"]=-5.0
        st.session_state["der_xmax"]=5.0
    col1,col2=st.columns(2)
    expr=col1.text_input("f(variable)", value="x^3 + 2*x^2 + sin(x)", key="der_expr")
    variable=col2.selectbox("Variable", ['x','y','z'], key="der_var")
    col3,col4,col5=st.columns(3)
    rule=col3.selectbox("Rule", ['Power','Sum/Difference','Product','Quotient','Chain','General'], key="der_rule")
    xmin=col4.slider("Graph x-min", -10.0, 0.0, -5.0, key="der_xmin")
    xmax=col5.slider("Graph x-max", 0.0, 10.0, 5.0, key="der_xmax")
    st.button("Show example", key="der_ex", on_click=_reset)
    try:
        steps,final,plot=solve_derivative_rules(expr, variable, rule)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

def solve_integral_rules(expr_str, var_name, rule, kind, a, b):
    var=get_var(var_name); x=var
    f=parse_expr(expr_str, var_name)
    definite=kind=='Definite'
    if definite:
        result=sp.integrate(f,(x,a,b))
        antiderivative=sp.integrate(f,x)
        steps=[
            ("1. Identify Integral", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)}$$"),
            ("2. Choose Method", f"Rule: **{rule}**"),
            ("3. Find Antiderivative", f"$$F = {sp.latex(antiderivative)}$$"),
            ("4. Apply FTC", f"$$\\int_a^b f = F(b)-F(a)$$"),
            ("5. Evaluate at Bounds", f"$$= {sp.latex(result)}$$"),
            ("6. Result & Graph", f"$$= {sp.latex(result)}$$")
        ]
        final=f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)} = {sp.latex(result)}"
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f(x) = {expr_str}','eq':f'f(x) = {expr_str}','color':'blue'}],'x_min':float(a)-1,'x_max':float(b)+1,'shade':{'expr':for_plot(f,x),'from':float(a),'to':float(b),'eq':f'f(x) = {expr_str}'}}
    else:
        result=sp.integrate(f,x)
        steps=[
            ("1. Identify Integral", f"$$\\int {sp.latex(f)}\\,d{sp.latex(x)}$$"),
            ("2. Choose Method", f"Rule: **{rule}**"),
            ("3. Apply Rule", f"Apply {rule}"),
            ("4. Compute Antiderivative", f"$$= {sp.latex(result)} + C$$"),
            ("5. Verify", f"Derivative = {sp.latex(sp.diff(result,x))}"),
            ("6. Final Answer & Graph", f"$$= {sp.latex(result)} + C$$")
        ]
        final=f"\\int {sp.latex(f)} = {sp.latex(result)} + C"
        plot={'exprs':[{'expr':for_plot(f,x),'label':f'f(x) = {expr_str}','eq':f'f(x) = {expr_str}','color':'blue'}],'x_min':-5,'x_max':5}
    return steps,final,plot

def render_integral():
    st.subheader("Integrals (Rules) - 6 Steps + Interactive Graph")
    def _reset():
        st.session_state["int_expr"]="x^2 + 3*x + 2"
        st.session_state["int_var"]="x"
        st.session_state["int_rule"]="Power"
        st.session_state["int_kind"]="Indefinite"
        st.session_state["int_a"]=0.0
        st.session_state["int_b"]=2.0
        st.session_state["int_xmin"]=-2.0
        st.session_state["int_xmax"]=4.0
    col1,col2=st.columns(2)
    expr=col1.text_input("Integrand", value="x^2 + 3*x + 2", key="int_expr")
    variable=col2.selectbox("Variable", ['x','y','z'], key="int_var")
    col3,col4=st.columns(2)
    rule=col3.selectbox("Method/Rule", ['Power','Substitution','By Parts','Definite','Indefinite','FTC'], key="int_rule")
    kind=col4.selectbox("Type", ['Indefinite','Definite'], key="int_kind")
    a=b=0.0
    if kind=='Definite' or rule in ('Definite','FTC'):
        col5,col6=st.columns(2)
        a=col5.number_input("Lower limit a", value=0.0, key="int_a")
        b=col6.number_input("Upper limit b", value=2.0, key="int_b")
    col7,col8=st.columns(2)
    xmin=col7.slider("Graph x-min", -10.0, 5.0, -2.0, key="int_xmin")
    xmax=col8.slider("Graph x-max", -5.0, 10.0, 4.0, key="int_xmax")
    st.button("Show example", key="int_ex", on_click=_reset)
    try:
        steps,final,plot=solve_integral_rules(expr, variable, rule, kind, a, b)
        plot['x_min']=xmin; plot['x_max']=xmax
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))

# APP
st.set_page_config(page_title="CalculusFlow - English Enhanced", page_icon="➗", layout="centered")
st.title("CalculusFlow")
st.caption("Interactive math companion — arithmetic ideal design + calculus 6-7 steps with interactive graphs (hover shows equation). Adjustable limits. Plotly optional.")

MODULES={
    "Arithmetic":{
        "Addition (carry)":render_addition,
        "Subtraction (borrow)":render_subtraction,
        "Long Multiplication (Ideal)":render_multiplication,
        "Long Division (Ideal)":render_long_division,
    },
    "Calculus":{
        "Limits (7 steps)":render_limit,
        "Derivative by Definition (7 steps)":render_derivative_limit,
        "Integral by Riemann (7 steps)":render_integral_limit,
        "Derivatives - Rules (6 steps)":render_derivative,
        "Integrals - Rules (6 steps)":render_integral,
    },
}

group=st.sidebar.radio("Area", list(MODULES.keys()))
modules=MODULES[group]
choice=st.sidebar.radio("Module", list(modules.keys()))
st.sidebar.markdown("---")
if PLOTLY_AVAILABLE:
    st.sidebar.success("Plotly available - interactive graphs enabled")
else:
    st.sidebar.warning("Plotly not installed - using matplotlib fallback. Add `plotly` to requirements.txt for hover graphs.")
    st.sidebar.code("plotly\nsympy\nmatplotlib\nstreamlit\nnumpy", language="text")
modules[choice]()
