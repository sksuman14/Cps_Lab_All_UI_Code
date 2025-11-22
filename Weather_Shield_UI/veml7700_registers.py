# veml7700_registers.py
ID = 0x0C

# Register addresses
ALS_CONF = 0x00
ALS_WH = 0x01
ALS_WL = 0x02
P_SM = 0x03
ALS = 0x04
WHITE = 0x05
ALS_IF = 0x06

# Gain Settings
GAIN_2 = 0x0     # x2
GAIN_1 = 0x1     # x1
GAIN_1_8 = 0x2   # x1/8
GAIN_1_4 = 0x3   # x1/4

# Integration time settings
IT_25MS  = 0xC
IT_50MS  = 0x8
IT_100MS = 0x0
IT_200MS = 0x1
IT_400MS = 0x2
IT_800MS = 0x3

# Other configuration bit masks (bit positions)
ALS_SD = 0  # Shutdown
ALS_INT_EN = 1
ALS_SM = 12
ALS_IT = 6
