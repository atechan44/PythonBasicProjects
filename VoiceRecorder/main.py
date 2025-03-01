import sys
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import queue
import time


class AudioRecorder(QMainWindow):
    def __init__(self, samplerate=44100, channels=1, window=200, downsample=1):
        super().__init__()
        self.samplerate = samplerate
        self.channels = channels
        self.window = window
        self.downsample = downsample
        self.q = queue.Queue()
        self.recording = False
        self.stream = None
        self.file = None

        # UI Setup
        self.setWindowTitle("Voice Recorder")
        self.setGeometry(100, 100, 600, 400)

        # Matplotlib canvas
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.length = int(self.window * self.samplerate / (1000 * self.downsample))
        self.plotdata = np.zeros((self.length, self.channels))
        self.lines = self.ax.plot(self.plotdata)
        self.ax.axis((0, self.length, -1, 1))
        self.ax.set_yticks([0])
        self.ax.yaxis.grid(True)
        self.ax.tick_params(bottom=False, top=False, labelbottom=False,
                            right=False, left=False, labelleft=False)
        self.fig.tight_layout(pad=0)

        # Buttons
        self.start_button = QPushButton("Recording started")
        self.stop_button = QPushButton("Recording stopped")
        self.save_button = QPushButton("Record saved")

        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.save_button.clicked.connect(self.save_recording)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for plot update and recording
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.setInterval(30)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        data = indata[::self.downsample, [0]]
        self.q.put(data.copy())

        # Titreşim simülasyonu
        amplitude = np.max(np.abs(indata))
        if amplitude > 0.5:
            self.simulate_vibration()

    def simulate_vibration(self):
        self.ax.set_title("Ses Algılandı!", color="red")
        self.canvas.draw()
        QApplication.processEvents()
        QTimer.singleShot(100, lambda: self.ax.set_title(""))

    def update_plot(self):
        while True:
            try:
                data = self.q.get_nowait()
            except queue.Empty:
                break
            shift = len(data)
            self.plotdata = np.roll(self.plotdata, -shift, axis=0)
            self.plotdata[-shift:, :] = data
            if self.recording and self.file:
                self.file.write(data)
        for column, line in enumerate(self.lines):
            line.set_ydata(self.plotdata[:, column])
        self.canvas.draw()

    def start_recording(self):
        if not self.recording:
            self.recording = True
            # Her kayıt için benzersiz dosya adı
            self.filename = f"output_{int(time.time())}.wav"
            self.stream = sd.InputStream(
                samplerate=self.samplerate, channels=self.channels,
                callback=self.audio_callback)
            self.file = sf.SoundFile(self.filename, mode='w', samplerate=self.samplerate,
                                     channels=self.channels)
            self.stream.start()
            self.timer.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.save_button.setEnabled(False)
            print("Recording started")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.stream.stop()
            self.stream.close()
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.save_button.setEnabled(True)
            print("Recording stopped")

    def save_recording(self):
        if self.file:
            self.file.close()
            print(f"Record saved as {self.filename}.")
            self.save_button.setEnabled(False)
            self.file = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioRecorder()
    window.show()
    sys.exit(app.exec_())