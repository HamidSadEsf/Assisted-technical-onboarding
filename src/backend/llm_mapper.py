import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json

# Define the Strict Internal Standard Schema
class InternalEndpointSchema(BaseModel):
    internal_name: str = Field(description="A normalized name for the endpoint, e.g., get_user_profile")
    partner_method: str = Field(description="The HTTP method used by the partner (GET, POST, etc.)")
    partner_path: str = Field(description="The exact path of the partner endpoint, e.g., /v1/users/{id}")
    authentication_type: str = Field(description="Type of authentication required (Bearer, API Key, Basic, None)")
    required_payload_fields: List[str] = Field(default=[], description="List of exact required field names in the request payload")

class SchemaMappingResult(BaseModel):
    endpoints: List[InternalEndpointSchema]
    base_url: Optional[str] = Field(description="The base URL of the partner API if found")

def map_schema(chunks: List[any], api_key: str = None) -> dict:
    """
    Calls the Gemini API with structured outputs to map the partner docs 
    to the InternalEndpointSchema. Implements the 3-strike fallback route.
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY_FOR_TESTING")
    
    if api_key != "DUMMY_KEY_FOR_TESTING":
        genai.configure(api_key=api_key)
        
    context_text = "\n\n=== CHUNK BOUNDARY ===\n\n".join([f"[{c.title}]\n{c.content}" for c in chunks])
    
    prompt = f"""
    You are a Senior Integration Engineer mapping external partner API documentation to our strict internal schema.
    Extract the base URL and all API endpoints from the provided documentation.
    
    Documentation:
    {context_text}
    """
    
    max_retries = 3
    attempts = 0
    
    while attempts < max_retries:
        try:
            # If no API key, we mock the deterministic output for PoC testing
            if api_key == "DUMMY_KEY_FOR_TESTING":
                endpoints = []
                for chunk in chunks:
                    if any(method in chunk.title.upper() for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]):
                        parts = chunk.title.split()
                        method = parts[0] if len(parts) > 0 else "UNKNOWN"
                        path = parts[1] if len(parts) > 1 else "/"
                        endpoints.append(InternalEndpointSchema(
                            internal_name="mapped_" + method.lower() + "_" + path.replace("/", "_").strip("_"),
                            partner_method=method,
                            partner_path=path,
                            authentication_type="Bearer",
                            required_payload_fields=["id"] if "POST" in method else []
                        ))
                
                # Mock validation failure randomly if we want to test the 3-strike rule later
                result = SchemaMappingResult(
                    base_url="https://api.partner.com",
                    endpoints=endpoints
                )
                return result.model_dump()

            # Real Gemini Call with Structured Outputs
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=SchemaMappingResult,
                )
            )
            
            # Validating the output
            parsed_json = json.loads(response.text)
            validated_data = SchemaMappingResult(**parsed_json)
            return validated_data.model_dump()
            
        except Exception as e:
            attempts += 1
            print(f"Validation failed (Attempt {attempts}/{max_retries}): {e}")
            
    # Hard Fallback Route
    raise Exception("HARD FALLBACK TRIGGERED: Deterministic validation failed 3 times. Routing task to human engineer.")
