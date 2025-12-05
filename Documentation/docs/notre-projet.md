# Atténuateur Variable de Puissance Laser Automatisé

<!--
<p align="center">
    <img src="" width="300">
<p/>
-->

Ce projet vise à développer un atténuateur de puissance laser automatisé capable de contrôler précisément l’intensité d’un faisceau laser linéairement polarisé.
Le système repose sur une lame demi-onde motorisée, dont l’angle de rotation modifie la polarisation du faisceau, suivie d’un polariseur fixe assurant l’atténuation selon la loi de Malus. La puissance finale est mesurée par un photodiode reliée à un oscilloscope numérique, permettant une acquisition fiable et en temps réel.

L’objectif global est de créer un dispositif entièrement pilotable par ordinateur, intégrant :

- le [contrôle automatisé](scripts-python.md#code-controlleur-moteur) de la rotation de la [HWP (Half Waveplate)](materiel-et-librairies.md),

- la lecture continue de la [puissance optique](scripts-python.md#code-puissance-metre),

- une [interface graphique (GUI)](scripts-python.md#code-gui) facilitant l’[utilisation](interfaces-moteur-&-puissance-mètre.md) par tout opérateur.

Ce projet est structuré en plusieurs modules (interfaçage moteur, mesure optique, GUI, documentation), afin de fournir au final un système stable, reproductible et ergonomique permettant d’ajuster la puissance laser à distance avec précision.