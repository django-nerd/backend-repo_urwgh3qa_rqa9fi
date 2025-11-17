import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone

from database import db, create_document, get_documents
from schemas import AppItem, BlogPost, Category, ContactMessage

app = FastAPI(title="Mod APK Hub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API Mod APK Hub berjalan"}

# ---------- Utilities ----------

def collection(name: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database tidak tersedia")
    return db[name]

# ---------- Apps & Games ----------

@app.get("/api/items")
def list_items(
    q: Optional[str] = Query(None, description="Cari berdasarkan nama"),
    category: Optional[str] = Query(None, description="Slug kategori"),
    type: Optional[str] = Query(None, description="app/game"),
    limit: int = Query(24, ge=1, le=100),
    sort: str = Query("updated_at", description="Field sortir"),
    order: int = Query(-1, description="1 asc, -1 desc"),
):
    filt = {}
    if q:
        filt["title"] = {"$regex": q, "$options": "i"}
    if category:
        filt["category"] = category
    if type:
        filt["type"] = type

    col = collection("appitem")
    cursor = col.find(filt).sort(sort, order).limit(limit)
    items = []
    for d in cursor:
        d["_id"] = str(d["_id"])  # stringify id
        items.append(d)
    return {"items": items}

@app.get("/api/items/latest")
def latest_items(limit: int = 12):
    col = collection("appitem")
    cursor = col.find({}).sort("updated_at", -1).limit(limit)
    items = []
    for d in cursor:
        d["_id"] = str(d["_id"])  # stringify id
        items.append(d)
    return {"items": items}

@app.get("/api/items/{slug}")
def get_item(slug: str):
    col = collection("appitem")
    d = col.find_one({"slug": slug})
    if not d:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    d["_id"] = str(d["_id"])
    return d

class CreateItem(BaseModel):
    data: AppItem

@app.post("/api/items")
def create_item(payload: CreateItem):
    data = payload.data.model_dump()
    data["updated_at"] = datetime.now(timezone.utc)
    new_id = create_document("appitem", data)
    return {"id": new_id}

# ---------- Categories ----------

@app.get("/api/categories")
def list_categories():
    col = collection("category")
    cats = []
    for d in col.find({}).sort("name", 1):
        d["_id"] = str(d["_id"])
        cats.append(d)
    return {"categories": cats}

# ---------- Blog ----------

@app.get("/api/blog")
def list_blog(limit: int = 10):
    col = collection("blogpost")
    res = []
    for d in col.find({}).sort("created_at", -1).limit(limit):
        d["_id"] = str(d["_id"])
        res.append(d)
    return {"posts": res}

@app.get("/api/blog/{slug}")
def get_blog(slug: str):
    col = collection("blogpost")
    d = col.find_one({"slug": slug})
    if not d:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    d["_id"] = str(d["_id"])
    return d

class CreateBlog(BaseModel):
    data: BlogPost

@app.post("/api/blog")
def create_blog(payload: CreateBlog):
    data = payload.data.model_dump()
    now = datetime.now(timezone.utc)
    data["created_at"] = data.get("created_at") or now
    data["updated_at"] = now
    new_id = create_document("blogpost", data)
    return {"id": new_id}

# ---------- Contact ----------

class CreateContact(BaseModel):
    data: ContactMessage

@app.post("/api/contact")
def submit_contact(payload: CreateContact):
    new_id = create_document("contactmessage", payload.data)
    return {"status": "ok", "id": new_id}

# ---------- System ----------

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
