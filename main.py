import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Client, Website, SeoMetric, GmbProfile

app = FastAPI(title="Marketing CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilities
class ObjId(BaseModel):
    id: str

def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid object id")

@app.get("/")
def read_root():
    return {"message": "Marketing CRM API running"}

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
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# CRUD Endpoints
# Create endpoints (insert)
@app.post("/clients")
def create_client(client: Client):
    client_id = create_document("client", client)
    return {"id": client_id}

@app.post("/websites")
def create_website(website: Website):
    # ensure client exists
    cid = to_object_id(website.client_id)
    exists = db["client"].find_one({"_id": cid})
    if not exists:
        raise HTTPException(status_code=404, detail="Client not found")
    website_id = create_document("website", website)
    return {"id": website_id}

@app.post("/seo")
def create_seo_metric(metric: SeoMetric):
    cid = to_object_id(metric.client_id)
    if not db["client"].find_one({"_id": cid}):
        raise HTTPException(status_code=404, detail="Client not found")
    metric_id = create_document("seometric", metric)
    return {"id": metric_id}

@app.post("/gmb")
def create_gmb_profile(profile: GmbProfile):
    cid = to_object_id(profile.client_id)
    if not db["client"].find_one({"_id": cid}):
        raise HTTPException(status_code=404, detail="Client not found")
    gmb_id = create_document("gmbprofile", profile)
    return {"id": gmb_id}

# Read endpoints (lists)
@app.get("/clients")
def list_clients():
    items = get_documents("client")
    # string-ify ids
    for it in items:
        it["_id"] = str(it["_id"])
    return items

@app.get("/clients/{client_id}")
def get_client_detail(client_id: str):
    cid = to_object_id(client_id)
    client = db["client"].find_one({"_id": cid})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client["_id"] = str(client["_id"])
    websites = list(db["website"].find({"client_id": client_id}))
    for w in websites:
        w["_id"] = str(w["_id"])
    seo = list(db["seometric"].find({"client_id": client_id}).sort("date", -1))
    for s in seo:
        s["_id"] = str(s["_id"])
    gmb = list(db["gmbprofile"].find({"client_id": client_id}))
    for g in gmb:
        g["_id"] = str(g["_id"])
    return {"client": client, "websites": websites, "seo": seo, "gmb": gmb}

# Simple delete endpoints for cleanup
@app.delete("/clients/{client_id}")
def delete_client(client_id: str):
    cid = to_object_id(client_id)
    res = db["client"].delete_one({"_id": cid})
    # cascade delete related
    db["website"].delete_many({"client_id": client_id})
    db["seometric"].delete_many({"client_id": client_id})
    db["gmbprofile"].delete_many({"client_id": client_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
