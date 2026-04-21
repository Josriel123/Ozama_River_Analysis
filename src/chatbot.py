from google import genai
from google.genai import types

class ChatBot:
    def __init__(self, API_KEY, listaContaminantes={}, listaUbicaciones={}, MODEL_ID="gemini-3-flash-preview"):
        self.API_KEY = API_KEY
        self.MODEL_ID = MODEL_ID
        self.listaContaminantes = listaContaminantes
        self.listaUbicaciones = listaUbicaciones
        self.client = genai.Client(api_key=API_KEY)

    def updateInstructions(self, instructions):
        self.instructions = instructions

    def getInstructions(self):
        return self.instructions

    def getModel(self):
        return self.MODEL_ID

    def setModel(self, model):
        self.MODEL_ID = model

    def getUbicaciones(self):
        return self.listaUbicaciones

    def getContaminantes(self):
        return self.listaContaminantes

    def setContaminantes(self, contaminantes):
        self.listaContaminantes = contaminantes

    def setUbicaciones(self, ubicaciones):
        self.listaUbicaciones = ubicaciones

    def getData(self, pdfPath):

        return self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=self.instructions,
                config=types.GenerateContentConfig(response_mime_type="application/json")
)

