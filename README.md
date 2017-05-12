## Synopsis

This is a simple use case example of a device with sensitive data being isolated from insecure network exposure trough an output only channel. The use case is based in a Fall Detection application by video camera. The video streaming  is processed in a Raspberry Pi, which sends a single bit data through its GPIO pin to an Arduino Yun GPIO pin. The Arduino Yun run as an Access Point and the pin state are accessed trough a RESTfull web service.

The example is composed by:

- The example is composed of a python code to run in a Raspberry Pi with the Pi a cam. The alarm is sent by the Pi's GPIO 20 to Arduino's GPIO 3.
- An Arduino Yun code is based on the Bridge sample code.
- The java app is a JavaFX desktop application that requests the pin 3 state from the Arduino Yun.     

## Motivation

The main goal for this project is to be a starting point of more complex analyzes of Privacy-by-Design architectures.

## Installation

The Raspberry Pi and Arduino Yun applications are dependent on specific hardware configuration.
For the Raspberry Pi uses the Pi cam Python module with OpenCV.

For installing OpenCV in Raspberry Pi there is a really good tutorial [here](http://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/).

The Arduino code was design to run only in Arduinos Yun hardware since it depends on OpenWRT subsystem calls for the RESTful web service. The code is based in the Bridge example already offered in Arduino IDE with a modification to avoid the use of the UART pins that may damage the Raspberry Pi.  

## Tests

There are no tests developed for this application due to its simplicity so far.



