#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 <workdir> [options]

<workdir>             : directory in which to start Jupyter Lab
--partition  <name>   : PBS queue/partition (default: tamirQ)
--mem        <size>   : RAM per node, e.g. 30gb (default: 5gb)
--cpus       <n>      : number of CPUs (default: 2)
--walltime  <HH:MM:SS>: job walltime (default: 04:00:00)
--jobname   <name>    : PBS job name (default: jupyter)
--port      <port>    : Jupyter Lab port (default: 8888)
EOF
  exit 1
}

# defaults
partition="tamirQ"
mem="5gb"
cpus=2
walltime="04:00:00"
jobname="jupyter"
base_port=8888

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
    --walltime)   walltime=$2;  shift 2;;
    --jobname)    jobname=$2;   shift 2;;
    --port)       base_port=$2; shift 2;;
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

# submit the PBS job via here-doc
qsub <<EOF
#PBS -q $partition
#PBS -l select=1:ncpus=$cpus:mem=$mem
#PBS -l walltime=$walltime
#PBS -N $jobname
#PBS -j oe
#PBS -o $outdir/\$PBS_JOBID.out
#PBS -e $errdir/\$PBS_JOBID.err
#PBS -V

echo "=== Allocated on \$(hostname) ==="
echo "Job ID: \$PBS_JOBID"
echo "CPUs:   $cpus   Memory: $mem"
echo "Queue:  $partition   Walltime: $walltime"
echo "Starting in: $workdir"
echo

# load conda and activate
source /tamir2/nicolaslynn/home/miniconda3/etc/profile.d/conda.sh
conda activate base

# go to the workdir
cd $workdir

# launch Jupyter Lab
echo "Launching Jupyter Lab on port $base_port..."
jupyter lab --ip=0.0.0.0 --port=$base_port --no-browser
EOF

echo "Submitted PBS job '$jobname' in queue '$partition' with $cpus CPUs, $mem RAM, walltime $walltime."
echo "Logs will go to $outdir and $errdir.  Jupyter on port $base_port."

