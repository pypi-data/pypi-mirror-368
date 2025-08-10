from ..services.llm import LLM
from ..services.llm.models.openai_service.gpt import GPT
from typing import Generator
from .features.step import Step, StepMessage, DataStep, ResponseStep, QueryStep
from .features.llm_provider import LLMProvider
from ...config.llm_config import ConfigGPT
import json
from mcp.types import PromptMessage


class Chat:
    """
    Chat class for managing conversational interactions with an LLM (Large Language Model).
    This class orchestrates the process of handling user queries, selecting prompts and services,
    and generating responses using a language model. It supports context management, prompt selection,
    service invocation, and streaming responses in a step-wise manner.
    Args:
        llm_provider (LLMProvider): The provider of language model to use. Default is `LLMProvider.OPENAI`.
        model (str): The model name to use for the LLM. Defaults to ConfigGPT.DEFAULT_MODEL_NAME.
        len_context (int): Maximum length of the conversation history to maintain. Defaults to 10.
        history (list): Initial chat history. Defaults to an empty list.
        id (str | None): Optional identifier for the chat session.
    Methods:
        __call__(query: str) -> Generator[Step]:
            Processes a user query through multiple steps, including query analysis,
            prompt selection, service selection, and response generation. Yields Step objects
            representing each stage of the process.
        proccess_query(query: str) -> Generator[Step]:
            Handles the detailed processing of a single query, including updating chat history,
            selecting prompts and services, and generating the final response. Yields Step objects
            for each sub-step in the process.
    """

    def __init__(
        self,
        llm_provider: LLMProvider = LLMProvider.OPENAI,
        model=ConfigGPT.DEFAULT_MODEL_NAME,
        len_context: int = 10,
        history: list = [],
        id: str | None = None,
    ):
        """
        Initialize a Chat instance.
        Args:
            llm_provider (LLMProvider, optional): The language model provider. Defaults to LLMProvider.OPENAI.
            model (str, optional): The model name to use. Defaults to ConfigGPT.DEFAULT_MODEL_NAME.
            len_context (int, optional): Maximum number of messages to keep in context. Defaults to 10.
            history (list, optional): Initial chat history. Defaults to empty list.
            id (str | None, optional): Optional chat session identifier.
        """

        self.id = id
        self.llm: LLM = GPT(
            max_history_len=len_context,
            model=model,
            chat_history=history,
        )

    def __call__(self, query: str) -> Generator[Step]:
        """
        Processes a user query through the chat pipeline.
        This method analyzes the query, preprocesses it, selects relevant prompts and services,
        and generates a response. The process is broken down into steps, each represented by a Step object,
        which are yielded sequentially to allow for streaming or step-wise processing.
        Args:
            query (str): The user's input query.
        Yields:
            Step: An object representing each stage of the query processing pipeline.
        """
        yield Step(step_type=StepMessage.ANALYZE_QUERY)

        processed_query: dict = self.llm.preprocess_query(query=query)
        querys: list[str] = processed_query["querys"]
        self.llm.current_language = processed_query["language"]

        yield DataStep(data={"querys": querys})

        for query in querys:
            for step in self.proccess_query(query):
                yield step

    def proccess_query(self, query: str) -> Generator[Step]:
        """
        Handles the detailed processing of a single query.
        This method updates the chat history, selects prompts and services based on the query,
        invokes the appropriate service or tool, and generates the final response. Each sub-step
        is yielded as a Step object for granular control and streaming.
        Args:
            query (str): The user's input query.
        Yields:
            Step: An object representing each sub-step of the query processing, including prompt selection,
                  service selection, and response generation.
        """
        self.llm.append_chat_history()
        yield QueryStep(query)

        # region ########### GET PROMTPS ###########
        yield Step(step_type=StepMessage.SELECT_PROMPTS)
        prompts = json.loads(self.llm.select_prompts(query))["prompt_services"]

        if len(prompts) == 0:
            yield DataStep(data={"prompts": None})

        for index, prompt in enumerate(prompts):
            yield DataStep(data={f"prompt {index+1}": prompt["prompt_service"]})

        extra_messages = [
            self.llm.client_manager_mcp.prompts[prompt["prompt_service"]](
                prompt["args"]
            )
            for prompt in prompts
        ]
        extra_messages = [
            prompt_message2dict(message)
            for prompt_message in extra_messages
            for message in prompt_message
        ]
        # endregion ###################################################

        # region ########### SELECT SERVICE AND ARGS ############
        yield Step(step_type=StepMessage.SELECT_SERVICE)
        # Cargar los servicios utiles
        service = json.loads(
            self.llm.select_service(query, extra_messages=extra_messages)
        )
        args = service["args"]
        service = service["service"]
        # endregion ###################################################

        # region ########### RESPONSE ############
        if len(service) == 0:
            yield DataStep(data={"service": None})
            first_chunk = True
            for chunk in self.llm.simple_query(query, use_services_contex=True):
                yield ResponseStep(response=chunk, data=None, first_chunk=first_chunk)
                first_chunk = False
            yield ResponseStep(response="\n\n", data=None)

        else:
            yield DataStep(data={"service": service})
            yield DataStep(data={"args": args})
            service = (
                self.llm.client_manager_mcp.resources[service]
                if (self.llm.client_manager_mcp.service_type(service) == "resource")
                else (
                    self.llm.client_manager_mcp.tools[service]
                    if (self.llm.client_manager_mcp.service_type(service) == "tool")
                    else None
                )
            )

            data = service(args)[0].text
            first_chunk = True
            for chunk in self.llm.final_response(query, data):
                yield ResponseStep(response=chunk, data=None, first_chunk=first_chunk)
                first_chunk = False
            yield ResponseStep(response="\n\n", data=data)

        # endregion ###################################################


def prompt_message2dict(prompt_message: PromptMessage):
    data: dict = json.loads(prompt_message.content.text)
    return {"role": prompt_message.role, "content": data["content"]["text"]}


""" FLOW
see https://github.com/rb58853/fastchat-mcp/tree/main/doc/FLOW.md
"""
