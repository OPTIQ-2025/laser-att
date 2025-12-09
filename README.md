# Projet Atténuation Laser

Ce projet propose une application complète permettant de régler l’atténuation d’un faisceau laser en pilotant la rotation d’une lame demi-onde et en mesurant la puissance optique transmise.

L’application s’appuie sur trois modules principaux :

1. Motorisation

Pilotage d’un moteur Dynamixel pour orienter la lame demi-onde avec précision.
Le système convertit automatiquement les angles optiques souhaités (0–45°) en angles moteur et permet une utilisation en mode réel ou simulation.

    - Ilyas AIT IKKOU
    - Rémi CHATEAU
    - François TOSETTI
    - Noa TYMCZUK

2. Photodétection

Mesure de la puissance à l’aide d’un powermeter Gentec INTEGRA.
Le programme peut fonctionner en mode réel (communication série) ou via un powermeter simulé pour tester l’interface hors laboratoire.

    - Sokhna GUEYE
    - Fernanda CARBAJAL
    - Thivya KRISHNAKUMAR
    - Ibrahima LO

3. Interface utilisateur

Interface NiceGUI permettant :
- de visualiser la puissance mesurée en temps réel
- de contrôler la position de la lame (angle manuel ou préréglages)
- d’atteindre une puissance cible (calcul automatique de l’angle via la loi en cos²)
- de basculer entre modes réel / simulation

    - Amadou DIOP
    - Mar NIANG
    - Ali YAGHI

4. Documentation
Plus d'informations sur la documentation MkDocs

    - Ryan ACHIBET
    - Luca ASSENZA
    - Samuel CABOUBASSY DIT BATIA
    - Oussama BAKHADIR


Encadrant : Matthieu BELLEC