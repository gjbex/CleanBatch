#!/usr/bin/env python3

import argparse
import shlex
import subprocess
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='Submit a job in a clean environment.')
    parser.add_argument('--cluster', type=str,
                        help='Cluster name to submit the job to.')
    parser.add_argument('--partition', type=str,
                        help='Partition to submit the job to.')
    env_group = parser.add_mutually_exclusive_group(required=False)
    env_group.add_argument('--conda', type=str,
                           help='Conda environment to activate before running the job.')
    env_group.add_argument('--modules', type=str,
                           help='file that lists the modules to be loaded before running the job.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print the sbatch command without executing it.')
    return parser.parse_known_args()

def main():
    args, sbatch_args = parse_arguments()
    print(sbatch_args)

    # command to ensure the environment is clean
    clean_command = 'module purge &> /dev/null'

    # command to initialize the environment
    if args.conda:
        env_command = f'conda activate {args.conda}'
    elif args.modules:
        env_command = f'module load cluster/{args.cluster}/{args.partition} && module load $(cat {args.modules})'
    else:
        env_command = ''

    # ensure environment variables are passed into the job
    sbatch_args.insert(0, '--export=ALL')

    # ensure that the --cluster and --partition arguments will be passed
    # to sbatch if they were intercepted
    if args.cluster:
        sbatch_args.insert(0, f'--cluster={args.cluster}')
    if args.partition:
        sbatch_args.insert(0, f'--partition={args.partition}')

    # ensure that the arguments for sbatch are properly quoted
    sbatch_args = [shlex.quote(arg) for arg in sbatch_args]

    # construct the sequence of commands to be executed
    command = f'{clean_command} && {env_command} && sbatch {" ".join(sbatch_args)}'

    if args.dry_run:
        print(f'Dry run: {command}')
        return

    # execute the command
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f'Error executing command: {e.stderr.strip()}', file=sys.stderr)
        sys.exit(e.returncode)


    
if __name__ == '__main__':
    main()
