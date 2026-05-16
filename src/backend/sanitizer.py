import re
from typing import Tuple, List

def sanitize_text(text: str) -> Tuple[str, List[str]]:
    """
    Pre-LLM Guardrail: Strips PII, IP addresses, and API keys.
    Returns the sanitized text and a list of redaction descriptions.
    """
    redactions = []
    
    # 1. IP Addresses
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    if re.search(ip_pattern, text):
        redactions.append("Redacted IP Addresses")
        text = re.sub(ip_pattern, '[REDACTED_IP]', text)
        
    # 2. Bearer Tokens / API Keys
    bearer_pattern = r'Bearer\s+[A-Za-z0-9\-\._~+\/]+'
    if re.search(bearer_pattern, text):
        redactions.append("Redacted Bearer Tokens")
        text = re.sub(bearer_pattern, 'Bearer [REDACTED_TOKEN]', text)
        
    sk_pattern = r'sk-[A-Za-z0-9_-]{20,}'
    if re.search(sk_pattern, text):
        redactions.append("Redacted Secret Keys (sk-...)")
        text = re.sub(sk_pattern, '[REDACTED_SECRET_KEY]', text)
        
    # 3. Emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if re.search(email_pattern, text):
        redactions.append("Redacted Email Addresses")
        text = re.sub(email_pattern, '[REDACTED_EMAIL]', text)

    return text, list(set(redactions))
