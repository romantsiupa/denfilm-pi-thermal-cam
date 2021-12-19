import time,board,busio, traceback
import numpy as np
import adafruit_mlx90640
import datetime as dt
import cv2
import cmapy
from screeninfo import get_monitors
from scipy import ndimage
import pyautogui
import Settings

class pithermalcam:
    _colormap_list = Settings.COLORMAP_LIST
    _interpolation_list = [cv2.INTER_NEAREST,cv2.INTER_LINEAR,cv2.INTER_AREA,cv2.INTER_CUBIC,cv2.INTER_LANCZOS4,5,6]
    _interpolation_list_name = ['Nearest','Inter Linear','Inter Area','Inter Cubic','Inter Lanczos4','Pure Scipy','Scipy/CV2 Mixed']
    _current_frame_processed=False  # Tracks if the current processed image matches the current raw image
    i2c=None
    mlx=None
    _temp_min=None
    _temp_max=None
    _raw_image=None
    _image=None
    _displaying_onscreen=False
    _exit_requested=False

    def __init__(self, filter_image:bool = False, image_width:int=1200, image_height:int=900):
        self.filter_image=filter_image
        self.image_width=image_width
        self.image_height=image_height

        self._colormap_index = Settings.DEFAULT_COLORMAP_INDEX
        self._interpolation_index = Settings.DEFAULT_INTERPOLATION_INDEX
        self._setup_therm_cam()
        self._t0 = time.time()
        self.update_image_frame()

    def __del__(self):
        print("ThermalCam Object deleted.")

    """Initialize the thermal camera"""
    def _setup_therm_cam(self):
        # Setup camera
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=Settings.I2C_FREQUENCY)  # setup I2C
        self.mlx = adafruit_mlx90640.MLX90640(self.i2c)  # begin MLX90640 with I2C comm
        self.mlx.refresh_rate = Settings.CAM_REFRESH_RATE  # set refresh rate
        time.sleep(0.1)
    
    """Get mean temp of entire field of view. Return both temp C and temp F."""
    def get_mean_temp(self):
        frame = np.zeros((24*32,))  # setup array for storing all 768 temperatures
        while True:
            try:
                self.mlx.getFrame(frame)  # read MLX temperatures into frame var
                break
            except ValueError:
                continue  # if error, just read again

        return np.mean(frame)
    
    """Get one pull of the raw image data, converting temp units if necessary"""
    def _pull_raw_image(self):
        # Get image
        self._raw_image = np.zeros((24*32,))
        try:
            self.mlx.getFrame(self._raw_image)  # read mlx90640
            self._temp_min = np.min(self._raw_image)
            self._temp_max = np.max(self._raw_image)
            self._raw_image=self._temps_to_rescaled_uints(self._raw_image,self._temp_min,self._temp_max)
            self._current_frame_processed=False  # Note that the newly updated raw frame has not been processed
        except ValueError:
            print("Math error; continuing...")
            self._raw_image = np.zeros((24*32,))  # If something went wrong, make sure the raw image has numbers
        except OSError:
            print("IO Error; continuing...")
            self._raw_image = np.zeros((24*32,))  # If something went wrong, make sure the raw image has numbers
    
    """Process the raw temp data to a colored image. Filter if necessary"""
    def _process_raw_image(self):
        # Image processing
        # Can't apply colormap before ndimage, so reversed in first two options, even though it seems slower
        if self._interpolation_index==5:  # Scale via scipy only - slowest but seems higher quality
            self._image = ndimage.zoom(self._raw_image,25)  # interpolate with scipy
            self._image = cv2.applyColorMap(self._image, cmapy.cmap(self._colormap_list[self._colormap_index]))
            self._image = cv2.resize(self._image, (screensize[0],screensize[1]), interpolation=cv2.INTER_CUBIC)
        elif self._interpolation_index==6:  # Scale partially via scipy and partially via cv2 - mix of speed and quality
            self._image = ndimage.zoom(self._raw_image,10)  # interpolate with scipy
            self._image = cv2.applyColorMap(self._image, cmapy.cmap(self._colormap_list[self._colormap_index]))
            self._image = cv2.resize(self._image, (screensize[0],screensize[1]), interpolation=cv2.INTER_CUBIC)
        else:
            self._image = cv2.applyColorMap(self._raw_image, cmapy.cmap(self._colormap_list[self._colormap_index]))
            self._image = cv2.resize(self._image, (screensize[0],screensize[1]), interpolation=self._interpolation_list[self._interpolation_index])
        #self._image = cv2.flip(self._image, 1)
        if self.filter_image:
            self._image=cv2.bilateralFilter(self._image,15,80,80)
    
    """Set image text content"""
    def _add_image_text(self):
        if Settings.DISPLAY_INFO_BY_DEFAULT:
            text = f'Tmin={self._temp_min:+.1f}C - Tmax={self._temp_max:+.1f}C - FPS={1/(time.time() - self._t0):.1f} - Interpolation: {self._interpolation_list_name[self._interpolation_index]} - Colormap: {self._colormap_list[self._colormap_index]} - Filtered: {self.filter_image}'
            cv2.putText(self._image, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)
            self._t0 = time.time()  # Update time to this pull
    
    """Resize image window and display it""" 
    def _show_processed_image(self):             
        cv2.namedWindow('Thermal Image', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty ("Thermal Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
        cv2.imshow('Thermal Image', self._image)
        
    """Add keyboard actions to image"""
    def _set_click_keyboard_events(self):
        # Set keyboard events
        key = cv2.waitKey(1) & 0xFF

        if key == ord(Settings.CONTROL_COLORMAP_NEXT):
            self.change_colormap()
        elif key == ord(Settings.CONTROL_COLORMAP_PREV):
            self.change_colormap(forward=False)
        elif key == ord(Settings.CONTROL_INTERPOLATION_NEXT):  
            self.change_interpolation()
        elif key == ord(Settings.CONTROL_INTERPOLATION_PREV):
            self.change_interpolation(forward=False)
        elif key == ord(Settings.CONTROL_DISPLAY_INFO):
            Settings.DISPLAY_INFO_BY_DEFAULT = not Settings.DISPLAY_INFO_BY_DEFAULT
        elif key == ord(Settings.CONTROL_FILTER_ENABLE_DISABLE):
            self.filter_image = not self.filter_image
        elif key==27:
            cv2.destroyAllWindows()
            self._displaying_onscreen = False
            self._exit_requested=True
    
    """Print out a summary of the shortcut keys available during video runtime."""
    def _print_shortcuts_keys(self):
        print("Control keys:")
        print("Esc - Exit and Close.")
        print(Settings.CONTROL_COLORMAP_NEXT + " - Colormap Next")
        print(Settings.CONTROL_COLORMAP_PREV + " - Colormap Previous")
        print(Settings.CONTROL_INTERPOLATION_NEXT + " - Interpolation Next")
        print(Settings.CONTROL_INTERPOLATION_PREV + " - Interpolation Previous")
        print(Settings.CONTROL_FILTER_ENABLE_DISABLE + " - Toggle Filtering On/Off")
        print(Settings.CONTROL_DISPLAY_INFO + " - Display Info")
    
    """Display the camera live to the display"""
    def display_next_frame_onscreen(self):    
        # Display shortcuts reminder to user on first run
        if not self._displaying_onscreen:
            self._print_shortcuts_keys()
            self._displaying_onscreen = True
        self.update_image_frame()
        self._show_processed_image()
        self._set_click_keyboard_events()
    
    """Cycle colormap. Forward by default, backwards if param set to false."""
    def change_colormap(self, forward:bool = True):      
        if forward:
            self._colormap_index+=1
            if self._colormap_index==len(self._colormap_list):
                self._colormap_index=0
        else:
            self._colormap_index-=1
            if self._colormap_index<0:
                self._colormap_index=len(self._colormap_list)-1
    """Cycle interpolation. Forward by default, backwards if param set to false."""
    def change_interpolation(self, forward:bool = True):
        if forward:
            self._interpolation_index+=1
            if self._interpolation_index==len(self._interpolation_list):
                self._interpolation_index=0
        else:
            self._interpolation_index-=1
            if self._interpolation_index<0:
                self._interpolation_index=len(self._interpolation_list)-1
    
    """Pull raw temperature data, process it to an image, and update image text"""
    def update_image_frame(self):
        self._pull_raw_image()
        self._process_raw_image()
        self._add_image_text()
        self._current_frame_processed=True
        return self._image
    
    """Update only raw data without any further image processing or text updating"""
    def update_raw_image_only(self):
        self._pull_raw_image
    
    """Return the current raw image"""
    def get_current_raw_image_frame(self):
        self._pull_raw_image
        return self._raw_image
    
    """Get the processed image"""
    def get_current_image_frame(self):
        # If the current raw image hasn't been procssed, process and return it
        if not self._current_frame_processed:
            self._process_raw_image()
            self._add_image_text()
            self._current_frame_processed=True
        return self._image
    
    """Function to convert temperatures to pixels on image"""
    def _temps_to_rescaled_uints(self,f,Tmin,Tmax):
        f=np.nan_to_num(f)
        norm = np.uint8((f - Tmin)*255/(Tmax-Tmin))
        norm.shape = (24,32)
        return norm

    def display_camera_onscreen(self):
        # Loop to display frames unless/until user requests exit
        while not self._exit_requested:
            try:
                self.display_next_frame_onscreen()
            # Catch a common I2C Error. If you get this too often consider checking/adjusting your I2C Baudrate
            except RuntimeError as e:
                if e.message == 'Too many retries':
                    print("Too many retries error caught, potential I2C baudrate issue: continuing...")
                    continue
                raise

if __name__ == "__main__":
    # If class is run as main, read ini and set up a live feed displayed to screen
    monitor1 = get_monitors()[Settings.MONITOR_INDEX]
    screensize = monitor1.width, monitor1.height
    print(screensize[0])
    print(screensize[1])
    pyautogui.moveTo(screensize[0]-1, screensize[1]-1)
    thermcam = pithermalcam()  # Instantiate class
    thermcam.display_camera_onscreen()
