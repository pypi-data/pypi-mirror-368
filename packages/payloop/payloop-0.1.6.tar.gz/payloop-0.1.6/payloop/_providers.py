r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

from payloop._base import BaseProvider
from payloop._clients import Anthropic as AnthropicPayloopClient
from payloop._clients import Google as GooglePayloopClient
from payloop._clients import LangChain as LangChainPayloopClient
from payloop._clients import OpenAi as OpenAiPayloopClient


class Anthropic(BaseProvider):
    def register(self, client):
        return AnthropicPayloopClient(self.config).register(client)


class Google(BaseProvider):
    def register(self, client):
        return GooglePayloopClient(self.config).register(client)


class LangChain(BaseProvider):
    def register(self, chatopenai=None, chatvertexai=None):
        return LangChainPayloopClient(self.config).register(
            chatopenai=chatopenai, chatvertexai=chatvertexai
        )


class OpenAi(BaseProvider):
    def register(self, client):
        return OpenAiPayloopClient(self.config).register(client)
