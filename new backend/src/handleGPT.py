from openai import OpenAI

class OpenAIClient:
    def __init__(self, API_KEY:str, ASST_ID:str):
        self.client = OpenAI(api_key=API_KEY)
        self.asst_id = ASST_ID

    