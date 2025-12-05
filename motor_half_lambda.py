import time
from pypot.dynamixel.io import DxlIO

# Configuration
BAUDRATE = 1000000
ID_MOTEUR = 1

# Paramètres de précision
TOLERANCE = 0.1  
TIMEOUT = 4.0    


PID_P = 10.0     
PID_I = 1.2    
PID_D = 25.0    
VITESSE = 140

def trouver_port():
    """Trouve le port du moteur en testant COM0-COM9 et quelques ports Linux"""

    
    # Liste des ports à tester (Windows)
    ports_windows = [f"COM{i}" for i in range(10)]  # COM0 à COM9
    
    # Ports Linux courants
    ports_linux = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
    
    # Combiner les listes
    ports_a_tester = ports_windows + ports_linux
    
    for port in ports_a_tester:
        print(f"Test {port}...", end=" ")
        
        try:
            # Essayer de se connecter
            dxl_io = DxlIO(port, baudrate=BAUDRATE)
            
            # Essayer de scanner les moteurs
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
    """Contrôleur pour le moteur"""
    
    def __init__(self):
        self.current_angle = 0.0
        self.is_connected = False
        self.port = trouver_port()
    
    def _connect(self):
        """Établit une connexion temporaire au moteur avec configuration PID"""
        try:
            dxl_io = DxlIO(self.port, baudrate=BAUDRATE)
            dxl_io.enable_torque({ID_MOTEUR: True})
            
            # Configuration PID et vitesse
            dxl_io.set_pid_gain({ID_MOTEUR: (PID_P, PID_I, PID_D)})
            dxl_io.set_moving_speed({ID_MOTEUR: VITESSE})
            
            print(f"Moteur connecté avec PID: P={PID_P}, I={PID_I}, D={PID_D}, Vitesse={VITESSE}")
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
                # Désactiver le torque avant de fermer
                dxl_io.disable_torque({ID_MOTEUR: True})
                dxl_io.close()
            except:
                pass
        self.is_connected = False
    
    def get_position(self):
        """Lit la position actuelle (0-360°) avec connexion temporaire"""
        dxl_io = self._connect()
        if not dxl_io:
            return self.current_angle
        
        try:
            angle = dxl_io.get_present_position([ID_MOTEUR])[0]
            self.current_angle = angle
            print(f"Position lue: {self.current_angle:.1f}°")
            return self.current_angle
        except Exception as e:
            print(f"Erreur lecture position: {e}")
            return self.current_angle
        finally:
            self._disconnect(dxl_io)
    
    def go_to_angle(self, angle):
        """Déplace le moteur vers un angle avec connexion temporaire"""
        dxl_io = self._connect()
        if not dxl_io:
            return False
        
        try:
            target_angle = angle
            print(f"Déplacement vers {target_angle}° (précision ±{TOLERANCE}°)")

            # Lire position de départ
            start_pos = dxl_io.get_present_position([ID_MOTEUR])[0]
            print(f"Position départ: {start_pos:.1f}°")
            # Commande de déplacement
            dxl_io.set_goal_position({ID_MOTEUR: target_angle})
            
            # Attente avec précision et timeout
            start_time = time.time()
            while time.time() - start_time < TIMEOUT:
                try:
                    current_pos = dxl_io.get_present_position([ID_MOTEUR])[0]
                    erreur = abs(current_pos - target_angle)
                    
                    # Affichage de progression
                    if int((time.time() - start_time) * 10) % 5 == 0:  
                        print(f"Position: {current_pos:6.1f}° | Erreur: {erreur:5.1f}°")
                    
                    if erreur <= TOLERANCE:
                        self.current_angle = target_angle
                        print(f"Position atteinte avec précision ({erreur:.1f}° d'erreur)")
                        return True
                except Exception as e:
                    print(f"Erreur lecture pendant mouvement: {e}")
                
                time.sleep(0.05)
            
            # Timeout atteint
            try:
                current_pos = dxl_io.get_present_position([ID_MOTEUR])[0]
                self.current_angle = current_pos
                erreur_finale = abs(current_pos - target_angle)
                print(f"Timeout - Position finale: {current_pos:.1f}° (erreur: {erreur_finale:.1f}°)")
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"Erreur pendant le déplacement: {e}")
            return False
        finally:
            self._disconnect(dxl_io)

# Instance globale
motor = MotorController()