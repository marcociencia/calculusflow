"""Módulos de cálculo: limites, derivada por definição, integral por Riemann, derivadas e integrais."""
import streamlit as st
import sympy as sp
from core import parse_expr, get_var, X, for_plot, num
import plot_util


def _show(steps, final, plot=None):
    for title, detail in steps:
        st.markdown(f"**{title}**")
        st.markdown(detail)
    st.markdown(f"**Resposta final**")
    st.latex(final) if not final.startswith('$$') else st.markdown(final)
    if plot:
        st.pyplot(plot_util.plot_functions(**plot))


def solve_limit(expr_str, point):
    f = parse_expr(expr_str)
    x = X
    p = sp.nsimplify(point)
    lim = sp.limit(f, x, p)
    sub = f.subs(x, p)
    steps = []
    steps.append(("Enunciado", f"$$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)}$$"))
    steps.append(("Substituição direta", f"$$f({sp.latex(p)}) = {sp.latex(sp.simplify(sub))}$$"))
    if sub == sp.zoo or sub.has(sp.nan) or (getattr(sub, 'is_infinite', None) and sub.is_infinite):
        steps.append(("Forma indeterminada", "A substituição direta dá uma forma infinita/indeterminada; é preciso simplificar algebricamente."))
    steps.append(("Cálculo do limite", f"$$\\lim_{{x \\to {sp.latex(p)}}} {sp.latex(f)} = {sp.latex(lim)}$$"))
    # verificação numérica
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
    expr = st.text_input("Função f(x)", value="sin(x)/x", key="lim_expr")
    point = st.number_input("x tende a", value=0.0, key="lim_point")
    if st.button("Mostrar exemplo", key="lim_ex"):
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
        ("Definição", f"$$f'({sp.latex(x)}) = \\lim_{{h \\to 0}} \\frac{{f({sp.latex(x)}+h)-f({sp.latex(x)})}}{{h}}$$"),
        ("Calcula f(x+h)", f"$$f({sp.latex(x)}+h) = {sp.latex(f_xh)}$$"),
        ("Quociente das diferenças", f"$$\\frac{{f({sp.latex(x)}+h)-f({sp.latex(x)})}}{{h}} = {sp.latex(quotient)}$$"),
        ("Tomar o limite h→0", f"$$f'({sp.latex(x)}) = \\lim_{{h\\to0}} {sp.latex(quotient)} = {sp.latex(deriv)}$$"),
        ("Inclinação no ponto", f"$$f'({sp.latex(point)}) = {sp.latex(slope)}$$"),
        ("Reta tangente", f"$$y = {sp.latex(tangent)}$$"),
    ]
    final = f"f'({sp.latex(x)}) = {sp.latex(deriv)}, \\quad y = {sp.latex(tangent)}"
    yv = num(f_pt)
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'},
                      {'expr': for_plot(tangent, x), 'label': 'tangente', 'dashed': True, 'color': 'orange'}],
            'x_min': float(point) - 4, 'x_max': float(point) + 4,
            'points': [{'x': float(point), 'y': yv, 'label': f'({point}, {f_pt})'}] if yv is not None else None}
    return steps, final, plot


def render_derivative_limit():
    st.subheader("Derivada — definição por limite")
    expr = st.text_input("f(x)", value="x^2", key="dl_expr")
    point = st.number_input("No ponto x =", value=1.0, key="dl_point")
    if st.button("Mostrar exemplo", key="dl_ex"):
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
    # soma de Riemann (retângulos à direita) numérica
    riemann = sum(float(f.subs(x, a + i * dx)) * dx for i in range(1, n + 1))
    exact = sp.integrate(f, (x, a, b))
    steps = [
        ("Definição", f"$$\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} {sp.latex(f)}\\,dx = \\lim_{{n\\to\\infty}} \\sum_{{i=1}}^{{n}} f(x_i)\\,\\Delta x$$"),
        ("Largura e pontos", f"$$\\Delta x = \\frac{{{b}-{a}}}{{{n}}} = {dx}, \\quad x_i = {a} + i\\Delta x$$"),
        ("Soma de Riemann (n=" + str(n) + ")", f"$$S_{{{n}}} = \\sum_{{i=1}}^{{{n}}} f(x_i)\\,\\Delta x = {round(riemann, 4)}$$"),
        ("Integral exata", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = {sp.latex(exact)} = {sp.latex(sp.N(exact, 5))}$$"),
    ]
    final = f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,dx = {sp.latex(exact)}"
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'}],
            'x_min': a - 1, 'x_max': b + 1,
            'shade': {'expr': for_plot(f, x), 'from': a, 'to': b}}
    return steps, final, plot


def render_integral_limit():
    st.subheader("Integral — limite das somas de Riemann")
    expr = st.text_input("f(x)", value="x^2", key="il_expr")
    a = st.number_input("Limite inferior a", value=0.0, key="il_a")
    b = st.number_input("Limite superior b", value=2.0, key="il_b")
    n = st.number_input("Retângulos n", value=5, step=1, key="il_n")
    if st.button("Mostrar exemplo", key="il_ex"):
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
    steps = [("Função", f"$$f({sp.latex(x)}) = {sp.latex(f)}$$")]
    if f.is_Add:
        steps.append(("Regra da soma", "Aplique a regra da soma, derivando termo a termo."))
        parts = []
        for term in sp.Add.make_args(f):
            d = sp.diff(term, x)
            parts.append(f"\\frac{{d}}{{d{sp.latex(x)}}}\\left({sp.latex(term)}\\right) = {sp.latex(d)}")
        steps.append(("Derivando cada termo", "$$" + " \\quad ".join(parts) + "$$"))
    else:
        steps.append(("Aplicar regras", f"Aplique a regra **{rule}**."))
    steps.append(("Resultado", f"$$f'({sp.latex(x)}) = {sp.latex(deriv)}$$"))
    final = f"f'({sp.latex(x)}) = {sp.latex(deriv)}"
    plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'},
                      {'expr': for_plot(deriv, x), 'label': "f'(x)", 'dashed': True, 'color': 'green'}],
            'x_min': -5, 'x_max': 5}
    return steps, final, plot


def render_derivative():
    st.subheader("Derivadas — regras")
    expr = st.text_input(f"f(variável)", value="x^3 + 2*x^2 + sin(x)", key="der_expr")
    col1, col2 = st.columns(2)
    variable = col1.selectbox("Variável", ['x', 'y', 'z'], key="der_var")
    rule = col2.selectbox("Regra a demonstrar", ['Geral', 'Constante', 'Potência', 'Soma/Diferença', 'Produto', 'Quociente', 'Cadeia'], key="der_rule")
    if st.button("Mostrar exemplo", key="der_ex"):
        st.session_state.der_expr, st.session_state.der_var, st.session_state.der_rule = "x^3 + 2*x^2 + sin(x)", "x", "Geral"
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
            ("Método", f"Regra: **{rule}**."),
            ("Aplicar Teorema Fundamental", f"Encontre a antiderivada F, depois calcule F({b}) − F({a})."),
            ("Resultado", f"$$\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)}$$"),
        ]
        final = f"\\int_{{{a}}}^{{{b}}} {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)}"
        plot = {'exprs': [{'expr': for_plot(f, x), 'label': 'f(x)'}],
                'x_min': float(a) - 1, 'x_max': float(b) + 1,
                'shade': {'expr': for_plot(f, x), 'from': float(a), 'to': float(b)}}
    else:
        result = sp.integrate(f, x)
        steps = [
            ("Integral", f"$$\\int {sp.latex(f)}\\,d{sp.latex(x)}$$"),
            ("Método", f"Regra: **{rule}**."),
            ("Antiderivada", f"$$\\int {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)} + C$$"),
            ("Verificação", "Derive o resultado para confirmar."),
        ]
        final = f"\\int {sp.latex(f)}\\,d{sp.latex(x)} = {sp.latex(result)} + C"
        plot = None
    return steps, final, plot


def render_integral():
    st.subheader("Integrais — regras")
    expr = st.text_input("Integrando", value="x^2 + 3*x + 2", key="int_expr")
    col1, col2 = st.columns(2)
    variable = col1.selectbox("Variável", ['x', 'y', 'z'], key="int_var")
    rule = col2.selectbox("Método/regra", ['Primitivas', 'Substituição', 'Por partes', 'Definida', 'Indefinida', 'Teorema Fundamental'], key="int_rule")
    definite = rule in ('Definida', 'Teorema Fundamental')
    a = b = 0.0
    if definite:
        a = st.number_input("Limite inferior a", value=0.0, key="int_a")
        b = st.number_input("Limite superior b", value=2.0, key="int_b")
    if st.button("Mostrar exemplo", key="int_ex"):
        st.session_state.int_expr, st.session_state.int_var, st.session_state.int_rule = "x^2 + 3*x + 2", "x", "Indefinida"
        st.rerun()
    try:
        steps, final, plot = solve_integral(expr, variable, rule,
                                            'Definite' if definite else 'Indefinite', a, b)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))