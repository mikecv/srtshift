#!/usr/bin/env python3

import argparse
import logging
import logging.handlers
import json
import time
import re

from config import *
from utils import *

# *******************************************
# Program history.
# 0.1   MDC 01/03/2021  Original.
# *******************************************

# *******************************************
# TODO List
#
# *******************************************

# Program version.
progVersion = "0.1"

# *******************************************
# Program main.
# *******************************************
def main(configFile, subsFile, outFile, timeAdjust):

    # Create configuration values class object.
    config = Config(configFile)

    # *******************************************
    # Create logger.
    # Use rotating log files.
    # *******************************************
    logger = logging.getLogger('srtshift')
    logger.setLevel(config.DebugLevel)
    handler = logging.handlers.RotatingFileHandler('srtshift.log', maxBytes=config.LogFileSize, backupCount=config.LogBackups)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s.%(msecs)03d [%(name)s] [%(levelname)-8s] %(message)s', datefmt='%Y%m%d-%H:%M:%S', style='%'))
    logging.Formatter.converter = time.localtime
    logger.addHandler(handler)

    # Log program version.
    logger.info("Program version : {0:s}".format(progVersion))

    # Requested to adjust timing by?
    adj = float(timeAdjust)
    logger.info("Adjusting timing by secs : {0:f}".format(adj))

    # Open the subtitle file, read-only.
    logger.info("Attempting to open subtitle file : {0:s}".format(subsFile))
    with open(subsFile) as f:
        subData = f.read()

    # Open the output subtitle file, write mode.
    logger.info("Attempting to open output subtitle file : {0:s}".format(outFile))
    f = open(outFile, "w")

    # Split file according to blank lines.
    x = 0
    srtDetail = re.split(r'\n\s*\n', subData)
    for srt in srtDetail:
        # Construct search string for subtitle ID number.
        srtID = re.compile(r'^([0-9]+)$', re.MULTILINE)
        sid = re.search(srtID, srt)
        if sid:
            logger.debug("Subtitle ID : {0:s}".format(sid.group(1)))
            # Write ID to output file.
            f.write(f"{sid.group(1)}\n")
            srt = srt[len(sid.group(0)):]

            # Construct search for time stamp.
            srtTime = re.compile(r'^([0-5][0-9]):([0-5][0-9]):([0-5][0-9]),([0-9][0-9][0-9]) --> ([0-5][0-9]):([0-5][0-9]):([0-5][0-9]),([0-9][0-9][0-9])$', re.MULTILINE)
            sts = re.search(srtTime, srt)
            if sts:
                logger.debug("Timestamp : {0:s}".format(sts.group(0)))
                # Need to work out new time stamp.
                fromTimeSec = conv2Secs(int(sts.group(1)), int(sts.group(2)), int(sts.group(3)), int(sts.group(4)))
                logger.debug("FROM timestamp (sec) : {0:f}".format(fromTimeSec))
                fh, fm, fs, fms = conv2time(fromTimeSec + adj)
                logger.debug("New FROM timestamp (sec) : {0:02d}:{1:02d}:{2:02d},{3:03d}".format(fh, fm, fs, fms))
                toTimeSec = conv2Secs(int(sts.group(5)), int(sts.group(6)), int(sts.group(7)), int(sts.group(8)))
                logger.debug("TO timestamp (sec) : {0:f}".format(toTimeSec))
                th, tm, ts, tms = conv2time(toTimeSec + adj)
                logger.debug("New TO timestamp (sec) : {0:02d}:{1:02d}:{2:02d},{3:03d}".format(th, tm, ts, tms))
                logger.debug("New timestamp : {0:02d}:{1:02d}:{2:02d},{3:03d} --> {4:02d}:{5:02d}:{6:02d},{7:03d}".format(fh, fm, fs, fms, th, tm, ts, tms))
                # Write timestamp to output file.
                f.write("{0:02d}:{1:02d}:{2:02d},{3:03d} --> {4:02d}:{5:02d}:{6:02d},{7:03d}\n".format(fh, fm, fs, fms, th, tm, ts, tms))
                srt = srt[len(sts.group(0))+2:]

                # Subtitle text is the rest of the block of data.
                logger.debug("Subtitle text : {0:s}".format(srt))
                # Write subtitle text to output file.
                f.write(f"{srt}\n\n")

    # Close the output subtitles file.
    f.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Subtitle file (srt) time shift program.')
    parser.add_argument("-c", "--config", help="Json configuration file.")
    parser.add_argument("-s", "--subs", help="Original subtitle file.")
    parser.add_argument("-o", "--outfile", help="Output subtitle file.")
    parser.add_argument("-a", "--adjust", help="Adjustment seconds (+ve is delay)")
    parser.add_argument("-v", "--version", help="Program version.", action="store_true")
    args = parser.parse_args()

    # Default output subtitle file.
    outFile = "output.srt"

    # Default time adjustment (seconds); +ve implies delay.
    timeAdjust = "0.0"

    # Check if program version requested.
    # Only show version and don't do anything else.
    if args.version:
        print("Program version : {0:s}".format(progVersion))
    else:
        # Check that a configuration file specified, else nothing to do.
        if args.config:
            if args.subs:
                if args.outfile:
                    outFile = args.outfile
                if args.adjust:
                    timeAdjust = args.adjust
                main(args.config, args.subs, outFile, timeAdjust)
            else:
                print("Specify an original subtitles file to time shift.")
        else:
            print("Specify a json configuration file.")