"""Plotagem com matplotlib para os módulos de cálculo/álgebra."""
import numpy as np
import matplotlib.pyplot as plt
from sympy import lambdify
from core import X


def plot_functions(exprs, x_min, x_max, points=None, shade=None, title=None):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    xs = np.linspace(float(x_min), float(x_max), 400)

    for e in exprs:
        f = lambdify(X, e['expr'], modules=['numpy'])
        try:
            ys = f(xs)
            ys = np.array(ys, dtype=float)
            finite = np.isfinite(ys)
            ax.plot(xs[finite], ys[finite],
                    label=e.get('label', ''),
                    linestyle='--' if e.get('dashed') else '-',
                    color=e.get('color'))
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