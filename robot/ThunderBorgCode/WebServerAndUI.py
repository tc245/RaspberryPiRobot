#!/usr/bin/env python3
# coding: Latin-1

# Creates a web-page interface for MonsterBorg

# Import library functions we need
import sys
sys.path.append('/home/pi/thunderborg')
import ThunderBorg3 as ThunderBorg
import time
import sys
import threading
import socketserver
import picamera
import picamera.array
import cv2
import datetime

# Settings for the web-page
webPort = 80                            # Port number for the web-page, 80 is what web-pages normally use
imageWidth = 240                        # Width of the captured image in pixels
imageHeight = 192                       # Height of the captured image in pixels
frameRate = 30                          # Number of images to capture per second
displayRate = 10                        # Number of images to request per second
photoDirectory = '/home/pi'             # Directory to save photos to
flippedCamera = True                    # Swap between True and False if the camera image is rotated by 180
jpegQuality = 80                        # JPEG quality level, smaller is faster, higher looks better (0 to 100)

# Global values
global TB
global lastFrame
global lockFrame
global camera
global processor
global running
global watchdog
running = True

TB = ThunderBorg.ThunderBorg()

TB.i2cAddress = 0x0a                  #Board address changed
TB.Init()
TB.SetCommsFailsafe(False)
TB.SetLedShowBattery(False)
TB.SetLeds(0,0,1)

# Power settings
voltageIn = 1.2 * 10                    # Total battery voltage to the ThunderBorg
voltageOut = 7                # Limit voltage to 7 volts (for devastator motors)

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Timeout thread
class Watchdog(threading.Thread):
    def __init__(self):
        super(Watchdog, self).__init__()
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.timestamp = time.time()

    def run(self):
        timedOut = True
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for a network event to be flagged for up to one second
            if timedOut:
                if self.event.wait(1):
                    # Connection
                    print("Reconnected...")
                    TB.SetLedShowBattery(True)
                    timedOut = False
                    self.event.clear()
            else:
                if self.event.wait(1):
                    self.event.clear()
                else:
                    # Timed out
                    print("Timed out...")
                    TB.SetLedShowBattery(False)
                    TB.SetLeds(0,0,1)
                    timedOut = True
                    TB.MotorsOff()

# Image stream processing thread
class StreamProcessor(threading.Thread):
    def __init__(self):
        super(StreamProcessor, self).__init__()
        self.stream = picamera.array.PiRGBArray(camera)
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.begin = 0

    def run(self):
        global lastFrame
        global lockFrame
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    # Read the image and save globally
                    self.stream.seek(0)
                    if flippedCamera:
                        flippedArray = cv2.flip(self.stream.array, -1) # Flips X and Y
                        retval, thisFrame = cv2.imencode('.jpg', flippedArray, [cv2.IMWRITE_JPEG_QUALITY, jpegQuality])
                        del flippedArray
                    else:
                        retval, thisFrame = cv2.imencode('.jpg', self.stream.array, [cv2.IMWRITE_JPEG_QUALITY, jpegQuality])
                    lockFrame.acquire()
                    lastFrame = thisFrame
                    lockFrame.release()
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()

# Image capture thread
class ImageCapture(threading.Thread):
    def __init__(self):
        super(ImageCapture, self).__init__()
        self.start()

    def run(self):
        global camera
        global processor
        print("Start the stream using the video port")
        camera.capture_sequence(self.TriggerStream(), format='bgr', use_video_port=True)
        print("Terminating camera processing...")
        processor.terminated = True
        processor.join()
        print("Processing terminated.")

    # Stream delegation loop
    def TriggerStream(self):
        global running
        while running:
            if processor.event.is_set():
                time.sleep(0.01)
            else:
                yield processor.stream
                processor.event.set()

# Class used to implement the web server
class WebServer(socketserver.BaseRequestHandler):
    def handle(self):
        global TB
        global lastFrame
        global watchdog
        # Get the HTTP request data
        reqData = self.request.recv(1024)
        reqData = str(reqData)
        print(reqData)
        reqData = reqData.split('')
        # Get the URL requested
        getPath = ''
        for line in reqData:
            if line.startswith('GET'):
                parts = line.split(' ')
                getPath = parts[1]
                break
        watchdog.event.set()
        if getPath.startswith('/cam.jpg'):
            # Camera snapshot
            lockFrame.acquire()
            sendFrame = lastFrame
            lockFrame.release()
            if sendFrame != None:
                self.send(sendFrame.tostring())
        elif getPath.startswith('/off'):
            # Turn the drives off
            httpText = '<html><body><center>'
            httpText += 'Speeds: 0 %, 0 %'
            httpText += '</center></body></html>'
            self.send(httpText.encode())
            TB.MotorsOff()
        elif getPath.startswith('/set/'):
            # Motor power setting: /set/driveLeft/driveRight
            parts = getPath.split('/')
            # Get the power levels
            if len(parts) >= 4:
                try:
                    driveLeft = float(parts[2])
                    driveRight = float(parts[3])
                except:
                    # Bad values
                    driveRight = 0.0
                    driveLeft = 0.0
            else:
                # Bad request
                driveRight = 0.0
                driveLeft = 0.0
            # Ensure settings are within limits
            if driveRight < -1:
                driveRight = -1
            elif driveRight > 1:
                driveRight = 1
            if driveLeft < -1:
                driveLeft = -1
            elif driveLeft > 1:
                driveLeft = 1
            # Report the current settings
            percentLeft = driveLeft * 100.0;
            percentRight = driveRight * 100.0;
            httpText = '<html><body><center>'
            httpText += 'Speeds: {}, {}'.format(percentLeft, percentRight)
            httpText += '</center></body></html>'
            self.send(httpText.encode())
            # Set the outputs
            driveLeft *= maxPower
            driveRight *= maxPower
            TB.SetMotor1(driveRight)
            TB.SetMotor2(driveLeft)
        elif getPath.startswith('/photo'):
            # Save camera photo
            lockFrame.acquire()
            captureFrame = lastFrame
            lockFrame.release()
            httpText = '<html><body><center>'
            if captureFrame != None:
                photoName = "{}/Photo {}.jpg".format(photoDirectory, datetime.datetime.utcnow())
                try:
                    photoFile = open(photoName, 'wb')
                    photoFile.write(captureFrame)
                    photoFile.close()
                    httpText += "Photo saved to {}".format(photoName)
                except:
                    httpText += 'Failed to take photo!'
            else:
                httpText += 'Failed to take photo!'
            httpText += '</center></body></html>'
            self.send(httpText.encode())
        elif getPath == '/':
            # Main page, click buttons to move and to stop
            httpText = '<html>'
            httpText += '<head>'
            httpText += '<script language="JavaScript"><!--'
            httpText += 'function Drive(left, right) {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' var slider = document.getElementById("speed");'
            httpText += ' left *= speed.value / 100.0;'
            httpText += ' right *= speed.value / 100.0;'
            httpText += ' iframe.src = "/set/" + left + "/" + right;'
            httpText += '}'
            httpText += 'function Off() {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' iframe.src = "/off";'
            httpText += '}'
            httpText += 'function Photo() {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' iframe.src = "/photo";'
            httpText += '}'
            httpText += '//--></script>'
            httpText += '</head>'
            httpText += '<body>'
            httpText += '<iframe src="/stream" width="100%" height="500" frameborder="0"></iframe>'
            httpText += '<iframe id="setDrive" src="/off" width="100%" height="50" frameborder="0"></iframe>'
            httpText += '<center>'
            httpText += '<button onclick="Drive(-1,1)" style="width:200px;height:100px;"><b>Spin Left</b></button>'
            httpText += '<button onclick="Drive(1,1)" style="width:200px;height:100px;"><b>Forward</b></button>'
            httpText += '<button onclick="Drive(1,-1)" style="width:200px;height:100px;"><b>Spin Right</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onclick="Drive(0,1)" style="width:200px;height:100px;"><b>Turn Left</b></button>'
            httpText += '<button onclick="Drive(-1,-1)" style="width:200px;height:100px;"><b>Reverse</b></button>'
            httpText += '<button onclick="Drive(1,0)" style="width:200px;height:100px;"><b>Turn Right</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onclick="Off()" style="width:200px;height:100px;"><b>Stop</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onclick="Photo()" style="width:200px;height:100px;"><b>Save Photo</b></button>'
            httpText += '<br /><br />'
            httpText += '<input id="speed" type="range" min="0" max="100" value="100" style="width:600px" />'
            httpText += '</center>'
            httpText += '</body>'
            httpText += '</html>'
            self.send(httpText.encode())
        elif getPath == '/hold':
            # Alternate page, hold buttons to move (does not work with all devices)
            httpText = '<html>'
            httpText += '<head>'
            httpText += '<script language="JavaScript"><!--'
            httpText += 'function Drive(left, right) {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' var slider = document.getElementById("speed");'
            httpText += ' left *= speed.value / 100.0;'
            httpText += ' right *= speed.value / 100.0;'
            httpText += ' iframe.src = "/set/" + left + "/" + right;'
            httpText += '}'
            httpText += 'function Off() {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' iframe.src = "/off";'
            httpText += '}'
            httpText += 'function Photo() {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' iframe.src = "/photo";'
            httpText += '}'
            httpText += '//--></script>'
            httpText += '</head>'
            httpText += '<body>'
            httpText += '<iframe src="/stream" width="100%" height="500" frameborder="0"></iframe>'
            httpText += '<iframe id="setDrive" src="/off" width="100%" height="50" frameborder="0"></iframe>'
            httpText += '<center>'
            httpText += '<button onmousedown="Drive(-1,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Spin Left</b></button>'
            httpText += '<button onmousedown="Drive(1,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Forward</b></button>'
            httpText += '<button onmousedown="Drive(1,-1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Spin Right</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onmousedown="Drive(0,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Turn Left</b></button>'
            httpText += '<button onmousedown="Drive(-1,-1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Reverse</b></button>'
            httpText += '<button onmousedown="Drive(1,0)" onmouseup="Off()" style="width:200px;height:100px;"><b>Turn Right</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onclick="Photo()" style="width:200px;height:100px;"><b>Save Photo</b></button>'
            httpText += '<br /><br />'
            httpText += '<input id="speed" type="range" min="0" max="100" value="100" style="width:600px" />'
            httpText += '</center>'
            httpText += '</body>'
            httpText += '</html>'
            self.send(httpText.encode())
        elif getPath == '/stream':
            # Streaming frame, set a delayed refresh
            displayDelay = int(1000 / displayRate)
            httpText = '<html>'
            httpText += '<head>'
            httpText += '<script language="JavaScript"><!--'
            httpText += 'function refreshImage() {'
            httpText += ' if (!document.images) return;'
            httpText += ' document.images["rpicam"].src = "cam.jpg?" + Math.random();'
            httpText += ' setTimeout("refreshImage()", {});'.format(displayDelay)
            httpText += '}'
            httpText += '//--></script>'
            httpText += '</head>'
            httpText += '<body onLoad="setTimeout(\'refreshImage()\', {})">'.format(displayDelay)
            httpText += '<center><img src="/cam.jpg" style="width:600;height:480;" name="rpicam" /></center>'
            httpText += '</body>'
            httpText += '</html>'
            self.send(httpText.encode())
        else:
            # Unexpected page
            self.send('Path : "{}"'.format(getPath).encode())

    def send(self, content):
        self.request.sendall('HTTP/1.0 200 OK {}'.format(content).encode())


# Create the image buffer frame
lastFrame = None
lockFrame = threading.Lock()

# Startup sequence
print("Setup camera")
camera = picamera.PiCamera()
camera.resolution = (imageWidth, imageHeight)
camera.framerate = frameRate

print("Setup the stream processing thread")
processor = StreamProcessor()

print("Wait ...")
time.sleep(2)
captureThread = ImageCapture()

print("Setup the watchdog")
watchdog = Watchdog()

# Run the web server until we are told to close
try:
    httpServer = None
    httpServer = socketserver.TCPServer(("0.0.0.0", webPort), WebServer)
except:
    # Failed to open the port, report common issues
    print
    print("Failed to open port {}".format(webPort))
    print("Make sure you are running the script with sudo permissions")
    print("Other problems include running another script with the same port")
    print("If the script was just working recently try waiting a minute first")
    # Flag the script to exit
    running = False
try:
    print("Press CTRL+C to terminate the web-server")
    while running:
        httpServer.handle_request()
except KeyboardInterrupt:
    # CTRL+C exit
    print("User shutdown")
finally:
    # Turn the motors off under all scenarios
    TB.MotorsOff()
    print("Motors off")
# Tell each thread to stop, and wait for them to end
if httpServer != None:
    httpServer.server_close()
running = False
captureThread.join()
processor.terminated = True
watchdog.terminated = True
processor.join()
watchdog.join()
del camera
TB.SetLedShowBattery(False)
TB.SetLeds(0,0,0)
TB.MotorsOff()
print("Web-server terminated.")
