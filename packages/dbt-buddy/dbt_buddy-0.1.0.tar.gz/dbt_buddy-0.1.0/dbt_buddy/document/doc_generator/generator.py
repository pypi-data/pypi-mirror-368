import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from dbt.cli.main import dbtRunner, dbtRunnerResult
from dbt.contracts.graph.nodes import ModelNode
from dotenv import get_key
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk._models.completions.model import GPTModel
from yandex_cloud_ml_sdk._models.completions.result import GPTModelResult

from dbt_buddy.document.doc_generator import constants

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DBTDocGenerator:
    """
    Class for generating documentation for dbt models using YandexGPT.
    """

    def __init__(
        self,
        model: str,
        examples: bool,
        save: bool,
        verbose: bool,
        project_dir: Optional[Path],
        profiles_dir: Optional[Path],
    ):
        """
        Initialize DBTDocGenerator with parameters.

        :param model: The dbt model name.
        :param examples: Flag to include examples in documentation.
        :param save: Flag to save documentation to file.
        :param verbose: Flag to enable verbose output.
        :param project_dir(optional): Path to the dbt-project directory.
        :param profiles_dir(optional): Path to the profiles.yml file.
        """
        self.dbt_cli = dbtRunner()
        self.model = model
        self.examples = examples
        self.save = save
        self.verbose = verbose
        self.project_dir = os.path.expanduser(project_dir) if project_dir else Path.cwd()
        self.profiles_dir = os.path.expanduser(profiles_dir) if profiles_dir else Path.cwd()

    def _get_dotenv_secret(self, secret_name: str) -> str:
        """
        Get a secret value from the .env file.

        :param secret_name: The name of the secret to retrieve.
        :returns:The value of the secret.
        """
        dotenv_path: str = os.path.join(self.project_dir, ".env")
        secret_value: Union[str, None] = get_key(dotenv_path, secret_name)
        if not secret_value:
            sys.exit()
        return secret_value

    def _get_dbt_cli_results(self, extra_args: list) -> ModelNode:
        """
        Get the results of running dbt CLI commands.

        :param extra_args: Extra arguments for the dbt CLI.
        :returns: The raw code result.
        """
        cli_args: list = constants.DBT_CLI_ARGS + extra_args
        dbt_compile_result: dbtRunnerResult = self.dbt_cli.invoke(cli_args)

        try:
            raw_code: ModelNode = dbt_compile_result.result.results[0].node
            return raw_code
        except IndexError:
            logging.error("Given model doesn't exist")
            sys.exit()

    def _generate_completion_prompt(self, sql: str) -> list:
        """
        Generate a completion prompt for YandexGPT.

        :param sql: The SQL query to generate documentation for.
        :returns: The completion prompt.
        """
        if self.examples:
            example_values: str = """
В блок description добавь примеры возможных значений там, где эти значения указаны явно: например, в блоке CASE.
"""
        else:
            example_values: str = ""
        gpt_answer_template: str = """
[{{"column_name": <название колонки>,"description": <описание колонки>}}..]
"""
        gpt_completion_prompt: list = [
            {
                "role": "system",
                "text": f"""
Напиши документацию для следующей dbt-модели: {sql.strip()}
Опиши значения колонок четко и ясно с использованием технического русского языка.
Опиши только колонки в блоке основного SELECT, игнорируй CTE.
Оформи ответ в виде JSON, используя шаблон {gpt_answer_template}.
{example_values}
""",
            }
        ]
        return gpt_completion_prompt

    def _get_doc_completion(self, sql: str) -> str:
        """
        Get documentation completion from YandexGPT formed as a raw text.

        :param sql: The SQL query to generate documentation for.
        :returns: The result of the completion.
        """
        sdk = YCloudML(
            folder_id=self._get_dotenv_secret(constants.DOTENV_CATALOG_ID_NAME),
            auth=self._get_dotenv_secret(constants.DOTENV_API_KEY_NAME),
        )
        model: GPTModel = sdk.models.completions("yandexgpt").configure(
            temperature=constants.GPT_TEMPERATURE,
            max_tokens=constants.GPT_MAX_TOKENS,
            response_format=constants.GPT_RESPONSE_FORMAT,
        )
        prompt: list = self._generate_completion_prompt(sql)
        result: GPTModelResult = model.run(prompt)
        if result.status != 3:
            logging.error(f"Yandex API message: {result.text}")
            sys.exit()
        if self.verbose:
            logging.info("Here is the raw answer from YandexGPT API:")
            logging.info(result.text)
        return result.text

    def _generate_documented_yaml(self, json_answer: list) -> str:
        """
        Generate a documented YAML.

        :param json_answer: The GPT answer in JSON format.
        :returns: The documented YAML.
        """
        dbt_yaml: dict = {
            "version": 2,
            "models": [
                {
                    "name": self.model,
                    "columns": [{"name": col["column_name"], "description": col["description"]} for col in json_answer],
                }
            ],
        }
        return yaml.dump(dbt_yaml, allow_unicode=True, sort_keys=False)

    def run(self):
        """Main function to compile dbt model, generate documentation, and fill YAML."""
        profiles_dir_arg: str = f"--profiles-dir={self.profiles_dir}"
        project_dir_arg: str = f"--project-dir={self.project_dir}"
        model_compile_args: list = [
            project_dir_arg,
            profiles_dir_arg,
            "--select",
            self.model,
        ]

        logging.info(f"Start compiling dbt-model {self.model}...")
        file_name: str = ""
        if self.save:
            compiled_model_node: ModelNode = self._get_dbt_cli_results(model_compile_args)
            compiled_model: str = compiled_model_node.compiled_code
            file_name: str = compiled_model_node.original_file_path.replace(".sql", ".yml")
        else:
            compiled_model: str = self._get_dbt_cli_results(model_compile_args).compiled_code
        logging.info(f"dbt-model {self.model} compiled.")

        logging.info("Start generating documentation with YandexGPT...")
        result: str = self._get_doc_completion(compiled_model)
        json_answer: list = self._parse_gpt_answer(result)

        documented_yaml: str = self._generate_documented_yaml(json_answer=json_answer)
        if self.save:
            file_name_full: str = os.path.join(self.project_dir, file_name)
            with open(file_name_full, "w") as file:
                file.write(documented_yaml)
            logging.info(f"AI-documentation for dbt-model {self.model} saved to file: {file_name_full}")
        else:
            logging.info(f"Here is AI-documentation for dbt-model {self.model}:")
            print(documented_yaml)

    @staticmethod
    def _parse_gpt_answer(raw_answer: str) -> List[Dict]:
        """
        Parse the YandexGPT answer.

        :param raw_answer: The raw answer from YandexGPT.
        :returns: The parsed answer as a list of dictionaries.
        """
        json_answer: list = []
        try:
            json_answer: List[Dict] = json.loads(raw_answer)
        except (ValueError, KeyError) as e:
            logging.error(f"Error parsing GPT answer: {e}")
        return json_answer
