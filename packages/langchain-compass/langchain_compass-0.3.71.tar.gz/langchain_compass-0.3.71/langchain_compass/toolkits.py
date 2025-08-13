"""LangchainCompass toolkits."""

from typing import List, Optional

from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import Field

from langchain_compass.openapi_tool_maker import make_tools


class LangchainCompassToolkit(BaseToolkit):
    """LangchainCompass toolkit."""  # noqa: E501

    api_key: Optional[str] = Field(default=None, alias="compass_api_key")
    verbose: bool = Field(
        default=False,
        description="Whether the Compass tools should print verbose information.",
    )
    direct_return_post: bool = Field(
        default=True,
        description="Whether to directly return the raw API response of "
        "POST requests to Compass API. If `False`, the agent"
        "will summarize the response in words. `POST` requests are typically"
        "on-chain transactions.",
    )
    direct_return_read: bool = Field(
        default=False,
        description="Whether to directory return the raw API response of"
        "GET requests to Compass API. If `False`, the agent"
        "will summarize the response in words. `GET` requests are typically "
        "data reads from chain, such as yield rates.",
    )

    def __init__(
        self,
        compass_api_key: Optional[str] = None,
        verbose: bool = False,
        direct_return_read=False,
        direct_return_post=True,
    ) -> None:
        super().__init__()
        self.api_key: Optional[str] = compass_api_key
        self.verbose: bool = verbose
        self.direct_return_post = direct_return_post
        self.direct_return_read = direct_return_read

    def get_tools(self) -> List[BaseTool]:
        compass_tools: List[BaseTool]
        compass_tools = make_tools(
            api_key=self.api_key,
            direct_return_post=self.direct_return_post,
            direct_return_read=self.direct_return_read,
            verbose=self.verbose,
        )
        compass_tools = [
            tool for tool in compass_tools if "set_any" not in tool.get_name()
        ]
        return compass_tools


# if __name__ == "__main__":
#     import os
#
#     compass_tools = LangchainCompassToolkit(
#         compass_api_key=os.environ.get("COMPASS_API_KEY"),
#         verbose=True,
#         direct_return_read=True,
#         direct_return_post=True,
#     ).get_tools()
#     for tool in compass_tools:
#         print(tool)
