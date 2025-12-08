import time
from pypot.dynamixel.io import DxlIO

# Configuration
BAUDRATE = 1000000
ID_MOTEUR = 1

# 180° moteur = 70° lame, rapport = 2.57:1
RAPPORT_REDUCTION = 2.57  

def trouver_port():
    """Trouve le port du moteur"""
    
    ports_windows = [f"COM{i}" for i in range(10)]
    ports_linux = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
    ports_a_tester = ports_windows + ports_linux
    
    for port in ports_a_tester:
        print(f"Test {port}...", end=" ")
        
        try:
            dxl_io = DxlIO(port, baudrate=BAUDRATE)
            
            try:
                moteurs = dxl_io.scan()
                if moteurs:
                    print(f"Moteurs détectés: {moteurs}")
                    dxl_io.close()
                    return port
                else:
                    print("Aucun moteur détecté")
            except:
                print("Erreur scan")
            
            dxl_io.close()
            
        except Exception as e:
            print("Échec")
    
    print("Aucun port valide trouvé")
    return None

class MotorController:
    """Contrôleur pour le moteur Dynamixel (version simplifiée 0-45°)"""
    
    def __init__(self, p=11.0, i=1.2, d=24.0, vitesse=140):
        """Initialise le contrôleur moteur avec paramètres PID réglables"""

        self.current_angle_lame = 0.0
        self.is_connected = False
        self.port = trouver_port()
        
        # Paramètres PID et vitesse 
        self.PID_P = p  
        self.PID_I = i  
        self.PID_D = d  
        self.VITESSE = vitesse  
        
        print(f"Paramètres PID initiaux: P={self.PID_P}, I={self.PID_I}, D={self.PID_D}, Vitesse={self.VITESSE}")
        
    def _connect(self):
        """Établit une connexion temporaire au moteur avec configuration PID"""
        try:
            dxl_io = DxlIO(self.port, baudrate=BAUDRATE)
            dxl_io.enable_torque({ID_MOTEUR: True})
            
            dxl_io.set_pid_gain({ID_MOTEUR: (self.PID_P, self.PID_I, self.PID_D)})
            dxl_io.set_moving_speed({ID_MOTEUR: self.VITESSE})
            
            print(f"Moteur connecté avec PID: P={self.PID_P}, I={self.PID_I}, D={self.PID_D}, Vitesse={self.VITESSE}")
            self.is_connected = True
            return dxl_io
        except Exception as e:
            print(f"Erreur connexion: {e}")
            self.is_connected = False
            return None
    
    def _disconnect(self, dxl_io):
        """Ferme la connexion au moteur"""
        if dxl_io:
            try:
                dxl_io.disable_torque({ID_MOTEUR: True})
                dxl_io.close()
            except:
                pass
        self.is_connected = False
    
    def set_pid(self, p=None, i=None, d=None, vitesse=None):
        """Modifie les paramètres PID et vitesse"""

        if p is not None:
            self.PID_P = p
        if i is not None:
            self.PID_I = i
        if d is not None:
            self.PID_D = d
        if vitesse is not None:
            self.VITESSE = vitesse
        
        print(f"Paramètres PID mis à jour: P={self.PID_P}, I={self.PID_I}, D={self.PID_D}, Vitesse={self.VITESSE}")
    
        if self.is_connected:
            dxl_io = DxlIO(self.port, baudrate=BAUDRATE)
            try:
                dxl_io.enable_torque({ID_MOTEUR: True})
                dxl_io.set_pid_gain({ID_MOTEUR: (self.PID_P, self.PID_I, self.PID_D)})
                dxl_io.set_moving_speed({ID_MOTEUR: self.VITESSE})
                dxl_io.disable_torque({ID_MOTEUR: True})
                dxl_io.close()
                print("Paramètres appliqués au moteur")
                return True
            except Exception as e:
                print(f"Erreur application paramètres: {e}")
                return False
        
        return True
    
    def lame_to_moteur(self, angle_lame):
        """Convertit l'angle lame en angle moteur"""
        if angle_lame < 0:
            angle_lame = 0
        elif angle_lame > 45:
            angle_lame = 45

        return angle_lame * RAPPORT_REDUCTION
    
    def moteur_to_lame(self, angle_moteur):
        """Convertit l'angle moteur en angle lame"""
        return angle_moteur / RAPPORT_REDUCTION
    
    def get_position(self):
        """Lit la position actuelle de la lame"""
        dxl_io = self._connect()
        if not dxl_io:
            return self.current_angle_lame
        
        try:
            motor_angle = dxl_io.get_present_position([ID_MOTEUR])[0]
            self.current_angle_lame = self.moteur_to_lame(motor_angle)

            if self.current_angle_lame < 0:
                self.current_angle_lame = 0
            elif self.current_angle_lame > 45:
                self.current_angle_lame = 45
            
            print(f"Position: moteur={motor_angle:.1f}° → lame={self.current_angle_lame:.1f}°")
            return self.current_angle_lame
            
        except Exception as e:
            print(f"Erreur lecture: {e}")
            return self.current_angle_lame
        finally:
            self._disconnect(dxl_io)
    
    def go_to_angle(self, target_angle_lame):
        """Déplace la lame vers un angle (0-45°)"""
        if target_angle_lame < 0:
            target_angle_lame = 0
        elif target_angle_lame > 45:
            target_angle_lame = 45
        
        dxl_io = self._connect()
        if not dxl_io:
            return False
        
        try:
            target_motor_angle = self.lame_to_moteur(target_angle_lame)
            
            print(f"Déplacement vers {target_angle_lame}° lame ({target_motor_angle:.1f}° moteur)")
            
            dxl_io.set_goal_position({ID_MOTEUR: target_motor_angle})
            
            time.sleep(2)

            motor_angle = dxl_io.get_present_position([ID_MOTEUR])[0]
            self.current_angle_lame = self.moteur_to_lame(motor_angle)
            

            erreur = abs(self.current_angle_lame - target_angle_lame)
            print(f"Mouvement terminé. Position: {self.current_angle_lame:.1f}°, Erreur: {erreur:.1f}°")
            
            return erreur <= 2.0  
            
        except Exception as e:
            print(f"Erreur pendant le déplacement: {e}")
            return False
        finally:
            self._disconnect(dxl_io)
    
    def get_pid_params(self):
        """Retourne les paramètres PID actuels"""
        return {
            'P': self.PID_P,
            'I': self.PID_I,
            'D': self.PID_D,
            'vitesse': self.VITESSE
        }

# Instance globale avec paramètres par défaut
motor = MotorController()