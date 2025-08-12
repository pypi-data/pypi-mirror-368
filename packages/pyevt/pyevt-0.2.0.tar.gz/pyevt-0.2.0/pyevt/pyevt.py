# -*- coding:utf-8 -*-

import hid
import logging, sys # simple log methods: debug, info, warning, error and critical
from types import *
import time


class EventExchanger:
    """This class is to communicate with EVT02 devices."""

    def __init__(self):
        self.device = None
        # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logging.basicConfig(stream=sys.stderr, level=logging.CRITICAL)

    # DEVICE HANDLING ITEMS

    def scan(self, matching_key="EventExchanger"):
        """
        Scan for plugged in EVT-devices.

        Parameters:
            matchingkey (string): scans for the available EVT-devices containing
            the matching_key string. The default lists all EVT-devices found.
            
        Returns:
            List of dicts of found devices.
        """
        # Attempt to list all connected EventExchanger HID devices
        all_devices = hid.enumerate() # get list of dicts of each device 
        list_of_found_devices = [] # subset device list

        # Filter out the device by partial product name match
        for d in all_devices:
            if matching_key.lower() in d['product_string'].lower():
                logging.info(
                'Device found that partial matches the product name: %s s/n: %s',
                d['product_string'], d['serial_number'])
                #selected_devices.append(device_id)
                list_of_found_devices.append(d) # returns a list of dicts
            else:
                logging.info('Device found that not partial matches the product name')
        return list_of_found_devices

    def attach_name(self, matching_key="EventExchanger"):
        """
        Attach EVT-device on matching product name.

        Parameters:
            matchingkey (string): attaches the available EVT-device containing
            the matching_key string. The default is the first EVT device found.
            
        Returns:
        
        """
        # Attempt to list all connected HID devices
        all_devices = hid.enumerate()

        # Filter out the device by partial product name match
        for d in all_devices:
            if matching_key.lower() in d['product_string'].lower():
                try:
                    # Open the device
                    self.device = hid.device()
                    self.device.open_path(d['path'])
                    logging.info(
                    'Device name partially matches %s and has been attached successfully as: %s s/n: %s',
                    d['product_string'], d['serial_number'])
                    self.device.set_nonblocking(True)
                    return True
                except IOError as e:
                    logging.error('Failed to attach device!')
                    return False
        logging.info('Device found that not matches the partial product name')
        return False

    def attach_id(self, path):
        """
        Attach EVT-device on matching 'path' id which is unique.

        Parameters:
            Attaches the available EVT-device containing
            the 'path' binary, which is an unique ID.
            
        Returns:
        
        """
        # Attempt to list all connected HID devices
        all_devices = hid.enumerate()

        # Filter out the device by partial product name match
        for d in all_devices:
            if path in d['path']:
                try:
                    # Open the device
                    self.device = hid.device()
                    self.device.open_path(d['path'])
                    logging.info(
                    'Device attached successfully as: %s s/n: %s',
                    d['product_string'], d['serial_number'])
                    self.device.set_nonblocking(True)
                    return True
                except IOError as e:
                    logging.error('Failed to attach device!')
                    return False
        logging.warning('Device not found!')
        return False

    def close(self):
        """
        Close the currently attached EVT device.

        Parameters:
            None
            
        Returns:
        
        """
        if self.device:
            self.device.close()
            logging.info('Device successfully detached.')
            return True
        else:
            logging.warning('No device found to close.')
            return False
            
    def reset(self):
        """
        Reset EVT device. WARNING! Will disconnect the device from USB.

        Returns:
        
        """
        if self.device:
            self.device.write([0, self.__RESET, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.device.close()
            logging.info('Device successfully reset and detached.')
            return True
        else:
            logging.warning('No device attached.')
            return False

    # FUNCTIONAL ITEMS

    def wait_for_event(self, allowed_event_lines, timeout_ms):
        """
        Wait for incoming digital events based on polling.

        Parameters:
            allowed_event_lines: bit mask [0-255] to select the
            digital input lines.
            timeout_ms: timeout period in ms. Set to None for infinite.
            
        Returns:
        
        """
        if self.device is None:
            logging.warning('No device attached.')
            return None

        if allowed_event_lines is not None:
            bit_mask = int(allowed_event_lines)

        t_start = time.time()
        # flush the buffer!
        while (self.device.read(self.__RXBUFSIZE) != []):
            continue
        # Blocking loop. read() itself is non-blocking.
        while True:
            last_event = self.device.read(self.__RXBUFSIZE)
            t_elapsed = (time.time() - t_start) * 1000 # convert seconds to milliseconds
            if (last_event != []):
                if ((last_event[0] & bit_mask) > 0):
                    break
            # break for timeout:
            if timeout_ms is not None:
                if (t_elapsed >= int(timeout_ms)):
                    last_event = [-1]
                    # t_elapsted = timeout
                    break
        return last_event[0], round(t_elapsed)

    def get_axis(self):
        """
        GetAxis data.

        Parameters: None

        Returns:
        
        """
        if self.device is None:
            logging.warning('No device attached.')
            return None

        while (self.device.read(1) != []):
            pass
        time.sleep(.01)
        valueList = self.device.read(3)
        if (valueList == []):
            return self.__AxisValue
        self.__AxisValue = valueList[1] + (256*valueList[2])
        return self.__AxisValue

    # Single command device functions:
    
    def write_lines(self, value):
        """
        Set output lines.

        Parameters:
            value: bit pattern [0-255] to set the digital output lines.
            
        Returns:
        
        """
        if self.device:
            try:
                self.device.write(
                [0, self.__SETOUTPUTLINES, value, 0, 0, 0, 0, 0, 0, 0, 0])
                return True
            except IOError as e:
                logging.error('Error sending data!')
                return False        
        else:
            logging.warning('No device attached.')
            return False

    def pulse_lines(self, value, duration_ms):
        """
        Pulse output lines.

        Parameters:
            value: bit pattern [0-255] to pulse the 
            digital output lines.
            duration_ms: sets the duration of the pulse.

        Returns:
        
        """
        if self.device:
                    self.device.write(
                    [0, self.__PULSEOUTPUTLINES, value, duration_ms & 255,
                    duration_ms >> 8, 0, 0, 0, 0, 0, 0])
        else:
            logging.warning('No device attached.')
            return True

    def clear_lines(self):
        """
        Clear all output lines (set low).

        Parameters:
            None

        Returns:

        """
        if self.device:
            try:
                self.device.write(
                [0, self.__SETOUTPUTLINES, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                return True
            except IOError as e:
                logging.error('Error sending data!')
                return False
        else:
            logging.warning('No device attached.')
            return False

    def set_analog_event_step_size(self, no_samples_per_step):
        """
        Set analog event step size.

        Parameters:
            no_samples_per_step: set the number of samples per step.
            
        Returns:
        """
        if self.device:
            self.device.write(
            [0, self.__SETANALOGEVENTSTEPSIZE, no_samples_per_step,
            0, 0, 0, 0, 0, 0, 0, 0])
        else:
            logging.warning('No device attached.')
            return True

    def renc_init(self, encoder_range, min_value, position,
                   input_change, pulse_input_divider):
        """
        Rotary Encoder setup.

        Parameters:
            encoder_range:
            minumumValue:
            position:
            input_change:
            pulse_input_divider:

        Returns:

        """
        if self.device:
            self.__AxisValue = position
            self.device.write(
            [0, self.__SETUPROTARYCONTROLLER, encoder_range & 255,
            encoder_range >> 8, min_value & 255, min_value >> 8,
            position & 255, position >> 8,
            input_change, pulse_input_divider, 0])
            return True
        else:
            logging.warning('No device attached.')
            return False

    def renc_set_pos(self, position):
        """Rotary Encoder set position.

            Parameters:
                position: Set the current position.

        Returns:

        """
        if self.device:
            self.__AxisValue = position
            self.device.write(
            [0, self.__SETROTARYCONTROLLERposition, position & 255,
            position >> 8, 0, 0, 0, 0, 0, 0, 0])
            return True
        else:
            logging.warning('No device attached.')
            return False

    def set_led_rgb(self, red_value, green_value, blue_value,
                    led_number, mode):
        """Set LED color.

        Parameters:
            red_value:
            green_value:
            blue_value:
            led_number:
            mode:

        Returns:

        """
        if self.device:
            self.device.write(
            [0, self.__SETWS2811RGBLEDCOLOR, red_value, green_value,
            blue_value, led_number, mode, 0, 0, 0, 0])
            return True
        else:
            logging.warning('No device attached.')
            return False

    def send_led_rgb(self, number_of_leds, mode):
        """Set LED color.

        Parameters:
            red_value:
            green_value:
            blue_value:
            led_number:
            mode:

        Returns:

        """
        if self.device:
            self.device.write(
            [0, self.__SENDLEDCOLORS, number_of_leds, mode,
            0, 0, 0, 0, 0, 0, 0])
            return True
        else:
            logging.warning('No device attached.')
            return False

    __AxisValue = 0

    # CONSTANTS:
    __RXBUFSIZE = 1 # Receive buffer size=1

    __CLEAROUTPUTPORT = 0  # 0x00
    __SETOUTPUTPORT = 1  # 0x01
    __SETOUTPUTLINES = 2  # 0x02
    __SETOUTPUTLINE = 3  # 0x03
    __PULSEOUTPUTLINES = 4  # 0x04
    __PULSEOUTPUTLINE = 5  # 0x05

    __SENDLASTOUTPUTBYTE = 10  # 0x0A

    __CONVEYEVENT2OUTPUT = 20  # 0x14
    __CONVEYEVENT2OUTPUTEX = 21  # 0x15
    __CANCELCONVEYEVENT2OUTPUT = 22  # 0x16

    __CANCELEVENTREROUTES = 30  # 0x1E
    __REROUTEEVENTINPUT = 31  # 0x1F

    __SETUPROTARYCONTROLLER = 40  # 0x28
    __SETROTARYCONTROLLERposition = 41  # 0x29

    __CONFIGUREDEBOUNCE = 50  # 0x32

    __SETWS2811RGBLEDCOLOR = 60  # 0x3C
    __SENDLEDCOLORS = 61  # 0x3D

    __SWITCHALLLINESEVENTDETECTION = 100  # 0x64
    __SWITCHLINEEVENTDETECTION = 101  # 0x65

    __SETANALOGINPUTDETECTION = 102  # 0x66
    __REROUTEANALOGINPUT = 103  # 0X67
    __SETANALOGEVENTSTEPSIZE = 104  # 0X68

    __SWITCHDIAGNOSTICmode = 200  # 0xC8
    __SWITCHEVENTTEST = 201  # 0xC9

    __RESET = 255  # 0xFF

# -*- coding:utf-8 -*-
