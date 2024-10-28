from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Agregar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes cambiar "*" por una lista específica de dominios para restringir el acceso.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectar a MongoDB
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
database_name = os.getenv("DATABASE_NAME", "whatsapp_db")
client = MongoClient(mongodb_uri)
db = client[database_name]
contactos_collection = db["contactos"]
mensajes_collection = db["mensajes"]

class Message(BaseModel):
    sender: str
    content: str
    timestamp: str

@app.get("/contacts")
def get_contacts():
    contacts = list(contactos_collection.find())
    # Convertir ObjectId a string
    for contact in contacts:
        contact["_id"] = str(contact["_id"])
    return contacts

@app.get("/messages/{contact_id}")
def get_messages(contact_id: str):
    contact = contactos_collection.find_one({"id": contact_id})
    if not contact:
        return {"error": "Contacto no encontrado"}
    return contact.get("mensajes", [])

@app.post("/messages/{contact_id}")
def post_message(contact_id: str, message: Message):
    result = contactos_collection.update_one(
        {"id": contact_id},
        {"$push": {"mensajes": message.dict()}}
    )
    if result.matched_count == 0:
        return {"error": "Contacto no encontrado"}
    return {"status": "Mensaje agregado con éxito"}

@app.get("/contact/{contact_id}")
def get_contact(contact_id: str):
    contact = contactos_collection.find_one({"id": contact_id})
    if contact:
        contact["_id"] = str(contact["_id"])
        return contact
    return {"error": "Contacto no encontrado"}

@app.post("/contact")
def create_contact(contact: dict):
    if "id" not in contact:
        return {"error": "El campo 'id' es obligatorio"}
    contactos_collection.insert_one(contact)
    return {"status": "Contacto creado con éxito"}
