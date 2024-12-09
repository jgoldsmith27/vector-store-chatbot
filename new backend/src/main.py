from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from assistant_api import AssistantAPI

app = FastAPI()

origins = ["*", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = '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'
assistant = AssistantAPI(api_key=api_key)

@app.get('/get_new_thread')
def get_new_thread():
	"""
	Generates a new thread for the user conversation. This should be called on the page startup and only then
    """
	assistant.create_thread()

@app.get('/delete_thread')
def delete_thread():
	"""
	Deletes the current thread. This should be called on the page closure and only then
    """
	assistant.delete_thread()

@app.get('/get_response')
def get_response(prompt:str) -> tuple(str, list):
	"""
	Takes the user prompt and returns the generated response from the assistant
	
	Args:
        prompt:
            the prompt of the user
    """
	return assistant.prompt_assistant(prompt)


if __name__ == '__main__':
	uvicorn.run("main:app", port=8080, reload=True)