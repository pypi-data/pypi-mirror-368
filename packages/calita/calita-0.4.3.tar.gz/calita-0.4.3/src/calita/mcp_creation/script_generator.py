"""script_generator.py

This module implements the ScriptGenerator class, which takes a tool specification
(from MCPBrainstorm) and a list of external resource items (from ResearchAgent) to generate a
self-contained executable Python script. The generated script includes not only the
desired functionality but also the environment setup commands (such as conda environment
creation and dependency installation).

The script generation is powered by an LLM API (via OpenAI's ChatCompletion interface),
using a prompt template loaded from the path specified in the configuration (under
agent.script_gen_prompt_template). This module relies on shared utilities for logging,
configuration loading, and error handling.
"""

import logging
import re
from typing import Any, Dict, List

from calita.utils.model_client import ModelClientFactory, ModelClient
from calita.utils.utils import read_template, handle_error


class ScriptGenerator:
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the ScriptGenerator with configuration settings.

        Loads the script generation prompt template from the file specified under
        agent.script_gen_prompt_template in the configuration. Creates an appropriate
        model client based on the configured model (OpenAI or Anthropic).

        Args:
            config (Dict[str, Any]): Configuration dictionary loaded from config.yaml.
                Expected keys:
                    - agent.script_gen_prompt_template: File path for script generation prompt template.
                    - agent.primary_llm: The primary LLM model name to use.
                    - api.openai_api_key: API key for OpenAI (if using OpenAI models).
                    - api.anthropic_api_key: API key for Anthropic (if using Anthropic models).
                    - Optional: api.temperature: Temperature for API calls (default 0.7).
                    - Optional: api.max_tokens: Maximum tokens for the API response (default 300).
        """
        try:
            # Agent configuration
            agent_config: Dict[str, Any] = config.get("agent", {})
            self.prompt_template_path: str = agent_config.get(
                "script_gen_prompt_template", "templates/script_template.txt"
            )
            self.prompt_template: str = read_template(self.prompt_template_path)
            
            # API configuration
            api_config: Dict[str, Any] = config.get("api", {})
            self.temperature: float = float(api_config.get("temperature", 0.7))
            self.max_tokens: int = int(api_config.get("max_tokens", 16384))

            # added by zhangx, use coder LLM
            model = config.get("agent", {}).get("coder_llm")
            self.model  = model if model else config.get("agent", {}).get("primary_llm")
            # end

            # Initialize model client using factory
            self.model_client: ModelClient = ModelClientFactory.create_client(config)

            logging.info("ScriptGenerator initialized with model: %s, prompt template: %s",
                         self.model_client.get_model_name(), self.prompt_template_path)
        except Exception as e:
            handle_error(e)

    def generate_script(self, spec: Dict[str, Any], resources, verify_context: str) -> Dict[str, str]:
        """
        Generate a self-contained Python script based on the given specification and external resources.

        This method constructs a prompt by inserting the task description and tool specifications
        from 'spec' along with external resource context (if any) into the loaded prompt template.
        It then calls the LLM API to generate the script, processes the response to remove any extraneous 
        formatting (like markdown code fences), and returns the cleaned Python script.

        Args:
            spec (Dict[str, Any]): Dictionary containing the tool specification.
                Expected keys include:
                    - "task_description": Description of the task.
                    - "mcp_spec": Functional specifications or design details.
            resources: External resource items. Can be either:
                - List[Dict[str, Any]]: Legacy format with list of resource dictionaries
                - Dict[str, Any]: Enhanced format with 'web_results', 'github_repos', 'pypi_packages' keys

        Returns:
            Dict[str, str]: Dictionary containing 'script' and 'requirements' keys.
        """
        try:
            # Extract task and tool specification details from the spec dictionary.
            task_description: str = spec.get("task_description", "No task description provided.")
            tool_spec: str = spec.get("mcp_spec", "No specific tool specification provided.")
            
            # Combine external resource items into a coherent text block.
            external_context = self._format_resources(resources)

            # Format the prompt using the loaded template.
            # The template should have placeholders:
            # {task_description}, {tool_spec}, and {external_context}
            # prompt: str = self.prompt_template.format(
            #     task_description=task_description,
            #     tool_spec=tool_spec,
            #     external_context=external_context
            # )

            prompt = self.prompt_template.replace("{task_description}", task_description)
            prompt = prompt.replace("{tool_spec}", tool_spec)
            prompt = prompt.replace("{external_context}", external_context)
            prompt = prompt.replace("{verify_context}", verify_context)

            logging.info("generate_script: Task description: %s", task_description)
            logging.debug("Constructed script generation prompt: %s", prompt)

            # Call LLM API using unified client interface
            messages = [{"role": "user", "content": prompt}]
            response_text: str = self.model_client.create_completion(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                model=self.model, # add by zhangx
            )
            logging.info("Generated script from LLM: %s", response_text)

            # Clean the LLM output to remove markdown fences or extraneous formatting.
            # Also extract requirements if XML format is used

            result = self.parse_code(response_text)
            logging.debug("Generated script: %s", result["script"])

            return result

        except Exception as e:
            handle_error(e)
            # In case error handling does not raise, return empty result.
            return {'script': '', 'requirements': ''}
    
    def _format_resources(self, resources) -> str:
        """
        Format resources into a coherent text block for the prompt.
        
        Args:
            resources: Can be either legacy list format or enhanced dict format
            
        Returns:
            str: Formatted resource context string
        """
        if not resources:
            return "No external resources provided."
            
        # Handle enhanced search format (dict with categorized results)
        if isinstance(resources, dict):
            resource_lines: List[str] = []
            
            # Format web search results
            web_results = resources.get('web_results', [])
            if web_results:
                resource_lines.append("=== Web Search Results ===")
                for result in web_results:
                    title = result.get('title', '').strip()
                    url = result.get('url', '').strip()
                    snippet = result.get('snippet', '').strip()
                    resource_entry = f"Title: {title}\nURL: {url}\nSnippet: {snippet}"
                    resource_lines.append(resource_entry)
            
            # Format GitHub repositories
            github_repos = resources.get('github_repos', [])
            if github_repos:
                resource_lines.append("=== GitHub Repositories ===")
                for repo in github_repos:
                    name = repo.get('name', '').strip()
                    url = repo.get('url', '').strip()
                    description = repo.get('description', '').strip()
                    stars = repo.get('stars', '')
                    resource_entry = f"Repository: {name}\nURL: {url}\nDescription: {description}\nStars: {stars}"
                    resource_lines.append(resource_entry)
            
            # Format PyPI packages
            pypi_packages = resources.get('pypi_packages', [])
            if pypi_packages:
                resource_lines.append("=== PyPI Packages ===")
                for package in pypi_packages:
                    name = package.get('name', '').strip()
                    version = package.get('version', '').strip()
                    description = package.get('description', '').strip()
                    resource_entry = f"Package: {name}\nVersion: {version}\nDescription: {description}"
                    resource_lines.append(resource_entry)
            
            return "\n---\n".join(resource_lines) if resource_lines else "No external resources provided."
        
        # Handle legacy format (list of resource dicts)
        elif isinstance(resources, list):
            resource_lines: List[str] = []
            for resource in resources:
                title: str = resource.get("title", "").strip()
                url: str = resource.get("url", "").strip()
                snippet: str = resource.get("snippet", "").strip()
                resource_entry: str = f"Title: {title}\nURL: {url}\nSnippet: {snippet}"
                resource_lines.append(resource_entry)
            return "\n---\n".join(resource_lines) if resource_lines else "No external resources provided."
        
        else:
            return "No external resources provided."

    def parse_code(self, script_text: str) -> dict[str, str]:
        """
        Clean the generated script text by removing markdown code fences, JSON wrappers, and extraneous formatting.
        Also handles XML format with separate requirements and code sections.

        Args:
            script_text (str): The raw script text returned by the LLM API.

        Returns:
            str: The cleaned script text.
        """
        generate_code = {
            'function_name': '',
            'script': '',
            'verify_code': '',
            'requirements': ''
        }
        try:
            cleaned_script = script_text.strip()

            # Check if the response contains XML format with requirements and code sections
            if cleaned_script:
                logging.info("Extracted requirements and code from XML format")

                requirements_match = re.search(r'<requirements>(.*?)</requirements>', cleaned_script, re.DOTALL)
                code_match = re.search(r'<code>(.*?)</code>', cleaned_script, re.DOTALL)
                function_name_match = re.search(r'<function_name>(.*?)</function_name>', cleaned_script, re.DOTALL)
                verify_code_match = re.search(r'<verify_code>(.*?)</verify_code>', cleaned_script, re.DOTALL)


                if requirements_match:
                    generate_code['requirements'] = requirements_match.group(1).strip()

                if code_match:
                    generate_code['script'] = code_match.group(1).strip()

                if function_name_match:
                    generate_code['function_name'] = function_name_match.group(1).strip()

                if verify_code_match:
                    generate_code['verify_code'] = verify_code_match.group(1).strip()

        except Exception as e:
            logging.error("Error during script cleanup: %s", str(e))

        return generate_code