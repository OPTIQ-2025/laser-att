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