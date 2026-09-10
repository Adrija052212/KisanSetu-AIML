import { Link } from "react-router-dom";

import {
  ArrowRight,
  BrainCircuit,
  MapPin,
} from "lucide-react";

import type { MarketIntelligenceResponse } from "../../services/marketIntelligenceApi";

interface AIAdvisorCardProps {
  data: MarketIntelligenceResponse | null;
  loading: boolean;
}

export default function AIAdvisorCard({
  data,
  loading,
}: AIAdvisorCardProps) {
  const action =
    data?.recommendation?.action?.toUpperCase() || "";

  /*
   * Backend prices are returned in ₹/kg.
   * Dashboard displays prices in ₹/quintal.
   *
   * 1 quintal = 100 kg
   */

  const predictedPricePerKg =
    data?.forecast?.predicted_price;

  const currentPricePerKg =
    data?.current_price?.modal;

  const predictedPrice =
    predictedPricePerKg !== undefined
      ? predictedPricePerKg * 100
      : undefined;

  const currentPrice =
    currentPricePerKg !== undefined
      ? currentPricePerKg * 100
      : undefined;

  const percentageChange =
    currentPricePerKg !== undefined &&
    currentPricePerKg > 0 &&
    predictedPricePerKg !== undefined
      ? ((predictedPricePerKg - currentPricePerKg) /
          currentPricePerKg) *
        100
      : null;

  // --------------------------------------------------
  // Recommendation
  // --------------------------------------------------

  let recommendation = "Recommendation: Monitor";

  if (action === "WAIT") {
    recommendation = "Recommendation: Wait";
  } else if (action === "SELL") {
    recommendation = "Recommendation: Sell";
  } else if (action === "BUY") {
    recommendation = "Recommendation: Buy";
  }

  // --------------------------------------------------
  // Recommendation reason
  // --------------------------------------------------

  const recommendationReason =
    data?.recommendation?.reason ||
    "Market intelligence is currently unavailable.";

  // --------------------------------------------------
  // Formatted values
  // --------------------------------------------------

  const formattedPredictedPrice =
    predictedPrice !== undefined
      ? `₹${predictedPrice.toLocaleString("en-IN", {
          maximumFractionDigits: 2,
        })} /quintal`
      : "—";

  const formattedMarketPrice =
    currentPrice !== undefined
      ? `₹${currentPrice.toLocaleString("en-IN", {
          maximumFractionDigits: 2,
        })} /quintal`
      : "—";

  const formattedChange =
    percentageChange !== null
      ? `${percentageChange > 0 ? "+" : ""}${percentageChange.toFixed(1)}%`
      : "—";

  return (
    <section className="flex flex-col rounded-2xl border border-[#E1E5E1] bg-white p-5 shadow-[0_10px_30px_-18px_rgba(17,17,17,0.12)] sm:p-6">

      {/* Header */}

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="grid h-[42px] w-[42px] place-items-center rounded-2xl bg-[#EAF6EA] text-[#2E7D32]">
            <BrainCircuit
              className="h-[21px] w-[21px]"
              strokeWidth={2}
            />
          </span>

          <h2 className="font-display text-[16.5px] font-semibold text-[#111111]">
            AI Advisor
          </h2>
        </div>

        <span className="rounded-full border border-dashed border-[#2E7D32]/35 bg-[#EAF6EA]/70 px-3 py-1 text-[10.5px] font-semibold uppercase tracking-wide text-[#2E7D32]">
          {loading
            ? "LOADING"
            : data
              ? "LIVE ML"
              : "UNAVAILABLE"}
        </span>
      </div>

      {/* Recommendation */}

      <span className="mt-5 w-fit rounded-full bg-[#EAF6EA] px-3.5 py-1.5 text-[12.5px] font-bold text-[#2E7D32]">
        {loading
          ? "Recommendation: Loading..."
          : recommendation}
      </span>

      {/* Description */}

      <p className="mt-3 text-[12.5px] leading-relaxed text-[#666666]">
        {loading
          ? "Analyzing current market prices and the expected next-day price."
          : recommendationReason}
      </p>

      {/* Data */}

      <dl className="mt-4 flex flex-col gap-3 border-t border-[#F0F3F0] pt-4 text-[12.5px]">

        {/* Predicted price */}

        <div className="flex items-baseline justify-between gap-3">
          <dt className="text-[#777777]">
            Predicted Price
          </dt>

          <dd className="font-semibold text-[#111111]">
            {loading
              ? "—"
              : formattedPredictedPrice}
          </dd>
        </div>

        {/* Recommended market */}

        <div className="flex items-baseline justify-between gap-3">
          <dt className="text-[#777777]">
            Recommended Market
          </dt>

          <dd className="flex items-center gap-1.5 text-right font-semibold text-[#111111]">
            {!loading && data && (
              <MapPin
                className="h-3.5 w-3.5 text-[#2E7D32]"
              />
            )}

            <span>
              {loading
                ? "—"
                : data?.market || "—"}
            </span>

            {!loading && data && (
              <span className="font-medium text-[#777777]">
                · {formattedMarketPrice}
              </span>
            )}
          </dd>
        </div>

        {/* Expected price change */}

        <div className="flex items-baseline justify-between gap-3">
          <dt className="text-[#777777]">
            Expected Price Change
          </dt>

          <dd className="font-display text-[15px] font-bold text-[#2E7D32]">
            {loading
              ? "—"
              : formattedChange}
          </dd>
        </div>

      </dl>

      {/* Button */}

      <div className="mt-auto pt-5">
        <Link
          to="/dashboard/ai-advisor"
          className="group inline-flex h-[44px] w-full items-center justify-center gap-2 rounded-xl border-[1.5px] border-[#2E7D32] text-[13.5px] font-semibold text-[#2E7D32] transition-all duration-200 hover:bg-[#2E7D32] hover:text-white"
        >
          View Full Analysis

          <ArrowRight
            className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5"
            strokeWidth={2.4}
          />
        </Link>

        <p className="mt-3 text-[10.5px] text-[#999999]">
          Powered by AGMARKNET market data and the KisanSetu XGBoost model.
        </p>
      </div>

    </section>
  );
}