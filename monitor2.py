# Idealne ustawienie Attenuation TX1 (dB) = 1.2 w bloku "Pluto SDR Sink"
# W Rx ACG = Fast Attack

import adi
import csv
import keyboard
import numpy as np
from scipy.signal import lfilter
import sys
import time
import pandas as pd
import plotly.express as px
from modules.rrc import rrc_filter

# Import lokalnego modułu RRC
sys.path.append ( "modules" )

# App settings
verbose = True
#verbose = False

# Parametry SDR
RX_GAIN = 0.1

# Parametry RF 
F_C = 2_900_000_000
F_S = 521_100
BW  = 1_000_000
NUM_SAMPLES = 32768
NUM_POINTS = 16384
SPS = 4
GAIN_CONTROL = "fast_attack"
#GAIN_CONTROL = "manual"
# Parametry filtru RRC
RRC_BETA = 0.35 # Excess_bw
RRC_SPS = SPS   # Samples per symbol
RRC_SPAN = 11

# Inicjalizacja Pluto SDR
sdr = adi.Pluto ( uri = "usb:" )
sdr.rx_lo = int ( F_C )
sdr.sample_rate = int ( F_S )
sdr.rx_rf_bandwidth = int ( BW )
sdr.rx_buffer_size = int ( NUM_SAMPLES )
sdr.gain_control_mode_chan0 = GAIN_CONTROL
sdr.rx_hardwaregain_chan0 = float ( RX_GAIN )
sdr.rx_output_type = "SI"
if verbose : help ( adi.Pluto.rx_output_type ) ; help ( adi.Pluto.gain_control_mode_chan0 ) ; help ( adi.Pluto.tx_lo ) ; help ( adi.Pluto.tx  )

# Inicjalizacja pliku CSV
filename = "complex_rx.csv"
csv_file = open ( filename , mode = "w" , newline = '' )
csv_writer = csv.writer ( csv_file )
csv_writer.writerow ( [ "timestamp" , "real" , "imag" ] )

# Inicjalizacja filtry RRC
rrc_taps = rrc_filter ( RRC_BETA , RRC_SPS , RRC_SPAN )

# Bufor konstelacji (cykliczny)
iq_buffer = np.zeros ( NUM_POINTS , dtype = np.complex64 )
write_index = 0

if verbose : print ( "Rozpoczynam zbieranie danych... (wciśnij Esc, aby zakończyć)" )
t0 = time.time ()
try :
    while True:
        if keyboard.is_pressed ('esc') :
            print ( "Naciśnięto Esc. Kończę zbieranie." )
            break

        new_samples = sdr.rx ()
        #filtered = lfilter ( rrc_taps , 1.0 , new_samples )
        ts = time.time () - t0
        acg_vaule = sdr._get_iio_attr ( 'voltage0' , 'hardwaregain' , False )
        print ( f"{acg_vaule=}" )
        for sample in new_samples :
            csv_writer.writerow ( [ ts , sample.real , sample.imag ] )
        csv_file.flush () 
        #if verbose : print ( f"Typ danych: {type ( new_samples )}, dtype: {new_samples.dtype}" ) ; print ( f"{new_samples=}" )
        if verbose : print ( f"Typ danych: {type ( new_samples )}, dtype: {new_samples.dtype}" ) ; print ( f"{new_samples=}" )

except KeyboardInterrupt :
    print ( "Zakończono ręcznie (Ctrl+C)" )

finally:
    csv_file.close ()

# Wczytanie danych i wyświetlenie wykresu w Plotly
print ( "Rysuję wykres..." )

df = pd.read_csv ( filename )

# Zbuduj sygnał zespolony
signal = df["real"].values + 1j * df["imag"].values

# Filtracja za pomocą scipy.signal.lfilter
filtered_signal = lfilter(rrc_taps, 1.0, signal)

# Dodaj kolumny z wynikami
df["real_filt"] = filtered_signal.real
df["imag_filt"] = filtered_signal.imag

# Wykres Plotly Express – wersja liniowa z filtrem
fig = px.line(df, x="timestamp", y="real_filt", title="Sygnał BPSK po filtracji RRC – I i Q (lfilter)")
fig.add_scatter(x=df["timestamp"], y=df["imag_filt"], mode="lines", name="Q (imag filtrowane)", line=dict(dash="dash"))

fig.update_layout(
    xaxis_title="Czas względny [s]",
    yaxis_title="Amplituda",
    xaxis=dict(
        rangeslider_visible=True
    ),
    yaxis=dict(
        autorange=True
    ),
    legend=dict(x=0.01, y=0.99)
)


fig.show ()