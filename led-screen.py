import libBar.gpio as eIO

eIO.all()  # disable all leds
L3 = [45, 49, 117, 26, 69, 67, 47, 20]
L4 = [45, 49, 117, 69, 67, 60]
L5 = [45, 49, 117, 26, 69, 67, 47, 44]

L = [L3, L4, L5]
while True:
    eIO.all()
    for element in L:
        eIO.all()
        for child in element:
            eIO.writePin(child)
