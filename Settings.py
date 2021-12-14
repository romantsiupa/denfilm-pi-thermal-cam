import cv2
# See https://gitlab.com/cvejarano-oss/cmapy/-/blob/master/docs/colorize_all_examples.md to for options that can be put in this list
COLORMAP_LIST = ['jet','tab20b','gist_ncar','Set1','prism','tab20b_r','brg_r','bwr','seismic','coolwarm','PiYG_r','tab10','tab20','gnuplot2','brg']
DEFAULT_COLORMAP_INDEX = 0

# Next Color map
DISPLAY_INFO = True

# Interpolation
INTERPOLATION_LIST = [cv2.INTER_NEAREST,cv2.INTER_LINEAR,cv2.INTER_AREA,cv2.INTER_CUBIC,cv2.INTER_LANCZOS4,5,6]
INTERPOLATION_LIST_NAME = ['Nearest','Inter Linear','Inter Area','Inter Cubic','Inter Lanczos4','Pure Scipy','Scipy/CV2 Mixed']
DEFAULT_INTERPOLATION_INDEX = 5