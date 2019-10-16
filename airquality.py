#!/usr/bin/env python3

import serial, time, datetime, os, platform, sys, argparse
import binascii

usbFilename = '/dev/ttyUSB0'
if not os.path.exists(usbFilename):
    sys.exit('serial device '+usbFilename+' not found, quitting...')

ser = serial.Serial(usbFilename)
dataPath = '/var/www/html/airquality/'
sleeptime = 10 # seconds
host = platform.node()

parser = argparse.ArgumentParser(description='Air Quality using SDS011 particulate sensor.')
parser.add_argument('-q', '--quiet', action="store_true",
                    help='be quiet, no printing to stdout, also enables logging to file')
parser.add_argument("-s", "--sleep", type=int, default='10',
                    help="sleep time in seconds between samples")
parser.add_argument('--outdir',
                    default=dataPath,
                    help="output directory, defaults to "+dataPath)
args = parser.parse_args()


headerLine = 'Time,PM2.5,PM10'
printHeaderLine = True

if not args.quiet:
    print(headerLine)

while True:
    data = []
    nowTime = datetime.datetime.utcnow()
    d = ser.read()
    while d != b'\xaa':
        print('read not AA: '+binascii.hexlify(d).decode("ascii"), file=sys.stderr)
        d = ser.read()
    data.append(d)
    for i in range(1,10):
       d = ser.read()
       data.append(d)
    if data[9] != b'\xab':
        print('read tail not AB: '+binascii.hexlify(data[9]).decode("ascii"), file=sys.stderr)
        continue


    pmtwofive = int.from_bytes(b''.join(data[2:4]), byteorder='little') /10
    pmten = int.from_bytes(b''.join(data[4:6]), byteorder='little') /10
    nowTimeString = nowTime.strftime('%Y-%m-%dT%H:%M:%S')
    outLine = '{} UTC,{},{}'.format(nowTimeString, pmtwofive, pmten)
    if args.quiet:
        dataFileName = nowTime.strftime('data_'+host+'_%Y_%b_%d.txt')
        dataFile = os.path.join(args.outdir, dataFileName)
        if os.path.exists(dataFile):
            printHeaderLine = False
        with open(dataFile, "a") as f:
            if printHeaderLine:
                f.write(headerLine)
                f.write("\n")
            f.write(outLine)
            f.write("\n")
    else:
        print(outLine)
    try:
        time.sleep(args.sleep)
    except KeyboardInterrupt:
        print()
        break
