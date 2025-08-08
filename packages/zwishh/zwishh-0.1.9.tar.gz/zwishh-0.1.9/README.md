# 🧰 zwishh – Internal SDK and Utilities

This package provides shared utilities and client SDKs for Zwishh's internal microservices.

It is intended for **internal use only** and should be used by trusted services inside the Zwishh platform infrastructure.

---

## 📦 What's Included

### 🔑 Authentication & Security
- `verify_service_api_key_dep`: FastAPI dependency for verifying internal service API keys
- `get_current_user_id_dep`: Extracts and validates the current authenticated user from headers

### 🧬 SDK Clients
Clients for accessing core Zwishh services:

- `OrdersClient` – create & fetch orders
- `AuthClient` – validate tokens, get user info
- `CartClient` – manage cart state

Each client:
- Uses async `httpx`
- Injects service-to-service API key headers
- Handles standard error responses
- Retries the request with exponential backoff

---

## 🛠 Installation

You can install it directly from GitHub Packages:

```bash
pip install "zwishh==0.1.0" --extra-index-url https://pypi.pkg.github.com/zwishh
