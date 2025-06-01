import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import os

# Ścieżki do plików
tx_file = "complex_tx.csv"
rx_file = "complex_rx.csv"

# Konfiguracja
WINDOW_DURATION = 0.005  # okno czasowe w sekundach

# Wczytaj dane CSV z separatorem średnikowym i zamień przecinki na kropki
def load_csv(file_path):
    df = pd.read_csv(file_path, delimiter=',')
    return df

tx_df = load_csv(tx_file)
rx_df = load_csv(rx_file)

# Zakładamy kolumny: timestamp, real, imag
min_time = min(tx_df["timestamp"].min(), rx_df["timestamp"].min())
max_time = max(tx_df["timestamp"].max(), rx_df["timestamp"].max())

# Ustawienia początkowe
start_time = min_time
end_time = start_time + WINDOW_DURATION

# Tworzenie wykresu
fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
plt.subplots_adjust(bottom=0.25)

tx_real_line, = ax[0].plot([], [], label="TX Real")
tx_imag_line, = ax[0].plot([], [], label="TX Imag", linestyle="--")
ax[0].set_ylabel("TX Amplituda")
ax[0].legend()
ax[0].grid(True)

rx_real_line, = ax[1].plot([], [], label="RX Real")
rx_imag_line, = ax[1].plot([], [], label="RX Imag", linestyle="--")
ax[1].set_ylabel("RX Amplituda")
ax[1].set_xlabel("Czas [s]")
ax[1].legend()
ax[1].grid(True)

# Suwak czasu
ax_slider = plt.axes([0.1, 0.05, 0.8, 0.03])
time_slider = Slider(
    ax=ax_slider,
    label="Czas",
    valmin=min_time,
    valmax=max_time - WINDOW_DURATION,
    valinit=start_time,
    valstep=0.01,
)


def update(val):
    t0 = time_slider.val
    t1 = t0 + WINDOW_DURATION

    # Filtruj dane z podanych przedziałów
    tx_window = tx_df[(tx_df["timestamp"] >= t0) & (tx_df["timestamp"] <= t1)]
    rx_window = rx_df[(rx_df["timestamp"] >= t0) & (rx_df["timestamp"] <= t1)]

    tx_real_line.set_data(tx_window["timestamp"], tx_window["real"])
    tx_imag_line.set_data(tx_window["timestamp"], tx_window["imag"])
    rx_real_line.set_data(rx_window["timestamp"], rx_window["real"])
    rx_imag_line.set_data(rx_window["timestamp"], rx_window["imag"])

    # Dostosuj zakresy
    ax[0].set_xlim(t0, t1)
    ax[1].set_xlim(t0, t1)
    ax[0].relim()
    ax[1].relim()
    ax[0].autoscale_view(scalex=False)
    ax[1].autoscale_view(scalex=False)
    fig.canvas.draw_idle()


time_slider.on_changed(update)
update(start_time)  # Inicjalna aktualizacja
plt.show()
