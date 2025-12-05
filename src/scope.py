import matplotlib.pyplot as plt
import time


class Scope:
    def __init__(self):
        """ Constructor """
        self.sleepDelay = 0.0

    def restart(self):
        """ Clear data """
        self.start = self.get_cur_time()
        self.curTime = 0
        self.x = []
        self.y = []
        plt.grid(True)
        plt.plot(self.x, self.y)
        plt.title("Puissance mètre en fonction du temps")
        plt.xlabel("Time from start [s]")
        plt.ylabel("powermeter (µW)")

    def get_cur_time(self):
        """ Return the current time """
        return time.time()

    def set_value(self, _y):
        """ Set the value of the scope """
        self.y.append(_y)

    def update(self):
        """ Update real-time graphic"""
        cur = self.get_cur_time()-self.start
        self.x.append(cur)
        time.sleep(self.sleepDelay)
        self.curTime = self.get_cur_time()

        plt.gca().lines[0].set_xdata(self.x)
        plt.gca().lines[0].set_ydata(self.y)
        plt.gca().relim()
        plt.gca().autoscale_view()
        plt.pause(0.05)
