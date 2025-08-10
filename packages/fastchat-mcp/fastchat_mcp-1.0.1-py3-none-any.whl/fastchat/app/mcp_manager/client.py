from .servers import Servers
from .sessions import httpstrem, stdio
from .services import Tool, Resource, Prompt
from ...config.logger import logger, CustomFormatter


class ClientManagerMCP:
    """
    ClientManagerMCP is responsible for managing and interacting with tools, resources, and prompts
    provided by multiple MCP (Multi-Component Platform) servers. It handles the initialization,
    refreshing, and retrieval of these components, as well as facilitating their invocation.
    Attributes:
        app_name (str): The name of the application using the manager.
        tools (dict[str, Tool]): Dictionary of available tools, keyed by server and tool name.
        resources (dict[str, Resource]): Dictionary of available resources, keyed by server and resource name.
        prompts (dict[str, Prompt]): Dictionary of available prompts, keyed by server and prompt name.
    ## Methods
        call_tool(name: str, args: dict) -> str | None:
            Calls a tool by name with the provided arguments.
        read_resource(name: str, args: dict) -> str | None:
            Reads a resource by name with the provided arguments.
        get_prompt(name: str, args: dict) -> dict:
            Retrieves a prompt by name with the provided arguments.
        refresh_data():
            Initializes or refreshes the lists of tools, resources, and prompts from all registered MCP servers.
        service_type(service_key: str) -> str:
            Determines whether a given service key corresponds to a tool or a resource.
        get_services() -> list[dict[str, any]]:
            Returns a list of dictionaries representing the available services.
        get_prompts() -> list[dict[str, any]]:
            Returns a list of dictionaries representing the available prompts.
    ## Private Methods
        __get_session(server: dict) -> dict:
            Establishes a session with a given server and retrieves its available tools, resources, and prompts.
    ## Usage
        Instantiate ClientManagerMCP to manage and interact with MCP server components in a unified way.
    """

    def __init__(self, app_name: str = "fastchat-mcp"):
        self.app_name: str = app_name
        self.tools: dict[str:Tool] | None = {}
        self.resources: dict[str:Resource] | None = {}
        self.prompts: dict[str:Prompt] | None = {}
        self.refresh_data()
        self.__services: list[dict] = []
        """List of services as strings to be passed to the LLM"""
        self.__prompts_context: list[dict] = []
        """List of prompts as strings to be passed to the LLM"""

    def call_tool(self, name: str, args: dict) -> str | None:
        return self.tools[name](args)

    def read_resource(self, name: str, args: dict) -> str | None:
        return self.resources[name](args)

    def get_prompt(self, name: str, args: dict) -> dict:
        self.prompts[name](args)

    def refresh_data(self):
        """
        ### Refresh Datas
        - Initializes or refreshes the lists of tools, resources, and prompts provided by each mcp server,
        organizing them into dictionaries.
        - For each registered MCP servers, retrieves their available tools, resources,
        and prompts via a session, and stores them in the corresponding self dictionaries.
        - If a session cannot be established with a server, that server is skipped.
        """

        self.tools, self.resources, self.prompts = ({}, {}, {})
        mcp_servers: dict[str, dict] = Servers().mcp_servers

        for server_key in mcp_servers.keys():
            server = {"key": server_key} | mcp_servers[server_key]
            session = self.__get_session(server)
            if session is None:
                continue

            for tool in session["tools"]:
                self.tools[f"{server_key}_{tool.name}"] = Tool(data=tool, server=server)
            for resource in session["resources"]:
                self.resources[f"{server_key}_{resource.name}"] = Resource(
                    data=resource, server=server
                )

            for prompt in session["prompts"]:
                self.prompts[f"{server_key}_{prompt.name}"] = Prompt(
                    data=prompt, server=server
                )

    def __get_session(self, server: dict) -> dict:
        try:
            session: dict = {}

            if server["protocol"] == "httpstream":
                session = httpstrem.get_session_data(
                    server["httpstream-url"],
                    server["oauth_client"],
                    headers=server.get("headers", None),
                )
            elif server["protocol"] == "stdio":
                session = stdio.get_session_data(server=server)
            else:
                logger.error(
                    f"Unsupported protocol type {CustomFormatter.bold_red}{server['protocol']}{CustomFormatter.reset} for server {server['key']}"
                )
                return None

            logger.info(
                f"Establish connection with server {CustomFormatter.green}{server['key']}{CustomFormatter.reset} successfully."
            )
            return session
        except Exception as e:
            logger.error(
                f"Failed to establish connection with server {CustomFormatter.bold_red}{server['key']}{CustomFormatter.reset}. Cause: {e}"
            )
            return None

    def service_type(self, service_key: str) -> str:
        """
        Determine the type of service associated with the given service key.
        Args:
            service_key (str): The key identifying the service.
        Returns:
            str: "tool" if the service key corresponds to a tool, "resource" if it corresponds to a resource.
        """

        if service_key in self.tools.keys():
            return "tool"
        if service_key in self.resources.keys():
            return "resource"

    def get_services(self) -> list[dict[str, any]]:
        """
        Returns a list of dictionaries representing the available services. Creates
        a dictionary for each service with the service name as the key and its string
        representation as the value.
        Returns:
            list[dict]: A list of dictionaries, each containing a service name
            and its corresponding string representation.
        """

        if len(self.__services) != len(self.tools) + len(self.resources):
            services = self.tools | self.resources
            self.__services = [
                {service: str(services[service])} for service in services.keys()
            ]

        return self.__services

    def get_prompts(self) -> list[dict[str, any]]:
        """
        Returns a list of prompt dictionaries, ensuring each prompt is represented as a dictionary
        with string values.
        Returns:
            list[dict]: A list of dictionaries containing the current prompts.
        """

        if len(self.__prompts_context) != len(self.prompts):
            self.__prompts_context = [
                {key: str(self.prompts[key])} for key in self.prompts.keys()
            ]
        return self.__prompts_context
