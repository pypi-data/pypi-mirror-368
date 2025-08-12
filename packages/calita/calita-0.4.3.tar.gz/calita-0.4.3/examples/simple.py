from calita.manager_agent import ManagerAgent
from calita.utils.utils import get_global_config, setup_logging

if __name__ == "__main__":
    # Load configuration
    config = get_global_config("config.yaml")
    setup_logging(config)

    # Initialize the agent
    manager = ManagerAgent(config)

    result = manager.generate("Create a function to sort a list of numbers, sort [6,8,7,5]")
    print(result)