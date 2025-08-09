# PowerBankTau

Advanced Dask cluster utilities for HPC environments with PBS/SLURM schedulers.

## Installation

```bash
pip install powerbanktau
```

## Features

- 🚀 **Easy cluster spawning** for PBS and SLURM schedulers
- 🖥️ **Local cluster support** with automatic resource detection  
- 🔄 **Complete processing pipelines** with automatic cluster management
- 🛡️ **Safe error handling** with retry logic and incremental saving
- 🎮 **GPU-enabled clusters** support
- 📊 **Cluster monitoring** and health checks
- 🔁 **Checkpoint recovery** for long-running jobs
- 📈 **Adaptive scaling** based on workload
- 📋 **Multiple output formats** (CSV, JSON, Parquet, HDF5, Excel)
- 🔧 **Configuration presets** for common use cases

## Quick Start

### Using Presets (Recommended)

```python
from powerbanktau.utils import launch_preset_cluster, managed_cluster

# Quick launch with preset configurations
client, cluster = launch_preset_cluster(
    preset='large',  # 'small', 'medium', 'large', 'gpu', 'memory_intensive'
    cluster_type='pbs',
    queue='power-general'  # Override preset values
)

# Or use context manager for automatic cleanup
with managed_cluster('pbs', preset='medium') as (client, cluster):
    # Your processing code here
    results = client.map(your_function, your_data)
```

### Advanced Processing Pipeline

```python
from powerbanktau.utils import process_dataframe_with_dask, setup_logging
import pandas as pd

# Setup logging
setup_logging(level='INFO', log_file='processing.log')

def process_mutation(row, **kwargs):
    # Your processing logic here
    return some_complex_computation(row)

# Process with all the bells and whistles
df = pd.read_csv("mutations.csv")
output_file = process_dataframe_with_dask(
    df=df,
    process_func=process_mutation,
    output_file="results.parquet",  # Supports multiple formats
    cluster_config={
        'memory_size': '8GB',
        'num_workers': 100,
        'queue': 'power-general'
    },
    cluster_type='pbs',
    func_kwargs={'param1': 'value1'},
    default_result=None,
    save_interval=50
)
```

### Checkpoint Recovery for Long Jobs

```python
from powerbanktau.utils import process_with_checkpoint

# Process with automatic checkpoint recovery
output_file = process_with_checkpoint(
    items=your_large_dataset,
    process_func=your_function,
    checkpoint_dir="./checkpoints",
    output_file="results.csv",
    cluster_config={'preset': 'large'},
    checkpoint_interval=100  # Save checkpoint every 100 items
)
```

### Monitoring and Benchmarking

```python
from powerbanktau.utils import (
    get_cluster_status, 
    benchmark_cluster,
    track_resource_usage,
    setup_adaptive_cluster
)

# Monitor cluster health
status = get_cluster_status(client)
print(f"Workers: {status['workers']}, Memory: {status['total_memory_gb']:.1f}GB")

# Enable adaptive scaling
setup_adaptive_cluster(cluster, minimum=10, maximum=200)

# Benchmark performance
benchmark_results = benchmark_cluster(client, task_count=1000)
print(f"Performance: {benchmark_results['tasks_per_second']:.1f} tasks/sec")
```

### Multiple Output Formats

```python
from powerbanktau.utils import save_results_multi_format

# Save results in different formats
save_results_multi_format(
    records=your_results,
    output_file="output",
    format='parquet'  # 'csv', 'json', 'parquet', 'hdf5', 'excel'
)
```

## Configuration Presets

| Preset | Workers | Memory/Worker | Cores | Use Case |
|--------|---------|---------------|-------|----------|
| `small` | 10 | 2GB | 1 | Testing, small datasets |
| `medium` | 50 | 4GB | 2 | Standard processing |
| `large` | 100 | 8GB | 4 | Large datasets |
| `gpu` | 10 | 16GB | 4 + 1 GPU | GPU computation |
| `memory_intensive` | 20 | 32GB | 8 | Memory-heavy tasks |

## Error Handling & Reliability

- **Automatic retries** with exponential backoff
- **Checkpoint recovery** for interrupted jobs  
- **Safe error handling** with configurable defaults
- **Resource monitoring** and adaptive scaling
- **Comprehensive logging** for debugging

## License

BSD 2-Clause License