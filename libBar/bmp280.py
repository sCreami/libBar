#!/usr/bin/python3
"""
The BMP280 is an absolute barometric pressure sensor especially designed for
mobile applications. The sensor module is housed in an extremely compact 8-pin
metal-lid LGA package with a footprint of only 2.0 × 2.5 mm2 and 0.95 mm
package height. Its small dimensions and its low power consumption of 2.7 μA
@1Hz allow the implementation in battery driven devices such as mobile phones,
GPS modules or watches.

Usage:
>>> import bmp280 as sensor
>>> mySensor = sensor.createContext()
>>> sensor.getTemperature(mySensor)
28
>>> sensor.purgeContext(mySensor)
"""
import os
import fcntl

# Power Modes Constants
cfg_PWRSLP = 0b00  # Sleep mode
cfg_PWRFOR = 0b01  # Forced mode
cfg_PWRNRM = 0b11  # Normal mode

# StandBy Time Constants
cfg_TSBhalf = 0b000  # 0.5ms
cfg_TSB62h = 0b001  # 62.5ms
cfg_TSB125 = 0b010  # 125ms
cfg_TSB250 = 0b011  # 250ms
cfg_TSB500 = 0b100  # 500ms
cfg_TSB1000 = 0b101  # 1000ms
cfg_TSB2000 = 0b110  # 2000ms
cfg_TSB4000 = 0b111  # 4000ms

# Over-Sampling Setting Constants
# -- pressure
cfg_OSSPSKP = 0b000  # Skipped (output set to 0x80000)
cfg_OSSP1 = 0b001  # oversampling x 1
cfg_OSSP2 = 0b010  # oversampling x 2
cfg_OSSP4 = 0b011  # oversampling x 4
cfg_OSSP8 = 0b100  # oversampling x 8
cfg_OSSP16 = 0b101  # oversampling x 16
# -- time
cfg_OSSTSKP = 0b000  # Skipped (output set to 0x80000)
cfg_OSST1 = 0b001  # oversampling x 1
cfg_OSST2 = 0b010  # oversampling x 2
cfg_OSST4 = 0b011  # oversampling x 4
cfg_OSST8 = 0b100  # oversampling x 8
cfg_OSST16 = 0b101  # oversampling x 16

# Filter Constants
cfg_FLTROFF = 0b000  # filter off
cfg_FLTR2 = 0b001  # filter coefficient 2
cfg_FLTR4 = 0b010  # filter coefficient 4
cfg_FLTR8 = 0b011  # filter coefficient 8
cfg_FLTR16 = 0b100  # filter coefficient 16

# Register Constants
reg_ID = 0xD0
reg_RESET = 0xE0
reg_STATUS = 0xF3
reg_CTRLMEAS = 0xF4
reg_CONFIG = 0xF5
# -- pressure value
reg_PRESS0 = 0xF7  # press_msb[7:0]
reg_PRESS1 = 0xF8  # press_lsb[7:0]
reg_PRESS2 = 0xF9  # press_xlsb[3:0]
# -- temperature value
reg_TEMP0 = 0xFA  # temp_msb[7:0]
reg_TEMP1 = 0xFB  # temp_lsb[7:0]
reg_TEMP2 = 0xFC  # temp_xlsb[3:0]


def createContext(vco=False):
    """
    Give a new module context, mandatory for every functions.
    Every parameters has a default value and can be re-assigned later.

    Keyword arguments:
    vco -- True if the vco pin is High state, False otherwise
    @return a new module context
    """
    ctx = {
        # i2c port module
        'port': 2,
        # module address
        'addr': 0x77 if vco else 0x76,
        # power mode
        'mode': cfg_PWRNRM,
        # oversampling pressure
        'prss': cfg_OSSPSKP,
        # oversampling temperature
        'temp': cfg_OSSTSKP,
        # standby time
        'sByT': cfg_TSB125,
        # filter coefficient
        'fltr': cfg_FLTR2,

        # DO NOT TOUCH THE PROPERTIES BELOW THIS LINE
        # carries a fine resolution temperature value
        # over to the pressure compensation formula
        't_fine': 0,
        # trimming values
        'trim': {
            'dig_T': None,
            'dig_P': None,
        },
        # File Descriptor for I2C
        'fd': None,
    }

    try:
        ctx['fd'] = os.open("/dev/i2c-{}".format(ctx['port']), os.O_RDWR)
        fcntl.ioctl(ctx['fd'], 0x0703, ctx['addr'])
    except Exception as e:
        print(e.value)
        raise e

    def _getTrim(LSB, MSB):
        return (rawGet(ctx, MSB) << 8) | rawGet(ctx, LSB)

    ctx['trim']['dig_T'] = [
        None, _getTrim(0x88, 0x89),
        _getTrim(0x8A, 0x8B), _getTrim(0x8C, 0x8D),
    ]

    ctx['trim']['dig_P'] = [
        None, _getTrim(0x8E, 0x8F),
        _getTrim(0x90, 0x91), _getTrim(0x92, 0x93),
        _getTrim(0x94, 0x95), _getTrim(0x96, 0x97),
        _getTrim(0x98, 0x99), _getTrim(0x9A, 0x9B),
        _getTrim(0x9C, 0x9D), _getTrim(0x9E, 0x9F),
    ]

    reset(ctx)
    # ctrl_measure register
    rawSet(ctx, False, (ctx['temp'] << 5) | (ctx['prss'] << 2) | ctx['mode'])
    # config register
    rawSet(ctx, True, (ctx['sByT'] << 5) | (ctx['fltr'] << 2) | 0)
    return ctx


def purgeContext(ctx):
    """
    Close the I2C stream as a well behaved script

    Keyword arguments:
    ctx -- the module context
    """
    os.close(ctx['fd'])


def getTemperature(ctx):
    """
    Get the compensated temperature

    Keyword arguments:
    ctx -- the module context
    @return the compensated temperature as a double
    """
    def _getTemp(ctx):
        _msb = rawGet(ctx, reg_TEMP0)
        _lsb = rawGet(ctx, reg_TEMP1)
        _xlsb = rawGet(ctx, reg_TEMP2)
        return (_msb << 12) | (_lsb << 4) | _xlsb

    adc_T = _getTemp(ctx)
    T = ctx['trim']['dig_T']

    var1 = (adc_T / 16384.0 - T[1] / 1024.0) * T[2]
    var2 = (adc_T / 131072.0 - T[1] / 8192.0) * \
           (adc_T / 131072.0 - T[1] / 8192.0) * T[3]
    ctx['t_fine'] = var1 + var2
    return ctx['t_fine'] / 5120.0


def getPressure(ctx):
    """
    Get the compensated pressure

    Keyword arguments:
    ctx -- the module context
    @return the compensated temperature as a double
    """
    def _getPress(ctx):
        _msb = rawGet(ctx, reg_PRESS0)
        _lsb = rawGet(ctx, reg_PRESS1)
        _xlsb = rawGet(ctx, reg_PRESS2)
        return (_msb << 12) | (_lsb << 4) | _xlsb

    adc_P = _getPress(ctx)
    P = ctx['trim']['dig_P']

    # the following code comes from the datasheet, it made me throw up too
    var1 = ctx['t_fine'] / 2.0 - 64000.0
    var2 = var1 * var1 * P[6] / 32768.0
    var2 = var2 + var1 * P[5] * 2.0
    var2 = (var2 / 4.0) + (P[4] * 65536.0)
    var1 = (P[3] * var1 * var1 / 524288.0 + P[2] * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * P[1]
    if var1 == 0.0:
        return 0  # avoid exception caused by division by zero
    p = 1048576.0 - adc_P
    p = (p - (var2 / 4096.0)) * 6250.0 / var1
    var1 = P[9] * p * p / 2147483648.0
    var2 = p * P[8] / 32768.0
    p = p + (var1 + var2 + P[7]) / 16.0
    return p


def getID(ctx):
    """
    Return the chip identification number, which is always 0x58 so this is
    useless but whatever.
    """
    return rawGet(ctx, reg_ID)


def setMode(ctx, val):
    """
    Set the power mode

    Keyword arguments:
    ctx -- the module context
    val -- the value to set
    See Power Modes Constants for possible value
    """
    try:
        _setConfig(ctx, 2, False,
                   (ctx['temp'] << 5) | (ctx['prss'] << 2) | val)
    except Exception as e:
        print(e)


def setOverSampPressure(ctx, val):
    """
    Set the over-sampling pressure coefficient

    Keyword arguments:
    ctx -- the module context
    val -- the value to set
    See Over-Sampling Pressure Constants for possible value
    """
    try:
        _setConfig(ctx, 3, False,
                   (ctx['temp'] << 5) | (val << 2) | ctx['mode'])
    except Exception as e:
        print(e)


def setOverSampTemperature(ctx, val):
    """
    Set the over-sampling temperature coefficient

    Keyword arguments:
    ctx -- the module context
    val -- the value to set
    See Over-Sampling Temperature Constants for possible value
    """
    try:
        _setConfig(ctx, 3, False,
                   (val << 5) | (ctx['prss'] << 2) | ctx['mode'])
    except Exception as e:
        print(e)


def setStandByTime(ctx, val):
    """
    Set the standby time value

    Keyword arguments:
    ctx -- the module context
    val -- the value to set
    See StandBy Time Constants for possible value
    """
    try:
        _setConfig(ctx, 3, True, (val << 5) | (ctx['fltr'] << 2) | 0)
    except Exception as e:
        print(e)


def setFilter(ctx, val):
    """
    Select the filter to apply

    Keyword arguments:
    ctx -- the module context
    val -- the value to set
    See Filter Constants for possible value
    """
    try:
        _setConfig(ctx, 3, True, (ctx['sByT'] << 5) | (val << 2) | 0)
    except Exception as e:
        print(e)


def _setConfig(ctx, bit, cfg, val):
    """
    Auxiliary function to ensure parameters

    Keyword arguments:
    ctx -- the module context
    bit -- the number of bits that can be written
    cfg -- the register in which the configuration must be saved
    val -- the full register value
    """
    lim = [
        [None], [None],
        [0b00, 0b11],
        [0b000, 0b111],
    ]

    if not (lim[bit][0] <= val <= lim[bit][1]):
        raise ValueError
    rawSet(ctx, reg_CONFIG if cfg else reg_CTRLMEAS, val)


def reset(ctx):
    """
    Apply a soft reset on the module, setting any other value than 0xB6 has no
    effect.

    Keyword arguments:
    ctx -- the module context
    """
    rawSet(ctx, reg_RESET, 0xB6)


def isMeasuring(ctx):
    """
    Inform if a conversion is running

    Keyword arguments:
    ctx -- the module context
    @return true if a conversion is running
    """
    _1 = rawGet(ctx, reg_STATUS)
    _2 = _1 & 0x8
    return bool(_2)


def isUpdating(ctx):
    """
    Inform if the module is copying data from the non volatire memory to the
    image registers

    Keyword arguments:
    ctx -- the module context
    @return true if the memory is being copied
    """
    _1 = rawGet(ctx, reg_STATUS)
    _2 = _1 & 0x1
    return bool(_2)


def rawSet(ctx, reg, val):
    """
    Allow direct access to set the module registers

    Keyword arguments:
    ctx -- the module context
    reg -- the register to access
    val -- the value to set in the register
    """
    try:
        os.write(ctx['fd'], bytes([reg, val]))
    except Exception as e:
        raise e


def rawGet(ctx, reg):
    """
    Allow direct access to retrieve the module registers

    Keyword arguments:
    ctx -- the module context
    reg -- the register to access
    @return what has been read on /dev/i2c-%
    """
    try:
        os.write(ctx['fd'], bytes([reg]))
        return os.read(ctx['fd'], 1)[0]
    except Exception as e:
        raise e
