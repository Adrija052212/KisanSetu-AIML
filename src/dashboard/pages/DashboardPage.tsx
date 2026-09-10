import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Handshake, Package, Plus, Store, Users } from "lucide-react";

import { useAuth } from "../../context/AuthContext";
import { supabase } from "../../lib/supabase";

import AIAdvisorCard from "../components/AIAdvisorCard";
import CropLotsTable from "../components/CropLotsTable";
import DashboardLayout from "../components/DashboardLayout";
import MarketPriceChart from "../components/MarketPriceChart";
import SummaryCard from "../components/SummaryCard";
import TopBuyers from "../components/TopBuyers";

import type { SummaryMetric } from "../data/farmerDashboardData";
import { GREETING } from "../data/farmerDashboardData";

import {
  getMarketIntelligence,
  type MarketIntelligenceResponse,
} from "../../services/marketIntelligenceApi";

export default function FarmerDashboardPage() {
  const { user, profile } = useAuth();

  const [farmerCrops, setFarmerCrops] = useState<any[]>([]);

  const [preferredBuyer, setPreferredBuyer] =
    useState<string>("Wholesaler");

  const [marketIntelligence, setMarketIntelligence] =
    useState<MarketIntelligenceResponse | null>(null);

  const [marketLoading, setMarketLoading] =
    useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      if (!user) return;

      try {
        // --------------------------------------------------
        // 1. Load farmer crop lots
        // --------------------------------------------------

        const {
          data: cropsData,
          error: cropsError,
        } = await supabase
          .from("farmer_crops")
          .select("*")
          .eq("farmer_id", user.id);

        if (!cropsError && cropsData) {
          setFarmerCrops(cropsData);
        }

        // --------------------------------------------------
        // 2. Load preferred buyer
        // --------------------------------------------------

        const { data: profileData } = await supabase
          .from("farmer_profiles")
          .select("preferred_buyer_type")
          .eq("id", user.id)
          .maybeSingle();

        if (profileData?.preferred_buyer_type) {
          setPreferredBuyer(
            profileData.preferred_buyer_type
          );
        }

        // --------------------------------------------------
        // 3. Load real market intelligence
        // --------------------------------------------------

        setMarketLoading(true);

        const firstCrop = cropsData?.[0];

        /*
         * The dashboard currently uses the farmer's first
         * cultivated crop for the market overview.
         *
         * Fallback values keep the dashboard working even
         * when the crop record does not contain every field.
         */

        const commodity =
          firstCrop?.commodity ||
          firstCrop?.crop ||
          firstCrop?.crop_name ||
          firstCrop?.crop_type ||
          "Tomato";

        const state =
          firstCrop?.state ||
          "Maharashtra";

        const district =
          firstCrop?.district ||
          "Ahilyanagar";

        const market =
          firstCrop?.market ||
          null;

        const variety = null;
        const grade = null;

        try {
          const intelligence =
            await getMarketIntelligence({
              state,
              district,
              market,
              commodity,
              variety,
              grade,
              days: 7,
            });

          setMarketIntelligence(intelligence);
        } catch (marketError) {
          console.error(
            "Error loading dashboard market intelligence:",
            marketError
          );

          setMarketIntelligence(null);
        }
      } catch (err) {
        console.error(
          "Error loading dashboard data:",
          err
        );
      } finally {
        setMarketLoading(false);
      }
    }

    loadDashboardData();
  }, [user]);

  // --------------------------------------------------
  // Calculate crop-lot counts
  // --------------------------------------------------

  const totalLotsCount = farmerCrops.length;

  const activeLotsCount = farmerCrops.filter(
    (c) =>
      c.status?.toLowerCase() === "live" ||
      c.list_for_sale === true
  ).length;

  const negotiationLotsCount = farmerCrops.filter(
    (c) =>
      c.status?.toLowerCase() === "negotiation" ||
      (!c.list_for_sale &&
        c.status?.toLowerCase() !== "live")
  ).length;

  // --------------------------------------------------
  // Dashboard summary cards
  // --------------------------------------------------

  const summaryMetrics: SummaryMetric[] = [
    {
      id: "total-lots",
      label: "Total Crop Lots",
      value: String(totalLotsCount),
      supporting:
        totalLotsCount === 1
          ? "1 cultivated crop"
          : `${totalLotsCount} cultivated crops`,
      trend: "neutral",
      icon: Package,
    },

    {
      id: "active-lots",
      label: "Active Crop Lots",
      value: String(activeLotsCount),
      supporting: "Listed for sale (Live)",
      trend: "up",
      icon: Store,
    },

    {
      id: "negotiation-lots",
      label: "Negotiation Lots",
      value: String(negotiationLotsCount),
      supporting: "Open for buyer offers",
      trend: "neutral",
      icon: Handshake,
    },

    {
      id: "preferred-buyer",
      label: "Preferred Buyer",
      value: preferredBuyer,
      supporting: "Target selling preference",
      trend: "neutral",
      icon: Users,
    },
  ];

  // --------------------------------------------------
  // Greeting
  // --------------------------------------------------

  const greetingTitle = profile?.full_name
    ? `Welcome back, ${profile.full_name}`
    : GREETING.title;

  return (
    <DashboardLayout>
      <div className="mx-auto flex w-full max-w-[1200px] flex-col gap-5 sm:gap-6">

        {/* Welcome */}

        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-display text-[24px] font-bold tracking-[-0.01em] text-[#111111] sm:text-[28px]">
              {greetingTitle} 👋
            </h1>

            <p className="mt-1 text-[13.5px] text-[#666666]">
              {GREETING.subtitle}
            </p>
          </div>

          <Link
            to="/dashboard/crop-lots"
            className="inline-flex h-[46px] items-center gap-2 rounded-xl bg-[#2E7D32] px-5 text-[14px] font-semibold text-white shadow-[0_12px_24px_-10px_rgba(46,125,50,0.55)] transition-all duration-200 hover:-translate-y-0.5 hover:bg-[#256628]"
          >
            <Plus
              className="h-[17px] w-[17px]"
              strokeWidth={2.5}
            />

            Add Crop Lot
          </Link>
        </div>

        {/* 4 Summary cards */}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {summaryMetrics.map((metric) => (
            <SummaryCard
              key={metric.id}
              metric={metric}
            />
          ))}
        </div>

        {/* Chart + AI advisor */}

        <div className="grid gap-5 xl:grid-cols-3">

          <div className="xl:col-span-2">
            <MarketPriceChart
              data={marketIntelligence}
              loading={marketLoading}
            />
          </div>

          <AIAdvisorCard
            data={marketIntelligence}
            loading={marketLoading}
          />

        </div>

        {/* Crop lots + Top Buyers */}

        <div className="grid gap-5 xl:grid-cols-3">

          <div className="xl:col-span-2">
            <CropLotsTable
              crops={farmerCrops}
            />
          </div>

          <TopBuyers />

        </div>

      </div>
    </DashboardLayout>
  );
}