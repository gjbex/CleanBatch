#!/usr/bin/env python3

import argparse
import pathlib
import shlex
import subprocess
import sys

# Defaults
DEFAULT_PARTITION = 'batch'

def extract_sbatch_tokens(script_path):
    '''Extract all tokens from #SBATCH lines in a Slurm job script.'''
    tokens = []
    with open(script_path) as script_file:
        for line in script_file:
            line = line.strip()
            if line.startswith("#SBATCH"):
                tokens.extend(shlex.split(line[len("#SBATCH"):].strip()))
    return tokens


# # Step 2: Parse #SBATCH tokens to get defaults
# job_script_path = Path("job_script.sh")
# sbatch_tokens = extract_sbatch_tokens(job_script_path)
# slurm_defaults, _ = slurm_parser.parse_known_args(sbatch_tokens)
# 
# # Step 3: Main parser with slurm_parser as parent
# main_parser = argparse.ArgumentParser(parents=[slurm_parser])
# main_parser.add_argument("--foo")  # Example of script-specific option
# main_parser.set_defaults(**vars(slurm_defaults))
# 
# # Step 4: Parse CLI args (CLI overrides script defaults)
# args = main_parser.parse_args()
# 
# print("Cluster:", args.cluster)
# print("Partition:", args.partition)
# print("Foo:", args.foo)

def main():
    # Define the parser for the Slurm job script directives.  It only cares about
    # * --cluster
    # * --partition
    script_parser = argparse.ArgumentParser(
        description='Submit a job in a clean environment.',
        add_help=False
    )
    script_parser.add_argument(
        '--cluster',
        help='Cluster name to submit the job to.'
    )
    script_parser.add_argument(
        '--partition',
        help='Partition to submit the job to.'
    )

    # Define the parser for the command line arguments.  It cares about
    # * --cluster (inherited from parent)
    # * --partition (inherited from parent)
    # * --conda or --modules
    # * --dry-run
    # * JOB_SCRIPT
    # * JOB_SCRIPT_ARGS
    parser = argparse.ArgumentParser(
        description='Submit a job in a clean environment.',
        parents=[script_parser]
    )
    env_group = parser.add_mutually_exclusive_group(required=False)
    env_group.add_argument(
        '--conda',
        help='Conda environment to activate before running the job.'
    )
    env_group.add_argument(
        '--modules',
        help='file that lists the modules to be loaded before running the job.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print the sbatch command without executing it.'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Do not provide progess information.'
    )
    parser.add_argument(
        'jobscript',
        metavar='JOB_SCRIPT',
        help='Job script to submit to Slurm.'
    )
    parser.add_argument(
        'jobscript_args',
        nargs='*',
        metavar='JOB_SCRIPT_ARGS',
        help='Arguments for the job script.'
    )

    # Parse the command line arguments to determine JOB_SCRIPT
    args, sbatch_args = parser.parse_known_args()

    # Extract the Slurm directives from the job script
    script_args = extract_sbatch_tokens(args.jobscript)
    # Parse the job script using the job script parser
    script_args, _ = script_parser.parse_known_args(script_args)

    # Parse the command line arguments again, potentially overriding options
    # that were set as directives in the job script
    args, sbatch_args = parser.parse_known_args(namespace=script_args)

    # If no --cluster was given, exit
    if not args.cluster:
        print('Error: no cluster specified', file=sys.stderr)
        sys.exit(1)

    # If no partition is given, set to default
    if not args.partition:
        args.partition = DEFAULT_PARTITION

    # Command to ensure the environment is clean
    clean_command = 'module purge &> /dev/null'
    if not args.quiet:
        clean_command = '(>&2 echo "cleaning environment...") && ' + clean_command

    # Command to initialize the environment
    if args.conda:
        env_command = f'source ~/.bashrc && conda activate {args.conda}'
    elif args.modules:
        env_command = f'module load cluster/{args.cluster}/{args.partition} && module load $(cat {args.modules})'
    else:
        env_command = 'true'
    if not args.quiet:
        env_command = '(>&2 echo "preparing environment...") && ' + env_command

    # Ensure environment variables are passed into the job
    sbatch_args.insert(0, '--export=ALL')

    # Ensure that the --cluster and --partition arguments will be passed
    # to sbatch if they were intercepted
    sbatch_args.insert(0, f'--cluster={args.cluster}')
    sbatch_args.insert(0, f'--partition={args.partition}')

    # Append job script to the sbatch arguments, as well as any arguments for the job script
    sbatch_args.append(args.jobscript)
    sbatch_args.extend(args.jobscript_args)

    # Ensure that the arguments for sbatch are properly quoted
    sbatch_args = [shlex.quote(arg) for arg in sbatch_args]

    # Construct the sequence of commands to be executed
    command = f'{clean_command} && {env_command} && sbatch {" ".join(sbatch_args)}'

    if args.dry_run:
        print(f'Dry run:\n{command}')
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
