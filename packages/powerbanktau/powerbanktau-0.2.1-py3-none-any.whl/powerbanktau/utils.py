import os
import gc
import time
import json
import logging
from tqdm import tqdm
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
import pandas as pd
from dask_jobqueue import PBSCluster, SLURMCluster
from dask.distributed import Client, wait, LocalCluster, as_completed, performance_report
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
import csv

# Setup logging
logger = logging.getLogger('powerbanktau')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Cluster configuration presets
CLUSTER_PRESETS = {
    'small': {
        'num_workers': 10,
        'memory_size': '2GB',
        'cores': 1,
        'walltime': '3600'
    },
    'medium': {
        'num_workers': 50,
        'memory_size': '4GB',
        'cores': 2,
        'walltime': '7200'
    },
    'large': {
        'num_workers': 100,
        'memory_size': '8GB',
        'cores': 4,
        'walltime': '14400'
    },
    'gpu': {
        'num_workers': 10,
        'memory_size': '16GB',
        'cores': 4,
        'gpus': 1,
        'walltime': '7200'
    },
    'memory_intensive': {
        'num_workers': 20,
        'memory_size': '32GB',
        'cores': 8,
        'walltime': '14400'
    }
}

def launch_slurm_dask_cluster(memory_size="3GB", num_workers=25, queue="engineering",
                        walltime="7200", dashboard_address=":23154", cores=1, processes=1,
                        log_directory="~/../logging/dask-logs", working_directory=None,
                        gpus=0, gpu_module="miniconda/miniconda3-2023-environmentally"):
    """
    :param memory_size: The amount of memory allocated for each Dask worker (default is '3GB').
    :param num_workers: The number of workers to be created in the Dask cluster (default is 25).
    :param queue: The SLURM queue/partition to use for job scheduling (default is 'tamirQ').
    :param walltime: The maximum wall clock time for the job in seconds (default is '7200').
    :param dashboard_address: The address for the Dask dashboard (default is ':23154').
    :param cores: The number of CPU cores to allocate for each worker (default is 1).
    :param processes: The number of processes per worker (default is 1).
    :param log_directory: The directory to store Dask worker logs (default is '~/.dask-logs').
    :param working_directory: The working directory where the SLURM job will execute (default is None).
    :return: A tuple consisting of the Dask client and the SLURMCluster instance.
    """
    pre_executors = []
    if working_directory is not None:
        pre_executors.append(f"cd {working_directory}")

    if gpus > 0:
        # Load the specified GPU module before execution
        pre_executors.append(f"module load {gpu_module}")

    if gpus == 0:
        cluster = SLURMCluster(
            cores=cores,
            memory=memory_size,
            processes=processes,
            queue=queue,
            walltime=walltime,
            scheduler_options={"dashboard_address": dashboard_address},
            log_directory=log_directory,
            job_script_prologue=pre_executors
        )
    else:
        cluster = SLURMCluster(
            cores=cores,
            memory=memory_size,
            processes=processes,
            queue=queue,
            walltime=walltime,
            scheduler_options={"dashboard_address": dashboard_address},
            log_directory=log_directory,
            job_script_prologue=pre_executors,
            extra=[f"--gres=gpu:{gpus}"]
        )


    cluster.scale(num_workers)
    client = Client(cluster)
    return client, cluster


def launch_local_dask_cluster(memory_size="3GB", num_workers=25, dashboard_address=":23154", cores=1):
    cluster = LocalCluster(
        n_workers=num_workers,
        threads_per_worker=cores,
        memory_limit=memory_size,
        dashboard_address=dashboard_address,
    )
    client = Client(cluster)
    return client, cluster


def launch_pbs_dask_cluster(memory_size="3GB", num_workers=25, queue="tamirQ",
                        walltime="24:00:00", dashboard_address=":23154", cores=1, processes=1,
                        log_directory="~/.dask-logs", working_directory=None):
    """
    :param memory_size: The amount of memory to allocate for each worker node, specified as a string (e.g., "3GB").
    :param num_workers: The number of worker nodes to start in the PBS cluster.
    :param queue: The job queue to submit the PBS jobs to.
    :param walltime: The maximum walltime for each worker node, specified as a string in the format "HH:MM:SS".
    :param dashboard_address: The address where the Dask dashboard will be hosted.
    :param cores: The number of CPU cores to allocate for each worker node.
    :param processes: The number of processes to allocate for each worker node.
    :param log_directory: The directory where Dask will store log files.
    :param working_directory: The directory to change to before executing the job script on each worker node.
    :return: A tuple consisting of the Dask client and the PBS cluster objects.
    """
    pre_executors = []
    if working_directory is not None:
        pre_executors.append(f"cd {working_directory}")

    cluster = PBSCluster(
        cores=cores,
        memory=memory_size,
        processes=processes,
        queue=queue,
        walltime=walltime,
        scheduler_options={"dashboard_address": dashboard_address},
        log_directory=log_directory,
        job_script_prologue=pre_executors
    )

    cluster.scale(num_workers)
    client = Client(cluster)
    return client, cluster


def process_and_save_tasks(tasks, funct, dask_client, save_loc, file_index=0, capacity=1000, save_multiplier=10):
    def save_results(results, index):
        if results:
            df = pd.concat(results)
            df.to_csv(os.path.join(save_loc, f'results_{index}.csv'))
            return []

        return results

    futures, all_results = [], []
    for i, task in tqdm(enumerate(tasks), total=len(tasks)):
        futures.append(dask_client.submit(funct, task))
        if (i + 1) % capacity == 0:
            wait(futures)
            all_results.extend([f.result() for f in futures if f.status == 'finished' and f.result() is not None])
            futures = []

        if (i + 1) % (capacity * save_multiplier) == 0:
            all_results = save_results(all_results, file_index)
            file_index += 1
            gc.collect()

    wait(futures)
    all_results.extend([f.result() for f in futures if f.status == 'finished' and f.result() is not None])
    save_results(all_results, file_index)
    return all_results


def collect_results(result_dir):
    """
    :param result_dir: Directory containing result CSV files to be collected
    :return: A concatenated pandas DataFrame containing data from all CSV files in the result directory
    """
    result_path = Path(result_dir)
    data = [pd.read_csv(file) for file in result_path.iterdir()]
    return pd.concat(data)


def restart_checkpoint(result_dir, patern='*'):
    """
    :param patern:
    :param result_dir: Directory path where checkpoint result files are stored.
    :return: A tuple containing a list of unique mutation IDs processed from the checkpoint files and the highest checkpoint index found.
    """
    result_path = Path(result_dir)
    files = sorted(result_path.glob(patern), key=lambda x: int(x.stem.split('_')[-1]), reverse=True)

    if not files:
        return [], 0

    try:
        data = []
        latest_file = files[0]
        for file in files:
            data.append(pd.read_csv(file))
        processed_muts = pd.concat(data).mut_id.unique().tolist()
        highest_checkpoint = int(latest_file.stem.split('_')[-1])
        return processed_muts, highest_checkpoint

    except Exception as e:
        print(f"Error processing file {files}: {e}")
        return [], 0


def launch_dask_cluster(cluster_type: str = "local", **kwargs) -> tuple:
    """
    Unified function to launch different types of Dask clusters.
    
    :param cluster_type: Type of cluster ("local", "slurm", "pbs")
    :param kwargs: Arguments specific to the cluster type
    :return: A tuple of (client, cluster)
    """
    if cluster_type == "local":
        return launch_local_dask_cluster(**kwargs)
    elif cluster_type == "slurm":
        return launch_slurm_dask_cluster(**kwargs)
    elif cluster_type == "pbs":
        return launch_pbs_dask_cluster(**kwargs)
    else:
        raise ValueError(f"Unknown cluster type: {cluster_type}")


def launch_local_cluster_from_job(n_workers: Optional[int] = None, 
                                   threads_per_worker: Optional[int] = None,
                                   memory_per_worker: Optional[str] = None,
                                   dashboard_address: str = ":8787") -> tuple:
    """
    Launch a local Dask cluster optimized for running within an existing job allocation.
    Automatically detects available resources if not specified.
    
    :param n_workers: Number of workers (if None, uses available CPU cores)
    :param threads_per_worker: Threads per worker (if None, calculates based on available cores)
    :param memory_per_worker: Memory per worker (if None, divides available memory)
    :param dashboard_address: Dashboard address
    :return: A tuple of (client, cluster)
    """
    import multiprocessing
    import psutil
    
    if n_workers is None:
        n_workers = multiprocessing.cpu_count()
    
    if threads_per_worker is None:
        threads_per_worker = max(1, multiprocessing.cpu_count() // n_workers)
    
    if memory_per_worker is None:
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        memory_per_worker = f"{available_memory_gb / n_workers:.1f}GB"
    
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        memory_limit=memory_per_worker,
        dashboard_address=dashboard_address,
        silence_logs=40
    )
    
    client = Client(cluster)
    return client, cluster


def process_with_dask_pipeline(
    items: List[Any],
    process_func: Callable,
    output_file: str,
    cluster_config: Optional[Dict[str, Any]] = None,
    func_kwargs: Optional[Dict[str, Any]] = None,
    default_result: Any = None,
    batch_size: int = 1000,
    save_interval: int = 100,
    item_to_dict: Optional[Callable] = None,
    cluster_type: str = "local",
    append_mode: bool = True
) -> str:
    """
    Complete pipeline that spawns a Dask cluster, processes items, and saves results incrementally.
    
    :param items: List of items to process
    :param process_func: Function to apply to each item
    :param output_file: Path to save results (CSV format)
    :param cluster_config: Configuration for the cluster (passed to launch functions)
    :param func_kwargs: Additional kwargs to pass to process_func
    :param default_result: Default value to use if processing fails
    :param batch_size: Number of futures to maintain at once
    :param save_interval: Save results every N processed items
    :param item_to_dict: Optional function to convert item to dict for saving
    :param cluster_type: Type of cluster to launch ("local", "slurm", "pbs")
    :param append_mode: Whether to append to existing file or overwrite
    :return: Path to the output file
    """
    cluster_config = cluster_config or {}
    func_kwargs = func_kwargs or {}
    
    client, cluster = launch_dask_cluster(cluster_type, **cluster_config)
    
    try:
        def safe_process(item):
            try:
                return process_func(item, **func_kwargs)
            except Exception as e:
                print(f"Error processing item: {e}")
                return default_result
        
        futures = []
        results_buffer = []
        processed_count = 0
        file_exists = os.path.exists(output_file) and append_mode
        
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        
        for i, item in tqdm(enumerate(items), total=len(items), desc="Submitting tasks"):
            future = client.submit(safe_process, item)
            future.item = item
            futures.append(future)
            
            if len(futures) >= batch_size:
                for completed_future in as_completed(futures[:batch_size]):
                    result = completed_future.result()
                    item_data = completed_future.item
                    
                    # Check if result is already a DataFrame
                    if isinstance(result, pd.DataFrame):
                        record = result
                    elif item_to_dict:
                        record = item_to_dict(item_data, result)
                    else:
                        record = {"item": str(item_data), "result": result}
                    
                    results_buffer.append(record)
                    processed_count += 1
                    
                    if processed_count % save_interval == 0:
                        _save_results_to_csv(results_buffer, output_file, file_exists)
                        results_buffer = []
                        file_exists = True
                
                futures = futures[batch_size:]
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Collecting remaining"):
            result = future.result()
            item_data = future.item
            
            # Check if result is already a DataFrame
            if isinstance(result, pd.DataFrame):
                record = result
            elif item_to_dict:
                record = item_to_dict(item_data, result)
            else:
                record = {"item": str(item_data), "result": result}
            
            results_buffer.append(record)
            processed_count += 1
            
            if processed_count % save_interval == 0:
                _save_results_to_csv(results_buffer, output_file, file_exists)
                results_buffer = []
                file_exists = True
        
        if results_buffer:
            _save_results_to_csv(results_buffer, output_file, file_exists)
        
        print(f"Processing complete. Results saved to {output_file}")
        return output_file
        
    finally:
        client.close()
        cluster.close()


def _save_results_to_csv(records: List[Union[Dict, pd.DataFrame]], output_file: str, append: bool = True):
    """Helper function to save records to CSV."""
    if not records:
        return
    
    # Check if records contain DataFrames
    if records and isinstance(records[0], pd.DataFrame):
        # If records are DataFrames, concatenate them
        df = pd.concat(records, ignore_index=True)
    else:
        # Otherwise, create DataFrame from dictionaries
        df = pd.DataFrame(records)
    
    mode = 'a' if append else 'w'
    header = not append
    
    df.to_csv(output_file, mode=mode, header=header, index=False)


def process_dataframe_with_dask(
    df: pd.DataFrame,
    process_func: Callable,
    output_file: str,
    cluster_config: Optional[Dict[str, Any]] = None,
    func_kwargs: Optional[Dict[str, Any]] = None,
    default_result: Any = None,
    batch_size: int = 1000,
    save_interval: int = 100,
    cluster_type: str = "local",
    row_to_dict: Optional[Callable] = None,
    append_mode: bool = True
) -> str:
    """
    Process a DataFrame row by row using Dask, with incremental saving.
    
    :param df: DataFrame to process
    :param process_func: Function to apply to each row
    :param output_file: Path to save results
    :param cluster_config: Configuration for the cluster
    :param func_kwargs: Additional kwargs for process_func
    :param default_result: Default value if processing fails
    :param batch_size: Number of futures to maintain
    :param save_interval: Save results every N items
    :param cluster_type: Type of cluster to launch
    :param row_to_dict: Function to convert row and result to dict
    :param append_mode: Whether to append to existing file
    :return: Path to output file
    """
    
    def default_row_to_dict(row, result):
        row_dict = row.to_dict() if hasattr(row, 'to_dict') else {"row": str(row)}
        row_dict["result"] = result
        return row_dict
    
    row_to_dict = row_to_dict or default_row_to_dict
    
    rows = [row for _, row in df.iterrows()]
    
    return process_with_dask_pipeline(
        items=rows,
        process_func=process_func,
        output_file=output_file,
        cluster_config=cluster_config,
        func_kwargs=func_kwargs,
        default_result=default_result,
        batch_size=batch_size,
        save_interval=save_interval,
        item_to_dict=row_to_dict,
        cluster_type=cluster_type,
        append_mode=append_mode
    )


def launch_preset_cluster(preset: str = 'medium', cluster_type: str = 'pbs', **override_kwargs) -> Tuple[Client, Any]:
    """
    Launch a cluster using predefined configuration presets.
    
    :param preset: Preset name ('small', 'medium', 'large', 'gpu', 'memory_intensive')
    :param cluster_type: Type of cluster ('local', 'slurm', 'pbs')
    :param override_kwargs: Override preset values with custom settings
    :return: Tuple of (client, cluster)
    """
    if preset not in CLUSTER_PRESETS:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(CLUSTER_PRESETS.keys())}")
    
    config = CLUSTER_PRESETS[preset].copy()
    config.update(override_kwargs)
    
    logger.info(f"Launching {cluster_type} cluster with '{preset}' preset")
    return launch_dask_cluster(cluster_type, **config)


def get_cluster_status(client: Client) -> Dict[str, Any]:
    """
    Get detailed cluster status including worker health and resource usage.
    
    :param client: Dask client
    :return: Dictionary with cluster status information
    """
    try:
        scheduler_info = client.scheduler_info()
        workers_info = scheduler_info.get('workers', {})
        
        total_memory = sum(w.get('memory_limit', 0) for w in workers_info.values())
        used_memory = sum(w.get('memory', 0) for w in workers_info.values())
        
        status = {
            'workers': len(workers_info),
            'total_threads': sum(w.get('nthreads', 0) for w in workers_info.values()),
            'total_memory_gb': total_memory / (1024**3),
            'used_memory_gb': used_memory / (1024**3),
            'memory_usage_percent': (used_memory / total_memory * 100) if total_memory > 0 else 0,
            'dashboard_link': client.dashboard_link,
            'tasks_processing': len(client.processing()),
            'tasks_in_memory': len(client.who_has()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add per-worker status
        status['worker_details'] = []
        for worker_id, worker_info in workers_info.items():
            status['worker_details'].append({
                'id': worker_id,
                'threads': worker_info.get('nthreads', 0),
                'memory_gb': worker_info.get('memory_limit', 0) / (1024**3),
                'cpu_percent': worker_info.get('cpu', 0),
                'status': 'healthy' if worker_info.get('status') == 'OK' else 'unhealthy'
            })
        
        return status
    except Exception as e:
        logger.error(f"Error getting cluster status: {e}")
        return {'error': str(e)}


def monitor_progress(futures: List, interval: int = 5, show_progress: bool = True) -> Dict[str, Any]:
    """
    Monitor progress of futures with live updates.
    
    :param futures: List of Dask futures
    :param interval: Update interval in seconds
    :param show_progress: Show progress bar
    :return: Summary statistics
    """
    total = len(futures)
    completed = 0
    failed = 0
    results = []
    
    pbar = tqdm(total=total, desc="Processing") if show_progress else None
    
    start_time = time.time()
    for future in as_completed(futures):
        try:
            result = future.result()
            results.append(result)
            completed += 1
        except Exception as e:
            logger.warning(f"Task failed: {e}")
            failed += 1
        
        if pbar:
            pbar.update(1)
            pbar.set_postfix({'completed': completed, 'failed': failed})
    
    if pbar:
        pbar.close()
    
    elapsed = time.time() - start_time
    
    return {
        'total': total,
        'completed': completed,
        'failed': failed,
        'success_rate': completed / total if total > 0 else 0,
        'elapsed_seconds': elapsed,
        'tasks_per_second': total / elapsed if elapsed > 0 else 0,
        'results': results
    }


def process_with_retry(func: Callable, item: Any, max_retries: int = 3, 
                       backoff_factor: float = 2.0, initial_delay: float = 1.0,
                       **kwargs) -> Any:
    """
    Process item with automatic retry on failure using exponential backoff.
    
    :param func: Function to execute
    :param item: Item to process
    :param max_retries: Maximum number of retry attempts
    :param backoff_factor: Multiplier for delay between retries
    :param initial_delay: Initial delay in seconds
    :param kwargs: Additional arguments for func
    :return: Result of func(item, **kwargs)
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            return func(item, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_retries + 1} attempts failed for item")
    
    raise last_exception


def save_results_multi_format(records: List[Dict], output_file: str, 
                              format: str = 'csv', append: bool = False) -> None:
    """
    Save results in multiple formats.
    
    :param records: List of dictionaries to save
    :param output_file: Output file path (extension will be adjusted based on format)
    :param format: Output format ('csv', 'json', 'parquet', 'hdf5', 'excel')
    :param append: Whether to append (where supported)
    """
    if not records:
        return
    
    df = pd.DataFrame(records)
    base_path = os.path.splitext(output_file)[0]
    
    if format == 'csv':
        mode = 'a' if append else 'w'
        header = not append or not os.path.exists(f"{base_path}.csv")
        df.to_csv(f"{base_path}.csv", mode=mode, header=header, index=False)
    
    elif format == 'json':
        mode = 'a' if append else 'w'
        with open(f"{base_path}.json", mode) as f:
            df.to_json(f, orient='records', lines=True)
    
    elif format == 'parquet':
        df.to_parquet(f"{base_path}.parquet", engine='pyarrow', compression='snappy')
    
    elif format == 'hdf5':
        mode = 'a' if append else 'w'
        df.to_hdf(f"{base_path}.h5", key='data', mode=mode, format='table')
    
    elif format == 'excel':
        with pd.ExcelWriter(f"{base_path}.xlsx", mode='a' if append and os.path.exists(f"{base_path}.xlsx") else 'w') as writer:
            sheet_name = f'data_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    logger.info(f"Saved {len(records)} records to {base_path}.{format}")


def track_resource_usage(client: Client, duration: int = 60, interval: int = 5) -> List[Dict]:
    """
    Track resource usage over time.
    
    :param client: Dask client
    :param duration: Total duration to track in seconds
    :param interval: Sampling interval in seconds
    :return: List of resource usage snapshots
    """
    usage_history = []
    end_time = time.time() + duration
    
    while time.time() < end_time:
        status = get_cluster_status(client)
        usage_history.append(status)
        time.sleep(interval)
    
    return usage_history


def setup_adaptive_cluster(cluster: Any, minimum: int = 1, maximum: int = 100,
                          wait_count: int = 3, interval: str = '2s') -> None:
    """
    Enable adaptive scaling for a cluster.
    
    :param cluster: Dask cluster object
    :param minimum: Minimum number of workers
    :param maximum: Maximum number of workers
    :param wait_count: Number of intervals to wait before scaling
    :param interval: Time between checks
    """
    try:
        cluster.adapt(
            minimum=minimum,
            maximum=maximum,
            wait_count=wait_count,
            interval=interval
        )
        logger.info(f"Adaptive scaling enabled: {minimum}-{maximum} workers")
    except Exception as e:
        logger.error(f"Failed to enable adaptive scaling: {e}")


def process_with_checkpoint(items: List[Any], process_func: Callable,
                           checkpoint_dir: str, output_file: str,
                           cluster_config: Optional[Dict] = None,
                           func_kwargs: Optional[Dict] = None,
                           cluster_type: str = 'local',
                           checkpoint_interval: int = 100) -> str:
    """
    Process items with automatic checkpoint recovery.
    
    :param items: Items to process
    :param process_func: Processing function
    :param checkpoint_dir: Directory for checkpoints
    :param output_file: Final output file
    :param cluster_config: Cluster configuration
    :param func_kwargs: Arguments for process_func
    :param cluster_type: Type of cluster
    :param checkpoint_interval: Save checkpoint every N items
    :return: Path to output file
    """
    checkpoint_path = Path(checkpoint_dir)
    checkpoint_path.mkdir(parents=True, exist_ok=True)
    
    # Load checkpoint if exists
    checkpoint_file = checkpoint_path / 'checkpoint.json'
    processed_items = set()
    
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
            processed_items = set(checkpoint_data.get('processed', []))
            logger.info(f"Resuming from checkpoint: {len(processed_items)} items already processed")
    
    # Filter out already processed items
    remaining_items = [item for item in items if str(item) not in processed_items]
    
    if not remaining_items:
        logger.info("All items already processed")
        return output_file
    
    # Process remaining items
    def process_and_checkpoint(item):
        result = process_func(item, **(func_kwargs or {}))
        
        # Update checkpoint periodically
        processed_items.add(str(item))
        if len(processed_items) % checkpoint_interval == 0:
            with open(checkpoint_file, 'w') as f:
                json.dump({'processed': list(processed_items)}, f)
        
        return result
    
    # Run processing
    output_file = process_with_dask_pipeline(
        items=remaining_items,
        process_func=process_and_checkpoint,
        output_file=output_file,
        cluster_config=cluster_config,
        cluster_type=cluster_type,
        append_mode=True
    )
    
    # Clean up checkpoint on success
    checkpoint_file.unlink(missing_ok=True)
    logger.info("Processing completed, checkpoint removed")
    
    return output_file


@contextmanager
def managed_cluster(cluster_type: str = 'local', **kwargs):
    """
    Context manager for automatic cluster setup and cleanup.
    
    Usage:
        with managed_cluster('pbs', num_workers=50) as (client, cluster):
            # Use client for processing
            results = client.map(func, items)
    
    :param cluster_type: Type of cluster
    :param kwargs: Arguments for cluster creation
    :yields: Tuple of (client, cluster)
    """
    client = None
    cluster = None
    
    try:
        logger.info(f"Starting managed {cluster_type} cluster")
        client, cluster = launch_dask_cluster(cluster_type, **kwargs)
        yield client, cluster
    except Exception as e:
        logger.error(f"Error in managed cluster: {e}")
        raise
    finally:
        if client:
            client.close()
            logger.info("Client closed")
        if cluster:
            cluster.close()
            logger.info("Cluster closed")


def setup_logging(level: str = 'INFO', log_file: Optional[str] = None,
                 format_string: Optional[str] = None) -> logging.Logger:
    """
    Configure logging for the library.
    
    :param level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    :param log_file: Optional file to write logs to
    :param format_string: Custom format string for log messages
    :return: Configured logger
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")
    
    return logger


def benchmark_cluster(client: Client, task_count: int = 100,
                     data_size: int = 1000) -> Dict[str, Any]:
    """
    Benchmark cluster performance with synthetic tasks.
    
    :param client: Dask client
    :param task_count: Number of tasks to run
    :param data_size: Size of data per task
    :return: Benchmark results
    """
    import numpy as np
    
    logger.info(f"Starting benchmark: {task_count} tasks, {data_size} data points each")
    
    def benchmark_task(x):
        # Synthetic computation
        data = np.random.random(data_size)
        return np.sum(data ** 2)
    
    start_time = time.time()
    futures = client.map(benchmark_task, range(task_count))
    results = client.gather(futures)
    end_time = time.time()
    
    elapsed = end_time - start_time
    
    return {
        'task_count': task_count,
        'data_size': data_size,
        'total_time_seconds': elapsed,
        'tasks_per_second': task_count / elapsed,
        'average_task_time': elapsed / task_count,
        'cluster_info': get_cluster_status(client)
    }

