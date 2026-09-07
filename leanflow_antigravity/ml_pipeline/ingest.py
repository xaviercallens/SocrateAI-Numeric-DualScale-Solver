import asyncio
import os
from datasets import load_dataset
from safetensors.numpy import save_file
import numpy as np

async def fetch_and_export_dataset(repo_id: str, split: str, output_path: str):
    """
    Fetches a real dataset from Hugging Face and exports the grid data to a zero-copy safetensors file.
    Uses streaming to pull just a subset/single record to demonstrate the pipeline.
    """
    print(f"Loading {repo_id} ({split}) in streaming mode...")
    
    # We use streaming=True so we don't download hundreds of GBs of data.
    # We just grab the first item for the PoC.
    dataset = await asyncio.to_thread(load_dataset, repo_id, split=split, streaming=True)
    
    print(f"Extracting first record and exporting to {output_path}...")
    
    iterator = iter(dataset)
    try:
        first_item = next(iterator)
    except StopIteration:
        print(f"Dataset {repo_id} is empty or inaccessible.")
        return

    # Extract tensors and cast to numpy arrays
    tensors = {}
    for key, val in first_item.items():
        if isinstance(val, list) or isinstance(val, (int, float)):
            tensors[key] = np.array(val)
        else:
            try:
                tensors[key] = np.asarray(val)
            except Exception as e:
                print(f"Skipping key {key} due to cast error: {e}")
                continue
    
    # Save the tensors using Safetensors for zero-copy memory-mapped loading
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_file(tensors, output_path)
    print(f"Successfully exported subset to {output_path}.")

async def main():
    # Using ITER tearing mode dataset for Anisotropy Phase 2 stress test
    targets = [
        {"repo_id": "plasma-physics/iter-m2n1-tearing-mode", "split": "train", "output": "data/iter_m2n1_grid.safetensors"}
    ]
    
    tasks = [
        fetch_and_export_dataset(target["repo_id"], target["split"], target["output"])
        for target in targets
    ]
    
    # Run fetches concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
