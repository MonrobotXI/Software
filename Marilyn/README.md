Marilyn Program tape and output.
Courtesy John Mann, who owns the tape and built the reader.

The Marilyn program automated the typewriters to produce a large poster of Marilyn Monroe as text art.

The files are:

MAR-P.bin - Binary copy of Marilyn Program tape\
MAR-P.txt - ^ Emulator tape text version\
MAR-P-ut1.txt - ^ tape with UT-1 decoded instructions
    and 5,5,5,5,5 chars, 2 flags decode

bin2ppt.py - conversion program\
./bin2ppt.py -t -m  MAR-P.bin > MAR-P.txt\
./bin2ppt.py -t -m --ut1 MAR-P.bin > MAR-P-ut1.txt

Screenshots during, at end of running program

MAR-P_load.txt - text grabs before/after running program

MAR-T.bin - Binary copy of Marilyn Typewriter output\
MAR-T.txt - ^ Emulator tape text version\
These 2 not tested yet.
