"""Módulos de álgebra: equação linear, equação quadrática e sistemas lineares."""
import streamlit as st
import sympy as sp
from core import parse_expr, parse_equation, X, for_plot, num
import plot_util


def _show(steps, final, plot=None):
    for title, detail in steps:
        st.markdown(f"**{title}**")
        st.markdown(detail)
    st.markdown(f"**Resposta final**")
    st.latex(final)
    if plot:
        st.pyplot(plot_util.plot_functions(**plot))


def solve_linear(eq_str):
    eq = parse_equation(eq_str)
    x = X
    poly = sp.Poly(eq, x)
    coeffs = poly.all_coeffs()
    if len(coeffs) > 2:
        raise ValueError("A equação não é do 1º grau.")
    a = coeffs[0]
    b = coeffs[1] if len(coeffs) == 2 else 0
    if a == 0:
        raise ValueError("Coeficiente de x é zero — não é equação do 1º grau.")
    root = sp.simplify(-b / a)
    steps = [
        ("Equação original", f"$$ {sp.latex(sp.Eq(parse_expr(eq_str.split('=')[0]), parse_expr(eq_str.split('=')[1])))} $$"),
        ("Forma padrão", f"$$ {sp.latex(a)}\\,x + {sp.latex(b)} = 0 $$"),
        ("Identificar coeficientes", f"$$a = {sp.latex(a)}, \\quad b = {sp.latex(b)}$$"),
        ("Isolar x", f"$$a\\,x = -b \\implies x = \\frac{{-b}}{{a}} = \\frac{{{sp.latex(-b)}}}{{{sp.latex(a)}}}$$"),
        ("Resultado", f"$$x = {sp.latex(root)}$$"),
        ("Verificação", f"Substituindo x = {sp.latex(root)}: {sp.latex(sp.simplify(eq.subs(x, root)))} = 0 ✓"),
    ]
    final = f"x = {sp.latex(root)}"
    rv = num(root)
    plot = {'exprs': [{'expr': for_plot(eq, x), 'label': 'a·x + b'}],
            'x_min': (rv - 5) if rv is not None else -5,
            'x_max': (rv + 5) if rv is not None else 5,
            'points': [{'x': float(root), 'y': 0, 'label': f'x = {root}', 'color': 'red'}] if rv is not None else None}
    return steps, final, plot


def render_linear():
    st.subheader("Equação linear (1º grau)")
    eq = st.text_input("Equação", value="2*x + 3 = 7", key="lin_eq")
    if st.button("Mostrar exemplo", key="lin_ex"):
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
        raise ValueError("A equação precisa ser do 2º grau (a·x² + b·x + c).")
    a, b, c = coeffs
    disc = sp.simplify(b**2 - 4 * a * c)
    roots = sp.solve(eq, x)
    steps = [
        ("Equação original", f"$$ {sp.latex(sp.Eq(parse_expr(eq_str.split('=')[0]), parse_expr(eq_str.split('=')[1])))} $$"),
        ("Forma padrão", f"$$ {sp.latex(a)}\\,x^2 + {sp.latex(b)}\\,x + {sp.latex(c)} = 0 $$"),
        ("Coeficientes", f"$$a = {sp.latex(a)}, \\quad b = {sp.latex(b)}, \\quad c = {sp.latex(c)}$$"),
        ("Discriminante", f"$$\\Delta = b^2 - 4ac = {sp.latex(b)}^2 - 4({sp.latex(a)})({sp.latex(c)}) = {sp.latex(disc)}$$"),
        ("Fórmula de Bhaskara", f"$$x = \\frac{{-b \\pm \\sqrt{{\\Delta}}}}{{2a}} = \\frac{{{sp.latex(-b)} \\pm \\sqrt{{{sp.latex(disc)}}}}}{{{sp.latex(2*a)}}}$$"),
        ("Soluções", f"$$x = {sp.latex(roots)}$$"),
    ]
    final = "x = " + (", \\quad ".join(sp.latex(r) for r in roots) if isinstance(roots, list) else sp.latex(roots))
    real_roots = [num(r) for r in roots if isinstance(roots, list) and num(r) is not None and abs(num(r).imag) < 1e-9]
    pts = [{'x': float(r.real), 'y': 0.0, 'label': f'x={r.real:.3g}'} for r in real_roots] if real_roots else None
    # faixa do gráfico em torno do vértice/raízes
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
    st.subheader("Equação quadrática (2º grau)")
    eq = st.text_input("Equação", value="x^2 - 5*x + 6 = 0", key="quad_eq")
    if st.button("Mostrar exemplo", key="quad_ex"):
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
    steps = [
        ("Sistema", "$$\\begin{cases}" + " \\\ ".join(sp.latex(sp.Eq(lhs, rhs)) for lhs, rhs in [(sp.Add(*[A[i, j]*syms[j] for j in range(len(syms))]), bb[i]) for i in range(A.rows)]) + "\\end{cases}$$"),
        ("Forma matricial", f"$$A = {sp.latex(A)}, \\quad b = {sp.latex(bb)}$$"),
        ("Matriz aumentada [A | b]", f"$$[A \\mid b] = {sp.latex(aug)}$$"),
        ("Forma escalonada (RREF)", f"$$\\text{{RREF}} = {sp.latex(rref)}$$"),
        ("Solução", f"$$({', '.join(str(v) for v in variables)}) = {sp.latex(sol)}$$"),
    ]
    if isinstance(sol, sp.FiniteSet) and sol:
        vals = list(sol)[0]
        verify = []
        for i, e in enumerate(eqs):
            sub = sp.simplify(e.subs(dict(zip(syms, vals))))
            verify.append(f"{sp.latex(e)} → {sp.latex(sub)} = 0" + (" ✓" if sub == 0 else ""))
        steps.append(("Verificação", "  ".join(verify)))
    final = "(" + ", ".join(str(v) for v in variables) + ") = " + sp.latex(sol)
    return steps, final, None


def render_system():
    st.subheader("Sistemas lineares")
    size = st.radio("Tamanho", ['2x2', '3x3'], horizontal=True, key="sys_size")
    variables = ['x', 'y'] if size == '2x2' else ['x', 'y', 'z']
    eq1 = st.text_input("Equação 1", value="2*x + 3*y = 5", key="sys_e1")
    eq2 = st.text_input("Equação 2", value="x - y = 1", key="sys_e2")
    eq3 = None
    if size == '3x3':
        eq3 = st.text_input("Equação 3", value="x + y + z = 6", key="sys_e3")
    if st.button("Mostrar exemplo", key="sys_ex"):
        st.session_state.sys_size = '2x2'
        st.session_state.sys_e1, st.session_state.sys_e2 = "2*x + 3*y = 5", "x - y = 1"
        st.rerun()
    equations = [eq1, eq2] + ([eq3] if size == '3x3' and eq3 else [])
    try:
        steps, final, plot = solve_system(equations, variables)
        _show(steps, final, plot)
    except Exception as ex:
        st.error(str(ex))