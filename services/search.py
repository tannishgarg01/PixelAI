import re
from collections import Counter
from services.vector_store import semantic_search
STOP={"show","me","the","ones","with","a","an","in","on","of","and","image","images","photo","photos","picture","pictures","find","all","please","are","is","my"}
def words(text): return [x for x in re.findall(r"[a-z0-9]+",(text or "").lower()) if x not in STOP]
def lexical_search(query,records):
    terms=set(words(query))
    if not terms: return records
    ranked=[]
    for record in records:
        counts=Counter(words(record.get("filename","")+" "+record.get("caption","")))
        score=sum(1+0.1*min(counts[t],3) for t in terms if counts[t])
        if score: ranked.append((score,record))
    ranked.sort(key=lambda x:x[0],reverse=True)
    return [r for _,r in ranked]
def search_images(query,records,query_embedding=None):
    """Use cosine similarity over Gemini caption vectors; fall back to lexical matching."""
    if query_embedding:
        results=semantic_search(query_embedding,records)
        if results: return [record for _,record in results]
    return lexical_search(query,records)
