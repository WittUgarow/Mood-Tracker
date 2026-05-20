from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import psycopg
from fastapi.middleware.cors import CORSMiddleware

# Connect using a connection string or URI
conn = psycopg.connect("dbname=myapp user=myuser password=1234 host=10.0.1.163")

app = FastAPI()    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginData(BaseModel):
    username: str
    password: str

class Emotion(BaseModel):
    type: str
    value: int

class EntryCreate(BaseModel):
    user_id: int
    emotions: List[Emotion]


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/login")
def login(loginData : LoginData):
    with conn.cursor() as cur:
        cur.execute("SELECT password, id FROM users WHERE name=%s", (loginData.username,))
        result = cur.fetchone()
        if result is None:
            return {"status": False, "error": "User not found"}
        if result[0].decode('utf-8') == loginData.password:
            return {"status": True, "userId": result[1]} 
        else:
            return {"status": False, "error": "Invalid password"}
    
@app.get("/users")
def getUsers():
    with conn.cursor() as cur:
        # Execute a command
        cur.execute("SELECT * FROM users") 
        # Fetch data
        result = cur.fetchall()
        users = []
        for item in result:
            users.append({"id": item[0], "name": item[1], "email": item[2]})
        return users


@app.post("/entries")
def createEntry(newEntry : EntryCreate):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO entries (user_id) VALUES (%s) RETURNING id", (newEntry.user_id,))
        entry_id = cur.fetchone()[0]

    insertEmotions(entry_id, newEntry.emotions)
    conn.commit()
    return {"entry_id": entry_id}

def insertEmotions(entryId, emotions):
    with conn.cursor() as cur:
        for emotion in emotions:    
            cur.execute("INSERT INTO emotions (entry_id, type, value) VALUES (%s, %s, %s)", (entryId, emotion.type, emotion.value))


@app.get("/entries")
def getUserEntries(userId : int):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                entries.id, 
                entries.created_at, 
                emotions.type, 
                emotions.value 
            FROM entries 
            JOIN emotions 
            ON entries.id=emotions.entry_id 
            WHERE entries.user_id=%s 
            ORDER BY entries.created_at DESC
            """, (userId,))
        
        result = cur.fetchall()
    
    entries = {}

    for item in result:
        entryId = item[0]
        createdAt = item[1]
        emotion = item[2]
        emotionValue = item[3]

        if entryId not in entries:
            entries[entryId] = {
                "created_at": createdAt,
                "emotions": []    
            }
        
        entries[entryId]["emotions"].append({"emotion": emotion, "emotion_value": emotionValue})  
    
    return entries

# API Endpoints
    # @app.post("/auth/login") #Handle logins5
    # @app.post("/users") #Create user
    # @app.get("/entries/{id}") #Get entry by ID (Only return if the user matches the owner)
    # @app.get("/entries") #Get all entries
    # @app.post("/entries") #Create new entry
 
# Tables
    # Users: id, name, password
    # Entries: id, user_id, created_at    
    # Emotions: id, type, value, entry_id
    
#Emotions: 
    # Happy
    # Hopeful
    # Content
    # Irritated
    # Anxious
    # Depressed
    # Custom


# Array for colors so custom colors update