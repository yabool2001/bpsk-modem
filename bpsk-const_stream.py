import adi
import numpy as np
import time
import zlib
from scipy.signal import upfirdn


# ------------------------ PARAMETRY KONFIGURACJI ------------------------
F_C = 2_900_000_000     # częstotliwość nośna [Hz]
#F_S = 521_100           # częstotliwość próbkowania [Hz]
F_S = 3_000_000           # częstotliwość próbkowania [Hz]
SPS = 4                 # próbek na symbol
TX_ATTENUATION = 10.0   # tłumienie TX [dB]
BW = 1_000_000          # szerokość pasma [Hz]
RRC_BETA = 0.35         # roll-off factor
RRC_SPAN = 11           # długość filtru RRC w symbolach
CYCLE = 0            # opóźnienie między pakietami [ms]; <0 = liczba powtórzeń

# ------------------------ DANE DO MODULACJI ------------------------
header = [ 0xAA , 0xAA , 0xAA , 0xAA ]
# payload = [ 0x0F , 0x0F , 0x0F , 0x0F ]  # można zmieniać dynamicznie
payload = [ 0x0F ]  # można zmieniać dynamicznie

def bits_to_bpsk ( bits ) :
    return np.array ( [1.0 if bit else -1.0 for bit in bits] , dtype = np.float32 )

def rrc_filter(beta, sps, span):
    N = sps * span
    t = np.arange(-N//2, N//2 + 1, dtype=np.float32) / sps
    taps = np.sinc(t) * np.cos(np.pi * beta * t) / (1 - (2 * beta * t)**2)
    taps[np.isnan(taps)] = 0
    taps /= np.sqrt(np.sum(taps**2))
    return taps

def modulate_packet(packet, sps, beta, span):
    bits = np.unpackbits ( np.array ( packet , dtype = np.uint8 ) )
    symbols = bits_to_bpsk ( bits )
    rrc = rrc_filter(beta, sps, span)
    shaped = upfirdn(rrc, symbols, up=sps)
    return (shaped + 0j).astype(np.complex64)

def transmit_loop(waveform, cycle_ms, sdr):
    try: 
        sdr.tx_destroy_buffer()
        sdr.tx_cyclic_buffer = False
        if cycle_ms > 0:
            while True:
                print ( f"Powtórka..." )
                sdr.tx(waveform)
                time.sleep(cycle_ms / 1000.0)
        elif cycle_ms == 0:
            sdr.tx_cyclic_buffer = True
            sdr.tx ( waveform )
            while True :
                pass
        else:
            for _ in range(-cycle_ms):
                print ( f"Powtórka..." )
                sdr.tx(waveform)
    except KeyboardInterrupt :
        print ( "Zakończono ręcznie (Ctrl+C)" )
    finally:
        sdr.tx_destroy_buffer()
        sdr.tx_cyclic_buffer = False
        print ( f"{sdr.tx_cyclic_buffer=}" )

# ------------------------ KONFIGURACJA SDR ------------------------
def main():
    waveform = modulate_packet ( payload , SPS , RRC_BETA , RRC_SPAN )

# Inicjalizacja Pluto SDR
    sdr = adi.Pluto ( uri = "usb:" )
    sdr.tx_destroy_buffer()
    sdr.sample_rate = int ( F_S )
    sdr.tx_rf_bandwidth = int ( BW )
    sdr.tx_lo = int ( F_C )
    sdr.tx_cyclic_buffer = False
    sdr.tx_hardwaregain_chan0 = float ( -TX_ATTENUATION )

    print ( f"Nadawanie pakietu: {packet}" )
    transmit_loop ( waveform , CYCLE , sdr )

if __name__ == "__main__":
    main ()
