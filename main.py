from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

# Initialize OpenAI API with your API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Load from environment variables or set directly.

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic model for the message request
class Message(BaseModel):
    user_message: str
    conversation_history: list  # List of previous messages (if any)

# Function to call the OpenAI Chat API
def call_openai_assistant(all_messages):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=all_messages
    )
    assistant_response = response.choices[0].message.content.strip()

    # Format the response for better readability
    formatted_response = assistant_response.replace("**", "").replace("##", "").replace("•", "\n•").replace("1.", "\n1.").replace("2.", "\n2.")
    return formatted_response

@app.get("/")
def read_root():
    return {"message": "Welcome to the Orchestro AI assistant API!"}

@app.post("/chat/")
async def chat(message: Message):
    # Initialize the conversation if it's the first message
    if len(message.conversation_history) == 0:
        message.conversation_history.append({
            "role": "system",
            "content": """
You are ShipTalk AI, the assistant for the ShipTalk forum—a community focused on logistics, parcels, and shipping. Your knowledge is based on the posts and comments within the ShipTalk forum. When a user asks you a question, you should provide accurate and detailed answers as if you are referencing information from the ShipTalk forum. Your responses should be informative, professional, and reflect the collective expertise of the ShipTalk community. If relevant, you may summarize discussions, best practices, or advice that have been shared in the forum. Ensure that your answers are clear, concise, and helpful, guiding the user to understand or resolve their query related to logistics, parcels, or shipping.
"""
        })

    # Add user's message to the conversation history
    message.conversation_history.append({
        "role": "user",
        "content": message.user_message
    })

    # Call the OpenAI assistant
    assistant_response = call_openai_assistant(message.conversation_history)

    # Append the assistant's response to the conversation history
    message.conversation_history.append({
        "role": "assistant",
        "content": assistant_response
    })

    # Return the assistant's response and the updated conversation history
    return {
        "assistant_response": assistant_response,
        "conversation_history": message.conversation_history  # Include conversation history in the response
    }
