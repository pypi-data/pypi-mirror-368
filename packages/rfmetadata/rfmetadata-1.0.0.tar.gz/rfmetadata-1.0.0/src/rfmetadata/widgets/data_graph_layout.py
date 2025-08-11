from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from rfmetadata.signal_manager.data_signal_manager import signal_manager, graph_type_manager
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from scipy.interpolate import griddata
from matplotlib import cm
from matplotlib.colors import Normalize


class DataGraph3D(FigureCanvas):
    def __init__(self, figure:Figure=None)->None:        
        self.figure = Figure()
        super().__init__(figure)

        self.min_power = 20.0
        self.max_power = 60.0

        self.type = "scatter"

        self.data = []
        self.freq = []
        self.pow = []
        self.time = []


        self.ax = self.figure.add_subplot(projection='3d')
        self.ax.set_title("Data Graph")
        
        signal_manager.data_signal.connect(self.receive_data)
        graph_type_manager.data_signal.connect(self.set_type)

        
                    
    def receive_data(self, data):
        self.data = data
        self.freq.clear()
        self.pow.clear()
        self.time.clear()

        for row_data in self.data:
            self.freq.append(row_data[1])
            self.pow.append(row_data[2])
            dt = datetime.strptime(row_data[3], "%d-%m-%Y %H:%M:%S")
            self.time.append(mdates.date2num(dt))

        self.draw_graph()

    def set_type(self, type):
        self.type = type
        self.draw_graph()

    
    def draw_graph(self):

        if not (self.freq and self.pow and self.time):
            return

        
        if self.type == "scatter":
            self.figure.clear()
            self.ax = self.figure.add_subplot(projection='3d')

            self.ax.set_title("Data Graph")

            self.ax.set_title("Data Graph")
            self.ax.set_xlabel("Frequency")
            self.ax.set_ylabel("Time")
            self.ax.set_zlabel("Power")
            self.ax.yaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
            self.ax.set_zlim(self.min_power, self.max_power)
            self.ax.scatter(self.freq, self.time, self.pow)
            self.draw()

        elif self.type == "meshgrid":
            self.figure.clear()

            self.ax = self.figure.add_subplot(projection='3d')

            self.ax.set_title("Data Graph")

            # Preparing data as numpy arrays
            freq = np.array(self.freq)
            time = np.array(self.time)
            power = np.array(self.pow)

            # Building a grid
            freq_lin = np.linspace(freq.min(), freq.max(), 100)
            time_lin = np.linspace(time.min(), time.max(), 100)
            FREQ, TIME = np.meshgrid(freq_lin, time_lin)

            # Interpolating power data onto grid
            POWER = griddata(
                points=(freq, time),
                values=power,
                xi=(FREQ, TIME),
                method='nearest'
            )

            POWER = np.nan_to_num(POWER, nan=np.nanmin(power))


            surf = self.ax.plot_surface(
                FREQ, TIME, POWER,
                cmap='inferno',
                linewidth=0.5,
                antialiased=True
            )
            
            self.ax.set_title("Data Graph")
            self.ax.set_xlabel("Frequency")
            self.ax.set_ylabel("Time")
            self.ax.set_zlabel("Power")

            self.ax.yaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))

            self.ax.set_zlim(self.min_power, self.max_power)

            self.draw()

        elif self.type == "line":
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)

            # Normalizing frequency values for colormap
            norm = Normalize(vmin=min(self.freq), vmax=max(self.freq))
            cmap = cm.get_cmap('viridis')

            # Plotting each segment with color based on frequency
            for i in range(len(self.pow) - 1):
                x_vals = [self.time[i], self.time[i+1]]
                y_vals = [self.pow[i], self.pow[i+1]]
                freq_avg = (self.freq[i] + self.freq[i+1]) / 2
                color = cmap(norm(freq_avg))

                self.ax.plot(x_vals, y_vals, color=color, linewidth=2)

            # Formatting time axis
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Power')
            self.ax.set_title('Power vs Time (Colored by Frequency)')

            # Adding colorbar
            sm = cm.ScalarMappable(norm=norm, cmap=cmap)
            sm.set_array([])  # Required to register mappable
            cbar = self.figure.colorbar(sm, ax=self.ax)
            cbar.set_label("Frequency")

            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
            self.figure.autofmt_xdate()

            self.draw()


