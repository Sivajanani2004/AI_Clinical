from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np
import faiss
from groq import Groq
from sqlalchemy.orm import Session
from models.table_schema import ClinicalDocument

client = Groq(api_key="API_KEY")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

def load_chunks(text: str, source: str, chunk_size=200, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append({
            "text": text[start:end],
            "source": source
        })
        start = end - overlap
    return chunks

def load_templates(db: Session):
    templates = db.query(ClinicalDocument).all()
    all_chunks = []
    for t in templates:
        chunks = load_chunks(t.content, t.filename)
        all_chunks.extend(chunks)
    return all_chunks

def embed_chunks(chunks):
    texts = [c["text"] for c in chunks]
    embeddings = embed_model.encode(texts, show_progress_bar=False)
    embeddings = np.array(embeddings)
    faiss.normalize_L2(embeddings)
    return embeddings

def embed_query(query: str):
    query_embedding = embed_model.encode([query])
    faiss.normalize_L2(query_embedding)
    return query_embedding

def create_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

def search(index, query_embedding, chunks, top_k=10):
    _, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0]]

def rerank(query, chunks):
    if not chunks:
        return chunks
    pairs = [[query, c["text"]] for c in chunks]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [r[0] for r in ranked[:5]]

def generate_summary(query, context_chunks):
    context = ""
    for c in context_chunks:
        context += f"--- TEMPLATE: {c['source']} ---\n{c['text']}\n\n"
    
    prompt = f"""You are a senior clinical documentation specialist at a hospital.

TASK: Generate a professional, complete discharge summary based on the patient information and reference templates below.

PATIENT INFORMATION:
{query}

REFERENCE TEMPLATES:
{context}

DISCHARGE SUMMARY FORMAT:

PATIENT OVERVIEW:
[Patient name, age, admission date, brief reason for admission]

DIAGNOSIS:
• Primary diagnosis:
• Secondary diagnoses (if any):

HOSPITAL COURSE & TREATMENT:
[Summary of treatment provided, procedures performed, medications administered, and patient's response]

DISCHARGE MEDICATIONS:
• Medication name | Dosage | Frequency | Duration
• [Continue list]

DISCHARGE INSTRUCTIONS:
• Activity restrictions:
• Wound care (if applicable):
• Diet recommendations:
• Symptoms to watch for:

FOLLOW-UP APPOINTMENTS:
• Provider: [Specialty] - [Timeframe]
• Additional tests needed:

CONDITION AT DISCHARGE:
[Patient's status - stable, improved, etc.]

RULES:
1. ONLY use information from the provided context
2. Do NOT invent medications, diagnoses, or treatments
3. If information is missing, write "Not specified in records"
4. Use professional medical terminology
5. Be concise but comprehensive
6. Format as plain text without markdown
7. Include specific dosages and frequencies when available

Generate the discharge summary now:"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500
    )
    return response.choices[0].message.content

def rag_pipeline(query: str, db: Session) -> str:
    chunks = load_templates(db)
    if not chunks:
        return "No templates available. Please upload templates first."
    
    embeddings = embed_chunks(chunks)
    index = create_index(embeddings)
    query_embedding = embed_query(query)
    retrieved = search(index, query_embedding, chunks, top_k=15)
    reranked = rerank(query, retrieved)
    summary = generate_summary(query, reranked)
    return summary