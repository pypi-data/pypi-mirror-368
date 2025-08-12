"""run_app.py

Entry point for the Alita project. This file loads configuration from config.yaml, sets up logging,
instantiates the ManagerAgent and Benchmark modules, and runs the experiment mode as specified in the configuration.
Experiment mode can be "benchmark" to run evaluation over datasets (GAIA, Mathvista, PathVQA) or "single_task"
to process a single natural language query.
"""

import json
import sys
from typing import Dict, Any

from calita.utils import get_global_config
from calita.manager_agent import ManagerAgent
from calita.benchmark import Benchmark

def main() -> None:
    try:
        # Load the global configuration from config.yaml using utils.
        config: Dict[str, Any] = get_global_config("config.yaml")
        
        # Determine experiment mode from configuration under misc; default to "benchmark".
        misc_config: Dict[str, Any] = config.get("misc", {})
        experiment_mode: str = misc_config.get("experiment_mode", "benchmark").strip().lower()
        
        # Instantiate ManagerAgent with configuration.
        manager_agent: ManagerAgent = ManagerAgent(config)
        # Instantiate Benchmark with ManagerAgent and configuration.
        benchmark: Benchmark = Benchmark(manager_agent, config)
        # Run benchmark experiment; this will process GAIA, Mathvista, and PathVQA datasets.
        metrics: Dict[str, Any] = benchmark.run_benchmark()
        # Print and log the aggregated benchmark results.
        print("Benchmark Results:")
        print(json.dumps(metrics, indent=4))

    except Exception as e:
        print(f"An error occurred in the application: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
