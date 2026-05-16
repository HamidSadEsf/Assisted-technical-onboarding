document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const loading = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    const resultsSection = document.getElementById('results-section');
    const sourceText = document.getElementById('source-text');
    const mappedJson = document.getElementById('mapped-json');
    const errorMsg = document.getElementById('error-msg');
    const redactionBadges = document.getElementById('redaction-badges');

    const approveBtn = document.getElementById('approve-btn');
    const demoBtn = document.getElementById('demo-btn');

    // Standard API Upload Logic
    uploadBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) {
            showError("Please select a Markdown (.md) file.");
            return;
        }

        // Reset UI
        errorMsg.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loading.classList.remove('hidden');
        loadingText.textContent = "Running Sanitization & RAG Pipeline...";
        redactionBadges.innerHTML = '';

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://localhost:8000/api/process", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "An error occurred during processing.");
            }

            // Populate UI
            sourceText.textContent = data.original_text; 
            mappedJson.textContent = JSON.stringify(data.mapped_schema, null, 2);
            
            // Add Redaction Badges
            if (data.redactions && data.redactions.length > 0) {
                data.redactions.forEach(r => {
                    const span = document.createElement('span');
                    span.className = 'badge';
                    span.textContent = r;
                    redactionBadges.appendChild(span);
                });
            } else {
                const span = document.createElement('span');
                span.className = 'badge success';
                span.textContent = "Clean Doc (No PII)";
                redactionBadges.appendChild(span);
            }

            loading.classList.add('hidden');
            resultsSection.classList.remove('hidden');

        } catch (err) {
            loading.classList.add('hidden');
            showError(err.message);
        }
    });

    // Auto-Run Demo Mode Logic
    demoBtn.addEventListener('click', async () => {
        // Reset UI
        errorMsg.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loading.classList.remove('hidden');
        redactionBadges.innerHTML = '';
        fileInput.value = ''; // clear any file
        
        // Artificial Delays for Demo Recording
        const sleep = ms => new Promise(r => setTimeout(r, ms));
        
        loadingText.textContent = "Initiating Pipeline...";
        await sleep(800);
        
        loadingText.textContent = "Guardrail Active: Stripping PII locally...";
        await sleep(1500);
        
        loadingText.textContent = "Semantic Chunking: Preserving payload structures...";
        await sleep(1200);
        
        loadingText.textContent = "LLM Mapping via Gemini: Enforcing deterministic Pydantic schema...";
        await sleep(2000);

        loadingText.textContent = "Validating JSON Schema...";
        await sleep(800);

        // Mock Data Payload to simulate backend response
        const mockSourceText = `# Global Partner API Documentation - V 2.4 (Draft)

Contact: [REDACTED_EMAIL]
Test Environment: [REDACTED_IP]
Auth Header: Authorization: Bearer [REDACTED_SECRET_KEY]

## User Investment Profile Endpoint

This endpoint retrieves the risk appetite and asset allocation for a specific client. It's used during the initial onboarding phase.  

GET /v1/clients/{client_id}/strategy

Request Parameters:
- client_id (string, required): The internal UUID for the partner's customer.
- include_history (boolean, optional): Set to true to see past allocation changes.`;

        const mockMappedSchema = {
            "base_url": "https://api.partner.com",
            "endpoints": [
                {
                    "internal_name": "mapped_get_v1_clients_{client_id}_strategy",
                    "partner_method": "GET",
                    "partner_path": "/v1/clients/{client_id}/strategy",
                    "authentication_type": "Bearer",
                    "required_payload_fields": []
                }
            ]
        };

        const mockRedactions = [
            "Redacted Email Addresses",
            "Redacted IP Addresses",
            "Redacted Secret Keys (sk-...)"
        ];

        // Populate UI
        sourceText.textContent = mockSourceText;
        mappedJson.textContent = JSON.stringify(mockMappedSchema, null, 2);
        
        mockRedactions.forEach(r => {
            const span = document.createElement('span');
            span.className = 'badge';
            span.textContent = r;
            redactionBadges.appendChild(span);
        });

        loading.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Stop pulse animation after running demo
        demoBtn.classList.remove('demo-pulse');
    });

    approveBtn.addEventListener('click', () => {
        alert("Mapping Approved! Proceeding to code generation pipeline...");
    });

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }
});
