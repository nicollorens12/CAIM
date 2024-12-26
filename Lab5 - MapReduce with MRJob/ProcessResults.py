"""
.. module:: ProcessResults

ProcessPrototype
******

:Description: ProcessResults

    Prints the results of a clustering,basically the prototypes, selecting the --attr
    tokens with the highest probability

    It assumes that the results are written in a file with the adequate format

:Authors:
    bejar

:Version: 

:Date:  14/07/2017
"""


import argparse

__author__ = 'bejar'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prot', default='prototypes-final.txt', help='prototype file')
    parser.add_argument('--natt', default=5, type=int, help='Number of attributes to show')
    args = parser.parse_args()

    f = open(args.prot, 'r')

    parts = args.prot.split('_', 1)
    resulting_file_name = f"{parts[0]}-final_{parts[1]}" if len(parts) > 1 else args.prot

    with open(resulting_file_name, 'w') as result_file:
        for line in f:
            cl, attr = line.split(':')
            result_file.write(cl + '\n')
            latt = sorted([(float(at.split('+')[1]), at.split('+')[0]) for at in attr.split()], reverse=True)
            result_file.write(str(latt[:args.natt]) + '\n')

