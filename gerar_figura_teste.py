"""Gera a Figura 5 usando apenas as observações do teste cronológico."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent


def main():
    df = pd.read_csv(ROOT / 'suplementar/previsoes_teste_turbidez.csv')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig, ax = plt.subplots(figsize=(6.3, 4.1), layout='constrained')
    for estacao, cor in [('EF24', '#165a87'), ('EF26', '#ad5d17')]:
        grupo = df[df.estacao == estacao]
        ax.scatter(grupo.turbidez, grupo.rf_turbidez, label=f'{estacao} (n = {len(grupo)})',
                   color=cor, s=30, alpha=.85, edgecolors='white', linewidths=.4)
    limite = max(df[['turbidez', 'rf_turbidez']].max().max(), 90) * 1.07
    ax.plot([0, limite], [0, limite], label='Igualdade entre observado e estimado',
            color='#666666', linestyle='--', linewidth=1)
    ref = float(df.referencia_media_treino.iloc[0])
    ax.axhline(ref, label=f'Referência pela média do treino ({ref:.2f} NTU)'.replace('.', ','),
               color='#222222', linestyle=':', linewidth=1.3)
    ax.set(xlabel='Turbidez observada no teste (NTU)', ylabel='Turbidez estimada no mesmo dia (NTU)',
           xlim=(0, limite), ylim=(0, limite))
    ax.grid(alpha=.15)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, loc='upper left', fontsize=8)
    pasta = ROOT / 'suplementar/figuras'
    pasta.mkdir(exist_ok=True)
    fig.savefig(pasta / 'figura5_teste_turbidez.png', dpi=220)
    plt.close(fig)


if __name__ == '__main__':
    main()
