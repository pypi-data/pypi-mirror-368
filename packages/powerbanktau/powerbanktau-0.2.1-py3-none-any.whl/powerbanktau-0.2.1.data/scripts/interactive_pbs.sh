#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [options]

Options:
--partition  <name>   : PBS queue/partition (default: tamirQ)
--mem        <size>   : RAM per node, e.g. 30gb (default: 5gb)
--cpus       <n>      : number of CPUs (default: 2)
--walltime  <HH:MM:SS>: job walltime (default: 04:00:00)
--gpus       <n>      : number of GPUs (default: 0)
EOF
  exit 1
}

# defaults
partition="tamirQ"
mem="5gb"
cpus=2
walltime="04:00:00"
gpus=0

# parse optional flags
while [ $# -gt 0 ]; do
  case $1 in
    --partition)  partition=$2; shift 2;;
    --mem)        mem=$2;       shift 2;;
    --cpus)       cpus=$2;      shift 2;;
    --walltime)   walltime=$2;  shift 2;;
    --gpus)       gpus=$2;      shift 2;;
    -h|--help)    usage;;
    *)
      echo "Unknown option: $1"; usage;;
  esac
done

# calculate virtual memory (2x physical memory)
mem_value=$(echo $mem | sed 's/[^0-9]//g')
mem_unit=$(echo $mem | sed 's/[0-9]//g')
vmem="${mem_value}${mem_unit}"
pvmem="$((mem_value * 2))${mem_unit}"

echo "Requesting interactive PBS session:"
echo "  Partition: $partition"
echo "  CPUs:      $cpus"
echo "  Memory:    $mem (virtual: $pvmem)"
echo "  GPUs:      $gpus"
echo "  Walltime:  $walltime"
echo

# submit interactive PBS job
qsub -q $partition -I -l select=1:ncpus=$cpus:ngpus=$gpus:mem=$mem,walltime=$walltime