## Code Controlleur moteur
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

```python
{% include "../../src/main.py" %}
```