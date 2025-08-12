"""code_runner_e2b
This module defines the CodeRunner class. CodeRunner is responsible for executing a generated Python script
in an isolated Conda environment. It leverages EnvironmentManager to create and configure the environment
(e.g., install required dependencies) and then uses subprocess calls to execute the script. All outputs
(stdout and stderr) are captured and logged, with detailed error handling to support iterative refinement
in the overall CodeReAct loop.
"""

import logging
import re
from textwrap import dedent
from typing import Any, Dict, List, Tuple

from e2b_code_interpreter import Sandbox

from calita.utils.utils import handle_error


class CodeRunnerSandbox:
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the CodeRunner with configuration settings.

        Args:
            config (Dict[str, Any]): Global configuration dictionary loaded from config.yaml.
                Expected keys include environment configurations and optional execution timeout.
        """
        self.config: Dict[str, Any] = config

        # Set script execution timeout (in seconds) with a default value if not specified.
        self.code_exec_timeout: int = int(config.get("code_exec_timeout", 600))
        logging.info("E2bCodeRunner initialized with execution timeout of %d seconds", self.code_exec_timeout)

    def run_script(self, function_name:str, script: str, verify_code: str, dependencies: List[str]) -> Tuple[str, bool]:
        sandbox = None
        try:
            sandbox = Sandbox(timeout=self.code_exec_timeout)

            status = True
            for dependencie in dependencies:
                pip_cmd = f"pip install --quiet {dependencie}"
                logging.info(f"run_script: command=:  {pip_cmd}")
                sandbox.commands.run(pip_cmd)

            tool_code = re.sub(r'@mcp\.tool\(.*?\)\s+def', 'def', script, flags=re.DOTALL)
            run_code = f"{tool_code}\n{verify_code}"
            run_code = dedent(run_code)

            #logging.info(f"run_script: code=:\n{run_code}")
            execution = sandbox.run_code(run_code)
            if execution.error:
                error_name = execution.error.name
                error_value = execution.error.value
                logging.error(f"run_script: AI-generated code run in sandbox error: function_name={function_name}, error.name={execution.error.name}, error.value={execution.error.value}, error.traceback=\n{execution.error.traceback}")
                status = False
                result = f"AI-generated code run in sandbox error: function_name={function_name}, error.name={execution.error.name}, error.value={execution.error.value}"
            else:
                result = '. '.join(execution.logs.stdout)
                logging.info(f"run_script: AI-generated code success: function_name={function_name}, result={result}")

            return (result, status)
        except Exception as e:
            handle_error(e)
            # In case of unexpected error, return error message with failure status.
            return (f"Unexpected error: {str(e)}", False)
        finally:
            if(sandbox):
                sandbox.kill()