#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 <workdir> [options]

<workdir>             : directory in which to start Jupyter Lab
--partition  <name>   : SLURM partition (default: gpu-general)
--mem        <size>   : RAM per node, e.g. 150G (default: 150G)
--cpus       <n>      : number of CPUs (default: 12)
--time      <HH:MM:SS>: job time (default: 120:00:00)
--jobname   <name>    : SLURM job name (default: gpu_jupyter)
--port      <port>    : Jupyter Lab port (default: 8778)
--gpus      <n>       : number of GPUs (default: 1)
--exclude   <nodes>   : comma-separated list of nodes to exclude
--env       <name>    : conda environment to activate (default: base)
EOF
  exit 1
}

# defaults
partition="gpu-general"
mem="150G"
cpus=12
time="120:00:00"
jobname="gpu_jupyter"
base_port=8778
gpus=1
exclude_nodes="compute-0-420,compute-0-332,compute-0-333,compute-0-58,compute-0-53,compute-0-390"
conda_env="base"

# require at least one arg
if [ $# -lt 1 ]; then
  usage
fi

# first positional is workdir
workdir=$1
shift

# parse optional flags
while [ $# -gt 0 ]; do
  case $1 in
    --partition)  partition=$2; shift 2;;
    --mem)        mem=$2;       shift 2;;
    --cpus)       cpus=$2;      shift 2;;
    --time)       time=$2;      shift 2;;
    --jobname)    jobname=$2;   shift 2;;
    --port)       base_port=$2; shift 2;;
    --gpus)       gpus=$2;      shift 2;;
    --exclude)    exclude_nodes=$2; shift 2;;
    --env)        conda_env=$2; shift 2;;
    -h|--help)    usage;;
    *)
      echo "Unknown option: $1"; usage;;
  esac
done

# make sure workdir exists
if [ ! -d "$workdir" ]; then
  echo "Error: workdir '$workdir' not found."
  exit 1
fi

# ensure logging directories exist
outdir="${HOME}/logging/output"
errdir="${HOME}/logging/error"
mkdir -p "$outdir" "$errdir"

# submit the SLURM job
sbatch <<EOF
#!/bin/bash
#SBATCH --partition=$partition
#SBATCH --mem=$mem
#SBATCH --job-name=$jobname
#SBATCH --ntasks=$cpus
#SBATCH --time=$time
#SBATCH --output=$outdir/slurm-%j.out
#SBATCH --error=$errdir/slurm-%j.err
#SBATCH --gres=gpu:$gpus -A gpu-general-users
#SBATCH --exclude=$exclude_nodes

echo "=== Allocated on \$(hostname) ==="
echo "Job ID: \$SLURM_JOB_ID"
echo "Node List: \$SLURM_NODELIST"
echo "CPUs:   $cpus   Memory: $mem   GPUs: $gpus"
echo "Partition:  $partition   Time: $time"
echo "Starting in: $workdir"
echo

# Load user environment
source ~/.bashrc
source /tamir2/nicolaslynn/home/miniconda3/etc/profile.d/conda.sh

# Load the Miniconda module for GPU support
module load miniconda/miniconda3-2023-environmentally || { echo "Failed to load miniconda module"; exit 1; }

# go to the workdir
cd $workdir

# activate conda environment
conda activate $conda_env

# launch Jupyter Lab
echo "Launching Jupyter Lab on port $base_port..."
jupyter lab --ip=* --port=$base_port --no-browser

# Keep the job alive
sleep 604800
EOF

echo "Submitted GPU SLURM job '$jobname' in partition '$partition' with $cpus CPUs, $mem RAM, $gpus GPU(s), time $time."
echo "Logs will go to $outdir and $errdir.  Jupyter on port $base_port."
echo "Excluded nodes: $exclude_nodes"