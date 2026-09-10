from typing import List, Optional

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.matching.buyer_matching import match_buyers
from src.forecasting.predictor import predict_price
from src.recommendations.sell_recommendation import (
    get_sell_recommendation,
)
from src.recommendations.buy_recommendation import (
    get_buy_recommendation,
)
from src.recommendations.market_recommendation import (
    recommend_best_market,
)
from src.recommendations.timing import (
    recommend_best_time,
)
from src.recommendations.net_return import (
    calculate_net_return,
)
from src.matching.farmer_matching import match_farmers
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="KisanSetu AI API",
    description=(
        "AI and decision intelligence services "
        "for the KisanSetu agriculture platform."
    ),
    version="1.0.0",
)
chat_service = ChatService()

@app.post("/ai/chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest):
    response = await chat_service.chat(
        conversation_id=request.conversation_id,
        message=request.message,
        language=request.language,
    )

    return ChatResponse(
        conversation_id=request.conversation_id,
        response=response,
        language=request.language,
    )

# ============================================================
# Request Models
# ============================================================

class SellRecommendationRequest(BaseModel):
    current_price: float = Field(..., ge=0)
    predicted_price: float = Field(..., ge=0)
    transport_cost: float = Field(0.0, ge=0)
    quantity: float = Field(1.0, gt=0)
    price_unit: str = "Rs./Quintal"
    min_change_percent: float = Field(0.0, ge=0)


class BuyRecommendationRequest(BaseModel):
    current_price: float = Field(..., ge=0)
    predicted_price: float = Field(..., ge=0)
    quantity: float = Field(1.0, gt=0)
    min_change_percent: float = Field(2.0, ge=0)
    price_unit: str = "Rs./Quintal"


class MarketRequest(BaseModel):
    market: str
    current_price: float = Field(..., ge=0)
    transport_cost: float = Field(..., ge=0)
    predicted_price: Optional[float] = Field(None, ge=0)


class MarketRecommendationRequest(BaseModel):
    markets: List[MarketRequest]
    quantity: float = Field(1.0, gt=0)
    mode: str = "sell"


class TimingPrediction(BaseModel):
    date: str
    predicted_price: float = Field(..., ge=0)


class TimingRequest(BaseModel):
    predictions: List[TimingPrediction]
    mode: str = "sell"


class NetReturnRequest(BaseModel):
    price: float = Field(..., ge=0)
    quantity: float = Field(..., gt=0)
    transport_cost: float = Field(0.0, ge=0)
    storage_cost: float = Field(0.0, ge=0)
    other_costs: float = Field(0.0, ge=0)
    mode: str = "sell"
    price_unit: str = "Rs./Quintal"


# ============================================================
# Historical Market Data Models
# ============================================================

class HistoricalPriceRecord(BaseModel):
    Date: str
    State: str
    District: str
    Market: str
    Commodity: str
    Variety: Optional[str] = None
    Grade: Optional[str] = "Unknown"
    Modal_Price: float = Field(..., ge=0)
    Arrival_Quantity: Optional[float] = Field(None, ge=0)


class ForecastRequest(BaseModel):
    historical_data: List[HistoricalPriceRecord]
    arrival_quantity: Optional[float] = Field(None, ge=0)


# ============================================================
# Sell Decision Request
# ============================================================

class SellDecisionRequest(BaseModel):
    historical_data: List[HistoricalPriceRecord]
    quantity: float = Field(..., gt=0)
    transport_cost: float = Field(0.0, ge=0)
    min_change_percent: float = Field(2.0, ge=0)


# ============================================================
# Buy Decision Request
# ============================================================

class BuyDecisionRequest(BaseModel):
    historical_data: List[HistoricalPriceRecord]
    quantity: float = Field(..., gt=0)
    min_change_percent: float = Field(2.0, ge=0)


# ============================================================
# Buyer Matching Request Models
# ============================================================

class FarmerLotRequest(BaseModel):
    farmer_id: str
    lot_id: str
    commodity: str
    variety: Optional[str] = None
    quantity: float = Field(..., gt=0)
    quantity_unit: str = "Quintal"
    grade: str = "Unknown"
    location: str
    expected_price: Optional[float] = Field(None, ge=0)
    available_date: str


class BuyerRequirementRequest(BaseModel):
    buyer_id: str
    requirement_id: str
    commodity: str
    variety: Optional[str] = None
    required_quantity: float = Field(..., gt=0)
    quantity_unit: str = "Quintal"
    grade: str = "Any"
    location: str
    offered_price: float = Field(..., ge=0)
    required_by_date: str


class BuyerMatchingRequest(BaseModel):
    farmer_lot: FarmerLotRequest
    buyers: List[BuyerRequirementRequest]


class FarmerMatchingRequest(BaseModel):
    buyer_requirement: BuyerRequirementRequest
    farmers: List[FarmerLotRequest]


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "KisanSetu AI API",
        "version": "1.0.0",
    }


# ============================================================
# Price Forecast
# ============================================================

@app.post("/forecast/price")
def forecast_price(request: ForecastRequest):

    historical_data = pd.DataFrame(
        record.model_dump()
        for record in request.historical_data
    )

    forecast = predict_price(
        historical_data=historical_data,
        arrival_quantity=request.arrival_quantity,
    )

    return forecast.model_dump()


# ============================================================
# Combined Sell Decision
# ============================================================

@app.post("/decision/sell")
def sell_decision(request: SellDecisionRequest):

    # Convert request records into DataFrame
    historical_data = pd.DataFrame(
        record.model_dump()
        for record in request.historical_data
    )

    # Convert date column
    historical_data["Date"] = pd.to_datetime(
        historical_data["Date"],
        errors="coerce",
    )

    # Sort chronologically
    historical_data = historical_data.sort_values("Date")

    # Get latest market price
    latest_record = historical_data.iloc[-1]

    current_price = float(
        latest_record["Modal_Price"]
    )

    # Generate next-day price forecast
    forecast = predict_price(
        historical_data=historical_data,
    )

    predicted_price = float(
        forecast.predicted_price
    )

    # Generate sell recommendation
    recommendation = get_sell_recommendation(
        current_price=current_price,
        predicted_price=predicted_price,
        transport_cost=request.transport_cost,
        quantity=request.quantity,
        min_change_percent=request.min_change_percent,
    )

    return {
        "forecast": forecast.model_dump(),
        "recommendation": recommendation,
    }


# ============================================================
# Combined Buy Decision
# ============================================================

@app.post("/decision/buy")
def buy_decision(request: BuyDecisionRequest):

    # Convert request records into DataFrame
    historical_data = pd.DataFrame(
        record.model_dump()
        for record in request.historical_data
    )

    # Convert date column
    historical_data["Date"] = pd.to_datetime(
        historical_data["Date"],
        errors="coerce",
    )

    # Sort chronologically
    historical_data = historical_data.sort_values("Date")

    # Get latest market price
    latest_record = historical_data.iloc[-1]

    current_price = float(
        latest_record["Modal_Price"]
    )

    # Generate next-day price forecast
    forecast = predict_price(
        historical_data=historical_data,
    )

    predicted_price = float(
        forecast.predicted_price
    )

    # Generate buy recommendation
    recommendation = get_buy_recommendation(
        current_price=current_price,
        predicted_price=predicted_price,
        quantity=request.quantity,
        min_change_percent=request.min_change_percent,
    )

    return {
        "forecast": forecast.model_dump(),
        "recommendation": recommendation,
    }


# ============================================================
# Direct Sell Recommendation
# ============================================================

@app.post("/recommend/sell")
def sell_recommendation(
    request: SellRecommendationRequest
):

    return get_sell_recommendation(
        current_price=request.current_price,
        predicted_price=request.predicted_price,
        transport_cost=request.transport_cost,
        quantity=request.quantity,
        price_unit=request.price_unit,
        min_change_percent=request.min_change_percent,
    )


# ============================================================
# Direct Buy Recommendation
# ============================================================

@app.post("/recommend/buy")
def buy_recommendation(
    request: BuyRecommendationRequest
):

    return get_buy_recommendation(
        current_price=request.current_price,
        predicted_price=request.predicted_price,
        quantity=request.quantity,
        min_change_percent=request.min_change_percent,
        price_unit=request.price_unit,
    )


# ============================================================
# Market Recommendation
# ============================================================

@app.post("/recommend/market")
def market_recommendation(
    request: MarketRecommendationRequest
):

    markets = [
        market.model_dump()
        for market in request.markets
    ]

    return recommend_best_market(
        markets=markets,
        quantity=request.quantity,
        mode=request.mode,
    )


# ============================================================
# Timing Recommendation
# ============================================================

@app.post("/recommend/time")
def timing_recommendation(
    request: TimingRequest
):

    predictions = [
        prediction.model_dump()
        for prediction in request.predictions
    ]

    return recommend_best_time(
        predictions=predictions,
        mode=request.mode,
    )


# ============================================================
# Net Return Calculation
# ============================================================

@app.post("/recommend/net-return")
def net_return(
    request: NetReturnRequest
):

    return calculate_net_return(
        price=request.price,
        quantity=request.quantity,
        transport_cost=request.transport_cost,
        storage_cost=request.storage_cost,
        other_costs=request.other_costs,
        mode=request.mode,
        price_unit=request.price_unit,
    )


# ============================================================
# Buyer Matching / Whom to Sell
# ============================================================

@app.post("/recommend/buyer")
def buyer_recommendation(
    request: BuyerMatchingRequest
):
    farmer_lot = request.farmer_lot.model_dump()

    buyers = [
        buyer.model_dump()
        for buyer in request.buyers
    ]

    return match_buyers(
        farmer_lot=farmer_lot,
        buyers=buyers,
    )


# ============================================================
# Farmer Matching / Who to Buy From
# ============================================================

@app.post("/recommend/farmer")
def farmer_recommendation(
    request: FarmerMatchingRequest
):
    buyer_requirement = request.buyer_requirement.model_dump()

    farmers = [
        farmer.model_dump()
        for farmer in request.farmers
    ]

    return match_farmers(
        buyer_requirement=buyer_requirement,
        farmers=farmers,
    )    

    