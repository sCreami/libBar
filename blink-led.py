import libBar.gpio as eIO
import time

# led connectée sur la GPIO P9_42
while True:
    eIO.writePin(7, 1)
    time.sleep(.5)
    eIO.writePin(7, 0)
    time.sleep(.5)
