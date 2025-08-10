r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import os
import time
from uuid import uuid4

from payloop._config import Config
from payloop._network import Collector
from payloop._providers import Anthropic as LlmProviderAnthropic
from payloop._providers import Google as LlmProviderGoogle
from payloop._providers import LangChain as LlmProviderLangChain
from payloop._providers import OpenAi as LlmProviderOpenAi

__all__ = ["Payloop"]


class Payloop:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.environ.get("PAYLOOP_API_KEY", None)

        if api_key is None:
            self.__runtime_error(
                "API key is missing. Either set the PAYLOOP_API_KEY environment\n"
                + "variable or set the api_key parameter when instantiating Payloop."
            )

        self.config = Config()
        self.config.api_key = api_key
        self.config.attribution = None
        self.config.tx_uuid = uuid4()
        self.config.version = 0.1

        self.anthropic = LlmProviderAnthropic(self.config)
        self.google = LlmProviderGoogle(self.config)
        self.langchain = LlmProviderLangChain(self.config)
        self.openai = LlmProviderOpenAi(self.config)

    def attribution(
        self,
        parent_id=None,
        parent_uuid=None,
        parent_name=None,
        subsidiary_id=None,
        subsidiary_uuid=None,
        subsidiary_name=None,
    ):
        if parent_id is not None:
            if not isinstance(parent_id, int):
                self.__runtime_error("parent ID must be an integer")

        if subsidiary_id is not None:
            if not isinstance(subsidiary_id, int):
                self.__runtime_error("subsidiary ID must be an integer")

        if (
            parent_id
            or parent_uuid
            or parent_name
            or subsidiary_id
            or subsidiary_uuid
            or subsidiary_name
        ):
            self.config.attribution = {
                "parent": {"id": parent_id, "name": parent_name, "uuid": parent_uuid},
                "subsidiary": {
                    "id": subsidiary_id,
                    "name": subsidiary_name,
                    "uuid": subsidiary_uuid,
                },
            }

        return self

    def __format_exception_message(self, text):
        return f"""
----- Payloop Exception

{text}

-----"""

    def new_transaction(self):
        self.config.tx_uuid = uuid4()
        return self

    def __runtime_error(self, message):
        raise RuntimeError(self.__format_exception_message(message))
