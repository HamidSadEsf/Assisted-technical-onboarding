import re
from typing import List

class SemanticChunk:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content

def semantic_chunk_by_endpoint(text: str) -> List[SemanticChunk]:
    """
    Chunks markdown API documentation semantically by endpoint headers
    (e.g., '## GET /users', '### POST /login') to ensure payload tables
    are not broken across arbitrary token limits.
    """
    lines = text.split('\n')
    chunks = []
    current_title = "Global/Overview"
    current_content = []
    
    # Regex to find markdown headers
    header_pattern = re.compile(r'^(#{1,4})\s+(.*)$')
    
    for line in lines:
        match = header_pattern.match(line)
        if match:
            # If we have accumulated content, save the chunk
            if current_content:
                chunks.append(SemanticChunk(current_title, '\n'.join(current_content).strip()))
            
            # Start a new chunk
            current_title = match.group(2).strip()
            current_content = [line]
        else:
            current_content.append(line)
            
    # Add the last chunk
    if current_content:
        chunks.append(SemanticChunk(current_title, '\n'.join(current_content).strip()))
        
    # Filter out empty chunks
    return [c for c in chunks if c.content]
