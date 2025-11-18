import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Hat

app = FastAPI(title="Hats Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hats Store API running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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
            response["database_url"] = "✅ Configured"
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

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ------------------------
# Helpers
# ------------------------

def _serialize(doc: dict) -> dict:
    if not doc:
        return doc
    d = dict(doc)
    _id = d.pop("_id", None)
    if _id is not None:
        d["id"] = str(_id)
    # Convert datetimes to isoformat if present
    for k, v in list(d.items()):
        try:
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        except Exception:
            pass
    return d


# ------------------------
# Hats Endpoints
# ------------------------

@app.get("/api/hats")
def list_hats(category: Optional[str] = Query(None, description="Filter by category")):
    filter_dict = {"category": category} if category else {}
    docs = get_documents("hat", filter_dict)
    return [_serialize(doc) for doc in docs]


class HatCreate(Hat):
    pass


@app.post("/api/hats")
def create_hat(hat: HatCreate):
    hat_id = create_document("hat", hat)
    return {"id": hat_id}


@app.post("/api/seed")
def seed_data(force: bool = False):
    """Seed the database with a curated set of hats. If force=false and hats exist, do nothing."""
    existing = get_documents("hat", {}, limit=1)
    if existing and not force:
        return {"status": "ok", "message": "Hats already seeded"}

    samples: List[Hat] = [
        Hat(
            title="Azure Breeze Wide Brim",
            description="Elegant sun protection with a soft blue ribbon.",
            price=59.0,
            category="Women",
            images=[
                "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1600&auto=format&fit=crop",
            ],
            color="Beige",
            material="Straw",
            rating=4.7,
            in_stock=True,
        ),
        Hat(
            title="Coastal Surfer Cap",
            description="Lightweight mesh back for salty sessions.",
            price=35.0,
            category="Surfer",
            images=[
                "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1600&auto=format&fit=crop",
            ],
            color="Navy",
            material="Cotton",
            rating=4.6,
            in_stock=True,
        ),
        Hat(
            title="Fairway Pro Visor",
            description="Low-profile visor engineered for the green.",
            price=29.0,
            category="Golfer",
            images=[
                "https://images.unsplash.com/photo-1519680772-8b1b0b84b1cb?q=80&w=1600&auto=format&fit=crop",
            ],
            color="White",
            material="Poly Blend",
            rating=4.5,
            in_stock=True,
        ),
        Hat(
            title="Lone Star Cowboy",
            description="Classic western silhouette with modern comfort.",
            price=89.0,
            category="Cowboy",
            images=[
                "https://images.unsplash.com/photo-1542996966-1b3c1a7d6401?q=80&w=1600&auto=format&fit=crop",
            ],
            color="Sand",
            material="Felt",
            rating=4.8,
            in_stock=True,
        ),
        Hat(
            title="City Fedora",
            description="Timeless style for every occasion.",
            price=72.0,
            category="Women",
            images=[
                "https://images.unsplash.com/photo-1508186225823-0963cf9ab0de?q=80&w=1600&auto=format&fit=crop",
            ],
            color="Black",
            material="Wool",
            rating=4.6,
            in_stock=True,
        ),
        Hat(
            title="Sunrise Bucket",
            description="Packable bucket hat for beach dawn patrol.",
            price=26.0,
            category="Surfer",
            images=[
                "https://images.unsplash.com/photo-1520975954732-35dd2ef51d76?q=80&w=1600&auto=format&fit=crop",
            ],
            color="Peach",
            material="Nylon",
            rating=4.4,
            in_stock=True,
        ),
    ]

    # Clear and re-seed if force
    if force:
        db["hat"].delete_many({})

    for item in samples:
        create_document("hat", item)

    return {"status": "ok", "inserted": len(samples)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
