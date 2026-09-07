# KisanSetu AI

The AI/ML component of the KisanSetu agricultural marketplace platform.

KisanSetu connects farmers and buyers while providing AI-powered market intelligence, price forecasting, recommendations, and intelligent matching.

---

## AI System

The AI system is designed around shared agricultural intelligence that can serve both farmers and buyers.

### Farmer-side Intelligence

- Market price forecasting
- Price trend analysis
- Market comparison
- Best market to sell
- Best time to sell
- Expected net return
- Buyer matching
- Weather-based agricultural insights

### Buyer-side Intelligence

- Current market price analysis
- Price forecasting
- Market comparison
- Available farmer-lot matching
- Supplier/farmer ranking
- Procurement recommendations
- Farmer matching

### Shared Intelligence

- Market price data
- Historical price analysis
- Price forecasting
- Market intelligence
- Farmer-buyer matching

### AI Chatbot

The AI chatbot will provide a conversational interface for both farmers and buyers.

Claude will act as the conversational reasoning layer, while MCP tools will provide access to KisanSetu's data, ML models, recommendation engines, and other services.

---

## Project Structure

```text
ai/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── models/
│   ├── price_forecasting/
│   └── matching/
│
├── src/
│   ├── data/
│   ├── features/
│   ├── forecasting/
│   ├── recommendations/
│   ├── matching/
│   ├── buyer/
│   ├── weather/
│   └── utils/
│
├── notebooks/
├── tests/
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md