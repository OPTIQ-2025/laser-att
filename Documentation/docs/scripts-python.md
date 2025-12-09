## Code Controlleur moteur

La motorisation a pour rôle de contrôler l’orientation d’une lame demi-onde montée sur un moteur Dynamixel afin de régler l’atténuation du faisceau laser.  
En modifiant l’angle de la lame, on modifie la polarisation du faisceau, ce qui permet de faire varier la puissance transmise au détecteur.
  
Les objectifs principaux de cette partie sont :  
  
- permettre un déplacement précis de la lame à un angle choisi  
- garantir un mouvement fiable, reproductible et stable  
- fournir à l’interface une API simple (go_to_angle et get_position)  
- gérer les paramètres PID et la vitesse du moteur  
- convertir les angles demandés en angles moteur réels en tenant compte du rapport mécanique  
- assurer une compatibilité simulation / matériel réel pour que l’interface fonctionne dans tous les contextes  
  
La motorisation constitue donc le bras mécanique du projet : c’est elle qui applique physiquement l’atténuation demandée par l’utilisateur ou calculée automatiquement.  

Cette partie est entièrement codée dans le fichier `motor_half_lambda.py`  

Ce fichier contient une classe unique (MotorController) qui encapsule toutes les opérations nécessaires au pilotage du Dynamixel :  
  
- détection automatique du port série utilisé par le moteur  
- gestion de l’ouverture et fermeture du port  
- configuration des paramètres moteur (PID, vitesse)  
- conversion des angles entre la lame et le moteur (rapport ≈ 2.57:1)  
- déplacements contrôlés à un angle donné  
- lecture de la position réelle  
- protection contre les angles hors plage (0–45° sur la lame)  
- création d’une instance globale motor utilisée directement par l’interface  


```python
{% include "../../src/motor_half_lambda.py" %}
```


## Code Puissance-mètre

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

```python
{% include "../../src/port.py" %}
```

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

```python
{% include "../../src/status.py" %}
```

### 3 - `scope.py`  

`scope.py` scope.py fournit un petit oscilloscope logiciel basé sur matplotlib.  
  
Il permet :  
- d’enregistrer une série de mesures dans des buffers  
- de mettre à jour une courbe en temps réel  
- d’afficher un historique glissant des valeurs mesurées  

```python
{% include "../../src/scope.py" %}
```

### 4 - `integra.py`

`integra.py` est un fichier officiel Gentec-EO pour le powermeter INTEGRA.
  
Il gère :  
- la gestion complète du protocole Gentec  
- les commandes de contrôle (*PWC, LEV?, *STS, *CAU, ZRO, etc.)  
- la récupération et l’interprétation du statut  
- l’accès aux fonctions internes du détecteur (longueur d’onde, échelle, etc.)

```python
{% include "../../src/integra.py" %}
```

### 5 - `emulation.py`

Le fichier emulation.py fournit deux éléments essentiels pour le fonctionnement du projet lorsque le matériel réel n’est pas disponible.  

Il contient :
  
- une émulation logicielle du powermeter (PMEmulation), qui génère des valeurs de puissance simulées afin de tester l’interface sans instrument Gentec  
  
- un wrapper unifié (IntegraPowerMeter) qui permet à l’application d’utiliser indifféremment le powermeter réel (INTEGRA) ou son équivalent simulé, via une API commune (measure(), zero(), get_wavelength())  
  
Ce module assure donc la compatibilité entre mode réel et mode simulation et simplifie considérablement le code de l’interface utilisateur.  

```python
{% include "../../src/emulation.py" %}
```

### 6 - `detect.py`

Le fichier detect.py est un script de test autonome permettant de vérifier la communication avec le powermeter INTEGRA en dehors de l’application principale.  
  
Il établit une connexion série, règle la longueur d’onde, envoie une commande de calibration et affiche la réponse renvoyée par l’appareil.  
  
Ce script n’est pas utilisé par l’interface NiceGUI : il sert uniquement au diagnostic, à la validation du port COM, et à confirmer que le driver Gentec fonctionne correctement sur la machine.  

```python
{% include "../../src/detect.py" %}
```

## Code GUI

L’interface utilisateur a pour but de piloter le système de manière simple et intuitive, sans que l’utilisateur ait à manipuler directement les modules internes (moteur, powermeter, conversions, communication série, etc.).  

Elle permet :  
  
- de suivre en temps réel la puissance mesurée  
- de contrôler la position de la lame demi-onde  
- de définir une puissance cible (calcul automatique de l’angle)  
- de choisir entre les modes réel et simulation pour le moteur et le powermeter  
- de visualiser immédiatement les résultats (bargraph, aiguille, messages)  

Toute l’interface est gérée dans `main.py`    
Ce fichier contient :  
  
- l’initialisation de NiceGUI  
- la création de toutes les cartes et widgets (boutons, champs, bargraph, jauge)  
- le choix automatique entre mode réel et émulation pour le moteur et le powermeter  
- le rafraîchissement automatique de la puissance mesurée  
- les fonctions de contrôle appelées par les boutons (déplacement moteur, zero, connect, etc.)  
  
Le fichier main.py construit l’interface graphique NiceGUI et orchestre les interactions entre l’utilisateur et les modules internes.  
  
Fonctionnement de l'interface :  

1. Sélection du mode
L’utilisateur choisit si le moteur et le powermeter fonctionnent en mode réel ou en simulation.  
L’UI crée automatiquement le bon backend correspondant.  
  
2. Affichage et mise à jour de la puissance  
Un timer NiceGUI interroge régulièrement pm.measure() et met à jour :  
  
- la valeur numérique de puissance  
- la barre verticale d’intensité  
- la longueur d’onde affichée  

3. Contrôle du moteur  
Lorsqu’un angle est entré ou lorsqu’un préréglage est cliqué :  
- l’UI appelle `active_motor.go_to_angle(angle)`  
- lit la position réelle ou simulée via `get_position()`  
- met à jour l’indicateur circulaire et l’affichage numérique  

4. Mode puissance cible  
L’utilisateur peut entrer une puissance souhaitée.  
L’UI calcule automatiquement l’angle nécessaire via la loi en cos², puis `appelle active_motor.  go_to_angle()`

```python
{% include "../../src/main.py" %}
```