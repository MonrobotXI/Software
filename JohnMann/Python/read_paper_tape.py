#! /usr/bin/env python3
# From https://github.com/tomverbeure/fake_parallel_printer/blob/main/fake_printer.py

import sys
import getopt
import serial
import time


def usage():
    print(f"""{sys.argv[0]}
-p <serial port>, --port=<serial port>  : serial port device. E.g. -p /dev/ttyACM0, --port=COM3. No default. Required.
[-t <time>, --timeout=<time>]           : idle time, in seconds, after which an end-of-page is declared. Default: 2
[-f <prefix>, --prefix=<prefix>]        : fixed filename prefix of generated capture files. Default: paper_tape_
[-s <suffix>, --suffix=<suffix>]        : filename extension of generated capture files. Default: bin
[-n <tape nr>, --tapenr=<tape nr>]      : starting number of the generated capture file. Default: 0
[-v, --verbose]                         : print a bit more info
[-h, --help]                            : print this information

read_paper_tape.py listens to the USB serial port to which a paper tape reader is connected.
When it detects incoming traffic, it forwards the data to a capture file (default: paper_tape_0.bin).

If no traffic is detected for a specified timeout value, the end of a tape read is assumed
and the capture file is closed. When new data is detected after that, new capture file is opened with
an page number that is increased by one.

Example: ./read_paper_tape.py --port=/dev/ttyACM0 -t 2 --prefix=tape1 -s pcl
    """)
    pass

def main():
    port = None
    timeout = 2
    prefix = "paper_tape_"
    suffix = "bin"
    tape_nr = 0
    verbose = False

    try:
        optlist, args = getopt.getopt(sys.argv[1:], "hvp:t:s:n:f:", ["help", "verbose", "port=", "prefix=", "suffix=", "timeout=", "--tapenr="])
    except getopt.GetoptError as err:
        print(err)
        print()
        usage()
        sys.exit(1)

    for o, a in optlist:
        if o in ("-p", "--port"):
            port = a
        elif o in ("-t", "--timeout"):
            timeout = int(a)
        elif o in ("-f", "--prefix"):
            prefix = a
        elif o in ("-s", "--suffix"):
            suffix = a
        elif o in ("-n", "--tapenr"):
            tape_nr = int(a)
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)

    if len(args) > 0:
        print(f"Unprocessed arguments: {args}\n")
        usage()
        sys.exit(2)

    if port is None:
        print("No serial port specified.\n")
        usage()
        sys.exit(3)

    print("paper tape:")
    if verbose:
        print(f"    verbose = {verbose}")
        print(f"    port    = {port}")
        print(f"    timeout = {timeout}")
        print(f"    prefix  = {prefix}")
        print(f"    suffix  = {suffix}")
        print(f"    tape nr = {tape_nr}")
    sys.stdout.flush()

    with serial.Serial(port, timeout=1) as ser:
        while True:
            d = ser.read(1024)
            start_time = time.time()
            last_received_time = start_time

            if len(d) > 0:
                filename = f"{prefix}{tape_nr}.{suffix}"
                print(f"Printer data received. Creating printer capture file {filename}.")

                bytes_received = len(d)

                with open(filename, "wb") as prt_file:
                    prt_file.write(d)

                    while time.time() < (last_received_time+timeout):
                        d = ser.read(1024)
                        if len(d) > 0:
                            print(".", end="")
                            sys.stdout.flush()
                            bytes_received += len(d)
                            prt_file.write(d)
                            last_received_time = time.time()

                    end_time = time.time() - timeout
                    duration = end_time - start_time
                    print()
                    print(f"{bytes_received} bytes received in {int(duration)}s. ({int(bytes_received/duration)} bytes/s)")
                    print(f"No printer data received for {timeout} seconds. Closing printer capture file.")
                    sys.stdout.flush()

                tape_nr += 1

if __name__ == "__main__":
    main()

