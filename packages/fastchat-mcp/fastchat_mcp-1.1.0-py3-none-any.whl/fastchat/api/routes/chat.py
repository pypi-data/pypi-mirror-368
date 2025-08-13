from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...app.chat.features.llm_provider import LLMProvider

# from ...app.chat.features.step import Step
from ...app.chat.chat import Fastchat
from ...config.llm_config import ConfigGPT, ConfigLLM
from ...app.environment import Environment


router = APIRouter(prefix="/chat", tags=["chating"])


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    chat_id: str = None,
    model: str = ConfigGPT.DEFAULT_MODEL_NAME,
    llm_provider: str = ConfigLLM.DEFAULT_PROVIDER.value,
    len_context: int = ConfigLLM.DEFAULT_HISTORY_LEN,
):
    await websocket.accept()
    llm_provider = LLMProvider(llm_provider)
    chat = Fastchat(
        id=chat_id,
        model=model,
        llm_provider=llm_provider,
        len_context=len_context,
    )
    # chat.set_client_manager_mcp(Environment.CLIENT_MANAGER_MCP)
    await chat.initialize(print_logo=False)

    try:
        while True:
            # Espera mensaje del usuario, típicamente texto (puedes cambiarlo si envías JSON)
            query = await websocket.receive_text()
            response = chat(query)

            # Enviar respuesta al cliente (puede ser texto o JSON)
            async for step in response:
                await websocket.send_json(step.json)
            await websocket.send_text("--next")

    except WebSocketDisconnect:
        # Cierra conexión limpia si el cliente se desconecta
        pass
