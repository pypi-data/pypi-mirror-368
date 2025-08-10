from fastchat import Chat
from fastchat.utils.clear_console import clear_console
import os


def open_local_chat():
    """
    ### open_local_chat
    - Launches an interactive local chat session in the console.
    - The conversation is also recorded in Markdown format. When the user exits (by typing 'exit' or pressing Enter),
    the chat history is saved to a Markdown file in the 'chats' directory, using the first query as the filename.
    """

    clear_console()
    print(logo)
    chat: Chat = Chat()
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
        for step in chat(query):
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


logo = """\x1b[32;1m
         _ __ ___ ______           __        __          __    
        _ __ ___ / ____/___  _____/ /_ _____/ /    ___  / /_
       _ __ ___ / /_  / __ `/ ___/ __/ ____/ /_  / __ `/___/
      _ __ ___ / __/ / /_/ (__  ) /_/ (___/ __ \/ /_/ / /_ 
     _ __ ___ /_/    \__,_/____/\__/\____/_/ /_/\__,__\__/ 
"""
