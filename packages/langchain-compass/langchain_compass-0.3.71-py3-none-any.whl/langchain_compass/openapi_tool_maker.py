import importlib
import json
import sys
from typing import Any, List, Optional, Type

import requests
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from requests import get

from langchain_compass.model_generator import models_from_openapi
from langchain_compass.params_converter import generate_pydantic_model


class EmptySchema(BaseModel):
    pass


class PostRequestTool(BaseTool):
    name: str = "This is the tool name."
    description: str = "A description of what your tools is doing"
    url: str = "https://api.compasslabs.ai"
    args_schema: Type[BaseModel] = EmptySchema
    return_direct: bool = False
    verbose: bool = False
    response_type: Any = None
    example_args: dict = {}
    api_key: Optional[str] = None

    def _run(
        self,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> dict:  # type: ignore
        """Use the tool."""

        headers = {"accept": "application/json", "Content-Type": "application/json"}
        if self.api_key is not None:
            headers["x-api-key"] = self.api_key

        response = requests.post(
            self.url,
            json=self.args_schema(**kwargs).model_dump(mode="json"),
            headers=headers,
        )
        if response.status_code != 200:
            raise Exception(response.text)
        if self.return_direct:  # TODO
            if "image" in response.json():
                return {"type": "image", "content": response.json()["image"]}
            return {"type": "unsigned_transaction", "content": response.json()}
        return self.response_type(**response.json())


class GetRequestTool(BaseTool):
    name: str
    description: str
    url: str
    return_direct: bool
    args_schema: Any
    verbose: bool = False
    response_type: Any
    api_key: Optional[str] = None

    def _run(
        self, run_manager: CallbackManagerForToolRun | None = None, **kwargs: Any
    ) -> dict:  # type: ignore
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        if self.api_key is not None:
            headers["x-api-key"] = self.api_key
        params = {
            key: value
            for key, value in kwargs.items()
            if "{" + key + "}" not in self.url
        }

        response = requests.get(
            self.url.format(**kwargs), params=params, headers=headers
        )
        if response.status_code != 200:
            raise Exception(response.text)
        data = response.json()
        if isinstance(data, list):
            try:
                result = self.response_type(response.json())
            except:  # noqa: E722
                result = [self.response_type(**i) for i in data][0]  # strange hack
        else:
            result = self.response_type(**response.json())

        return result


def make_tools(
    direct_return_post: bool,
    direct_return_read: bool,
    api_key: Optional[str] = None,
    verbose: bool = False,
) -> List[BaseTool]:
    response = get("https://api.compasslabs.ai/openapi.json")
    if response.status_code != 200:
        raise Exception("Could not fetch https://api.compasslabs.ai/openapi.json!")
    openapi_data = json.loads(response.text)

    import tempfile
    from pathlib import Path

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp_file_path = Path(tmp_file.name)

    models_from_openapi(response.text, tmp_file_path)

    ###

    module_name = "temp_schemas"
    spec = importlib.util.spec_from_file_location(module_name, tmp_file_path.as_posix())
    if not spec:
        raise Exception("Unable to generate openapi model spec.")
    schemas = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = schemas
    spec.loader.exec_module(schemas)  # type: ignore
    ###

    def _to_pascal(name: str) -> str:
        # Split on underscores (collapse runs), skip empties, title-case first char only
        # This is mostly needed when FastAPI changes names due to name-collisions
        parts = [p for p in name.split("_") if p]
        return "".join(p[:1].upper() + p[1:] for p in parts)

    def get_response_schema_name(endpoint: dict) -> str:
        return _to_pascal(
            endpoint["responses"]["200"]["content"]["application/json"]["schema"][
                "$ref"
            ].split("/")[-1]
        )

    tools: list[BaseTool] = []
    for path in openapi_data["paths"].keys():
        if "patch" in openapi_data["paths"][path]:
            raise ValueError("We don't support patch requests yet.")
        if "update" in openapi_data["paths"][path]:
            raise ValueError("We don't support update requests yet.")

        if "transaction_bundler" in path:  # Do not make multicall tools yet.
            continue
        if "smart_account" in path:  # Do not make smart account tools yet.
            continue

        url: str = (
            openapi_data["servers"][0]["url"].rstrip("/") + "/" + path.lstrip("/")
        )

        if "post" in openapi_data["paths"][path]:
            endpoint = openapi_data["paths"][path]["post"]

            schema_name = endpoint["requestBody"]["content"]["application/json"][
                "schema"
            ]["$ref"].split("/")[-1]

            # TODO: The SDK itself is inconsistent here.
            #  Maybe we should just run datamodel-codegen in CI.
            # args_schema = test.get(schema_name)
            # args_schema = globals()[schema_name]

            args_schema = getattr(schemas, _to_pascal(schema_name))

            description: str = (
                endpoint["description"]
                if "description" in endpoint
                else endpoint["summary"]
            )
            response_schema_name = get_response_schema_name(endpoint)

            # response_type = test.get(response_schema_name)
            response_type = getattr(schemas, response_schema_name)

            if "default" not in openapi_data["components"]["schemas"][schema_name]:
                raise ValueError(
                    "Unable to build tools."
                    "Pls message contact@compasslabs.ai to resolve this."
                )
            example_args = openapi_data["components"]["schemas"][schema_name]["default"]

            post_tool = PostRequestTool(
                name=endpoint["operationId"],
                description=description,
                url=url,
                args_schema=args_schema,
                return_direct=direct_return_post,
                verbose=verbose,
                response_type=response_type,
                example_args=example_args,
                api_key=api_key,
            )

            post_tool.__name__ = endpoint["operationId"]  # type: ignore
            tools.append(post_tool)

        if "get" in openapi_data["paths"][path]:
            endpoint = openapi_data["paths"][path]["get"]
            description1: str = (
                endpoint["description"]
                if "description" in endpoint
                else endpoint["summary"]
            )
            response_schema_name = get_response_schema_name(endpoint)
            response_type = getattr(schemas, response_schema_name)

            if "parameters" in endpoint:
                Params = generate_pydantic_model(
                    model_name="Params", parameters=endpoint["parameters"]
                )
            else:
                Params = None
            #
            get_tool = GetRequestTool(
                name=endpoint["operationId"],
                description=description1,
                url=url,
                return_direct=direct_return_read,
                args_schema=Params,
                verbose=verbose,
                response_type=response_type,
                api_key=api_key,
            )

            get_tool.__name__ = endpoint["operationId"]  # type: ignore
            tools.append(get_tool)

    return tools  # type: ignore


if __name__ == "__main__":
    tools = make_tools(
      api_key=None,
      direct_return_post=True,
      direct_return_read=False
    )
    print(tools)
