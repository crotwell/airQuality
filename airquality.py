#!/usr/bin/env python3

import serial, time, datetime, os, platform, sys, argparse
ser = serial.Serial('/dev/ttyUSB0')
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
    for i in range(0,10):
       d = ser.read()
       data.append(d)

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
