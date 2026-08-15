"""CalculusFlow — versão Streamlit. FIX FINAL para Streamlit Cloud."""
import sys
from pathlib import Path

# --- BOOTSTRAP DE PATH: Isso tem que vir ANTES de importar calculus ---
HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
# Adiciona a própria pasta (calculusflow) e a raiz do repo
for p in [str(HERE), str(ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st

# Agora importa absoluto - vai funcionar porque HERE está no path
import arithmetic
import calculus
import algebra

st.set_page_config(page_title="CalculusFlow", page_icon="➗", layout="centered")

st.title("CalculusFlow")
st.caption("Companheiro interativo de matemática — aritmética, cálculo e álgebra, passo a passo.")

MODULES = {
    "Aritmética": {
        "Adição (vai-um)": arithmetic.render_addition,
        "Subtração (empréstimo)": arithmetic.render_subtraction,
        "Multiplicação longa": arithmetic.render_multiplication,
        "Divisão longa": arithmetic.render_long_division,
    },
    "Cálculo": {
        "Limites": calculus.render_limit,
        "Derivada por definição": calculus.render_derivative_limit,
        "Integral por somas de Riemann": calculus.render_integral_limit,
        "Derivadas (regras)": calculus.render_derivative,
        "Integrais (regras)": calculus.render_integral,
    },
    "Álgebra": {
        "Equação linear": algebra.render_linear,
        "Equação quadrática": algebra.render_quadratic,
        "Sistemas lineares": algebra.render_system,
    },
}

groups = list(MODULES.keys())
group = st.sidebar.radio("Área", groups, horizontal=False)
modules = MODULES[group]
choice = st.sidebar.radio("Módulo", list(modules.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("Gerado a partir do app React CalculusFlow. "
                    "Cálculo simbólico com **SymPy** — sem chave de API.")

modules[choice]()
