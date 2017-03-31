# Librairie de gestion du capteur de pression BMP280

### Réalisée par :
 - Julien Kessels
 - Valentin Lemenu
 - Alexis Nootens

### La librairie se trouve dans le dossier libBar/
### Le dossier parent fourni les 3 exemples de code suivant :

	( À l'aide de la librairie libBar.gpio )
	1/ blink-led.py fait clignoter une led connectée sur la GPIO P9_42
	2/ led-screen.py affiche une petite croix sur un petit écran led
	   dont les branches n'ont aucun sens.

	( À l'aide de la librairie libBar.BMP280 )
	3/ libBar-example.py montre l'utilisation de la librairie du capteur
	   de pression et température BMP280


## Explication et utilisation de l'écran LED

  Le HL-M1388BR est composé de 64 leds arrangées en 8 rangées et colonnes.
  Pour y afficher des figures, chiffres et autres, il faut utiliser le principe
  de multiplexage qui repose sur le principe d'allumer des leds rangée par rangée
  et balayer parmi ces rangées pour afficher le résultat final.

### Schéma d'origine du HL-M1388BR

  ![alt tag](https://github.com/julienkessels/libBar/blob/master/doc/res/schema.png)

### Circuit interne
  ![alt tag](https://github.com/julienkessels/libBar/blob/master/doc/res/circuit.png)

  A l'aide de ce circuit et des branchemenents aux pins GPIO, nous avons pu
  créer une correlation entre pins GPIO et les connections aux leds du HL-M1388BR,
  ici entourées et allant de 1 à 16.

### Tableau des correspondances

  Connection Led's  |     Pins GPIO
  ----------------- | -----------------
         1          |        60
         2          |        48
