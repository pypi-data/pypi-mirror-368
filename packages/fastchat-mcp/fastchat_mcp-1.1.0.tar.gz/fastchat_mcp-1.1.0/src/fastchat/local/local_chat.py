import asyncio
from ..app.chat.chat import Fastchat
from ..utils.clear_console import clear_console
from ..config.logger import LoggerFeatures
import os


class TerminalChat:
    def open(self):
        return asyncio.run(self.__open())

    async def __open(self):
        """
        ### open_local_chat
        - Launches an interactive local chat session in the console.
        - The conversation is also recorded in Markdown format. When the user exits (by typing 'exit' or pressing Enter),
        the chat history is saved to a Markdown file in the 'chats' directory, using the first query as the filename.
        """

        clear_console()
        chat: Fastchat = Fastchat()
        await chat.initialize()
        print("\n")

        md: str = ""
        filename: str | None = None
        sep = os.path.sep

        while True:
            query = input("> ")
            if query == "exit" or query == "":
                if md != "":
                    chats_path = f"{os.getcwd()}{sep}chats{sep}"
                    os.makedirs(os.path.dirname(chats_path), exist_ok=True)
                    with open(f"{chats_path}{filename}.md", "w") as file:
                        file.write(md)
                break

            if filename is None:
                filename = f"{query[:15]}..."

            md += f"# {query}"
            index = 1
            async for step in chat(query):
                md += str(step)

                if step.type == "response":
                    if step.json["first_chunk"]:
                        print(f"<< {step.response}", end="")
                    else:
                        print(f"{step.response}", end="")

                if step.type == "query":
                    print(f">> {step.query}")
                    index = 1
                if step.type == "data":
                    print(f'   {str(step).replace("**", "").replace("- ", "• ")}')
                if step.type == "step":
                    print(f"  {index}. {step.step}")
                    index += 1
            md += "\n"
