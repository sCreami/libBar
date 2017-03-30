"""
Exemple d'utilisation de la librairie BMP280
"""
import libBar.BMP280 as piezo

# Get a context from the module
ctx = piezo.createContext()

# Be forward and print the temperature
print(piezo.getTemperature(ctx))

# Adjust the sampling x4 for temperature
piezo.setOverSampTemperature(ctx, piezo.cfg_OSST4)

# Increase the standBy time to 4000ms
piezo.setStandByTime(ctx, piezo.cfg_TSB4000)

# Wait for the measure to be done before displaying
while piezo.isMeasuring(ctx):
    pass
print(piezo.getTemperature(ctx))

# Also why not look at the pressure ?
print(piezo.getPressure(ctx))

# We could also update the pressure oversampling
piezo.setOverSampPressure(ctx, piezo.cfg_OSSPSKP)

# Nah let put the module in sleep mode
piezo.setMode(ctx, piezo.cfg_PWRSLP)

# Don't forget to clean when you're done
piezo.purgeContext(ctx)

""" Look into BMP280.py for more """
