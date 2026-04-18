# TMM TradingView Access Gateway

Manages invite-only TradingView script access for TMM indicators.
Receives webhook calls from Make automations triggered by Stripe and NOWPayments.

## Indicators Managed

| Shortname | Full Name                    | Pine ID                                      |
|-----------|------------------------------|----------------------------------------------|
| VCI       | Volume Confluence Indicator  | PUB;51ca8acd0b0d4ac00bd9684a3d989a427        |
| CCO       | Confluence Catalyst Osc      | PUB;ffa472cc81d34f908514dc05946cf84a         |
| CCPRO     | Confluence Catalyst Pro      | PUB;c37df8f0c33c41b1afccf49df071009a         |
| VPI       | Volume Pressure Indicator    | PUB;y7e62ed783a64aa99b6a302f1b2d97a3         |
| WCO       | Wave Confluence Oscillator   | PUB;5477dfc3518642228abbe2d6c5b55579         |

---

## Local Setup

```bash
git clone https://github.com/mattotee/Tradingview-Access-Management
cd Tradingview-Access-Management
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and fill in TV_SERVICE_PASSWORD and TMM_API_KEY
```

Generate a strong API key:
```bash
openssl rand -hex 32
```

Run locally:
```bash
python main.py
```

Test with curl:
```bash
# Health check (no auth)
curl http://localhost:5001/health

# Validate a username
curl -H "X-API-Key: your_key" "http://localhost:5001/validate-user?username=mattotee_trader"

# Grant access (1 month)
curl -X POST http://localhost:5001/add-access \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"username": "mattotee_trader", "indicators": ["VCI"], "duration": "1M"}'

# Revoke access
curl -X POST http://localhost:5001/remove-access \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"username": "mattotee_trader", "indicators": ["VCI"]}'
```

---

## VPS Deployment

```bash
# Copy files to VPS
scp -r . tmm@your-vps:/home/tmm/tmm-tv-gateway/

# SSH into VPS
ssh tmm@your-vps

# Set up virtualenv
cd /home/tmm/tmm-tv-gateway
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up systemd service
sudo cp tmm-tv-gateway.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tmm-tv-gateway
sudo systemctl start tmm-tv-gateway

# Check it's running
sudo systemctl status tmm-tv-gateway
journalctl -u tmm-tv-gateway -f
```

---

## API Endpoints

All endpoints except /health require header: `X-API-Key: <your_key>`

### GET /health
No auth. Returns service status and TV session state.

### GET /validate-user?username=<tv_username>
Validate a TradingView username before granting access.
Call this first in Make and halt if valid=false - email customer to resubmit.

### POST /add-access
Grant access. Body:
```json
{
  "username": "customer_tv_username",
  "indicators": ["VCI"],
  "duration": "1M"
}
```
Duration formats: "1M" (1 month), "7D" (7 days), "1Y" (1 year), "L" (lifetime)
For Edge Bundle: `"indicators": ["VCI", "CCO", "CCPRO", "VPI"]`

### POST /remove-access
Revoke access. Body:
```json
{
  "username": "customer_tv_username",
  "indicators": ["VCI"]
}
```

### GET /check-access?username=<tv_username>&indicators=VCI,CCO
Check current access status. Returns hasAccess, noExpiration, currentExpiration.

### POST /extend-access
Extend existing access (monthly renewal). Same body as /add-access.

---

## Make Automation Flow

### New subscription (Stripe checkout.session.completed):
1. Extract TV username from Stripe metadata
2. POST /validate-user - if invalid, email customer, halt
3. POST /add-access with indicators and duration "1M"
4. Send welcome email

### Monthly renewal (Stripe invoice.paid):
1. POST /extend-access with indicators and duration "1M"

### Cancellation (Stripe customer.subscription.deleted):
1. POST /remove-access with indicators

### NOWPayments crypto - same flows triggered by IPN status: finished/expired
