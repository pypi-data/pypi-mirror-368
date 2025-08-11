from __future__ import annotations

import argparse
import asyncio
import hashlib
import ssl
import time
from pathlib import Path
from traceback import format_exc
from typing import Any, ClassVar, Dict, List
import yaml
import aiohttp
import certifi
import dask.dataframe as dd
import pandas as pd
import uvloop
from aiohttp import ClientSession
from aiohttp.http_exceptions import TransferEncodingError
from aiohttp.client_exceptions import ClientPayloadError
from os import cpu_count
from pydantic import BaseModel, ConfigDict, Field, computed_field

from wombat.multiprocessing.models import Prop, RequiresProps, ResultTaskPair
from wombat.multiprocessing.orchestrator import Orchestrator
from wombat.multiprocessing.worker import Worker
from wombat.multiprocessing.tasks import RetryableTask
from models import (
    ConcreteIndicator,
    ParametrizedIndicator,
    ParametrizedIndicatorList,
    UnparametrizedIndicatorList,
    AsyncFetchUrlTask
)
from constants import BASE_API_URL
from exceptions import EmptyDataPullException

from pydantic_partial import create_partial_model
# from foundry.transforms import Dataset

###############################################################################
# Helper Functions for Indicator State Transitions
###############################################################################

async def fetch_raw_indicators() -> UnparametrizedIndicatorList:
    """Fetch raw (unparametrized) indicators from the WHO GHO API."""
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(f"{BASE_API_URL}/Indicator/") as resp:
                raw = await resp.json()
        return UnparametrizedIndicatorList(**raw)
    except Exception:
        print(format_exc())
        raise

def inject_indicator_parameters(
    indicators: UnparametrizedIndicatorList, output_root: Path
) -> ParametrizedIndicatorList:
    """
    Convert raw indicators into parametrized indicators by injecting the download URL
    and the output file path.
    """
    return ParametrizedIndicatorList(
        value=[
            ParametrizedIndicator(
                code=indicator.code,
                name=indicator.name,
                url=f"{BASE_API_URL}/{indicator.code}",
                output_path=output_root / f"{indicator.code}.csv",
            )
            for indicator in indicators.value
        ]
    )

    return results

###############################################################################
# Asynchronous Download Task
###############################################################################

async def async_fetch_url(
    worker: Worker,
    indicator_name: str,
    url: str,
    output_path: Path,
    overwrite: bool,
    props: Dict[str, Prop]
) -> Any:
    """
    Download the indicator data from the provided URL and save it to output_path.
    If force is True, download regardless of file existence.
    This transitions the indicator from parametrized to concrete.
    """
    # Return value tuple elements
    status: Optional[int] = None
    exception: Optional[Exception] = None
    result: Optional[pd.DataFrame] = None

    # Check if the file already exists and if override is False
    if output_path.exists() and not overwrite:
        df = pd.read_csv(output_path)
        return 200, None, df

    session_prop: Prop = props["aiohttp_session"]
    session_instance: ClientSession = session_prop.instance
    try:
        # Download the data
        async with session_instance.get(url) as resp:
            # These sleeps prevent asyncio timeouts
            await asyncio.sleep(1)
            data = await resp.json()
            await asyncio.sleep(1)
            df = pd.DataFrame(data.get("value", []))
            # Inject a column for the indicator name
            df["IndicatorName"] = indicator_name
            if df.empty:
                # WHO GHO API returns empty data for some indicators
                raise EmptyDataPullException(url=url, indicator=indicator_name)
            # Save the data to the output path
            df.to_csv(output_path, index=False)
            return resp.status, None, df
    except EmptyDataPullException:
        return None, EmptyDataPullException, format_exc()
    except (asyncio.TimeoutError, RuntimeError, ClientPayloadError, TransferEncodingError) as e:
        await worker.initialize_prop(props, "aiohttp_session")
        # Reraise so that the task is retried by the pool
        raise e

###############################################################################
# Main Workflow
###############################################################################
def aggregate_indicators(output_root: Path, bronze_root: Path, dataset_name: str) -> dd.DataFrame:
    """
    Aggregate datasets into a single DataFrame.
    """
    # Rewrite the above indicator code checking as it now just reads all csvs from a single output root
    ddf = dd.read_csv(
        str(bronze_root / "*.csv"),
        assume_missing=True,
        dtype={
            "Dim3": "object",
            "Dim3Type": "object",
            "Comments": "object",
            "TimeDimensionValue": "object",
            "DataSourceDim": "object",
            "DataSourceDimType": "object",
            "Value": "object",
        },
    )
    df = ddf.compute()
    df.to_csv(str(output_root / f"{dataset_name}.csv"), index=False)

    # Foundry dataset generation
    # dataset = Dataset.get(dataset_name)
    # dataset.write_table(df)

async def main(output_root: Path, mode: str) -> Any:
    """
    Workflow:
      1. Fetch raw indicators.
      2. Inject parameters to obtain parametrized indicators.
      3. Identify which indicators are already concrete (downloaded) if in delta mode.
      4. Enqueue delta tasks (or all tasks in full mode).
      5. Combine downloaded data into a unified dataset.
    """
    output_root.mkdir(exist_ok=True, parents=True)
    bronze_root = output_root / "bronze" # Where the raw indicator data will be stored
    datasets_root = output_root / "datasets" # Where the final csv file used for creating the dataset will be stored
    bronze_root.mkdir(exist_ok=True, parents=True)

    # 0. Configuration
    overwrite = False

    # 1. Fetch raw indicators
    raw_indicators = await fetch_raw_indicators()

    # 2. Transition to parametrized indicators
    parametrized_indicators: ParametrizedIndicatorList = inject_indicator_parameters(raw_indicators, bronze_root)

    if mode == "delta":
        # Rewrite the above indicator code checking as it now uses an indicatorlist and not a dictionary
        concrete_indicators = [
            ConcreteIndicator(
                code=ind.code,
                name=ind.name,
                url=ind.url,
                language=ind.language,
                output_path=bronze_root / f"{ind.code}.csv",
            )
            for ind in parametrized_indicators.value
            if (bronze_root / f"{ind.code}.csv").exists()
        ]
        # 3. Identify which indicators are already concrete (downloaded) if in delta mode
        concrete_codes = {ci.code for ci in concrete_indicators}
        print(f"Already acquired indicators: {len(concrete_codes)}")
        delta_indicators = [ind for ind in parametrized_indicators.value if ind.code not in concrete_codes]
        overwrite = False
    elif mode == "full":
        # In full mode, re-download all indicators
        delta_indicators = parametrized_indicators.value
        overwrite = True
    else:
        raise ValueError("Invalid mode. Must be 'full' or 'delta'.")

    # Create download tasks for each indicator
    tasks = [
        AsyncFetchUrlTask(
            args=[
                ind.name,
                ind.url,
                ind.output_path,
                overwrite,
            ]
        )
        for ind in parametrized_indicators.value
    ]

    total_tasks = len(tasks)

    print(f"Enqueueing {total_tasks} tasks.")

    num_workers = min(cpu_count(), total_tasks // 2)
    if total_tasks == 0:
        print("You didn't generate any tasks.")
        return
    orchestrator = Orchestrator(
        # General config
        num_workers=num_workers,
        show_progress=True,
        # Define the task models our workers can handle
        task_models=[AsyncFetchUrlTask],
        # Define the actions our workers can take
        actions={"async_fetch_url": async_fetch_url},
        # Stand up a new aiohttp session for each worker using a context manager
        props={
            "aiohttp_session": Prop(
                # Function that stands up an instance of the prop
                initializer=init_aiohttp_session,
                # Whether or not to enter the prop as a context manager
                use_context_manager=True,
            )
        },
        # How many tasks can be executed per minute, gets divided by the number of workers
        tasks_per_minute_limit=500,
    )

    start_time = time.monotonic()
    # Enqueue tasks
    pending_enqueues = orchestrator.add_tasks(tasks)
    # Get tasks you couldn't enqueue
    # - e.g. When the model type isn't in the models of the orchestrator
    enqueue_failures: List[AsyncFetchUrlTask] = await pending_enqueues
    # Wait for the workers to stop and get the results
    job_results: List[ResultTaskPair] = await orchestrator.stop_workers()
    elapsed = time.monotonic() - start_time
    print(f"Delta tasks completed in {elapsed:.2f} seconds with {len(enqueue_failures)} enqueue failures.")

    # Convert job results to a queryable dataframe
    df = pd.DataFrame(list(map(lambda x: {**x.task.model_dump(), **dict(zip(["status_code", "exception"], (x.result[0], x.result[1])))}, job_results)))
    exceptions = set(df[~df["exception"].isna()]["exception"].unique().tolist())

    # Check for unexpected exceptions
    if exceptions != {EmptyDataPullException}:
        raise Exception(f"Unexpected exceptions: {exceptions - {EmptyDataPullException}}")

    # Save the task results to a CSV file
    df.to_csv(output_root / "task_results.csv", index=False)
    # Aggregate the downloaded data into a single dataset
    aggregate_indicators(output_root, bronze_root, "who_gho_full")

def init_aiohttp_session() -> ClientSession:
    """Initialize an aiohttp session for workers."""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    timeout = aiohttp.ClientTimeout(total=60, connect=60, sock_read=60, sock_connect=60)
    return ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), timeout=timeout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch WHO GHO indicators.")
    parser.add_argument(
        "--mode",
        choices=["full", "delta"],
        default="delta",
        help="Mode: 'full' to pull all indicators (force re-download), or 'delta' to pull only missing ones.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./who/data",
        help="Output directory for CSV files.",
    )
    args = parser.parse_args()

    output_root = Path(args.output)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main(output_root, args.mode))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
