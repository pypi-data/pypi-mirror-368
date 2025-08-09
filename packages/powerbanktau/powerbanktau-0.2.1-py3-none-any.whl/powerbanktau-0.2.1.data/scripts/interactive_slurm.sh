#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [options]

Options:
--partition  <name>   : SLURM partition (default: engineering)
--mem        <size>   : RAM per node, e.g. 30G (default: 5G)
--cpus       <n>      : number of CPUs (default: 2)
--time      <HH:MM:SS>: job time (default: 04:00:00)
--gpus       <n>      : number of GPUs (default: 0)
EOF
  exit 1
}

# defaults
partition="engineering"
mem="5G"
cpus=2
time="04:00:00"
gpus=0

# parse optional flags
while [ $# -gt 0 ]; do
  case $1 in
    --partition)  partition=$2; shift 2;;
    --mem)        mem=$2;       shift 2;;
    --cpus)       cpus=$2;      shift 2;;
    --time)       time=$2;      shift 2;;
    --gpus)       gpus=$2;      shift 2;;
    -h|--help)    usage;;
    *)
      echo "Unknown option: $1"; usage;;
  esac
done

# GPU account setup
gres_opts=""
if [ "$gpus" -gt 0 ]; then
  gres_opts="--gres=gpu:$gpus -A gpu-general-users"
fi

echo "Requesting interactive SLURM session:"
echo "  Partition: $partition"
echo "  CPUs:      $cpus"
echo "  Memory:    $mem"
echo "  GPUs:      $gpus"
echo "  Time:      $time"
echo

# submit interactive SLURM job
srun --partition="$partition" \
     --nodes=1 \
     --ntasks=1 \
     --cpus-per-task=$cpus \
     --time=$time \
     --mem=$mem \
     $gres_opts \
     --pty bash