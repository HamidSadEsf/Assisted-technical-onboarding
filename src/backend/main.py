from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from .sanitizer import sanitize_text
from .rag_engine import semantic_chunk_by_endpoint
from .llm_mapper import map_schema

app = FastAPI(title="AI-Assisted Technical Onboarding")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process")
async def process_document(file: UploadFile = File(...)):
    """
    Main pipeline execution: Sanitize -> Chunk -> Map -> Return
    """
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only Markdown (.md) files are supported for this prototype.")
        
    content = await file.read()
    text = content.decode('utf-8')
    
    # Step 1: Pre-LLM Guardrail - Local Sanitization
    sanitized_text, redactions = sanitize_text(text)
    
    # Step 2: Semantic Chunking by Endpoint
    chunks = semantic_chunk_by_endpoint(sanitized_text)
    
    # Step 3: Map to Internal Schema via LLM with 3-Strike Fallback
    try:
        mapped_result = map_schema(chunks)
    except Exception as e:
        # Hard fallback triggered
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "status": "success",
        "redactions": redactions,
        "original_text": text, # Needed for the side-by-side exact source text comparison
        "sanitized_text": sanitized_text,
        "mapped_schema": mapped_result
    }

if __name__ == "__main__":
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=8000, reload=True)
