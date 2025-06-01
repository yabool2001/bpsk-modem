import numpy as np
import zlib
import adi
import time

# Parametry transmisji
F_C = 820_000_000
F_S = 521_100
SPS = 8
SILENCE_MS = 1000
MAX_PAYLOAD_LEN = 255

# Parametry Pluto
TX_GAIN = -50.0


# Preambuła
PREAMBLE = bytes ( [0xAA] * 4 + [0x55] * 4 )
silence_samples = int ( F_S * SILENCE_MS / 1000 )
silence = np.zeros ( silence_samples, dtype = np.complex64 )

# Wczytaj dane
with open ( "input.txt", "rb" ) as f:
    full_data = f.read ()

tx_signal_parts = []

for i in range ( 0, len ( full_data ), MAX_PAYLOAD_LEN ):

    payload = full_data[i : i + MAX_PAYLOAD_LEN]
    length_byte = len ( payload ).to_bytes ( 1, "big" )
    timestamp_ms = int ( time.time () * 1000 ) & 0xFFFFFFFF
    timestamp_bytes = timestamp_ms.to_bytes ( 4, "big" )

    crc_input = length_byte + timestamp_bytes + payload
    crc = zlib.crc32 ( crc_input )
    crc_bytes = crc.to_bytes ( 4, "big" )

    packet = PREAMBLE + crc_input + crc_bytes
    packet_bits = np.unpackbits ( np.frombuffer ( packet, dtype = np.uint8 ) )
    symbols = 2 * packet_bits - 1
    tx_symbols = np.repeat ( symbols, SPS ).astype ( np.complex64 )
    tx_symbols *= 0.2  # minimalna moc wyjściowa

    tx_signal_parts.append ( tx_symbols )
    tx_signal_parts.append ( silence )

tx_signal = np.concatenate ( tx_signal_parts )

# Inicjalizacja Pluto SDR
sdr = adi.Pluto ( uri = "ip:192.168.2.1" )
sdr.sample_rate = F_S
sdr.tx_rf_bandwidth = int ( F_S )
sdr.tx_lo = F_C
sdr.tx_cyclic_buffer = True
#sdr.tx_cyclic_buffer = False

sdr.tx ( tx_signal )

print ( f"Wysłano {len ( tx_signal_parts ) // 2} pakietów z F_C = {F_C / 1e6:.1f} MHz, F_S = {F_S:.1f} S/s, SPS = {SPS}." )
