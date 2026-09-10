const AI_API_URL = "http://127.0.0.1:8000";

export interface MarketIntelligenceRequest {
  state: string;
  district: string;
  market?: string | null;
  commodity: string;
  variety?: string | null;
  grade?: string | null;
  days?: number;
}

export interface MarketIntelligenceResponse {
  commodity: string;
  state: string;
  district: string;
  market: string;

  current_price: {
    min: number;
    max: number;
    modal: number;
    unit: string;
    date: string;
  };

  forecast: {
    predicted_price: number;
    forecast_date: string;
    model_version: string;
  };

  price_change: {
    absolute: number;
    percentage: number;
    direction: string;
  };

  recommendation: {
    action: string;
    reason: string;
    expected_price: number;
  };

  historical_prices: Array<{
    date: string;
    min: number;
    max: number;
    avg: number;
  }>;

  nearby_markets: Array<any>;

  market_comparison: Array<any>;

  insights: Array<{
    title: string;
    text: string;
  }>;
}

export async function getMarketIntelligence(
  request: MarketIntelligenceRequest
): Promise<MarketIntelligenceResponse> {
  const response = await fetch(
    `${AI_API_URL}/market/intelligence`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Market intelligence API returned HTTP ${response.status}`
    );
  }

  return (await response.json()) as MarketIntelligenceResponse;
}