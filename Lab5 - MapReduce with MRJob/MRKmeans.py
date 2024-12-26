"""
.. module:: MRKmeans

MRKmeans
*************

:Description: MRKmeans

    Iterates the MRKmeansStep script

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 10:16 

"""

from MRKmeansStep import MRKmeansStep
import shutil
import argparse
import os
import time
from mrjob.util import to_lines

__author__ = 'bejar'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prot', default='prototypes.txt', help='Initial prototypes file')
    parser.add_argument('--docs', default='documents.txt', help='Documents data')
    parser.add_argument('--iter', default=5, type=int, help='Number of iterations')
    parser.add_argument('--ncores', default=2, type=int, help='Number of parallel processes to use')

    args = parser.parse_args()
    assign = {}

    cwd = os.getcwd()
    shutil.copy(cwd + '/' + args.prot, cwd + '/prototypes0.txt')

    nomove = False  # Tracks convergence
    for i in range(args.iter):
        tinit = time.time()
        print(f'Iteration {i + 1} ...')

        mr_job1 = MRKmeansStep(args=['-r', 'local', args.docs,
                                     '--file', cwd + f'/prototypes{i}.txt',
                                     '--prot', cwd + f'/prototypes{i}.txt',
                                     '--num-cores', str(args.ncores)])

        with mr_job1.make_runner() as runner1:
            runner1.run()
            new_assign = {}
            new_proto = {}

            for cluster, prototype in mr_job1.parse_output(runner1.cat_output()):
                new_proto[cluster] = prototype

            # Save new prototypes for next iteration
            with open(cwd + f'/prototypes{i + 1}.txt', 'w') as f:
                for cluster, prototype in new_proto.items():
                    proto_str = ' '.join(f"{word}+{freq:.6f}" for word, freq in prototype)
                    f.write(f"{cluster}:{proto_str}\n")

            # Check for convergence
            if assign == new_assign:
                nomove = True
            else:
                assign = new_assign

        print(f"Time= {(time.time() - tinit)} seconds")

        if nomove:
            print("Algorithm converged")
            break

    print("Clustering complete. Results in prototypes file.")
