# Description: This script contains multiprocessing functions to speed up the data generation process.
import os
import time 

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

def robust_multiprocessing(worker, tasks):
    results = []
    pool_count = 3*os.cpu_count()//4
    with ProcessPoolExecutor(max_workers=pool_count) as executor:
        for i in tqdm(range(0, len(tasks), pool_count*4),  desc="Processing..."):
            sub_tasks = tasks[i:i+pool_count*4]
            results.extend(
                list(executor.map(worker, *zip(*sub_tasks)))
            )

        if len(tasks) > len(results):
            results.extend(
                list(executor.map(worker, *zip(*tasks[len(results):])))
            )
        
    return results

def fast_multiprocessing(worker, tasks, max_workers=os.cpu_count()//2):
    results = []
    with ProcessPoolExecutor(max_workers) as executor:
    # with ProcessPoolExecutor(max_workers=1) as executor:
        # Submit all your tasks to the executor
        future_tasks = set()
        for task in tqdm(tasks):
            future_tasks.add(executor.submit(worker, *task))
            time.sleep(0.001)
        with tqdm(total=len(tasks), desc="Processing...") as progress_bar:
            for future in as_completed(future_tasks):
                # Append the result to a list
                results.append(future.result())
                progress_bar.update(1)
    return results

def fast_multiprocessing_process_error(worker, tasks, max_workers=os.cpu_count() // 2):
    results = []
    errors = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all your tasks to the executor
        future_tasks = {executor.submit(worker, *task): task for task in tqdm(tasks, desc="Submitting tasks")}
        time.sleep(0.001)  # This sleep is not necessary and can be removed

        with tqdm(total=len(tasks), desc="Processing...", dynamic_ncols=True) as progress_bar:
            for future in as_completed(future_tasks):
                try:
                    # Append the result to a list
                    result = future.result()
                    results.append(result)
                    progress_bar.update(1)
                except Exception as e:
                    # Capture any exceptions raised by the worker function
                    associated_task = future_tasks[future]
                    errors.append((associated_task, e))
                    progress_bar.update(1)  # Update the progress bar even if there's an error

    if errors:
        # Handle errors if any occurred
        print("Detailed errors occurred during processing:")
        for task, error in errors:
            print(f"Error: {error}")

    return results


def fast_multiprocessing_without_return(worker, tasks, max_workers=os.cpu_count()//2):
    results = []
    errors = []
    
    with ProcessPoolExecutor(max_workers) as executor:
    # with ProcessPoolExecutor(max_workers=1) as executor:
        # Submit all your tasks to the executor
        future_tasks = set()
        for task in tqdm(tasks):
            future_tasks.add(executor.submit(worker, *task))
            time.sleep(0.001)
        with tqdm(total=len(tasks), desc="Processing...") as progress_bar:
            for future in as_completed(future_tasks):
                try:
                    # Append the result to a list
                    results.append(1)
                    progress_bar.update(1)
                except Exception as e:
                    # Capture any exceptions raised by the worker function
                    associated_task = future_tasks[future]
                    errors.append((associated_task, e))
                    print(f"Error occurred while processing task {associated_task[0].function_name}: {e}")
                    progress_bar.update(1)  # Update the progress bar even if 
    if errors:
        # Handle errors if any occurred
        print("Detailed errors occurred during processing:")
        for task, error in errors:
            print(f"Task: {task}, Error: {error}")
    
    return results
