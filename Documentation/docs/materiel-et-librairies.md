 # Materiel et Librairies
  
## Materiel
  
### Source laser :

- Laser HeNe : longueur d'onde à 633nm
 (Mettre scshéma d'un HeNe ?)

### Optiques utilisées :

- [Lame lambda/2](https://www.thorlabs.com/thorproduct.cfm?partnumber=WPH05M-633){: target = "_blank"}  
  
        - optimisé à 633nm  
        - 10.9mm de dimètre utile  
        - 25.4mm de dimètre total  
        - 5.8mm d'épaisseur
    
(image de la lame)  
  
- [PBS cube](https://www.thorlabs.com/thorproduct.cfm?partnumber=PBS251){: target = "_blank"}  
  
        - Optimisé pour des longueurs d'ondes entre 480-680nm  
        - Dimensions : 25.4 x 25.4 x 25.4mm  

(image du cube)    
  
### Éléments mécaniques et émectroniques :

- [Servomoteur pas à pas](https://emanual.robotis.com/docs/en/dxl/mx/mx-12w/){: target = "_blank"}  
    
        - Résolution angulaire : 0.088°  
        - Nombres de pas totaux : 4096  
  
(image du moteur)  
  
- [Alimentation du moteur](https://www.generationrobots.com/fr/400867-smps2dynamixel.html){: target = "_blank"}  
   
(image de l'alim)  

- [Contrôleur USB](https://emanual.robotis.com/docs/en/parts/interface/u2d2/){: target = "_blank"}  
  
(image du contrôleur USB)  

### Photodétection :

- [Photodiode](https://www.gentec-eo.com/fr/produits/ph100-si-ha-od1-d0){: target = "_blank"}  
  
        - Sensibilité à 633nm : 0.35A/W  
        - Surface de détection : ~0.8cm²  
        - Diamètre utile : 10mm  
  
(image de la photodiode)  
  
  
## Librairies utilisées

Voici la liste des librairies nécéssaires pour lancer le programme :  
  
- [nicegui](https://nicegui.io){: target = "_blank"} :  
  
        Permet de créer l’interface utilisateur web (UI) : boutons, sliders, cartes, graphiques, timers… Toute l'application graphique de main.py repose dessus.  
  
- [pyserial](https://pyserial.readthedocs.io/en/latest/pyserial.html){: target = "_blank"} :  
  
        Utilisée pour communiquer en port série avec le powermeter INTEGRA (Gentec-EO). C’est la base de PortSerial dans port.py.  
  
- [matplotlib](https://matplotlib.org){: target = "_blank"} :  
  
        Sert à tracer la courbe de puissance en temps réel dans scope.py lorsque le mode oscilloscope est utilisé.  
  
- [pypot](https://docs.poppy-project.org/en/software-libraries/pypot){: target = "_blank"} :  
  
        Permet de contrôler le moteur Dynamixel (position, vitesse, PID). C'est la librairie utilisée dans motor_half_lambda.py.  
  
- [time](https://docs.python.org/3/library/time.html){: target = "_blank"} :  

        Utilisé pour gérer les temporisations, pauses, timestamps dans tous les modules.  
  
- [math](https://docs.python.org/3/library/math.html){: target = "_blank"} :  
  
        Utilisé pour les calculs trigonométriques (ex. conversion angle ↔ puissance via loi en cos²).  
  
- [random](https://docs.python.org/3/library/random.html){: target = "_blank"} :  
  
        Sert dans emulation.py pour simuler une puissance de photodiode réaliste quand le powermeter n’est pas connecté.  

- [Plugins & extensions]

        pip install mkdocs-include-markdown-plugin
        pip install pymdown-extensions