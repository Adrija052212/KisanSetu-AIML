import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import DashboardLayout from "../components/DashboardLayout";

import AIPredictionCard from "../components/market/AIPredictionCard";
import CompareMarkets from "../components/market/CompareMarkets";
import HistoricalTable from "../components/market/HistoricalTable";
import MarketInsights from "../components/market/MarketInsights";
import MarketIntelligence from "../components/market/MarketIntelligence";
import MarketPriceFilters from "../components/market/MarketPriceFilters";
import type { PriceFilterValues } from "../components/market/MarketPriceFilters";
import MarketPriceHeader from "../components/market/MarketPriceHeader";
import NearbyMandis from "../components/market/NearbyMandis";
import PriceOverviewCard from "../components/market/PriceOverviewCard";
import SetPriceAlert from "../components/market/SetPriceAlert";

import {
  CROPS,
  DISTRICT_OPTIONS,
} from "../data/marketPrices";

import type {
  CropKey,
  CropPrediction,
  HistoryRow,
  MandiRow,
  PricePoint,
  PriceStats,
  TimeRange,
} from "../data/marketPrices";

import {
  getMarketIntelligence,
  type MarketIntelligenceResponse,
} from "../../services/marketIntelligenceApi";

import { cn } from "../../utils/cn";


function nowStamp(): string {
  const d = new Date();

  return `${d.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  })}, ${d.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })}`;
}


function cropParamToKey(
  value: string | null
): CropKey | null {
  if (!value) return null;

  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-");

  return normalized in CROPS
    ? (normalized as CropKey)
    : null;
}


function districtFromParam(
  value: string | null
): string {
  if (!value) return "Ahmednagar";

  const found = DISTRICT_OPTIONS.find(
    (d) =>
      d.toLowerCase() ===
      value.trim().toLowerCase()
  );

  return found ?? "Ahmednagar";
}


/*
 * Frontend uses "Ahmednagar".
 * AGMARKNET uses "Ahilyanagar".
 */
function districtForBackend(
  district: string
): string {
  if (
    district.trim().toLowerCase() ===
    "ahmednagar"
  ) {
    return "Ahilyanagar";
  }

  return district;
}


/*
 * Convert backend XGBoost prediction
 * into the existing frontend CropPrediction type.
 */
function createAIPrediction(
  data: MarketIntelligenceResponse
): CropPrediction {
  const current =
    Number(data.current_price.modal) || 0;

  const predicted =
    Number(data.forecast.predicted_price) || 0;

  const percentage =
    current > 0
      ? ((predicted - current) / current) * 100
      : 0;

  let recommendation =
    "Monitor the market before making a selling decision.";

  if (
    data.recommendation?.action ===
    "SELL"
  ) {
    recommendation =
      "The model indicates that selling now may be preferable based on the current forecast.";
  } else if (
    data.recommendation?.action ===
    "WAIT"
  ) {
    recommendation =
      "The model indicates that waiting may be preferable based on the expected price movement.";
  } else if (
    data.recommendation?.action ===
    "BUY"
  ) {
    recommendation =
      "The model indicates that current prices may be suitable for buying.";
  }

  return {
    price: predicted,

    days: "next day",

    increasePct:
      percentage === 0
        ? "0%"
        : `${percentage > 0 ? "+" : ""}${percentage.toFixed(
            1
          )}%`,

    note:
      `XGBoost forecast for ${data.commodity} at ${data.market.trim()} ` +
      `for ${data.forecast.forecast_date}. ` +
      `Current modal price is ₹${current.toFixed(2)}/kg.`,

    recommendation,
  };
}


/*
 * Convert backend current-price data
 * into the existing PriceStats type.
 */

function createStats(
  data: MarketIntelligenceResponse
): PriceStats {
  const history = data.historical_prices ?? [];

  let weeklyChange = 0;

  if (history.length >= 2) {
    const sortedHistory = [...history].sort(
      (a, b) =>
        new Date(a.date).getTime() -
        new Date(b.date).getTime()
    );

    const latest =
      sortedHistory[sortedHistory.length - 1];

    if (latest) {
      const latestDate = new Date(latest.date);

      const targetDate = new Date(latestDate);
      targetDate.setDate(
        targetDate.getDate() - 7
      );

      let previous = null;
      let smallestDifference = Infinity;

      for (const row of sortedHistory) {
        const rowDate = new Date(row.date);

        const difference = Math.abs(
          rowDate.getTime() -
            targetDate.getTime()
        );

        // Only accept data within 1 calendar day
        // of the target date.
        const oneDay =
          24 * 60 * 60 * 1000;

        if (
          difference <= oneDay &&
          difference < smallestDifference
        ) {
          previous = row;
          smallestDifference = difference;
        }
      }

      const latestPrice =
        Number(latest.avg) || 0;

      const previousPrice =
        Number(previous?.avg) || 0;

      if (previousPrice > 0) {
        weeklyChange =
          ((latestPrice - previousPrice) /
            previousPrice) *
          100;
      }
    }
  }

  return {
    min:
      Number(data.current_price.min) || 0,

    max:
      Number(data.current_price.max) || 0,

    avg:
      Number(data.current_price.modal) || 0,

    weeklyChange,
  };
}

/*
 * Convert backend historical prices
 * into the existing chart format.
 */
function createSeries(
  history: HistoryRow[],
  range: TimeRange
): PricePoint[] {
  if (!history.length) {
    return [];
  }

  let rows = history;

  if (range === "7d") {
    rows = history.slice(-7);
  } else if (range === "30d") {
    rows = history.slice(-30);
  } else if (range === "3m") {
    rows = history.slice(-90);
  } else if (range === "1y") {
    rows = history.slice(-365);
  }

  return rows.map((row) => ({
    label: row.date,
    price: Number(row.avg) || 0,
  }));
}


/*
 * Convert backend historical data
 * into HistoricalTable rows.
 */
function createHistoryRows(
  data: MarketIntelligenceResponse
): HistoryRow[] {
  return data.historical_prices.map(
    (row) => ({
      date: row.date,
      min: Number(row.min) || 0,
      max: Number(row.max) || 0,
      avg: Number(row.avg) || 0,
    })
  );
}


/*
 * Convert backend nearby-market data
 * into the existing MandiRow type.
 */
function createMandiRows(
  data: MarketIntelligenceResponse
): MandiRow[] {
  return data.nearby_markets.map(
    (market) => ({
      market: market.market,

      location:
        market.location ||
        `${data.district}, ${data.state}`,

      min:
        Number(market.min) || 0,

      max:
        Number(market.max) || 0,

      avg:
        Number(market.avg) || 0,

      change:
        Number(market.change) || 0,

      distance:
        market.distance || "—",

      arrivals:
        market.arrivals,

      demand:
        market.demand,

      transportCost:
        market.transportCost,
    })
  );
}


export default function MarketPricesPage() {
  const [params] =
    useSearchParams();

  const initialCrop =
    cropParamToKey(
      params.get("crop")
    ) ?? "tomato";

  const initialDistrict =
    districtFromParam(
      params.get("location")
    );

  const [draft, setDraft] =
    useState<PriceFilterValues>({
      crop: initialCrop,

      variety:
        CROPS[initialCrop]!
          .varieties[0]!,

      state: "Maharashtra",

      district:
        initialDistrict,
    });

  const [applied, setApplied] =
    useState<PriceFilterValues>(
      draft
    );

  const [range, setRange] =
    useState<TimeRange>("7d");

  const [historyRange, setHistoryRange] =
    useState("Last 30 Days");

  const [updating, setUpdating] =
    useState(false);

  const [refreshing, setRefreshing] =
    useState(false);

  const [lastUpdated, setLastUpdated] =
    useState(
      "Loading live market data..."
    );

  const [toast, setToast] =
    useState("");

  const [marketData, setMarketData] =
    useState<MarketIntelligenceResponse | null>(
      null
    );

  const [aiPrediction, setAiPrediction] =
    useState<CropPrediction | null>(
      null
    );

  const [aiError, setAiError] =
    useState("");


  useEffect(() => {
    if (!toast) return;

    const timer =
      window.setTimeout(
        () => setToast(""),
        2600
      );

    return () =>
      window.clearTimeout(timer);
  }, [toast]);


  const crop =
    CROPS[applied.crop]!;


  /*
   * Load all market intelligence
   * from the FastAPI backend.
   */
  const fetchMarketIntelligence =
    async (
      values: PriceFilterValues
    ) => {
      setAiError("");

      try {
        const backendDistrict =
          districtForBackend(
            values.district
          );

        const data =
          await getMarketIntelligence({
            state:
              values.state,

            district:
              backendDistrict,

            /*
             * null means the backend
             * selects the primary market.
             */
            market:
              null,

            commodity:
              CROPS[
                values.crop
              ]!.label,

            variety:
              values.variety ===
              "All Varieties"
                ? null
                : values.variety,

            grade:
              null,

            days:
              30,
          });

        setMarketData(data);

        setAiPrediction(
          createAIPrediction(data)
        );

        setLastUpdated(
          nowStamp()
        );

        return data;

      } catch (error) {
        console.error(
          "KisanSetu market intelligence failed:",
          error
        );

        setMarketData(null);

        setAiPrediction(null);

        setAiError(
          "Unable to load live market intelligence. Please make sure the AI backend is running and AGMARKNET is reachable."
        );

        return null;
      }
    };


  const patchDraft = (
    patch: Partial<PriceFilterValues>
  ) => {
    setDraft((current) => {
      const next = {
        ...current,
        ...patch,
      };

      if (
        patch.crop &&
        patch.crop !== current.crop
      ) {
        next.variety =
          CROPS[
            patch.crop
          ]!.varieties[0]!;
      }

      return next;
    });
  };


  const applyFilters =
    async () => {
      if (updating) return;

      setUpdating(true);

      setApplied(draft);

      const data =
        await fetchMarketIntelligence(
          draft
        );

      setUpdating(false);

      if (data) {
        setToast(
          `Live prices updated for ${
            CROPS[draft.crop]!.label
          } — ${draft.district}, ${draft.state}.`
        );
      }
    };


  const refresh =
    async () => {
      if (refreshing) return;

      setRefreshing(true);

      const data =
        await fetchMarketIntelligence(
          applied
        );

      setRefreshing(false);

      if (data) {
        setToast(
          "Live market prices and AI prediction refreshed."
        );
      }
    };


  const viewDetails = (
    row: MandiRow
  ) => {
    setToast(
      `${row.market} mandi — detailed breakdown coming soon.`
    );
  };


  /*
   * Initial live data load.
   */
  useEffect(() => {
    fetchMarketIntelligence(
      applied
    );

    // Initial load only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  /*
   * ----------------------------------------------------
   * DATA FOR EXISTING UI COMPONENTS
   * ----------------------------------------------------
   */

  const stats: PriceStats =
    marketData
      ? createStats(marketData)
      : {
          min: 0,
          max: 0,
          avg: 0,
          weeklyChange: 0,
        };


  const history: HistoryRow[] =
    marketData
      ? createHistoryRows(
          marketData
        )
      : [];


  const series =
    createSeries(
      history,
      range
    );


  const mandis: MandiRow[] =
    marketData
      ? createMandiRows(
          marketData
        )
      : [];


  const prediction =
    aiPrediction ??
    (marketData
      ? createAIPrediction(
          marketData
        )
      : {
          price: 0,

          days: "next day",

          increasePct:
            "0%",

          note:
            "Waiting for live XGBoost prediction.",

          recommendation:
            "Live market intelligence will appear when the backend responds.",
        });


  return (
    <DashboardLayout>

      <div className="mx-auto flex w-full max-w-[1240px] flex-col gap-5 sm:gap-6">

        <MarketPriceHeader
          lastUpdated={
            lastUpdated
          }
          refreshing={
            refreshing
          }
          onRefresh={
            refresh
          }
        />


        <MarketPriceFilters
          values={
            draft
          }
          varieties={
            CROPS[
              draft.crop
            ]!.varieties
          }
          updating={
            updating
          }
          onChange={
            patchDraft
          }
          onApply={
            applyFilters
          }
        />


        <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_370px]">

          <div className="flex min-w-0 flex-col gap-5">

            <MarketIntelligence
              cropLabel={
                marketData?.commodity ??
                crop.label
              }
              stats={
                stats
              }
              mandis={
                mandis
              }
              prediction={
                prediction
              }
            />


            <PriceOverviewCard
              crop={
                crop
              }
              variety={
                applied.variety
              }
              stats={
                stats
              }
              series={
                series
              }
              range={
                range
              }
              onRangeChange={
                setRange
              }
            />


            <NearbyMandis
              mandis={
                mandis
              }
              onViewDetails={
                viewDetails
              }
            />


            <HistoricalTable
              rows={
                history
              }
              range={
                historyRange
              }
              onRangeChange={
                setHistoryRange
              }
              onViewFullChart={() =>
                setToast(
                  "Full historical chart — coming soon."
                )
              }
            />

          </div>


          <div className="flex min-w-0 flex-col gap-5">

            {marketData === null &&
            !aiError ? (

              <section className="rounded-2xl border border-[#BFE3C5] bg-[#F0FAF1] p-5 shadow-[0_10px_30px_-18px_rgba(46,125,50,0.25)] sm:p-6">

                <div className="flex items-center gap-3">

                  <span className="grid h-[42px] w-[42px] place-items-center rounded-2xl bg-[#2E7D32] text-white">

                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />

                  </span>


                  <div>

                    <h2 className="font-display text-[16.5px] font-semibold text-[#111111]">
                      AI Price Prediction
                    </h2>

                    <p className="mt-1 text-[11px] text-[#666666]">
                      XGBoost is analysing recent market prices...
                    </p>

                  </div>

                </div>

              </section>

            ) : (

              <AIPredictionCard
                cropLabel={
                  marketData?.commodity ??
                  crop.label
                }
                prediction={
                  prediction
                }
              />

            )}


            {aiError && (
              <p
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-[12px] leading-relaxed text-red-700"
              >
                {aiError}
              </p>
            )}


            <SetPriceAlert
              onAlert={(t) =>
                setToast(
                  `Alert armed at ₹${Number(
                    t
                  ).toFixed(
                    2
                  )}/kg.`
                )
              }
            />


            <CompareMarkets
              rows={
                marketData?.market_comparison ??
                []
              }
            />


            <MarketInsights
              cropLabel={
                marketData?.commodity ??
                crop.label
              }
              weeklyChange={
                stats.weeklyChange
              }
            />

          </div>

        </div>

      </div>


      {toast && (
        <p
          role="status"
          className={cn(
            "animate-pop-in fixed bottom-6 left-1/2 z-[90] max-w-[92vw] -translate-x-1/2 rounded-full",
            "bg-[#155B32] px-5 py-3 text-center text-[13px] font-medium text-white shadow-[0_16px_40px_-12px_rgba(0,0,0,0.4)]"
          )}
        >
          {toast}
        </p>
      )}

    </DashboardLayout>
  );
}