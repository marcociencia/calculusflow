# CalculusFlow — versão Streamlit

Aplicativo de matemática passo a passo (aritmética, cálculo e álgebra) reescrito em **Python + Streamlit + SymPy** para rodar no [Streamlit Community Cloud](https://streamlit.io/cloud) de graça.

## Por que SymPy (e não LLM)
A versão original usa um backend de LLM para gerar os passos. Esta versão usa **SymPy** (cálculo simbólico real): mais confiável, sem chave de API e 100% gratuito para rodar no Streamlit Cloud.

## Estrutura
```
requirements.txt            # dependências (raiz — o Streamlit Cloud procura aqui)
streamlit_app/
  app.py                    # aplicativo principal (menu lateral)
  core.py                   # parsing de expressões + helpers
  plot_util.py              # gráficos com matplotlib
  arithmetic.py             # adição, subtração, multiplicação, divisão
  calculus.py               # limites, derivadas, integrais
  algebra.py                # equações linear/quadrática, sistemas
```

## Rodar localmente
```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

## Publicar no Streamlit Community Cloud
1. Crie um repositório no GitHub e suba estes arquivos (a pasta `streamlit_app/` e o `requirements.txt` na raiz).
2. Acesse https://streamlit.io/cloud e entre com o GitHub.
3. **New app** → selecione o repositório.
4. **Main file path**: `streamlit_app/app.py`
5. O `requirements.txt` na raiz é instalado automaticamente.
6. Clique em **Deploy**.

## Módulos incluídos
- **Aritmética**: adição com transporte, subtração com empréstimo, multiplicação longa, divisão longa (com botão "Mostrar exemplo").
- **Cálculo**: limites, derivada por definição (limite do quociente), integral como limite de somas de Riemann, derivadas e integrais por regras.
- **Álgebra**: equação linear, equação quadrática (Bhaskara), sistemas lineares 2×2 e 3×3 (matriz + RREF).

> Observação: esta é uma versão independente do app original em React/Base44. Os passos são gerados matematicamente pelo SymPy (não por IA).