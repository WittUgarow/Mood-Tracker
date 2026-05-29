# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from pydantic import BaseModel
from typing import List

#PostgreSQL
import psycopg

#.env
from dotenv import load_dotenv
import os
load_dotenv()

# JWT
import jwt
import datetime

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_IP")
SECRET = os.getenv("SECRET_KEY")
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
    emotions: List[Emotion]

class CreateUser(BaseModel):
    username: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str

def createToken(userId):
    payload = {
        "sub": str(userId),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACESS_TOKEN_EXPIRE_TIME)
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token

@app.post("/login")
def login(loginData : LoginData):
    with conn.cursor() as cur:

        cur.execute("SELECT password, id FROM users WHERE name=%s", (loginData.username,))
        result = cur.fetchone()

        if result is None:
            return {"status": False}
        
        storedPassword = result[0]
        userId = result[1]
        if pwd_context.verify(loginData.password, storedPassword):
            return {"status": True, "access_token": createToken(userId), "token_type": "bearer"} 

        return {"status": False}

def getCurrentUser(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    return payload["sub"]


@app.post("/users")
def createUser(userInfo : CreateUser):
    username = userInfo.username
    hashedPassword = pwd_context.hash(userInfo.password)
    with conn.cursor() as cur:

        cur.execute("SELECT name FROM users WHERE name=(%s)", (username,))
        if cur.fetchone():
            return {"status": False, "reason": "username taken"}
        
    
        cur.execute("INSERT INTO users (name, password) VALUES (%s, %s) RETURNING id", (username, hashedPassword))
        userId = cur.fetchone()[0]

    conn.commit()

    return {"status": True, "userId": userId}
    


@app.post("/entries")
def createEntry(newEntry : EntryCreate, userId: str = Depends(getCurrentUser)):
    
    with conn.cursor() as cur:
        cur.execute("INSERT INTO entries (user_id) VALUES (%s) RETURNING id", (userId,))
        entry_id = cur.fetchone()[0]

    insertEmotions(entry_id, newEntry.emotions)
    conn.commit()
    return {"entry_id": entry_id}

def insertEmotions(entryId, emotions):
    with conn.cursor() as cur:
        for emotion in emotions:    
            cur.execute("INSERT INTO emotions (entry_id, type, value) VALUES (%s, %s, %s)", (entryId, emotion.type, emotion.value))
    

@app.get("/entries")
def getUserEntries(userId: str = Depends(getCurrentUser)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                entries.id, 
                entries.user_id,
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
def getEntryById(entryId: int, userId: str = Depends(getCurrentUser)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                    entries.id,
                    entries.user_id,
                    entries.created_at,
                    emotions.type,
                    emotions.value
            FROM entries
            JOIN emotions ON
                    emotions.entry_id = entries.id
            WHERE entries.id = %s
                    """, (entryId,))
        result = cur.fetchall()
        if int(result[0][1])!=int(userId):
            # return {"result": result[0][1], "userId": userId, "status":result[0][1]!=userId}
            return {"status": "faliure", "reason": "user not authorized to acess entry"}
    return buildReturn(result)  


def buildReturn(result):
    entries = []
    currentId = None
    #if entry.length = 0 return
    for i in range(len(result)):
        entryId = result[i][0]
        userId = result[i][1]
        date = result[i][2]
        emotion = result[i][3]
        value = result[i][4]
        if entryId != currentId:
            currentId = result[i][0]
            entries.append({"id": entryId, "userId":userId, "created_at": date, "emotions": []})
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