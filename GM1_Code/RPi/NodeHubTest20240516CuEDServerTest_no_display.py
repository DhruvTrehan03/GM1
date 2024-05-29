# GSL 20230420 Added rainbow effect for RGB LED
import machine
#import utime
import time
import machine
#import ustruct
import sys
import struct # for some of the commented out tests
import os
import qrcode

data = []
############################################################################################################################
## Definitions and helper functions
############################################################################################################################


# Reference implementation tests - prepend the 'False' woth '#' to enable

# Wait until SoftSilicon responds (returns version) before continuing with anything
waitForStartup = True
#waitForStartup = False

# RGB 'rainbow' colour cycle.
# For SoftSilicon without an RGB LED, other LEDs are used or the RGB value is converted to ITU BT.601 luminance

rgbLedCycle = True
rgbLedCycle = False

# Send startup commands to interrogate the node (version number, time and time status, connectivity status, hubs available, etc)
startUpFlow = True
#startUpFlow = False

# Send a short message
sendShortMessage = True
#sendShortMessage = False

# Do a sustained transfer
#sendSustainedTransfer = True
sendSustainedTransfer = False

# Make filename '' to transfer a fixed test pattern instead of an onboard file
# Use the Thonny 'View files' mechanism (for example) to upload files to the Pico
            
sustainedXferFilename = 'PP_EGMRaw_653968E2_00.bin'
#sustainedXferFilename = ''

# Send a legacy message
sendLegacyMessage = True
sendLegacyMessage = False

# Message check loop
# If enabled, remain in a message check loop, retrieving and printing the messages it receives to the console
# THe loop also reports on connectivity changes, and for nodes, changes in the amount of hubs available to the node
messageCheckLoop = True
#messageCheckLoop = False


# Repeat the selected tests again (stop otherwise)
repeatTests = True
repeatTests = False


IS_PICO_EXPLORER = 0 # Set 0 for Pico Decker with Pico Display 2.0, 1 for Pico Explorer

HAS_PICO_EXPLORER_DISPLAY = 0
HAS_PICO_DISPLAY_2 = 1
WIDTH = 240
HEIGHT = 320
L2S2_SPI_BUS = 0


if IS_PICO_EXPLORER:
    HAS_PICO_EXPLORER_DISPLAY = 1
    WIDTH = 240
    HEIGHT = 240
    HAS_PICO_DISPLAY_2 = 0
    L2S2_SPI_BUS = 0


from pimoroni import Button
if HAS_PICO_EXPLORER_DISPLAY:
    from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER, PEN_P4
if HAS_PICO_DISPLAY_2:
    from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4
    from pimoroni import RGBLED

from pimoroni_bus import SPIBus

L2S2_TIMEOUT = 10





verbose = 1
quiet = 0


def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.set_pen(WHITE)
    display.rectangle(ox, oy, size, size)
    display.set_pen(BLACK)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)




def setDisplaySPI():
    global display
    # We're only using a few colours so we can use a 4 bit/16 colour palette and save RAM
    #if HAS_PICO_EXPLORER_DISPLAY:
        #display = PicoGraphics(display=DISPLAY_PICO_EXPLORER, pen_type=PEN_P4)
    #if HAS_PICO_DISPLAY_2:
        #display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_P4, rotate = 270)
    #print("Display SPI")
    #print(machine.SPI(0))

def setL2S2SPI():
    global spi1
    # Note TTP had CPHA set to 1
    if L2S2_SPI_BUS == 0:
        spi1 = machine.SPI(0,
                      baudrate=100000,
                      polarity=0,
                      phase=0,
                      bits=8,
                      firstbit=machine.SPI.MSB,
                      sck=machine.Pin(18),
                      mosi=machine.Pin(19),
                      miso=machine.Pin(16))
        #print("L2S2 SPI")
        #print(machine.SPI(0))
    if L2S2_SPI_BUS == 1:
        spi1 = machine.SPI(1,
                      baudrate=100000,
                      polarity=0,
                      phase=0,
                      bits=8,
                      firstbit=machine.SPI.MSB,
                      sck=machine.Pin(10),
                      mosi=machine.Pin(11),
                      miso=machine.Pin(12))
        #print("L2S2 SPI")
        #print(machine.SPI(1))


def myTimeNow():
    # return ""
    tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec, tm_foo, tm_bar = time.gmtime()
    return '{:02}:{:02}:{:02}'.format(tm_hour, tm_min, tm_sec)

def CCITT_crc16_false(data: bytes, start, length): # ignoring start and length for now as it wasn't used
    table = [ 
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7, 0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
        0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6, 0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
        0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485, 0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4, 0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
        0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823, 0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
        0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12, 0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
        0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41, 0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
        0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70, 0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
        0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F, 0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E, 0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
        0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D, 0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
        0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C, 0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB, 0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
        0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A, 0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
        0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9, 0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
        0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8, 0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
    ]
    
    crc = 0xFFFF
    for byte in data:
        crc = (crc << 8) ^ table[(crc >> 8) ^ byte]
        crc &= 0xFFFF
    return crc



    
def spiToL2S2(header, payload, verbose):
    #global display
    global spi1
    hdr = bytearray(header.to_bytes(1,'little'))
    length = bytearray(len(payload).to_bytes(2,'little'))
    
    if len(payload) > 512:
        print("Payload ("+str(len(payload))+" bytes) is too long. Maximum payload size is 512 bytes")
        return b'\x00', b'\x00'
        
    crc = CCITT_crc16_false(hdr + length + payload, 0, int(len(hdr + length + payload)))
    crcarray = bytearray(crc.to_bytes(2,'little'))
    packetToSend = hdr + length + crcarray + payload
    if verbose: #len(packetToSend) < 30:
        print(myTimeNow(),"Sending ", " ".join('{:02X}'.format(x) for x in packetToSend))
    
    '''
    if verbose:
        display.set_pen(GREEN)
        if HAS_PICO_DISPLAY_2:
            led.set_rgb(255, 255, 255)
    
    
            display.text("Sending packet...", 0, 48, 240, 2)
            display.set_pen(MAGENTA)
            display.text(" ".join('{:02X}'.format(x) for x in packetToSend), 0, 64, 240, 1)
            display.update()
    '''
    
    # We have to reset the SPI bus if sharing (as with Pico Explorer)
    if IS_PICO_EXPLORER:
        setL2S2SPI()
    
    spi1cs.value(0)
    spi1.write(packetToSend)
    spi1cs.value(1)
    time.sleep_ms(10) # MicroPython 1.21.0 seems to be hanging here sometimes (line 540 in <module>)
    spi1cs.value(0)
    replyHeader = b'\x00'
    startTime = time.ticks_ms()
    while (replyHeader == b'\x00' and time.ticks_diff(time.ticks_ms(), startTime)<(L2S2_TIMEOUT*1000)):
        spi1cs.value(0) # GSL
        replyHeader = spi1.read(1)
        time.sleep_ms(100)
        if replyHeader == b'\x00':
            spi1cs.value(1) # GSL
    
    '''
    if verbose:
        if HAS_PICO_DISPLAY_2:
            led.set_rgb(0, 0, 255)
    '''
    replyLength = spi1.read(2)
    replyCRC = spi1.read(2)
    replyLengthVal = int.from_bytes(replyLength, 'little')
    if replyLengthVal > 0x400:
        replyLengthVal = 0x400 # truncate bad reply lengths
    replyPayload = spi1.read(replyLengthVal)
    spi1cs.value(1)
    
    # Have to re-set the SPI display if sharing the bus (as with Pico Explorer)
    if IS_PICO_EXPLORER:
        setDisplaySPI()
    
    crc = CCITT_crc16_false(replyHeader + replyLength + replyPayload, 0, int(len(replyHeader + replyLength + replyPayload)))
    '''
    print(myTimeNow(),"Reply Header ", " ".join('{:02X}'.format(x) for x in replyHeader))
    print(myTimeNow(),"Reply Length ", " ".join('{:02X}'.format(x) for x in replyLength))
    print(myTimeNow(),"Reply CRC ", " ".join('{:02X}'.format(x) for x in replyCRC))
    print(myTimeNow(),"Reply Payload ", " ".join('{:02X}'.format(x) for x in replyPayload))
    print(myTimeNow(),"Calculated CRC ", " ".join('{:02X}'.format(x) for x in crc.to_bytes(2,'little')))
    '''
    
    if crc.to_bytes(2,'little') == replyCRC :
        if verbose:
            '''
            if HAS_PICO_DISPLAY_2:
                led.set_rgb(0, 255, 0)
            '''
            print(myTimeNow(),"Received: Header ", " ".join('{:02X}'.format(x) for x in replyHeader), "Payload ", " ".join('{:02X}'.format(x) for x in replyPayload))
        return replyHeader, replyPayload
    else:
        if HAS_PICO_DISPLAY_2:
            led.set_rgb(255, 0, 0)
        print(myTimeNow(),"Timeout or CRC error")
        #display.set_pen(RED)
        #display.text("Timeout or CRC error", 0, 200, 240, 2)
        #display.update()
        time.sleep(1)
        return b'\x00', b'\x00'
    

# sets up a handy function we can call to clear the screen
def clear():
    display.set_pen(BLACK)
    display.clear()
    display.update()
    
## Takes _record_id, plate_id, _control_id as strings; _type as number 1:5; content of different types; _units as string;
## Datatypes: 1 = bool; 2 = int; 3 = double; 4 = datetime; 5 = string
def legacy_data_send(_record_id, _plate_id, _control_id, _type, _content, _units):
    # Payload_diode init
    # payload_diode = bytearray([0x00, 0x00, 0xFF, 0x00]) #red = (0, 0, 255)

    # Diode on
    # spiToL2S2(99, payload_diode, verbose)

    # Creation of the field id as bytearray
    _field_id = _record_id + '|' + _plate_id + '|' + _control_id + '\0' # string terminator (see the MMDC doc)
    _field_id_b = bytearray(_field_id.encode("utf-8"))

    # Creation of the datatype of content as byte:
    _type_b = bytearray(1)
    _type_b[0]=_type

    # Creation of the content as bytearray (here content is an int) 
    # Need to make if options for different datatypes
    if (_type == 1):
        _content_b = bytearray([0x00])
        _content_b[0] = _content
    elif (_type == 2):
        _content_b = _content.to_bytes(4,'little')
    elif (_type == 3):
        _content_b = bytearray(struct.pack("d", _content))  
        print(_content_b)
    elif (_type == 4):
        _content_b = _content.to_bytes(8,'little') # seconds since 1st Jan 1970, held as a long (64-bit C type time_t)
        print(_content_b)
    elif (_type == 5):
        _content_b = bytearray((_content + '\0').encode("utf-8"))


    # Creation of the unit name as bytearray
    _units_b = bytearray(_units.encode("utf-8"))

    # Concatenation of the payload bytearray
    _payload=_field_id_b + _type_b + _content_b + _units_b

    # Sending of the payload to the server
    spiToL2S2(150, _payload, verbose)

    # Payload_diode off
    # payload_diode = bytearray([0x00, 0x00, 0x00, 0x00]) #off = (0, 0, 0)

    # Diode off
    # spiToL2S2(99, payload_diode, verbose)


# sustainedData is either a filename, or a byte array
def doSustainedTransfer(sustainedData):
    #'''            
    fh = 0
    filename = ''
    
    if type(sustainedData) == str:
        print("Sustained transfer is a file: "+sustainedData)
        filename = sustainedData


    if filename != '':
        sustainedXferLength = os.stat(filename)[6]
        print("Sustained transfer from file '"+filename+"', file size is "+str(sustainedXferLength))
        fh = open(filename, 'rb')
    else:
        #sustainedXferLength = 0x8000
        sustainedXferLength = len(sustainedData)
            
    # sectorSize = 480 # we read the sector size from the node
    sustainedXferId = 0x1234
    sustainedXferDestination = 0x0000001
    sustainedXferType = 0x0001
            
    bytesRemaining = sustainedXferLength
    xferAborted = False
    controlWord = 0
    startedTransfer = False

    print("Sending sustained transfer request...")
    while startedTransfer == False:
        sustainedXferRequest = bytearray( sustainedXferId.to_bytes(2, 'little') +
                                    sustainedXferDestination.to_bytes(4, 'little') +
                                    sustainedXferType.to_bytes(2, 'little') +
                                    sustainedXferLength.to_bytes(4, 'little'))
        spiToL2S2(170, sustainedXferRequest, verbose ) # Sustained Transfer Request

        bytesRemaining = sustainedXferLength
            
        replyHeader, replyPayload = spiToL2S2(171, bytearray(sustainedXferId.to_bytes(2, 'little') + controlWord.to_bytes(2, 'little') ), quiet ) # Sustained Transfer Status/Control message
        # print(replyHeader + " " + replyPayload)
        # Wait for the first ready after setting up the sustained transfer. This could be part of the main loop waiting to transfer each sector,
        # but we'll separate this first one for the purposes of a reference implementation (IE not hard optimised)
        # wait for 171 Sustained Transfer Status/Control message (we could be receiving Ack/No Message while the transfer is being arranged)
        # or am ACK/GENERAL ERROR which indicated something went wrong, in which case we'll try the sustained transfer request again
        print("Waiting for sustained transfer to initiate", end='')
        while replyHeader != b'\xAB' and not (replyHeader == b'\xc7' and replyPayload[0] == 255) :
            time.sleep(0.1)
            print(".", end='')
            replyHeader, replyPayload = spiToL2S2(171, bytearray(sustainedXferId.to_bytes(2, 'little') + controlWord.to_bytes(2, 'little') ), quiet ) # Sustained Transfer Status/Control message
        if replyHeader == b'\xAB':
            startedTransfer = True  # We got a control response
        else:
            startedTransfer = False # We got an ACK/GENERAL ERROR
            print("ACK/GENERAL ERROR received, restarting sustained transfer request")
            

    xferStatus = int.from_bytes(bytearray([replyPayload[0], replyPayload[1]]), 'little')
    sectorSize = int.from_bytes(bytearray([replyPayload[2], replyPayload[3]]), 'little')

    # Include to test with transfers less than the sector size
    # sectorSize -= 1
    bytesWaitingFor = int.from_bytes(bytearray([replyPayload[4], replyPayload[5], replyPayload[6], replyPayload[7]]), 'little')
            
    print("Sustained transfer initial response: Sector size "+str(sectorSize)+" bytes, hub and node waiting for "+str(bytesWaitingFor)+" bytes")
            
    if xferStatus & 1: # Should always be ready for the first sector
        print("Ready for sector transfer")
    else:
        print("Not ready for sector transfer")
            
    sectorNumber = 0 # For filling the sectors with a sector number value for testing
    toTransfer = 0 # number of bytes to transfer, usually a full sector, or less if there's less than a full sector left
    transferred = 0
            
    while (xferAborted == False and bytesRemaining > 0):
        xferStatus = 0
                
        # Get the next sector before we start polling the node to see if it's ready in order to parallel up with any over-the-air activity
                    
        if bytesRemaining < sectorSize:
            toTransfer = bytesRemaining
        else:
            toTransfer = sectorSize
                
                
        if filename == '':
            #sustainedTransferSector = bytearray([sectorNumber] * toTransfer ) # Each sector's data is filled with the transferred sector number
            sustainedTransferSector = bytearray(sustainedData[transferred : transferred + toTransfer])
            # print(sustainedTransferSector)
             
        else:
            sustainedTransferSector = bytearray(fh.read(toTransfer))
            print("Read "+str(len(sustainedTransferSector))+" bytes from '"+filename+"'")
                        
        if toTransfer != len(sustainedTransferSector):
            print("Didn't get expected amount of data for sector (wanted: "+str(toTransfer)+" got: "+str(len(sustainedTransferSector))+")")
                
        sustainedXferSectorTransfer = bytearray( sustainedXferId.to_bytes(2, 'little') +
                    sustainedTransferSector)
                
        print("Wait for sector transfer availability", end='')
        while xferAborted == False and (xferStatus & 1) == 0:
            print(".", end='')
            # wait for 171 Sustained Transfer Status/Control message, at this stage we should always get this response immediately as we've already waited for
            # our initial sustained transfer response above
            # This time we'll check the 'ready for sector' status too.
            '''
            if bytesRemaining < ( sustainedXferLength / 2 ): # Test - Cleanly abort a transfer roughly half way through
                print("*** Aborting transfer")
                xferAborted = True
                controlWord = 1
            else:
                controlWord = 0
            '''
            '''
            if bytesRemaining < ( sustainedXferLength / 2 ): # Test - stop performing a sustained transfer rouugly half way through, to test hub/node timeout and sustained transfer teardown
                print("Quitting transfer to test hub/node timeout and teardown mechanism")
                xferAborted = True
            '''    
                    
            replyHeader, replyPayload = spiToL2S2(171, bytearray(sustainedXferId.to_bytes(2, 'little') + controlWord.to_bytes(2, 'little') ), quiet ) # Sustained Transfer Status/Control message
            while xferAborted == False and replyHeader != b'\xAB': # 171 Sustained Transfer Status/Control response
                time.sleep(0.1)
                print("Unexpected response from Sustained Transfer Status/Control request, response " + str(replyHeader[0]) + " Payload " + " ".join('{:02X}'.format(x) for x in replyPayload))
                replyHeader, replyPayload = spiToL2S2(171, bytearray(sustainedXferId.to_bytes(2, 'little') + controlWord.to_bytes(2, 'little') ), quiet ) # Sustained Transfer Status/Control message
            xferStatus = int.from_bytes(bytearray([replyPayload[0], replyPayload[1]]), 'little')
                
        if xferAborted == False:
            bytesWaitingFor = int.from_bytes(bytearray([replyPayload[4], replyPayload[5], replyPayload[6], replyPayload[7]]), 'little')
                    
            print(" Reeady for next sector: "+str(bytesRemaining)+" bytes left to transfer overall, node/hub waiting for "+str(bytesWaitingFor)+" bytes")
                    
            #'''
            if bytesRemaining != bytesWaitingFor:
                print("Bytes remaining/bytes hub/node waiting for are out of sync, aborting...")
                xferAborted = True
                controlWord = 1
                replyHeader, replyPayload = spiToL2S2(171, controlWord.to_bytes(2, 'little'), quiet ) # Sustained Transfer Status/Control message
            #'''

            replyHeader, replyPayload = spiToL2S2(172, sustainedXferSectorTransfer, quiet ) # Transfer the sector we prepared
            sectorNumber = sectorNumber + 1
            bytesRemaining -= toTransfer
            transferred += toTransfer
    #'''
            
    print("Sustained transfer complete")
            
    if filename != '':
        print("File '"+filename+"' closed")
        fh.close()
    

############################################################################################################################
## Execution starts here
############################################################################################################################

# set up

qrcode = qrcode.QRCode()

# Assign chip select (CS) pin (and start it high)
if L2S2_SPI_BUS == 0:
    spi1cs = machine.Pin(17, machine.Pin.OUT)
if L2S2_SPI_BUS == 1:
    spi1cs = machine.Pin(13, machine.Pin.OUT)

spi1cs.value(1)


setL2S2SPI()
# Needs the following twice to correctly start from cold
#setDisplaySPI()
#setDisplaySPI()

#button_a = Button(12)
#button_b = Button(13)
#button_x = Button(14)
#button_y = Button(15)

if HAS_PICO_DISPLAY_2:
    led = RGBLED(6, 7, 8)


#WHITE = display.create_pen(255, 255, 255)
#BLACK = display.create_pen(0, 0, 0)
#CYAN = display.create_pen(0, 255, 255)
#MAGENTA = display.create_pen(255, 0, 255)
#YELLOW = display.create_pen(255, 255, 0)
#GREEN = display.create_pen(0, 255, 0)
#RED = display.create_pen(255, 0, 0)

#clear()


#
#display.set_font("bitmap8")


'''
# WiFi setup payload (for SoftSilicon)
payloadsetwifi = bytearray("SSID|PSK\0".encode("utf-8"))
spiToL2S2(5, payloadsetwifi, verbose)
'''

print(myTimeNow(),"Startup")
# Start CS pin high
spi1cs.value(1)
#clear()


#while True:
#    spiToL2S2(170, sustainedXferRequest, verbose ) # Sustained Transfer Request
#    time.sleep_ms(300)




while True:
    #clear()
    #display.set_pen(CYAN)
    #display.text("L2S2 SPI", 0, 0, 240, 4)
    #display.text("'A' button - Wifi Credentials Packet", 0, 230, 240, 1)
    
    #if button_a.read():                                   # if a button press is detected then...
        #clear()                                           # clear to black
        #display.set_pen(WHITE)                            # change the pen colour
        #display.text("Button A pressed", 10, 10, 240, 4)  # display some text on the screen
        #display.update()                                  # update the display
        #time.sleep(1)                                     # pause for a sec
        #clear()                                           # clear to black again
    #elif button_b.read():
        #clear()
        #display.set_pen(CYAN)
        #display.text("Button B pressed", 10, 10, 240, 4)
        #display.update()
        #time.sleep(1)
        #clear()
    #elif button_x.read():
        #clear()
        #display.set_pen(MAGENTA)
        #display.text("Button X pressed", 10, 10, 240, 4)
        #display.update()
        #time.sleep(1)
        #clear()
    #elif button_y.read():
        #clear()
        #display.set_pen(YELLOW)
        #display.text("Button Y pressed", 10, 10, 240, 4)
        #display.update()
        #time.sleep(1)
        #clear()
    #else:
        #display.set_pen(YELLOW)
        #display.text("Sending test payload", 0, 32, 240, 2)
        #display.update()
        # Define the RGB values for the colours of the rainbow


        # Wait for SoftSilicon startup (before going further)
        if waitForStartup == True:
            print("Waiting for SoftSilicon startup..", end='')
            statusRequest = 1
            
            # Status request (Get version)
            replyHeader = b'\x00'   
            while replyHeader != b'\x64': # Loop until we receive a response
                print(".", end='')
                statusRequestVersion = 0
                replyHeader, replyPayload = spiToL2S2(statusRequest, statusRequestVersion.to_bytes(1, 'little'), verbose ) # Status request
                if replyHeader == b'\x64': # 100 - Version status response
                    version1 = int.from_bytes(bytearray([replyPayload[0], replyPayload[1]]), 'little')
                    version2 = int.from_bytes(bytearray([replyPayload[2], replyPayload[3]]), 'little')
                    version3 = int.from_bytes(bytearray([replyPayload[4], replyPayload[5]]), 'little')
                    print(" SoftSilicon is responding, version number " + str(version1) + '.' + str(version2) + '.' + str(version3) )


        # Rainbow test, remove triple quotes to include
        if rgbLedCycle == True:
            red = (255, 0, 0)
            orange = (255, 165, 0)
            yellow = (255, 255, 0)
            green = (0, 255, 0)
            blue = (0, 0, 255)
            indigo = (75, 0, 130)
            violet = (143, 0, 255)
            payloadrainbow = bytearray([0x00, 0x00, 0x00, 0x00]) # RGB will be filled in, in the loop
            
            # Define the number of steps to use between each colour
            num_steps = 5

            # Loop through each colour of the rainbow and smoothly transition between them
            for colour1, colour2 in zip((red, orange, yellow, green, blue, indigo, violet), (orange, yellow, green, blue, indigo, violet, red)):
                r1, g1, b1 = colour1
                r2, g2, b2 = colour2
                for i in range(num_steps):
                    # Calculate the RGB values for the current step in the transition
                    r = int(r1 + (i / num_steps) * (r2 - r1))
                    g = int(g1 + (i / num_steps) * (g2 - g1))
                    b = int(b1 + (i / num_steps) * (b2 - b1))
                    # Print the RGB values for the current colour
                    # print(f"RGB({r}, {g}, {b})")
                    payloadrainbow[2] = r
                    payloadrainbow[1] = g
                    payloadrainbow[0] = b
                    spiToL2S2(99, payloadrainbow, verbose)
                    time.sleep(0.1)
            
        
        # Startup flow
        if startUpFlow == True:
            statusRequest = 1
            
            # Status request (Get version)
            replyHeader = b'\x00'   
            while replyHeader != b'\x64': # Loop until we receive a response
                statusRequestVersion = 0
                replyHeader, replyPayload = spiToL2S2(statusRequest, statusRequestVersion.to_bytes(1, 'little'), verbose ) # Status request
                if replyHeader == b'\x64': # 100 - Version status response
                    version1 = int.from_bytes(bytearray([replyPayload[0], replyPayload[1]]), 'little')
                    version2 = int.from_bytes(bytearray([replyPayload[2], replyPayload[3]]), 'little')
                    version3 = int.from_bytes(bytearray([replyPayload[4], replyPayload[5]]), 'little')
                    print("Received version number " + str(version1) + '.' + str(version2) + '.' + str(version3) )
                    
            # Status request (Get Device ID)
            replyHeader = b'\x00'   
            while replyHeader != b'\x65': # Loop until we receive a response
                statusRequestDeviceID = 1
                replyHeader, idPayload = spiToL2S2(statusRequest, statusRequestDeviceID.to_bytes(1, 'little'), verbose ) # Status request
                if replyHeader == b'\x65': # 101 - Device ID response
                    print("Received Device ID " + "".join(str(chr(x)) for x in idPayload))

                          
            # Status request (Get RTC)
            replyHeader = b'\x00'   
            while replyHeader != b'\x66': # Loop until we receive the correct response
                statusRequestRTC = 2
                replyHeader, replyPayload = spiToL2S2(statusRequest, statusRequestRTC.to_bytes(1, 'little'), verbose ) # RTC request
                if replyHeader == b'\x66': # 102 - RTC status response
                    rtcTime = int.from_bytes(bytearray([replyPayload[0], replyPayload[1],
                                                        replyPayload[2], replyPayload[3],
                                                        replyPayload[4], replyPayload[5],
                                                        replyPayload[6], replyPayload[7],
                                                        ]), 'little')
                    rtcValid = replyPayload[8]
                    if rtcValid == 0:
                        print("RTC not set")
                    elif rtcValid == 1:
                        print("RTC set and fresh")
                    elif rtcValid == 2:
                        print("RTC set but may be stale")
                    else:
                        print("Unknown RTC state "+str(rtcValid))
                        
                    tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec, tm_foo, tm_bar = time.gmtime(rtcTime)
                    
                    # Set the RTC while we're here
                    machine.RTC().datetime( (tm_year, tm_mon, tm_day, 0, tm_hour, tm_min, tm_sec, 0) ) # (year, month, day, weekday, hours, minutes, seconds, subseconds)
                    
                    print("Received RTC " + str(rtcTime) + ' : Date: {:02}/{:02}/{:02} : Time: {:02}:{:02}:{:02}'.format(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec))


            # Status request (Connectivity status)
            replyHeader = b'\x00'   
            while replyHeader != b'\x68': # Loop until we receive a response
                statusRequestConnectivity = 4
                replyHeader, replyPayload = spiToL2S2(statusRequest, statusRequestConnectivity.to_bytes(1, 'little'), verbose ) # Status request
                if replyHeader == b'\x68': # 104 - Connectivity response
                    connectivity = replyPayload[0]
                    if connectivity == 0:
                        print("Not connected to server")
                    elif connectivity == 1:
                        print("Connected to server")
                    else:
                        print("Unknown connectivity state "+str(connectivity))
                
                    print(str(replyPayload[1]) + " Hub(s) visible to this node")

            # Status request (BLE MAC address / Unicast address)
            replyHeader = b'\x00'   
            while replyHeader != b'\x6B': # Loop until we receive a response
                statusRequestMacs = 7
                replyHeader, replyPayload = spiToL2S2(statusRequest, statusRequestMacs.to_bytes(1, 'little'), verbose ) # Status request
                if replyHeader == b'\x6B': # 107 - BLE MAC address / Unicast address response
                    print("BLE MAC address: {:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(replyPayload[0], replyPayload[1], replyPayload[2], replyPayload[3], replyPayload[4], replyPayload[5]))
                    print("Unicast address: {:02X}{:02X}".format(replyPayload[7], replyPayload[6]))
            
            qrdata = ( chr(idPayload[8])+chr(idPayload[9])+chr(idPayload[10])+chr(idPayload[11])+chr(idPayload[12])+chr(idPayload[13])+chr(idPayload[14])+chr(idPayload[15])+":"+
                   "{:02X}{:02X}{:02X}{:02X}{:02X}{:02X}".format(replyPayload[0], replyPayload[1], replyPayload[2], replyPayload[3], replyPayload[4], replyPayload[5]) +":"+
                   "{:02X}{:02X}".format(replyPayload[7], replyPayload[6]))
            
            print(qrdata)
            
            #qrcode.set_text(qrdata)
            
            max_size = min(WIDTH, HEIGHT)
            #size, module_size = measure_qr_code(max_size, qrcode)
            #left = int((WIDTH // 2) - (size // 2))
            #top = int((HEIGHT // 2) - (size // 2))
            #draw_qr_code(left, top, max_size, qrcode)
            #display.update()
            
            #while True:
            #    time.sleep(0.1)

        if sendShortMessage == True:
            shortBinaryMessage = 159
            destinationId = 0x12345678
            formatType = 6
            versionNumber = 0
            
            #lowBatteryPayload = bytearray(b'B\x00\x0B\xCF\x4C\x65\x00\x00\x00\x00\x19\x00\x00\x0A\x0A') # low battery payload (1)

            #atrialBradycardiaAlertPayload = bytearray(b'\x52\x00\xAC\xE3\x4C\x65\x00\x00\x00\x00\x19\x00\x00\x0C\x60') # Atrial Bradycardia Alert
            
            '''
            shortMessagePayload = bytearray(b'I\xde\x00\x00\x00\x01\x13\x0b(e\x00\x00\x00\x00\xcd\x00\x13\x00\x8d\x00\xe0\x00\x97\x00\xaf\x01\xc7\x00')
            shortMessage = bytearray( destinationId.to_bytes(4, 'little') +
                                formatType.to_bytes(1, 'little') +
                                shortMessagePayload)
            '''

            # Send short binary message            
            
            #'''
            print("Sending low battery short message...")
            timestamp = time.time()
            shortMessagePayload = bytearray(b'\x41' + #b'B' +  # Low Battery Alert
                    versionNumber.to_bytes(1, 'little') +
                    timestamp.to_bytes(8, 'little') +
                    b'\x19\x00\x00\x0A\x0A')
            shortMessage = bytearray( destinationId.to_bytes(4, 'little') +
                                formatType.to_bytes(1, 'little') +
                                shortMessagePayload)
            replyHeader = b'\x00'   
            # while replyHeader != b'\xc7': # Loop until we receive a response
            spiToL2S2(159, shortMessage, verbose ) # Short Message
            #'''
        
            print("Sending keypad unlocked short message...")
            timestamp = time.time()
            shortMessagePayload = bytearray(b'\x41' + # b'K' + # K - Keypad unlocked
                    versionNumber.to_bytes(1, 'little') +
                    timestamp.to_bytes(8, 'little') +
                    b'\x34\x1F\x00\x00\x3C') # byte 10+: monitor, atrial, ventrical, rhythm, battery condition
            shortMessage = bytearray( destinationId.to_bytes(4, 'little') +
                                formatType.to_bytes(1, 'little') +
                                shortMessagePayload)
            replyHeader = b'\x00'   
            # while replyHeader != b'\xc7': # Loop until we receive a response
            spiToL2S2(159, shortMessage, verbose ) # Short Message
            #'''
            #'''
            print("Sending keypad locked short message...")
            data = [10, 20, 30, 4, 27]
            timestamp = time.time()
            heart_rate = data[0]
            spo2 = data[1]
            accel = data[2]
            colour = data[3]
            skin_temp = data[4]

            parameters = 0
            shortMessagePayload = bytearray(b'\x43' + # b'k' + # k - Keypad locked
                    versionNumber.to_bytes(1, 'little') +
                    timestamp.to_bytes(8, 'little')+
                    heart_rate.to_bytes(8,'little') +
                    spo2.to_bytes(8,'little') +
                    accel.to_bytes(8,'little') +
                    colour.to_bytes(4,'little') +
                    skin_temp.to_bytes(8,'little')) # byte 19+: 15,30,85,00 (from emulator)                       
                    #parameters.to_bytes(4, 'little'))
            
            shortMessage = bytearray( destinationId.to_bytes(4, 'little') +
                                formatType.to_bytes(1, 'little') +
                                shortMessagePayload)
            replyHeader = b'\x00'   
            # while replyHeader != b'\xc7': # Loop until we receive a response
            spiToL2S2(159, shortMessage, verbose ) # Short Message
            #'''


            print("Sending keypad locked short message...")
            timestamp = time.time()
            duration = 30
            parameters = 0
            shortMessagePayload = bytearray(b'\x41' + # b'k' + # k - Keypad locked
                    versionNumber.to_bytes(1, 'little') +
                    timestamp.to_bytes(8, 'little') +
                    b'\x34\x1F\x00\x00\x3C' + # byte 10+: monitor, atrial, ventrical, rhythm, battery condition
                    duration.to_bytes(4, 'little') +
                    b'\x0F\x1E\x55\x00') # byte 19+: 15,30,85,00 (from emulator)                       
                    #parameters.to_bytes(4, 'little'))
            spiToL2S2(159, shortMessage, verbose ) # Short Message
            
            # Send Martyn's message (testing effect on node)
            # 6B 15 00 48 97 00 E3 28 4E 65 00 00 00 00 18 00 00 00 34 1F 00 00 00 00 3C 96 Keypad locked
            # spiToL2S2(107, bytearray(b'\x00\xE3\x28\x4E\x65\x00\x00\x00\x00\x18\x00\x00\x00\x34\x1F\x00\x00\x00\x00\x3C\x96'), verbose ) # Broken
            
            # Test message 1 (from Martyn) to server
            # 0x50006B740600001929CA650000000081000000000000000D0000006900000000000000CC000000CC0000000000000000000000000000004D28CA6500000000410F00004D28CA6500000000560F0000
            #testData1 = bytearray.fromhex("50006B740600001929CA650000000081000000000000000D0000006900000000000000CC000000CC0000000000000000000000000000004D28CA6500000000410F00004D28CA6500000000560F0000")
            #spiToL2S2(159, testData1, verbose )
            
            # Test message 2 (from Jonathan) to server (too long for a short message, would need to be a sustained transfer)
            # 0x500012740600007025CA65000000001EEF03003FDA09009EA400002A9F030038003700432AE8221C9D847A9F9E604BAE567E386F7074537025CA6500000000410F6000EC010000E7010500E2010A00DD010F00D8011400D3011900CE011E00C9012300C4012800BF012D00BA013200B5013700B0013C00AB014100A6014600A1014B009C0150009701550092015A008D015F0088016400830169007E016E0079017300740178006F017D006A0182006501870060018C005B0191005601960051019B004C01A0004701A5004201AA003D01AF003801B4003301B9002E01BE002901C3002401C8001F01CD001A01D2001501D7001001DC000B01E1000601E6000101EB00FC00F000F700F500F200FA00ED00FF00E8000401E3000901DE000E01D9001301D4001801CF001D01CA002201C5002701C0002C01BB003101B6003601B1003B01AC004001A7004501A2004A019D004F0198005401930059018E005E0189006301840068017F006D017A0072017500770170007C016B0081016600860161008B015C0090015700950152009A014D009F014800A4014300A9013E00AE013900B3013400B8012F00BD012A00C2012500C7012000CC011B00D1011600D6011100DB017025CA6500000000560F6000C8000000C6000300C4000600C2000900C0000C00BE000F00BC001200BA001500B8001800B6001B00B4001E00B2002100B0002400AE002700AC002A00AA002D00A8003000A6003300A4003600A2003900A0003C009E003F009C0042009A0045009800480096004B0094004E0092005100900054008E0057008C005A008A005D008800600086006300840066008200690080006C007E006F007C0072007A0075007800780076007B0074007E0072008100700084006E0087006C008A006A008D006800900066009300640096006200990060009C005E009F005C00A2005A00A5005800A8005600AB005400AE005200B1005000B4004E00B7004C00BA004A00BD004800C0004600C3004400C6004200C9004000CC003E00CF003C00D2003A00D5003800D8003600DB003400DE003200E1003000E4002E00E7002C00EA002A00ED002800F0002600F3002400F6002200F9002000FC001E00FF001C0002011A0005011800080116000B0114000E0112001101100014010E0017010C001A010A001D011900000A60
            #testData2 = bytearray.fromhex("500012740600007025CA65000000001EEF03003FDA09009EA400002A9F030038003700432AE8221C9D847A9F9E604BAE567E386F7074537025CA6500000000410F6000EC010000E7010500E2010A00DD010F00D8011400D3011900CE011E00C9012300C4012800BF012D00BA013200B5013700B0013C00AB014100A6014600A1014B009C0150009701550092015A008D015F0088016400830169007E016E0079017300740178006F017D006A0182006501870060018C005B0191005601960051019B004C01A0004701A5004201AA003D01AF003801B4003301B9002E01BE002901C3002401C8001F01CD001A01D2001501D7001001DC000B01E1000601E6000101EB00FC00F000F700F500F200FA00ED00FF00E8000401E3000901DE000E01D9001301D4001801CF001D01CA002201C5002701C0002C01BB003101B6003601B1003B01AC004001A7004501A2004A019D004F0198005401930059018E005E0189006301840068017F006D017A0072017500770170007C016B0081016600860161008B015C0090015700950152009A014D009F014800A4014300A9013E00AE013900B3013400B8012F00BD012A00C2012500C7012000CC011B00D1011600D6011100DB017025CA6500000000560F6000C8000000C6000300C4000600C2000900C0000C00BE000F00BC001200BA001500B8001800B6001B00B4001E00B2002100B0002400AE002700AC002A00AA002D00A8003000A6003300A4003600A2003900A0003C009E003F009C0042009A0045009800480096004B0094004E0092005100900054008E0057008C005A008A005D008800600086006300840066008200690080006C007E006F007C0072007A0075007800780076007B0074007E0072008100700084006E0087006C008A006A008D006800900066009300640096006200990060009C005E009F005C00A2005A00A5005800A8005600AB005400AE005200B1005000B4004E00B7004C00BA004A00BD004800C0004600C3004400C6004200C9004000CC003E00CF003C00D2003A00D5003800D8003600DB003400DE003200E1003000E4002E00E7002C00EA002A00ED002800F0002600F3002400F6002200F9002000FC001E00FF001C0002011A0005011800080116000B0114000E0112001101100014010E0017010C001A010A001D011900000A60")
            #spiToL2S2(159, testData2, verbose )
            
            '''
            print("Sending Atrial Bradycardia Alert short message...")
            timestamp = time.time()
            shortMessagePayload = bytearray(b'R' +
                    versionNumber.to_bytes(1, 'little') +
                    timestamp.to_bytes(8, 'little') +
                    b'\x19\x00\x00\x0C\x60') # Atrial Bradycardia Alert
            shortMessage = bytearray( destinationId.to_bytes(4, 'little') +
                                formatType.to_bytes(1, 'little') +
                                shortMessagePayload)
            replyHeader = b'\x00'   
            # while replyHeader != b'\xc7': # Loop until we receive a response
            spiToL2S2(159, shortMessage, verbose ) # Short Message
            '''
            
        
        if sendLegacyMessage == True:
            _record_id = '3'
            _plate_id = '77D3E641-07A2-4357-AF81-4C33EE6B154A'
            _control_id = '58'
            _type = 5 # Datatype: 1 = bool; 2 = int; 3 = double; 4 = datetime; 5 = string
            _content = '26/10/23|11:22:40|Dr Leonard McCoy|2134D65GUE|Trina Wood|3333333333| Female|26/10/23|11:22:35|26/10/23|11:22:35|Positive|1|0.27|0.6|1.3|12900|41|Nothing Found|1|K54LA9856QA|v1.0.0|v1.0.0|P2-D6|Netpark'
            _units = ''
            legacy_data_send(_record_id, _plate_id, _control_id, _type, _content, _units)    


        if sendSustainedTransfer == True:
            doSustainedTransfer(sustainedXferFilename)
            doSustainedTransfer(bytearray.fromhex("500012740600007025CA65000000001EEF03003FDA09009EA400002A9F030038003700432AE8221C9D847A9F9E604BAE567E386F7074537025CA6500000000410F6000EC010000E7010500E2010A00DD010F00D8011400D3011900CE011E00C9012300C4012800BF012D00BA013200B5013700B0013C00AB014100A6014600A1014B009C0150009701550092015A008D015F0088016400830169007E016E0079017300740178006F017D006A0182006501870060018C005B0191005601960051019B004C01A0004701A5004201AA003D01AF003801B4003301B9002E01BE002901C3002401C8001F01CD001A01D2001501D7001001DC000B01E1000601E6000101EB00FC00F000F700F500F200FA00ED00FF00E8000401E3000901DE000E01D9001301D4001801CF001D01CA002201C5002701C0002C01BB003101B6003601B1003B01AC004001A7004501A2004A019D004F0198005401930059018E005E0189006301840068017F006D017A0072017500770170007C016B0081016600860161008B015C0090015700950152009A014D009F014800A4014300A9013E00AE013900B3013400B8012F00BD012A00C2012500C7012000CC011B00D1011600D6011100DB017025CA6500000000560F6000C8000000C6000300C4000600C2000900C0000C00BE000F00BC001200BA001500B8001800B6001B00B4001E00B2002100B0002400AE002700AC002A00AA002D00A8003000A6003300A4003600A2003900A0003C009E003F009C0042009A0045009800480096004B0094004E0092005100900054008E0057008C005A008A005D008800600086006300840066008200690080006C007E006F007C0072007A0075007800780076007B0074007E0072008100700084006E0087006C008A006A008D006800900066009300640096006200990060009C005E009F005C00A2005A00A5005800A8005600AB005400AE005200B1005000B4004E00B7004C00BA004A00BD004800C0004600C3004400C6004200C9004000CC003E00CF003C00D2003A00D5003800D8003600DB003400DE003200E1003000E4002E00E7002C00EA002A00ED002800F0002600F3002400F6002200F9002000FC001E00FF001C0002011A0005011800080116000B0114000E0112001101100014010E0017010C001A010A001D011900000A60"))


        if messageCheckLoop == True:
            hubsAvailable = 0
            connectivityStatus = 0
            
            print("Waiting for messages")
            while True:
                # Status request (Read Message)
                replyHeader = b'\x00'   
                while replyHeader != b'\xc7' and replyHeader != b'\x97' : # Loop until we receive an ACK or NOTIFICATION response
                    checkForMessage = 10
                    replyHeader, replyPayload = spiToL2S2(checkForMessage, bytearray(), quiet ) # Message check request
                    # We won't care about an ACK/no message response
                    if replyHeader == b'\xc7':
                        if replyPayload[0] != 7:
                            print("Message check ACK response "+str(replyPayload[0]))
                    if replyHeader == b'\x97': # 151 - Message notification response
                        print(myTimeNow(),"Received message (data type, payload): ", " ".join('{:02X}'.format(x) for x in replyPayload) )
                time.sleep(1.0)
                
                # Connectivity status check
                replyHeader = b'\x00'   
                while replyHeader != b'\x68': # Loop until we receive a response
                    statusRequestConnectivity = 4
                    replyHeader, replyPayload = spiToL2S2(statusRequest, statusRequestConnectivity.to_bytes(1, 'little'), quiet ) # Status request
                    if replyHeader == b'\x68': # 101 - Connectivity response
                        if connectivityStatus != replyPayload[0]:
                            if replyPayload[0] == 0:
                                print(myTimeNow(),"Not connected to server")
                            elif replyPayload[0] == 1:
                                print(myTimeNow(),"Connected to server")
                            else:
                                print(myTimeNow(),"Unknown connectivity state "+str(replyPayload[0]))
                            connectivityStatus = replyPayload[0]
                            
                        if hubsAvailable != replyPayload[1]:
                            print(myTimeNow(),str(replyPayload[1]) + " Hub(s) visible to this node (was "+str(hubsAvailable)+")")
                            hubsAvailable = replyPayload[1]
                time.sleep(1.0)




        # if repeatTests == False:
            # Uncomment to stop after a single transfer
            #'''
            #while True:
            #    time.sleep(0.1)
            #'''
        
        time.sleep(0.1)  # this is how frequently the Pico will check for button presses

 