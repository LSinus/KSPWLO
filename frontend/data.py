import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons

# Leggi i dati
df = pd.read_csv('../backend/build/output.csv')

# Raggruppa per 'k', 'theta' e 'alg' e calcola la media del 'time'
df_grouped = df.groupby(['k', 'theta', 'alg']).agg({'time': 'mean'}).reset_index()

# Estrai le colonne necessarie dal DataFrame raggruppato
x = df_grouped['k']
y = df_grouped['theta']
z = df_grouped['time']
alg = df_grouped['alg']

# Crea il grafico scatter con dimensioni maggiori
fig = plt.figure(figsize=(12, 8))  # Dimensione maggiore del grafico
ax = fig.add_subplot(111, projection='3d')

# Associa un colore a ogni algoritmo
algorithms = df['alg'].unique()
colors = plt.cm.tab10(range(len(algorithms)))

# Salva i punti in un dizionario
scatter_plots = {}
for alg_name, color in zip(algorithms, colors):
    mask = df_grouped['alg'] == alg_name
    scatter_plots[alg_name] = ax.scatter(
        x[mask],
        y[mask],
        z[mask],
        label=alg_name,
        color=color
    )

# Imposta i limiti degli assi
ax.set_xlim(0, 10)
ax.set_ylim(0, 1)
ax.set_zlim(0, 1000)

# Aggiungi etichette e legenda
ax.set_xlabel('k')
ax.set_ylabel('theta')
ax.set_zlabel('time')

# Posizione per i CheckButtons
rax = plt.axes([0.8, 0.4, 0.15, 0.2])  # [left, bottom, width, height]
check = CheckButtons(rax, algorithms, [True] * len(algorithms))  # Attivo per default

# Funzione per aggiornare la visibilità
def toggle_visibility(label):
    scatter = scatter_plots[label]
    scatter.set_visible(not scatter.get_visible())
    plt.draw()

check.on_clicked(toggle_visibility)

# Regola l'angolo di visualizzazione
ax.view_init(elev=20, azim=135)

# Mostra il grafico
plt.show()
