# See link to for options that can be put in this list
# https://gitlab.com/cvejarano-oss/cmapy/-/blob/master/docs/colorize_all_examples.md
COLORMAP_LIST = ['jet','tab20b','gist_ncar','Set1','prism','tab20b_r','brg_r','bwr','seismic','coolwarm','PiYG_r','tab10','tab20','gnuplot2','brg']
DEFAULT_COLORMAP_INDEX = 0

# 0 - Nearest
# 1 - Inter Linear
# 2 - Inter Area
# 3 - Inter Cubic
# 4 - Inter Lanczos4
# 5 - Pure Scipy       - nice but slow - 3 fps
# 6 - Scipy/CV2 Mixed' - nice and fast - 4 fps
DEFAULT_INTERPOLATION_INDEX = 6

# Keyboard controll
CONTROL_COLORMAP_NEXT = "d"
CONTROL_COLORMAP_PREV = "a"
CONTROL_INTERPOLATION_NEXT = "w"
CONTROL_INTERPOLATION_PREV = "s"
CONTROL_FILTER_ENABLE_DISABLE = "f"
CONTROL_DISPLAY_INFO = "i"

# !!! DO NOT CHANGE FOLLOWING SETTINGS !!!

# Main monitor index
MONITOR_INDEX=0

# Display fps, color map name, interpolation algorithm by default
DISPLAY_INFO_BY_DEFAULT = False

# The speed grades, read more: https://www.i2c-bus.org/speed
# 100000 - standard mode: 100 kbit/s
# 400000 - full speed: 400 kbit/s
# Dont put more
I2C_FREQUENCY=400000

# If using higher refresh rates yields a 'too many retries' exception, try decreasing this value to work with certain pi/camera combinations
# 1 = REFRESH_1_HZ
# 2 = REFRESH_2_HZ
# 3 = REFRESH_4_HZ
# 4 = REFRESH_8_HZ
# 5(TOO MUCH) = REFRESH_16_HZ
# 6(TOO MUCH) = REFRESH_32_HZ
CAM_REFRESH_RATE=4
