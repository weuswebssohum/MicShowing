import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk

# Function to enumerate available audio devices
def list_audio_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    devices = []
    for i in range(num_devices):
        device = p.get_device_info_by_host_api_device_index(0, i)
        devices.append(device['name'])
    p.terminate()
    return devices

# Function to initialize audio stream for a given device index
def initialize_stream(device_index, chunk_size, channels, rate):
    p = pyaudio.PyAudio()
    format = pyaudio.paInt16  # Data format (16-bit PCM)
    
    try:
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk_size,
                        input_device_index=device_index)
        return p, stream
    except Exception as e:
        print(f"Error initializing stream for device {device_index}: {e}")
        p.terminate()
        return None, None

# Function to update plot
def update_plot(frame):
    global data1, data2, stream1, stream2, CHUNK

    if stream1 is not None:
        try:
            new_data1 = np.frombuffer(stream1.read(CHUNK), dtype=np.int16)
            data1[:-CHUNK] = data1[CHUNK:]
            data1[-CHUNK:] = new_data1
            line1.set_ydata(data1)
        except IOError as e:
            print(f"Error reading from stream1: {e}")

    if stream2 is not None:
        try:
            new_data2 = np.frombuffer(stream2.read(CHUNK), dtype=np.int16)
            data2[:-CHUNK] = data2[CHUNK:]
            data2[-CHUNK:] = new_data2
            line2.set_ydata(data2)
        except IOError as e:
            print(f"Error reading from stream2: {e}")

    return line1, line2

# Function to handle device selection from GUI
def handle_device_selection():
    global stream1, stream2, p1, p2

    selected_device1 = combo1.current()
    selected_device2 = combo2.current()
    channels = int(channel_var.get())
    rate = int(rate_var.get())

    if stream1:
        stream1.stop_stream()
        stream1.close()
        p1.terminate()

    if stream2:
        stream2.stop_stream()
        stream2.close()
        p2.terminate()

    p1, stream1 = initialize_stream(selected_device1, CHUNK, channels, rate)
    p2, stream2 = initialize_stream(selected_device2, CHUNK, channels, rate)

# GUI Setup using tkinter
root = tk.Tk()
root.title("Audio Visualization")

devices = list_audio_devices()

label1 = tk.Label(root, text="Select Microphone 1:")
label1.pack(pady=5)
combo1 = ttk.Combobox(root, values=devices, state="readonly")
combo1.pack(pady=5)
combo1.current(0)

label2 = tk.Label(root, text="Select Microphone 2:")
label2.pack(pady=5)
combo2 = ttk.Combobox(root, values=devices, state="readonly")
combo2.pack(pady=5)
combo2.current(1)

label3 = tk.Label(root, text="Select Channels:")
label3.pack(pady=5)
channel_var = tk.StringVar(value="1")
channel_combo = ttk.Combobox(root, textvariable=channel_var, values=["1", "2"], state="readonly")
channel_combo.pack(pady=5)

label4 = tk.Label(root, text="Select Sampling Rate:")
label4.pack(pady=5)
rate_var = tk.StringVar(value="44100")
rate_combo = ttk.Combobox(root, textvariable=rate_var, values=["8000", "16000", "44100", "48000"], state="readonly")
rate_combo.pack(pady=5)

button_apply = tk.Button(root, text="Apply", command=handle_device_selection)
button_apply.pack(pady=10)

CHUNK = 1024
data1 = np.zeros(CHUNK)
data2 = np.zeros(CHUNK)

initial_channels = int(channel_var.get())
initial_rate = int(rate_var.get())
p1, stream1 = initialize_stream(combo1.current(), CHUNK, initial_channels, initial_rate)
p2, stream2 = initialize_stream(combo2.current(), CHUNK, initial_channels, initial_rate)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

line1, = ax1.plot(np.arange(CHUNK), data1)
ax1.set_title('Microphone 1')
ax1.set_xlabel('Samples')
ax1.set_ylabel('Amplitude')
ax1.set_ylim(-32768, 32767)
ax1.set_xlim(0, CHUNK)

line2, = ax2.plot(np.arange(CHUNK), data2)
ax2.set_title('Microphone 2')
ax2.set_xlabel('Samples')
ax2.set_ylabel('Amplitude')
ax2.set_ylim(-32768, 32767)
ax2.set_xlim(0, CHUNK)

plt.tight_layout()
ani = FuncAnimation(fig, update_plot, blit=True, interval=50)
plt.show()

root.mainloop()

if stream1:
    stream1.stop_stream()
    stream1.close()
if stream2:
    stream2.stop_stream()
    stream2.close()
p1.terminate()
p2.terminate()
