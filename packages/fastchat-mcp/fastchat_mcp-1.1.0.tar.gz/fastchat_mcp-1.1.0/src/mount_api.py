from .fastchat.api.api import FastApp, FastAPI

fastapp: FastApp = FastApp()
app: FastAPI = fastapp.app
