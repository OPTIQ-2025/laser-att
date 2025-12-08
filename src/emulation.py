from nicegui import ui
import random

class PMEmulation:
    """Classe de simulation pour le powermeter."""

    def measure(self) -> float:
        """Retourne une puissance aléatoire entre 5 et 20 mW."""
        return 5 + random.random() * 15
    
    def get_wavelength(self) -> float:
        """Retourne une longueur d'onde simulée (nm)."""
        return 633.0
    

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

    # Compatibilité: méthode attendue par `motor_half_lambda.MotorController`
    def get_position(self) -> float:
        """Alias pour read_angle() — retourne l'angle actuel en degrés (lame)."""
        return self.read_angle()
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
    
    def get_wavelength(self) -> float:
        """Récupère la longueur d'onde courante depuis l'appareil INTEGRA.
        Retourne 0.0 si non disponible ou en cas d'erreur.
        """
        try:
            self.device.get_status()
            # INTEGRA stocke la longueur d'onde dans wavelength_cur
            return float(self.device.wavelength_cur)
        except Exception:
            return 0.0
    