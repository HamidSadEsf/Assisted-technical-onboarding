# Global Partner API Documentation - V 2.4 (Draft)

Contact: dev-support@partner-fintech.io
Test Environment: 192.168.1.45
Auth Header: Authorization: Bearer sk_test_51Mz2p8L9qX0Z9

## User Investment Profile Endpoint

This endpoint retrieves the risk appetite and asset allocation for a specific client. It's used during the initial onboarding phase.  

GET /v1/clients/{client_id}/strategy

Request Parameters:
- client_id (string, required): The internal UUID for the partner's customer.
- include_history (boolean, optional): Set to true to see past allocation changes.

Example Response:
{
  "status": "success",
  "data": {
    "risk_level": 4,
    "strategy_type": "aggressive_growth",
    "last_updated": "2026-05-12T14:30:00Z",
    "assets": [
      {"ticker": "BTC", "weight": 0.05},
      {"ticker": "IWDA", "weight": 0.75},
      {"ticker": "EIMI", "weight": 0.20}
    ]
  }
}

## Order Execution Endpoint

Send trade instructions directly to our clearing engine.

POST /v1/orders/execute

Payload Requirements:
- instrument_id: ISIN or internal ID.
- side: BUY or SELL.
- amount: Decimal value in EUR.

Note: If the order fails, check the error_code against the legacy error table at 10.0.5.22/docs/errors.
