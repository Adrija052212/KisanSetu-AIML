from typing import Dict, List, Optional

import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.matching.buyer_matching import match_buyers
from src.matching.farmer_matching import match_farmers

from src.forecasting.predictor import predict_price

from src.data_access.agmarknet_data import (
    get_historical_market_prices,
    get_agmarknet_markets,
    get_current_market_prices,
)

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

from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService

from src.services.recommendation_service import (
    get_sell_decision_from_market,
    get_buy_decision_from_market,
)

from src.services.market_service import (
    get_market_recommendation,
)

from src.services.buyer_service import (
    get_best_buyers,
)


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


chat_service = ChatService()


# ============================================================
# AI Chat
# ============================================================

@app.post("/ai/chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest):
    response = await chat_service.chat(
        conversation_id=request.conversation_id,
        message=request.message,
        language=request.language,
        location=request.location,
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


class MarketDecisionRequest(BaseModel):
    commodity: str = Field(..., min_length=1)
    state: Optional[str] = None
    district: Optional[str] = None
    variety: Optional[str] = None
    grade: Optional[str] = None
    quantity: float = Field(..., gt=0)
    mode: str = "sell"
    transport_costs: Dict[str, float] = Field(default_factory=dict)


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
# Market Intelligence Request
# ============================================================

class MarketIntelligenceRequest(BaseModel):
    state: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1)
    market: Optional[str] = None
    commodity: str = Field(..., min_length=1)
    variety: Optional[str] = None
    grade: Optional[str] = None
    days: int = Field(30, ge=1, le=60)


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


# ============================================================
# Forecast Request
# ============================================================

class ForecastRequest(BaseModel):
    state: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1)
    market: str = Field(..., min_length=1)
    commodity: str = Field(..., min_length=1)
    variety: Optional[str] = None
    grade: Optional[str] = None
    days: int = Field(30, ge=1, le=60)
    arrival_quantity: Optional[float] = Field(None, ge=0)


# ============================================================
# Sell Decision Request
# ============================================================

class SellDecisionRequest(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    grade: str
    quantity: float = Field(..., gt=0)
    transport_cost: float = Field(0.0, ge=0)
    min_change_percent: float = Field(2.0, ge=0)


# ============================================================
# Buy Decision Request
# ============================================================

class BuyDecisionRequest(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    grade: str
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
# Real Buyer Recommendation Request
# ============================================================

class BuyerRecommendationRequest(BaseModel):
    commodity: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    grade: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    variety: Optional[str] = None
    expected_price: Optional[float] = Field(None, ge=0)


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

    historical_data = get_historical_market_prices(
        end_date=pd.Timestamp.now().strftime("%Y-%m-%d"),
        days=request.days,
        state=request.state,
        district=request.district,
        market=request.market,
        commodity=request.commodity,
        variety=request.variety,
        grade=request.grade,
    )

    forecast = predict_price(
        historical_data=historical_data,
        arrival_quantity=request.arrival_quantity,
    )

    result = forecast.model_dump()

    # AGMARKNET/model prices are stored in ₹/quintal.
    # Frontend displays farmer-facing prices in ₹/kg.
    result["predicted_price"] = (
        result["predicted_price"] / 100
    )

    return result


# ============================================================
# Unified Market Intelligence
# ============================================================

@app.post("/market/intelligence")
def market_intelligence(
    request: MarketIntelligenceRequest,
):
    """
    Unified Market Intelligence endpoint.

    Data flow:

    AGMARKNET
        ↓
    Current + historical prices
        ↓
    XGBoost next-day prediction
        ↓
    Sell / wait recommendation
        ↓
    District market comparison
        ↓
    Frontend Market Prices page
    """

    state = request.state.strip()
    district = request.district.strip()
    commodity = request.commodity.strip()

    today = pd.Timestamp.now().strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # 1. Resolve AGMARKNET markets
    # --------------------------------------------------------

    markets = get_agmarknet_markets(
        state=state,
        district=district,
    )

    if not markets:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No AGMARKNET markets found for "
                f"{state} / {district}."
            ),
        )

    # --------------------------------------------------------
    # 2. Select primary market
    # --------------------------------------------------------

    selected_market = None

    if request.market:
        requested_market = (
            request.market.strip().lower()
        )

        for item in markets:
            market_name = str(
                item.get("market", "")
            ).strip()

            if market_name.lower() == requested_market:
                selected_market = item
                break

    # If frontend did not specify a market,
    # use the first AGMARKNET market available.
    if selected_market is None:
        selected_market = markets[0]

    primary_market = str(
        selected_market["market"]
    ).strip()

    # --------------------------------------------------------
    # 3. Get historical data
    # --------------------------------------------------------

    try:
        historical_data = (
            get_historical_market_prices(
                end_date=today,
                days=request.days,
                state=state,
                district=district,
                market=primary_market,
                commodity=commodity,
                variety=request.variety,
                grade=request.grade,
            )
        )

    except Exception as market_error:

        print(
            "Unable to load historical AGMARKNET data: "
            f"{market_error}"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "AGMARKNET market data is temporarily "
                "unavailable. Please try again later."
            ),
        )

    if historical_data.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No historical AGMARKNET data found "
                f"for {commodity} at {primary_market}."
            ),
        )

    # --------------------------------------------------------
    # 4. Resolve exact variety and grade
    #
    # The XGBoost model needs a consistent series.
    # --------------------------------------------------------

    historical_data = (
        historical_data
        .sort_values("Date")
        .reset_index(drop=True)
    )

    latest = historical_data.iloc[-1]

    exact_variety = None

    if pd.notna(latest["Variety"]):
        exact_variety = str(
            latest["Variety"]
        ).strip()

    exact_grade = None

    if pd.notna(latest["Grade"]):
        exact_grade = str(
            latest["Grade"]
        ).strip()

    # If variety or grade was not explicitly supplied,
    # refetch the history using the latest exact series.

    if (
        request.variety is None
        or request.grade is None
    ):

        try:

            exact_history = (
                get_historical_market_prices(
                    end_date=today,
                    days=request.days,
                    state=state,
                    district=district,
                    market=primary_market,
                    commodity=commodity,
                    variety=exact_variety,
                    grade=exact_grade,
                )
            )

            if not exact_history.empty:

                historical_data = (
                    exact_history
                    .sort_values("Date")
                    .reset_index(drop=True)
                )

        except Exception as market_error:

            # Do not fail the complete request if the
            # refinement request hits a temporary AGMARKNET error.
            print(
                "Unable to refresh historical data with "
                f"exact variety/grade: {market_error}"
            )

    # --------------------------------------------------------
    # 5. Current market price
    # --------------------------------------------------------

    latest = (
        historical_data
        .sort_values("Date")
        .iloc[-1]
    )

    current_modal_quintal = float(
        latest["Modal_Price"]
    )

    # Historical forecasting data contains Modal_Price,
    # but not Min_Price / Max_Price.
    # Use modal price as the available current price.

    current_min_quintal = current_modal_quintal
    current_max_quintal = current_modal_quintal

    current_min_kg = (
        current_min_quintal / 100
    )

    current_max_kg = (
        current_max_quintal / 100
    )

    current_modal_kg = (
        current_modal_quintal / 100
    )

    # --------------------------------------------------------
    # 6. XGBoost prediction
    # --------------------------------------------------------

    forecast = predict_price(
        historical_data=historical_data,
    )

    predicted_quintal = float(
        forecast.predicted_price
    )

    predicted_kg = (
        predicted_quintal / 100
    )

    # --------------------------------------------------------
    # 7. Price movement
    # --------------------------------------------------------

    price_change = (
        predicted_kg
        - current_modal_kg
    )

    if current_modal_kg > 0:

        price_change_percentage = (
            price_change
            / current_modal_kg
        ) * 100

    else:
        price_change_percentage = 0.0

    if price_change_percentage > 0.5:

        direction = "increase"

    elif price_change_percentage < -0.5:

        direction = "decrease"

    else:

        direction = "stable"

    # --------------------------------------------------------
    # 8. Sell / wait recommendation
    # --------------------------------------------------------

    recommendation = get_sell_recommendation(
        current_price=current_modal_kg,
        predicted_price=predicted_kg,
        transport_cost=0.0,
        quantity=1.0,
        price_unit="Rs./kg",
        min_change_percent=0.0,
    )

    # Convert recommendation to a normal dictionary.

    if hasattr(
        recommendation,
        "model_dump",
    ):

        recommendation_data = (
            recommendation.model_dump()
        )

    elif isinstance(
        recommendation,
        dict,
    ):

        recommendation_data = (
            recommendation
        )

    else:

        recommendation_data = {
            "action": "WAIT",
            "reason": str(
                recommendation
            ),
        }

    recommendation_action = (
        recommendation_data.get(
            "action",
            recommendation_data.get(
                "decision",
                recommendation_data.get(
                    "recommendation",
                    "WAIT",
                ),
            ),
        )
    )

    recommendation_reason = (
        recommendation_data.get(
            "reason",
            "Monitor the market before making a selling decision.",
        )
    )

    # --------------------------------------------------------
    # 9. Historical prices
    # --------------------------------------------------------

    historical_prices = []

    grouped = (
        historical_data
        .groupby("Date")
        .agg(
            min=("Modal_Price", "min"),
            max=("Modal_Price", "max"),
            avg=("Modal_Price", "mean"),
        )
        .reset_index()
        .sort_values("Date")
    )

    for _, row in grouped.iterrows():

        historical_prices.append(
            {
                "date": pd.Timestamp(
                    row["Date"]
                ).strftime(
                    "%d %b %Y"
                ),

                "min": float(
                    row["min"]
                ) / 100,

                "max": float(
                    row["max"]
                ) / 100,

                "avg": float(
                    row["avg"]
                ) / 100,
            }
        )

    # --------------------------------------------------------
    # 10. Nearby / district markets
    # --------------------------------------------------------

    nearby_markets = []

    # Check only a limited number of markets.
    # This avoids sending too many requests to AGMARKNET
    # and reduces 503 errors.

    markets_to_check = markets[:5]

    for market_info in markets_to_check:

        market_name = str(
            market_info.get(
                "market",
                "",
            )
        ).strip()

        market_id = int(
            market_info["market_id"]
        )

        state_id = int(
            market_info["state_id"]
        )

        try:

            current_records = (
                get_current_market_prices(
                    date=today,
                    market_id=market_id,
                    state_id=state_id,
                    district=district,
                )
            )

            # Match commodity.

            matching = [
                record
                for record in current_records
                if str(
                    record.get(
                        "Commodity",
                        "",
                    )
                ).strip().lower()
                == commodity.lower()
            ]

            if not matching:
                continue

            # Match exact variety if available.

            if exact_variety:

                variety_matches = [
                    record
                    for record in matching
                    if str(
                        record.get(
                            "Variety",
                            "",
                        )
                    ).strip().lower()
                    == exact_variety.lower()
                ]

                if variety_matches:
                    matching = variety_matches

            # Match exact grade if available.

            if exact_grade:

                grade_matches = [
                    record
                    for record in matching
                    if str(
                        record.get(
                            "Grade",
                            "",
                        )
                    ).strip().lower()
                    == exact_grade.lower()
                ]

                if grade_matches:
                    matching = grade_matches

            if not matching:
                continue

            record = matching[-1]

            modal = record.get(
                "Modal_Price"
            )

            if modal is None:
                continue

            modal_kg = (
                float(modal) / 100
            )

            min_price = (
                float(
                    record.get(
                        "Min_Price"
                    ) or 0
                ) / 100
            )

            max_price = (
                float(
                    record.get(
                        "Max_Price"
                    ) or 0
                ) / 100
            )

            nearby_markets.append(
                {
                    "market": market_name,

                    "location": (
                        f"{district}, {state}"
                    ),

                    "min": min_price,

                    "max": max_price,

                    "avg": modal_kg,

                    "change": 0,

                    # AGMARKNET does not provide
                    # distance in this response.
                    "distance": "—",

                    "arrivals": record.get(
                        "Arrival_Quantity"
                    ),

                    # No demand value is invented.
                    "demand": None,

                    # No transport cost is invented.
                    "transportCost": None,
                }
            )

        except Exception as error:

            print(
                f"Unable to load market "
                f"{market_name}: {error}"
            )

            continue

    # --------------------------------------------------------
    # 11. Market comparison
    # --------------------------------------------------------

    market_comparison = []

    ranked_markets = sorted(
        nearby_markets,
        key=lambda item: item["avg"],
        reverse=True,
    )

    for rank, market in enumerate(
        ranked_markets,
        start=1,
    ):

        market_comparison.append(
            {
                "market": market["market"],

                "location": market["location"],

                "currentPrice": market["avg"],

                "effectivePrice": market["avg"],

                "rank": rank,

                "recommendation": (
                    "Best selling price"
                    if rank == 1
                    else "Compare before selling"
                ),
            }
        )

    # --------------------------------------------------------
    # 12. Market insights
    # --------------------------------------------------------

    insights = []

    if direction == "increase":

        insights.append(
            {
                "title": "Price outlook",

                "text": (
                    "XGBoost predicts a higher "
                    "price tomorrow, with an "
                    "expected change of "
                    f"{price_change_percentage:.1f}%."
                ),
            }
        )

    elif direction == "decrease":

        insights.append(
            {
                "title": "Price outlook",

                "text": (
                    "XGBoost predicts a lower "
                    "price tomorrow, with an "
                    "expected change of "
                    f"{abs(price_change_percentage):.1f}%."
                ),
            }
        )

    else:

        insights.append(
            {
                "title": "Price outlook",

                "text": (
                    "The predicted price is "
                    "relatively stable compared "
                    "with the current modal price."
                ),
            }
        )

    if nearby_markets:

        best_market = max(
            nearby_markets,
            key=lambda item: item["avg"],
        )

        insights.append(
            {
                "title": "Market comparison",

                "text": (
                    f"{best_market['market']} "
                    "currently has the highest "
                    "available modal price at "
                    f"₹{best_market['avg']:.2f}/kg "
                    "among the markets checked."
                ),
            }
        )

    insights.append(
        {
            "title": "Data source",

            "text": (
                "Current and historical market "
                "prices are sourced from "
                "AGMARKNET. The next-day price "
                "forecast is generated using "
                "the KisanSetu XGBoost model."
            ),
        }
    )

    # --------------------------------------------------------
    # 13. Final response
    # --------------------------------------------------------

    return {
        "commodity": commodity,

        "state": state,

        "district": district,

        "market": primary_market,

        "current_price": {
            "min": current_min_kg,

            "max": current_max_kg,

            "modal": current_modal_kg,

            "unit": "₹/kg",

            "date": pd.Timestamp(
                latest["Date"]
            ).strftime(
                "%Y-%m-%d"
            ),
        },

        "forecast": {
            "predicted_price": predicted_kg,

            "forecast_date": (
                forecast.forecast_date.isoformat()
            ),

            "model_version": (
                forecast.model_version
            ),
        },

        "price_change": {
            "absolute": price_change,

            "percentage": (
                price_change_percentage
            ),

            "direction": direction,
        },

        "recommendation": {
            "action": recommendation_action,

            "reason": recommendation_reason,

            "expected_price": predicted_kg,
        },

        "historical_prices": historical_prices,

        "nearby_markets": nearby_markets,

        "market_comparison": market_comparison,

        "insights": insights,
    }


# ============================================================
# Combined Sell Decision
# ============================================================

@app.post("/decision/sell")
def sell_decision(
    request: SellDecisionRequest,
):

    return get_sell_decision_from_market(
        state=request.state,
        district=request.district,
        market=request.market,
        commodity=request.commodity,
        variety=request.variety,
        grade=request.grade,
        quantity=request.quantity,
        transport_cost=request.transport_cost,
        min_change_percent=request.min_change_percent,
    )


# ============================================================
# Combined Buy Decision
# ============================================================

@app.post("/decision/buy")
def buy_decision(
    request: BuyDecisionRequest,
):

    return get_buy_decision_from_market(
        state=request.state,
        district=request.district,
        market=request.market,
        commodity=request.commodity,
        variety=request.variety,
        grade=request.grade,
        quantity=request.quantity,
        min_change_percent=request.min_change_percent,
    )


# ============================================================
# Direct Sell Recommendation
# ============================================================

@app.post("/recommend/sell")
def sell_recommendation(
    request: SellRecommendationRequest,
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
    request: BuyRecommendationRequest,
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
    request: MarketRecommendationRequest,
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
# Combined Market Decision
# ============================================================

@app.post("/decision/market")
def market_decision(
    request: MarketDecisionRequest,
):

    return get_market_recommendation(
        commodity=request.commodity,
        state=request.state,
        district=request.district,
        variety=request.variety,
        grade=request.grade,
        quantity=request.quantity,
        mode=request.mode,
        transport_costs=request.transport_costs,
    )


# ============================================================
# Timing Recommendation
# ============================================================

@app.post("/recommend/time")
def timing_recommendation(
    request: TimingRequest,
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
    request: NetReturnRequest,
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
    request: BuyerMatchingRequest,
):

    farmer_lot = (
        request.farmer_lot.model_dump()
    )

    buyers = [
        buyer.model_dump()
        for buyer in request.buyers
    ]

    return match_buyers(
        farmer_lot=farmer_lot,
        buyers=buyers,
    )


# ============================================================
# Real Buyer Recommendation / Whom to Sell
# ============================================================

@app.post("/recommend/buyers")
def real_buyer_recommendation(
    request: BuyerRecommendationRequest,
):

    return get_best_buyers(
        commodity=request.commodity,
        quantity=request.quantity,
        grade=request.grade,
        location=request.location,
        variety=request.variety,
        expected_price=request.expected_price,
    )


# ============================================================
# Farmer Matching / Who to Buy From
# ============================================================

@app.post("/recommend/farmer")
def farmer_recommendation(
    request: FarmerMatchingRequest,
):

    buyer_requirement = (
        request.buyer_requirement.model_dump()
    )

    farmers = [
        farmer.model_dump()
        for farmer in request.farmers
    ]

    return match_farmers(
        buyer_requirement=buyer_requirement,
        farmers=farmers,
    )