from nicegui import ui
import random

class PMEmulation:
    """Classe de simulation pour le powermeter."""

    def measure(self) -> float:
        """Retourne une puissance aléatoire entre 5 et 20 mW."""
        return 5 + random.random() * 15
    

class EmulatedMotor:
    """Classe de simulation pour le moteur."""

    def __init__(self):
        self.current_angle = 0.0

    def go_to_angle(self, angle: float):
        """Déplace instantanément le moteur à l’angle donné (simulation)."""
        self.current_angle = angle

    def read_angle(self) -> float:
        """Retourne l'angle actuel (simulation)."""
        return self.current_angle
motor = None
pm = None
powermeter_mode = 'emulation'
motor_mode = 'emulation'

from integra import INTEGRA

class IntegraPowerMeter:
    def __init__(self, port="COM3"):
        self.device = INTEGRA(port)

    def detect(self) -> str:
        self.device.set_pwc(633)
        self.device.send_command("*CAU")
        self.device.read_line()
        return self.device.reply

    def measure(self) -> float:
        self.device.send_command("LEV?")
        self.device.read_line()
        try:
            return float(self.device.reply)
        except:
            return 0.0

    def zero(self) -> str:
        self.device.send_command("ZRO")
        self.device.read_line()
        return self.device.reply
    