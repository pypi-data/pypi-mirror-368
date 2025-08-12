r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import copy
import json
import time

from google.protobuf import json_format

from payloop._config import Config
from payloop._network import Collector


class BaseClient:
    def __init__(self, config: Config):
        self.config = config

    def dict_to_json(self, dict_):
        result = {}
        for key, value in dict_.items():
            if hasattr(value, "__dict__"):
                result[key] = self.dict_to_json(value)
            else:
                result[key] = value

        return result

    def _format_payload(
        self, client_title, client_version, start_time, end_time, query, response
    ):
        response_json = self.response_to_json(response)

        payload = {
            "attribution": self.config.attribution,
            "conversation": {
                "client": {"title": client_title, "version": client_version},
                "query": query,
                "response": response_json,
            },
            "meta": {
                "api": {"key": self.config.api_key},
                "sdk": {"version": self.config.version},
            },
            "time": {"end": end_time, "start": start_time},
            "tx": {"uuid": str(self.config.tx_uuid)},
        }

        return payload

    def _invoke(
        self, client_title, client_version, method, kwargs, response_is_protobuf=False
    ):
        start = time.time()

        raw_response = method(**kwargs)
        formatted_response = copy.deepcopy(raw_response)

        if response_is_protobuf:
            formatted_response = json.loads(
                json_format.MessageToJson(formatted_response.__dict__["_pb"])
            )

        Collector().fire_and_forget(
            self._format_payload(
                client_title,
                client_version,
                start,
                time.time(),
                kwargs,
                formatted_response,
            )
        )

        return raw_response

    def list_to_json(self, list_):
        result = []
        for entry in list_:
            if isinstance(entry, list):
                result.append(self.list_to_json(entry))
            else:
                items = None
                if isinstance(entry, dict):
                    items = entry.items()
                elif hasattr(entry, "__dict__"):
                    items = entry.__dict__.items()

                if items is not None:
                    entry = {}
                    for key, value in items:
                        if isinstance(value, list):
                            entry[key] = self.list_to_json(value)
                        else:
                            try:
                                entry[key] = value.__dict__
                            except:
                                entry[key] = value

                    result.append(entry)
                else:
                    result.append(entry)

        return result

    def response_to_json(self, response):
        data = response
        if not isinstance(data, dict):
            data = response.__dict__

        result = {}

        for key, value in data.items():
            if isinstance(value, list):
                result[key] = self.list_to_json(value)
            else:
                if hasattr(value, "__dict__"):
                    result[key] = self.dict_to_json(value)
                else:
                    result[key] = value

        return result


class BaseProvider:
    def __init__(self, config: Config):
        self.config = config
