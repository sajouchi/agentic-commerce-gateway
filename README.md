# 🤖 Agent Commerce Gateway

> **An agentic B2B commerce gateway that searches products, evaluates offers, negotiates with buyers, and handles checkout through an AI-driven workflow.**

The **Agent Commerce Gateway** is a working prototype of an AI-powered commerce layer where a buyer can describe what they need in natural language and the system autonomously handles the journey from **intent → product search → offer evaluation → negotiation → payment**.

Built around a **LangGraph state machine**, specialized LLM agents, PostgreSQL + pgvector, FastAPI, Streamlit, and Razorpay.

**🚀Live Demo:** https://agentic-commerce-gateway-jmppspagvn8gxtxbey77kk.streamlit.app/

---

## ✨ What It Does

```text
Buyer Request
     │
     ▼
🧠 Intent Extraction
     │
     ▼
🔎 Product Search
     │
     ▼
🛡️ Offer Evaluation
     │
     ├──── Reject ──────────────► ❌
     │
     ├──── Negotiate ───────────► 🤝 Counter Offer
     │                                  │
     │                                  ▼
     │                            Buyer Response
     │                                  │
     │                         ┌────────┴────────┐
     │                         ▼                 ▼
     │                    Counter Again      Accept
     │                                           │
     ▼                                           ▼
💳 Payment Link ◄───────────────────────────────┘
     │
     ▼
💰 Razorpay Payment
     │
     ▼
✅ Payment Captured
```

---

## 🚀 Key Features

- 🧠 **Natural-language buyer intent extraction**
- 🔎 **Vector-based product search**
- 🛡️ **Automated offer evaluation**
- 🤝 **AI-powered price negotiation**
- 🔄 **Multi-step buyer ↔ agent negotiation**
- 💳 **Razorpay payment-link generation**
- 🔔 **Razorpay webhook payment confirmation**
- 🗄️ **PostgreSQL + pgvector persistence**
- 🕸️ **LangGraph stateful workflow**
- 🌐 **FastAPI backend**
- 🖥️ **Streamlit interactive demo**
- 🧵 **Thread-based graph state/checkpointing**

The LangGraph workflow uses conditional routing between offer evaluation, negotiation, acceptance/rejection, and payment nodes.

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Groq + `openai/gpt-oss-20b` |
| Agent orchestration | LangGraph |
| LLM framework | LangChain |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Database | PostgreSQL |
| Vector Search | pgvector |
| ORM | SQLModel / SQLAlchemy |
| Payments | Razorpay |
| Environment | Python 3.12+ |
| Package management | uv |
| Database container | Docker Compose |

The project currently targets **Python 3.12+** and includes LangGraph, FastAPI, Streamlit, pgvector, Razorpay and related dependencies in `pyproject.toml`.

---

## 📁 Project Structure

```text
agentic-commerce-gateway/
│
├── app/
│   ├── agent/
│   │   ├── prompts/
│   │   ├── agent_state_graph.py
│   │   └── agents.py
│   │
│   ├── api/
│   │   └── api_endpoints.py
│   │
│   ├── core/
│   │   ├── api_call_functions.py
│   │   ├── evaluate_offers.py
│   │   ├── pay_integration.py
│   │   ├── prep_and_response.py
│   │   └── routing_functions.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── sellerDatabase.py
│   │   ├── sellerPayments.py
│   │   └── sellerPolicies.py
│   │
│   ├── frontend/
│   │   └── app.py
│   │
│   ├── schema/
│   │   ├── agent_schema.py
│   │   └── allSchema.py
│   │
│   ├── scripts/
│   │   ├── mockDataCreate.py
│   │   └── mockSellerData.py
│   │
│   └── tools/
│       └── tools.py
│
├── app.py
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── test_graph.py
└── uv.lock
```

The repository is organized around separate agent, API, database, frontend, schema, script, and tool layers.

---

## ⚙️ How the Agent Works

The core workflow is implemented as a **LangGraph `StateGraph`**.

### 1. Intent

The buyer enters a natural-language request such as:

```text
I need 250 wireless headphones under ₹1700 each.
```

The intent agent extracts structured requirements such as:

- Quantity
- Target price
- Brand
- Product requirements

### 2. Product Search

The structured request is sent to the product search layer.

Products are retrieved using **vector search against PostgreSQL + pgvector**.

### 3. Offer Evaluation

The gateway evaluates the retrieved offer and determines whether it should:

- Accept/reject the offer
- Make a counter-offer
- Proceed to payment

### 4. Negotiation

If negotiation is required, the system generates a counter-offer.

The buyer can respond with:

```text
I accept the offer
```

or

```text
I reject the offer
```

The graph can also route the interaction back through another negotiation/evaluation cycle.

### 5. Checkout

Once an offer is accepted, the payment node creates a **Razorpay payment link**.

The Streamlit interface exposes the generated payment link to the buyer.

### 6. Payment Confirmation

Razorpay sends a webhook when the payment link is paid.

The API handles:

```text
POST /razorpay/webhook
```

and updates the payment status in the database when the `payment_link.paid` event is received.

---

## 🗄️ Database

The project uses **PostgreSQL with pgvector**.

A Docker Compose configuration is included and uses:

```text
Image: pgvector/pgvector:pg16
Database: commerce_db
User: test3
Password: test3
Port: 5432
```



Start the database with:

```bash
docker compose up -d
```

Check that it is running:

```bash
docker ps
```

Stop it with:

```bash
docker compose down
```

---

## 🛠️ Local Setup

### 1. Clone

```bash
git clone https://github.com/sajouchi/agentic-commerce-gateway.git
cd agentic-commerce-gateway
```

### 2. Create environment

Create a `.env` file:

```env
groq_api_key=YOUR_GROQ_API_KEY

razor_key_id=YOUR_RAZORPAY_KEY_ID
razor_secret_key=YOUR_RAZORPAY_SECRET_KEY
```

> Never commit your `.env` file or API keys.

### 3. Install dependencies

Using `uv`:

```bash
uv sync
```

Or using pip:

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL + pgvector

```bash
docker compose up -d
```

### 5. Run the application

```bash
uv run python app.py
```

Or:

```bash
python app.py
```

---

## 🖥️ Streamlit Demo

The project includes an interactive Streamlit interface for simulating the complete buyer journey.

You can also run it directly with:

```bash
streamlit run app/frontend/app.py
```

The UI exposes:

```text
Buyer Request
      ↓
Intent
      ↓
Matched Product
      ↓
Negotiation
      ↓
Accept / Reject
      ↓
Payment Link
      ↓
Payment Status
```

The frontend maintains a unique graph thread for each simulation and allows the buyer to start a fresh session.

---

## 🌐 API

The FastAPI application currently exposes endpoints including:

| Endpoint | Purpose |
|---|---|
| `GET /` | API health check |
| `POST /search` | Product/vector search |
| `POST /user_response` | Buyer response |
| `POST /razorpay/veryify` | Verify Razorpay payment signature |
| `POST /razorpay/webhook` | Receive Razorpay payment events |

The API is configured with the `/api/v1` root path.

---

## 🧪 Testing

Run the graph test:

```bash
python test_graph.py
```

The LangGraph implementation also exposes:

```python
initiate_graph(...)
human_response(...)
visual_graph(...)
```

for running and inspecting the agent workflow.

---

## 🔐 Payment Flow

The prototype uses Razorpay Payment Links:

```text
Offer Accepted
      │
      ▼
Create Payment Link
      │
      ▼
Buyer Opens Checkout
      │
      ▼
Razorpay Payment
      │
      ▼
Razorpay Webhook
      │
      ▼
payment_link.paid
      │
      ▼
Update PostgreSQL
      │
      ▼
Payment Status = paid
```

---

## 🎯 Example

**Buyer:**

```text
I need 250 wireless headphones under ₹1700 each.
```

**Gateway:**

```text
→ Extract requirements
→ Search product catalog
→ Evaluate seller offer
→ Generate counter-offer
→ Ask buyer for decision
```

**Buyer:**

```text
I accept the offer.
```

**Gateway:**

```text
→ Accept deal
→ Generate Razorpay payment link
→ Wait for payment
```

**After successful payment:**

```text
✅ Payment Successful & Captured!
```

---

## 🧠 Architecture

```text
                 ┌─────────────────────┐
                 │      Streamlit      │
                 │     Buyer UI        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │      LangGraph      │
                 │   Agent Workflow    │
                 └──────────┬──────────┘
                            │
            ┌───────────────┼────────────────┐
            ▼               ▼                ▼
       Intent Agent    Search Layer     Offer Evaluator
            │               │                │
            │               ▼                │
            │        PostgreSQL +            │
            │           pgvector             │
            │                                │
            └───────────────┬────────────────┘
                            ▼
                     Negotiation Agent
                            │
                            ▼
                     Payment Agent
                            │
                            ▼
                       Razorpay
                            │
                            ▼
                       Webhook
                            │
                            ▼
                    Payment Database
```

---

## 🚧 Project Status

**Prototype / Demo**

The current implementation demonstrates the core agentic commerce loop:

**Search → Evaluate → Negotiate → Accept/Reject → Checkout → Payment Confirmation**

It is intended as an experimental foundation for building more production-oriented agentic commerce infrastructure.

---

## 🔮 Future Improvements

Potential next steps include:

- Persistent LangGraph checkpoints
- Production-grade Redis/PostgreSQL state management
- Authentication & authorization
- Seller onboarding APIs
- Multiple seller/offer comparison
- Better negotiation policies
- Transaction/order lifecycle management
- Idempotent payment webhooks
- Payment failure/retry handling
- Observability and tracing
- Automated evaluation of agent decisions
- Production deployment
- API authentication and rate limiting
- More robust database migrations

---

## 📜 License

This project is currently provided as a prototype for experimentation and development.