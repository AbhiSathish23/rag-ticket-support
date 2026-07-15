from google import genai
import chromadb
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
app = FastAPI()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="./chroma.db")
collection = chroma_client.get_or_create_collection(name="tickets")

print("1")
def get_embeddings(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values

# Seed data if empty
tickets = [
    {"problem": "My laptop won't turn on",
     "solution": "Check power adapter, try removing battery and replugging"},
    {"problem": "Internet connection keeps dropping",
     "solution": "Restart router, update network drivers"},
    {"problem": "Cannot login to my account",
     "solution": "Reset password, clear browser cache and cookies"},
    {"problem": "Screen is flickering badly",
     "solution": "Update display drivers, check monitor cable connection"},
    {"problem": "Keyboard keys are not working",
     "solution": "Clean keyboard, check USB connection or replace batteries"}
]
print("2")
if collection.count() == 0:
    for i, ticket in enumerate(tickets):
        collection.add(
            ids=[str(i)],
            embeddings=[get_embeddings(ticket["problem"])],
            documents=[ticket["problem"]],
            metadatas=[{"solution": ticket["solution"]}]
        )
    print("✅ Tickets seeded!")

# Request model
class TicketRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "running", "tickets_in_db": collection.count()}

@app.post("/ask")
def ask(request : TicketRequest):
    query_embedding = get_embeddings(request.query)
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )

    similar_problem = result["documents"][0][0]
    past_solution = result["metadatas"][0][0]["solution"]

    prompt_gemini = f""" You are a helpful IT support assistant.
A similar past ticket was resolved with this information:
Problem: {similar_problem}
Solution: {past_solution}
Now help with this new user query: {request.query}
Give a concise, helpful response based on the past solution above.
Give it point wise and Highlight the important words"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_gemini
    )

    return {
        "query" : request.query,
        "similar_past_ticket" : similar_problem,
        "past_solution" : past_solution,
        "ai_answer" : response.text
    }

@app.post("/add-ticket")
def addTicket(request :TicketRequest, solution : str ):
    new_id = str(collection.count())
    collection.add(
        ids=new_id,
        embeddings=[get_embeddings(request.query)],
        documents=[request.query],
        metadatas=[{"solution" : solution}]

    )
    return {"message" : "Ticket added!" , "id": new_id}























