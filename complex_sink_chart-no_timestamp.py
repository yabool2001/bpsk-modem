import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Ścieżka do pliku RX
rx_file = "complex_rx.csv"

# Parametry
WINDOW_SIZE = 500  # liczba próbek w oknie

# Wczytaj dane
def load_csv(file_path):
    df = pd.read_csv(file_path, delimiter=',')
    return df

rx_df = load_csv(rx_file)

# Granice indeksu
max_index = len(rx_df) - WINDOW_SIZE

# Tworzenie wykresu
fig, ax = plt.subplots(1, 1, figsize=(12, 4))
plt.subplots_adjust(bottom=0.25)

rx_real_line, = ax.plot([], [], label="RX Real")
rx_imag_line, = ax.plot([], [], label="RX Imag", linestyle="--")
ax.set_ylabel("Amplituda")
ax.set_xlabel("Numer próbki")
ax.legend()
ax.grid(True)

# Suwak indeksu
slider_ax = plt.axes([0.1, 0.05, 0.8, 0.03])
index_slider = Slider(
    ax=slider_ax,
    label="Indeks początkowy",
    valmin=0,
    valmax=max_index,
    valinit=0,
    valstep=1,
)

# Funkcja aktualizacji wykresu
def update(index):
    idx = int(index)
    rx_window = rx_df.iloc[idx:idx+WINDOW_SIZE]

    rx_real_line.set_data(range(idx, idx+WINDOW_SIZE), rx_window["real"])
    rx_imag_line.set_data(range(idx, idx+WINDOW_SIZE), rx_window["imag"])

    ax.set_xlim(idx, idx+WINDOW_SIZE)
    ax.relim()
    ax.autoscale_view(scalex=False)
    fig.canvas.draw_idle()

# Inicjalizacja
index_slider.on_changed(update)
update(0)

plt.show()
