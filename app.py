"""
CalculusFlow - Correcao da divisao longa (substituir as funcoes antigas).

Cole este conteudo no ficheiro CalculusFlow original, substituindo:
  - long_divide(...)
  - render_long_division(...)
e mantendo o resto do ficheiro intacto.

A logica de alinhamento e identica a da subtração:
  - colunas de largura fixa (2.25rem) para que carregadores e digitos grandes
    compartilhem o mesmo centro de coluna;
  - o "36" do primeiro passo fica alinhado sob o "43";
  - o arco "⌒" fica centralizado acima do primeiro conjunto ("43");
  - os sinais "-" ocupam uma coluna reservada a esquerda;
  - 4356, 12 e 363 usam o mesmo tamanho de fonte (30px).

Testado com 4356 / 12 = 363.
"""
import streamlit as st


# ---------- alinhamento por colunas ----------
COL_W = "2.25rem"


def _step_borrows(cur_str, prod_str, chunk_start, W):
    """Marcadores de emprestimo (lilas/azul) da subtracao de um passo."""
    top = [int(c) for c in cur_str]
    bot = [int(c) for c in prod_str.rjust(len(top), "0")]
    n = len(top)
    w = top[:]
    violet = [""] * W
    blue = [""] * W
    for k in range(n - 1, -1, -1):
        if w[k] < bot[k]:
            jj = k - 1
            while jj >= 0 and w[jj] == 0:
                jj -= 1
            if jj >= 0:
                for m in range(jj + 1, k):
                    w[m] = 9
                    violet[chunk_start + m] = "10"
                    blue[chunk_start + m] = "9"
                w[jj] -= 1
                blue[chunk_start + jj] = str(w[jj])
                w[k] += 10
                violet[chunk_start + k] = str(w[k])
    return violet, blue


def _div_compute(dividend, divisor):
    absB = abs(divisor)
    D = str(abs(dividend))
    N = len(D)
    W = N
    qAbs = abs(dividend // absB) if absB else 0
    qStr = str(qAbs)
    quotient = [""] * W
    for j, ch in enumerate(qStr):
        quotient[W - len(qStr) + j] = ch

    steps = []
    cur = 0
    start = -1
    for i in range(N):
        if start == -1:
            start = i
        cur = cur * 10 + int(D[i])
        if cur < absB:
            continue
        qd = cur // absB
        prod = qd * absB
        remVal = cur - prod
        prodStr = str(prod)
        prodStart = i - len(prodStr) + 1
        violet, blue = _step_borrows(str(cur), prodStr, prodStart, W)
        rem = [""] * W
        for k in range(prodStart, i):
            rem[k] = "0"
        rem[i] = str(remVal)
        if i + 1 < N:
            rem[i + 1] = D[i + 1]
        steps.append(
            {
                "prodStr": prodStr,
                "prodStart": prodStart,
                "prodEnd": i,
                "violet": violet,
                "blue": blue,
                "rem": rem,
            }
        )
        cur = remVal
        start = i if remVal != 0 else -1
        if remVal == 0:
            cur = 0
    return {
        "D": D,
        "N": N,
        "W": W,
        "divisor": str(absB),
        "quotient": quotient,
        "qStr": qStr,
        "steps": steps,
    }


def _cells(values, cls, font="big"):
    """Constroi uma linha da grelha com W celulas deslocadas +1 (col 0 reservada)."""
    out = ['<div class="%s %s"></div>' % (cls, font)]  # col 0 vazia
    for v in values:
        out.append('<div class="%s %s">%s</div>' % (cls, font, v))
    return '<div class="divgrid">' + "".join(out) + "</div>"


def render_long_division():
    st.subheader("Long Division - Ideal Design")
    dividend = int(st.number_input("Dividend", value=4356, step=1, key="div_A"))
    divisor = int(st.number_input("Divisor", value=12, step=1, key="div_B"))
    if divisor == 0:
        st.error("Division by zero")
        return

    d = _div_compute(dividend, divisor)
    W = d["W"] + 1
    steps = d["steps"]

    css = (
        "<style>"
        ".divboard{display:inline-flex;align-items:flex-start;gap:4px;"
        "font-family:ui-monospace,monospace;font-weight:700;font-variant-numeric:tabular-nums;}"
        f".divgrid{{display:grid;grid-template-columns:repeat({W},{COL_W});"
        "justify-items:center;align-items:end;}"
        ".big{font-size:30px;line-height:1.1;}"
        ".small{font-size:11px;line-height:1.1;min-height:16px;}"
        ".faint{min-height:8px;}"
        ".arc{text-align:center;font-size:30px;line-height:1;}"
        ".bar{height:2px;background:#000;align-self:end;}"
        ".underline{border-bottom:3px solid #000;height:3px;align-self:end;}"
        ".empty{height:3px;}"
        ".red{color:#dc2626;}.violet{color:#7c3aed;}.blue{color:#2563eb;}.black{color:#000;}"
        "</style>"
    )

    rows = [css, '<div class="divboard">']
    rows.append(
        '<div class="big" style="align-self:stretch;padding:0 16px 16px 16px">%s</div>'
        % d["divisor"]
    )
    rows.append('<div class="divgridwrap">')

    # quociente
    rows.append('<div class="divgrid">')
    rows.append('<div class="big red"></div>')
    for c in d["quotient"]:
        rows.append('<div class="big red">%s</div>' % c)
    rows.append("</div>")

    # arco + barra superior
    first = steps[0]
    chunk = first["prodEnd"] - first["prodStart"] + 1
    start_track = first["prodStart"] + 2  # 1-indexed (+1 col reservada +1)
    bars = W - 1 - chunk
    rows.append('<div class="divgrid">')
    rows.append('<div class="arc"></div>')
    rows.append(
        '<div class="arc" style="grid-column:%d / span %d">&#8963;</div>'
        % (start_track, chunk)
    )
    for _ in range(bars):
        rows.append('<div class="bar"></div>')
    rows.append("</div>")

    # dividendo
    rows.append('<div class="divgrid">')
    rows.append('<div class="big"></div>')
    for c in d["D"]:
        rows.append('<div class="big">%s</div>' % c)
    rows.append("</div>")

    for s in steps:
        # marcadores de emprestimo
        if any(s["violet"]):
            rows.append('<div class="divgrid">')
            rows.append('<div class="small violet"></div>')
            for v in s["violet"]:
                rows.append('<div class="small violet">%s</div>' % v)
            rows.append("</div>")
            rows.append('<div class="divgrid">')
            rows.append('<div class="small blue"></div>')
            for v in s["blue"]:
                rows.append('<div class="small blue">%s</div>' % v)
            rows.append("</div>")

        # produto (com sinal - na coluna reservada)
        prod = [""] * d["W"]
        prod[s["prodStart"]] = "&minus;"
        for i, ch in enumerate(s["prodStr"]):
            prod[s["prodEnd"] - (len(s["prodStr"]) - 1 - i)] = ch
        rows.append('<div class="divgrid">')
        rows.append('<div class="big black"></div>')
        for c in prod:
            rows.append('<div class="big black">%s</div>' % c)
        rows.append("</div>")

        # linha sob o produto
        rows.append('<div class="divgrid faint">')
        for i in range(d["W"]):
            if i >= s["prodStart"] and i <= s["prodEnd"]:
                rows.append('<div class="underline"></div>')
            else:
                rows.append('<div class="empty"></div>')
        rows.append("</div>")

        # resto + digito baixado
        rows.append('<div class="divgrid">')
        rows.append('<div class="big"></div>')
        for c in s["rem"]:
            rows.append('<div class="big">%s</div>' % c)
        rows.append("</div>")

    rows.append("</div></div>")  # divgridwrap, divboard
    st.markdown("".join(rows), unsafe_allow_html=True)
    st.markdown(
        "%d &divide; %d = <span style='color:#dc2626'>%d</span>" % (dividend, divisor, dividend // divisor),
        unsafe_allow_html=True,
    )


def long_divide(dividend, divisor):
    """Mantida por compatibilidade - logica antiga, apenas numerica."""
    if divisor == 0:
        return {"error": "Division by zero"}
    dividend, divisor = abs(int(dividend)), abs(int(divisor))
    digits = list(map(int, str(dividend)))
    cur = 0
    steps = []
    q_digits = []
    for dgt in digits:
        cur = cur * 10 + dgt
        qd = cur // divisor
        if not steps and qd == 0:
            continue
        prod = qd * divisor
        rem = cur - prod
        steps.append({"product": prod})
        q_digits.append(qd)
        cur = rem
    q_str = "".join(map(str, q_digits)) or "0"
    return {
        "dividend": dividend,
        "divisor": divisor,
        "quotient_str": q_str,
        "steps": steps,
        "remainder": cur,
    }
