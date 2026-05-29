# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List

#PostgreSQL
import psycopg

#.env
from dotenv import load_dotenv
import os
load_dotenv()


from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_IP")
SECRET = os.getenv("SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

conn = psycopg.connect(f"dbname=myapp user=myuser password={DB_PASSWORD} host={DB_HOST}")

app = FastAPI()    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Emotion(BaseModel):
    type: str
    value: int

class EntryCreate(BaseModel):
    user_id: int
    emotions: List[Emotion]


class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(loginData : LoginData):
    with conn.cursor() as cur:
        cur.execute("SELECT password, id FROM users WHERE name=%s", (loginData.username,))
        result = cur.fetchone()

        if result is None:
            return {"status": False}
        
        storedPassword = result[0]
        
        valid = pwd_context.verify(loginData.password, storedPassword)
        return {"status": valid, "userID": result[1]}
    
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
    return buildReturn(result)
    #return result
    

@app.get("/entries/{entryId}")
def getEntryById(entryId: int):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                    entries.id,
                    entries.created_at,
                    emotions.type,
                    emotions.value
            FROM entries
            JOIN emotions ON
                    emotions.entry_id = entries.id
            WHERE entries.id = %s
                    """, (entryId,))
        result = cur.fetchall()
    return buildReturn(result)  


def buildReturn(result):
    entries = []
    currentId = None
    #if entry.length = 0 return
    for i in range(len(result)):
        entryId = result[i][0]
        date = result[i][1]
        emotion = result[i][2]
        value = result[i][3]
        if entryId != currentId:
            currentId = result[i][0]
            entries.append({"id": entryId, "created_at": date, "emotions": []})
        entries[len(entries)-1]["emotions"].append({"type": emotion, "value":value})
    
    for i in range(len(entries)):
        #return sortEmotions(entries[i]["emotions"])
        entries[i]["emotions"] = sortEmotions(entries[i]["emotions"])
    
    return entries

def sortEmotions(emotions):
    emotionOrder = ["happy","hopeful","content","irritated","anxious","depressed"]
    sortedEmotions = [None] * 6
    for i in range(len(emotions)):
        try:
            index = emotionOrder.index(emotions[i]["type"].decode())
            sortedEmotions[index] = emotions[i]
            emotions[i] = None
        except:
          pass
    sortedEmotions = list(filter(None, sortedEmotions))
    emotions = list(filter(None, emotions))
    emotions  = sorted(emotions, key=lambda x: x['type'])
    sortedEmotions.extend(emotions)
    return sortedEmotions

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