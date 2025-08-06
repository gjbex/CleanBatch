# CleanBatch

This is a drop-in replacement for Slurm's `sbatch` command that tries to ensure that a job starts in a consistent environment.

It can either prepare an evironment based on conda or load a set of modules.  This will reduce the startup time of jobs, especially array jobs.

## Requirements

The script only requires Python >= 3.10.x.

## Usage

```bash
cbatch [<sbatch-arguments>] [ --conda <env-name> | --modules <module-list-file> ] [--dry-run] <job-script>
```

## What is it?

* `src`: source directory that contains the Python script.
* `examples`: Slurm job scripts and module list files
