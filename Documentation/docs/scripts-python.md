# Code Controlleur moteur




# Code Puissance-mètre

Cette partie gère la mesure de puissance optique du système, soit via un powermeter INTEGRA réel (communication série et décodage du statut), soit via une émulation logicielle, afin de fournir à l’interface une mesure unifiée de la puissance et de la longueur d’onde.

Elle se décompose en plusieurs fichiers :  

- `port.py` :    
Gère toute la communication série bas niveau (ouverture du port COM, envoi de commandes, lecture des réponses) utilisée pour dialoguer avec le powermeter.
  
- `status.py` :  
Assure le décodage du statut renvoyé par l’INTEGRA (longueur d’onde, échelles, nom du détecteur, atténuateur, versions).
  
- `scope.py` :  
Fournit un petit oscilloscope logiciel basé sur matplotlib pour afficher la puissance en temps réel (optionnel dans ton UI).
  
- `integra.py` :  
Driver officiel Gentec-EO, téléchargé sur leur site, qui implémente toutes les commandes du powermeter INTEGRA.
  
- `emulation.py` : 
Contient une émulation logicielle du powermeter (`PMEmulation`) et un wrapper unifié (`IntegraPowerMeter`) utilisé par l’interface pour basculer entre mode réel et simulé.
   
- `detect.py` :  
Petit script de test servant uniquement à vérifier la connexion série et à envoyer manuellement quelques commandes au powermeter.
  
### 1 - `port.py`

`port.py` contient l’abstraction de la communication série utilisée par le powermeter Gentec-EO.  
Il repose sur la librairie pyserial pour : 
- détecter les ports COM disponibles  
- ouvrir et fermer un port série  
- envoyer des commandes ASCII au powermeter  
- lire les réponses renvoyées par l’appareil  
  
Ce fichier constitue la couche bas niveau de la photodétection :  
tous les échanges entre le PC et l’INTEGRA passent obligatoirement par lui.
  
    import serial
    import serial.tools.list_ports
    import time
  
    class PortSerial:
        """Class to facilitate the serial port object for Gentec-EO devices"""

        def __init__(self, comPort=""):
            """ Ask to select a com port if none is specified
                _comPort: the selected port name Ex.: COM6
            """


            self.reply = ""
            self.custom_delay = 0.02
            self.comPort = comPort
            self.serialPort = serial.Serial()
            self.verbose = True  # flag
            self.port_select = True

            if self.comPort != "":
                self.port_open(comPort)
            else:
                # if port select is true ask for port selection
                if self.port_select:
                    self.quit = PortSerial.port_select(self)*-1+1

        def port_list(self):
            """ Display available port."""
            ports = list(serial.tools.list_ports.comports())
            if len(ports) == 0:
                print("None. Check your connection.")
                return 0
            for p in ports:
                print(p)

        def port_select(self):
            """ Display all available ports on the computer and ask the port to connect to """
            self.comPort = ""  # reset the comPort
            if self.serialPort.is_open:
                self.serialPort.close()  # close the port

            print("Port(s) available:\r\n")
            if self.port_list() == 0:
                return 0

            while not self.serialPort.is_open:
                promptPort = input("\r\nPlease enter a COM port (ex.: COM3). Enter Q to quit:")
                if promptPort:
                    if promptPort == "Q":
                        return 0
                    self.comPort = promptPort.upper()
                    self.port_open()
            return 1

        def is_open(self):
            """ Indicate if the port is open """
            return self.serialPort.is_open

        def port_close(self):
            """ Close the selected port """
            self.serialPort.close()

        def port_open(self, _comport=""):
            """ Open the selected port
                _comport: the selected port name
            """
            if _comport != "":
                self.comPort = _comport

            if not self.serialPort.is_open:
                try:
                    self.serialPort = serial.Serial(port=self.comPort,
                                                    baudrate=115200,
                                                    timeout=2)
                except serial.serialutil.PortNotOpenError:
                    print(f"Unable to open port {self.comPort}")
                except serial.serialutil.SerialException:
                    print(f"Unable to open port {self.comPort}")
                    self.port_select

        def send_command(self, command, arg=""):
            """
            Send a command and argument to the selected port:
                : command: The command sent to the device
                : arg:     The argument of that command
            """
            self.reply = ""
            for c in command:
                self.serialPort.write(c.encode('ascii'))
                time.sleep(self.custom_delay)

            for c in arg:
                self.serialPort.write(c.encode('ascii'))
                time.sleep(self.custom_delay)

            if self.verbose:
                if arg:
                    print(f"< {command}[{arg}]")
                else:
                    print(f"< {command}")

        def read_line(self):
            """ Read one line from selected port"""
            self.reply = self.serialPort.readline().decode("ascii")
            if self.verbose:
                print(f"> {self.reply}")

        def read_lines(self, eot):
            """ Read line until eot "end of transmission" is reached
                eot: end of transmission to search for
            """
            self.reply = ""
            while self.reply != eot:
                self.reply = self.serialPort.readline().decode("ascii")
                if self.verbose:
                    print(f"> {self.reply}")

        def read(self, length):
            """ Read a fixed length of characters
            length : nb of char to read
            """
            self.reply = self.serialPort.read(length).decode("ascii")
            if self.verbose:
                print(self.reply)

### 2 - `status.py`

`status.py` gère le décodage des informations de statut envoyées par le powermeter INTEGRA.  
  
Il convertit des trames hexadécimales en données exploitables telles que :  
- la longueur d’onde réglée  
- la plage de longueurs d’onde supportée  
- les échelles de puissance (min / max / actuelle)  
- le nom du détecteur  
- le numéro de série  
- la présence d’un atténuateur  
- les versions logiciel / firmware / hardware.  

Ce module sert uniquement à interpréter les données que le powermeter renvoie  

    def format5(value):
        """ Convert a int in a 5 characters string long.
        This conversion is needed for *PWC for multiple monitor.
        """
        return "{0:5d}".format(value)


    def format8(value):
        """ Convert a float in a string 8 chararacters long.
        This conversion is needed for *MUL, *OFF.
        """

        if round(value, 0) <= -100000: return "{:.0f}.".format(round(value, 0))
        if round(value, 1) <= -10000:  return "{:.1f}".format(round(value, 1))
        if round(value, 2) <= -1000:   return "{:.2f}".format(round(value, 2))
        if round(value, 3) <= -100:    return "{:.3f}".format(round(value, 3))
        if round(value, 4) <= -10:     return "{:.4f}".format(round(value, 4))
        if round(value, 5) < 0:        return "{:.5f}".format(round(value, 5))
        if round(value, 6) < 1:        return "{:.6f}".format(round(value, 6))
        if round(value, 6) < 10:       return "{:.6f}".format(round(value, 6))
        if round(value, 5) < 100:      return "{:.5f}".format(round(value, 5))
        if round(value, 4) < 1000:     return "{:.4f}".format(round(value, 4))
        if round(value, 3) < 10000:    return "{:.3f}".format(round(value, 3))
        if round(value, 2) < 100000:   return "{:.2f}".format(round(value, 2))


    class Status:
        """ Status of a monitor """
        def __init__(self):
            self.mode = 0
            self.scale_max = 0
            self.scale_min = 0
            self.scale_cur = 0
            self.wavelength_max = 0
            self.wavelength_min = 0
            self.wavelength_cur = 0
            self.att_available = 0
            self.att_present = 0
            self.detector_name = ""
            self.detector_serial = ""
            self.version_sw = ""
            self.version_fw = ""
            self.version_hw = ""

        def print_status(self):
            print(f"sw: {self.version_sw}")
            print(f"fw: {self.version_fw}")
            print(f"hw: {self.version_hw}")
            print(f"Name: {self.detector_name}")
            print(f"Serial: {self.detector_serial}")
            print(f"Mode: {self.mode}")
            print(f"Scale Cur: {self.scale_cur}")
            print(f"Scale Min: {self.scale_min}")
            print(f"Scale Max: {self.scale_max}")
            print(f"Wavelength cur: {self.wavelength_cur}")
            print(f"Wavelength min: {self.wavelength_min}")
            print(f"Wavelength max: {self.wavelength_max}")
            print(f"attenuator available: {self.att_available}")
            print(f"attenuator present: {self.att_present}")

        def decode(self, input):
            # decode the status
            self.mode = int(f"0x{input[0x05][6:10]}{input[0x04][6:10]}", base=16)
            self.scale_cur = int(f"0x{input[0x07][6:10]}{input[0x06][6:10]}",
                                base=16)
            self.scale_max = int(f"0x{input[0x09][6:10]}{input[0x08][6:10]}",
                                base=16)
            self.scale_min = int(f"0x{input[0x0B][6:10]}{input[0x0A][6:10]}",
                                base=16)
            self.wavelength_cur = int(f"0x{input[0x0D][6:10]}{input[0x0C][6:10]}",
                                    base=16)
            self.wavelength_max = int(f"0x{input[0x0F][6:10]}{input[0x0E][6:10]}",
                                    base=16)
            self.wavelength_min = int(f"0x{input[0x11][6:10]}{input[0x10][6:10]}",
                                    base=16)
            self.att_available = int(f"0x{input[0x13][6:10]}{input[0x12][6:10]}",
                                    base=16)
            self.att_present = int(f"0x{input[0x15][6:10]}{input[0x14][6:10]}",
                                base=16)

            # decode name
            name = ""
            for i in range(0x1A, 0x24):
                name = name + input[i][6:10]

            for i in range(0, len(name), 4):
                if name[i+2:i+4] != "CC":
                    self.detector_name = self.detector_name + chr(int(
                        name[i+2:i+4],
                        base=16)
                    )

                if name[i:i+2] != "CC":
                    self.detector_name = self.detector_name + chr(int(
                        name[i:i+2],
                        base=16)
                    )

            sn = ""
            for i in range(0x2A, 0x2D):
                sn = sn + input[i][6:10]

            for i in range(0, len(sn), 4):
                if sn[i+2:i+4] != "CC":
                    self.detector_serial = self.detector_serial + chr(int(
                        sn[i+2:i+4],
                        base=16)
                    )

                if sn[i:i+2] != "CC":
                    self.detector_serial = self.detector_serial + chr(int(
                        sn[i:i+2],
                        base=16)
                    )

### 3 - `scope.py`  

`scope.py` scope.py fournit un petit oscilloscope logiciel basé sur matplotlib.  
  
Il permet :  
- d’enregistrer une série de mesures dans des buffers  
- de mettre à jour une courbe en temps réel  
- d’afficher un historique glissant des valeurs mesurées  

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

### 4 - `integra.py`

`integra.py` est un fichier officiel Gentec-EO pour le powermeter INTEGRA.
  
Il gère :  
- la gestion complète du protocole Gentec  
- les commandes de contrôle (*PWC, LEV?, *STS, *CAU, ZRO, etc.)  
- la récupération et l’interprétation du statut  
- l’accès aux fonctions internes du détecteur (longueur d’onde, échelle, etc.)

    from port import PortSerial
    from scope import Scope
    from status import *


    class INTEGRA(PortSerial, Scope, Status):
        """ Class to connect to an integra """

        def __init__(self, comPort=""):
            """ Default constructor """
            PortSerial.__init__(self, comPort)
            Status.__init__(self)
            Scope.__init__(self)

        def get_version(self):
            """ Get the versions of the device:
                VER, GFW and GHW
            """
            self.send_command("*VER")
            self.read_line()
            self.version_sw = self.reply.rstrip()

            self.send_command("*GFW")
            self.read_line()
            self.version_fw = self.reply.rstrip()

            self.send_command("*GHW")
            self.read_line()
            self.version_hw = self.reply.rstrip()

        def set_pwc(self, pwc):
            """
            Set the pwc
                : pwc: the desired wavelength
            """
            s = "{:05d}".format(pwc)

            if len(s) == 5:
                print("PWC: OK")
            else:
                print("PWC: Wrong length")
                return

            self.send_command("*PWC" + s)
            self.read_line()

        def set_user_multiplier(self, value):
            s = format8(value)
            n = 0
            if len(s) == 8:
                print("UserMultiplier: OK[", n, "] ", s, "for:", value)
            else:
                n += 1
                print("UserMultiplier: Wrong length:", s, "for:", value)

        def get_data(self):
            """ Read the line and convert the output into data """
            self.read_line()
            try:
                self.set_value(float(self.reply))
            except ValueError:
                self.set_value(0)

        def get_status(self):
            """ Request the status from the device and decode it"""
            self.send_command("*STS")
            self.verbose = False
            replys = []

            while self.reply[0:2] != ":1":
                self.read_line()
                replys.append(self.reply)

            self.read_line()  # read the ACK

            # decode the status
            self.mode = int(f"0x{replys[0x05][6:10]}{replys[0x04][6:10]}",
                            base=16)
            self.scale_cur = int(f"0x{replys[0x07][6:10]}{replys[0x06][6:10]}",
                                base=16)
            self.scale_max = int(f"0x{replys[0x09][6:10]}{replys[0x08][6:10]}",
                                base=16)
            self.scale_min = int(f"0x{replys[0x0B][6:10]}{replys[0x0A][6:10]}",
                                base=16)
            self.wavelength_cur = int(
                f"0x{replys[0x0D][6:10]}{replys[0x0C][6:10]}",
                base=16)
            self.wavelength_max = int(
                f"0x{replys[0x0F][6:10]}{replys[0x0E][6:10]}",
                base=16)
            self.wavelength_min = int(
                f"0x{replys[0x11][6:10]}{replys[0x10][6:10]}",
                base=16)
            self.att_available = int(f"0x{replys[0x13][6:10]}{replys[0x12][6:10]}",
                                    base=16)
            self.att_present = int(f"0x{replys[0x15][6:10]}{replys[0x14][6:10]}",
                                base=16)

            # decode name
            name = ""
            for i in range(0x1A, 0x24):
                name = name + replys[i][6:10]

            for i in range(0, len(name), 4):
                if name[i+2:i+4] != "CC":
                    self.detector_name = self.detector_name + chr(int(
                        name[i+2:i+4],
                        base=16)
                    )

                if name[i:i+2] != "CC":
                    self.detector_name = self.detector_name + chr(int(
                        name[i:i+2],
                        base=16)
                    )

        def print_status(self):
            """ Display the status of the device """
            
            print(f"sw: {self.version_sw}")
            print(f"fw: {self.version_fw}")
            print(f"hw: {self.version_hw}")
            print(f"Name: {self.detector_name}")
            print(f"Serial: {self.detector_serial}")
            print(f"Mode: {self.mode}")
            print(f"Scale Cur: {self.scale_cur}")
            print(f"Scale Min: {self.scale_min}")
            print(f"Scale Max: {self.scale_max}")
            print(f"Wavelength cur: {self.wavelength_cur}")
            print(f"Wavelength min: {self.wavelength_min}")
            print(f"Wavelength max: {self.wavelength_max}")
            print(f"Attenuator available: {self.att_available}")
            print(f"Attenuator present: {self.att_present}")

        def test_integra_D(self):
            """ Test to validate the scale_min of STS command """

            self.port.get_status()
            scale = True

            while scale:
                self.port.send_command("*GCR")
                self.port.read_line()
                valeur_1 = self.port.reply.rstrip()[7:]
                print("Valuer_1", valeur_1)
                self.port.send_command("*SSD")
                self.port.send_command("*GCR")
                self.port.read_line()
                valeur_2 = self.port.reply.rstrip()[7:]
                print("Valeur_2:", valeur_2)

                if valeur_2 == valeur_1:
                    scale = False
                    self.assertEqual(int(valeur_1), self.port.scale_min)

        def show_validscale(self):
            """Show the valid scales"""

            self.send_command("*DVS")
            self.verbose = False
            finish = 0

            while finish != 1:
                self.read_line()
                if self.reply == "":
                    finish = 1
                else:
                    print(self.reply)

        def set_range(self, range):
            """Set the current scale
                range: index of the scale"""

            s = "{0:2d}".format(range)

            if len(s) == 2:
                print("Scale: OK")
            else:
                print("Scale: Wrong length")
                return

            self.verbose = True
            self.send_command("*SCS" + s)


    def main():
        """ Functions manager for user """

        integra = INTEGRA()
        if integra.quit == 1:
            return
        rep = ""
        while rep != "5":
            integra.verbose = True
            print("-"*30)
            rep = input("Menu:\n\n\
    1. Display detector/Monitor info\n\
    2. Change the wavelength\n\
    3. Change the range\n\
    4. Display measurement\n\
    5. Quit\n\n Your choice: ")
            print("-"*30)

            if rep == "1":
                integra.get_status()
                integra.print_status()

            elif rep == "2":
                pwc = input("Enter the desired wavelength: ")
                integra.set_pwc(int(pwc))

            elif rep == "3":
                integra.show_validscale()
                range = input("Enter the desired scale: ")
                integra.set_range(int(range))

            elif rep == "4":
                integra.verbose = False
                integra.sleepDelay = 0
                integra.restart()
                integra.send_command("*CAU")
                integra.read_line()
                print("Close window or enter \"Ctrl C\" to stop the measurement.")
                end = 0
                while not end:
                    try:
                        integra.get_data()
                        integra.update()
                    except (KeyboardInterrupt, IndexError):
                        end = 1

                integra.send_command("*CSU")
                integra.read_line()

            elif rep != "5":
                print("Choose a valid option (1 to 5).")

    if __name__ == "__main__":

        main()

### 5 - `emulation.py`

Le fichier emulation.py fournit deux éléments essentiels pour le fonctionnement du projet lorsque le matériel réel n’est pas disponible.  

Il contient :
  
- une émulation logicielle du powermeter (PMEmulation), qui génère des valeurs de puissance simulées afin de tester l’interface sans instrument Gentec  
  
- un wrapper unifié (IntegraPowerMeter) qui permet à l’application d’utiliser indifféremment le powermeter réel (INTEGRA) ou son équivalent simulé, via une API commune (measure(), zero(), get_wavelength())  
  
Ce module assure donc la compatibilité entre mode réel et mode simulation et simplifie considérablement le code de l’interface utilisateur.  

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

### 6 - `detect.py`

Le fichier detect.py est un script de test autonome permettant de vérifier la communication avec le powermeter INTEGRA en dehors de l’application principale.  
  
Il établit une connexion série, règle la longueur d’onde, envoie une commande de calibration et affiche la réponse renvoyée par l’appareil.  
  
Ce script n’est pas utilisé par l’interface NiceGUI : il sert uniquement au diagnostic, à la validation du port COM, et à confirmer que le driver Gentec fonctionne correctement sur la machine.  

    from integra import INTEGRA
    power = INTEGRA("COM3")
    power.set_pwc(int(633))
    power.send_command("*CAU")
    power.read_line()
    print(power.reply)

# Code GUI