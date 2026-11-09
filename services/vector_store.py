"""Persistent JSON vector store for caption embeddings."""
import json, math, os, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "data" / "vector_store.json"

def _read():
    STORE.parent.mkdir(parents=True, exist_ok=True)
    if not STORE.exists(): return {"items": []}
    try:
        data=json.loads(STORE.read_text(encoding="utf-8"))
        return data if isinstance(data.get("items"), list) else {"items": []}
    except (OSError, json.JSONDecodeError):
        return {"items": []}

def upsert_embedding(image_id, text, vector):
    if not vector: raise ValueError("Embedding vector is empty.")
    data=_read(); item={"image_id":int(image_id),"text":text,"embedding":[float(x) for x in vector]}
    data["items"]=[x for x in data["items"] if int(x.get("image_id",-1)) != int(image_id)]
    data["items"].append(item)
    STORE.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(STORE.parent),suffix=".tmp")
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f: json.dump(data,f)
        os.replace(tmp,STORE)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def get_embedding(image_id):
    for item in _read()["items"]:
        if int(item.get("image_id",-1)) == int(image_id): return item.get("embedding")
    return None

def count_embeddings(): return len(_read()["items"])

def cosine_similarity(a,b):
    if not a or not b or len(a)!=len(b): return 0.0
    dot=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(y*y for y in b))
    return dot/(na*nb) if na and nb else 0.0

def semantic_search(query_vector, records, limit=50):
    by_id={int(r["id"]):r for r in records}; ranked=[]
    for item in _read()["items"]:
        image_id=int(item.get("image_id",-1))
        if image_id in by_id:
            score=cosine_similarity(query_vector,item.get("embedding",[]))
            ranked.append((score,by_id[image_id]))
    ranked.sort(key=lambda x:x[0],reverse=True)
    return [(score,record) for score,record in ranked[:limit] if score>0.05]
