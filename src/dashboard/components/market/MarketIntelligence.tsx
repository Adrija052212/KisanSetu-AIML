import { ArrowDown, ArrowUp, Boxes, IndianRupee, ShoppingCart, Truck } from "lucide-react";
import type { MandiRow, PriceStats, CropPrediction } from "../../data/marketPrices";

function DemandBadge({ value }: { value: MandiRow["demand"] }) {
  const cls = value === "High" ? "bg-[#EAF6EA] text-[#2E7D32]" : value === "Low" ? "bg-[#FFF2F2] text-[#B42318]" : "bg-[#FFF8E7] text-[#9A6700]";
  return <span className={`rounded-full px-2.5 py-1 text-[10.5px] font-bold ${cls}`}>{value ?? "Medium"} demand</span>;
}

export default function MarketIntelligence({
  cropLabel,
  stats,
  mandis,
  prediction,
}: {
  cropLabel: string;
  stats: PriceStats;
  mandis: MandiRow[];
  prediction: CropPrediction;
}) {
  const best = [...mandis].sort((a, b) => (b.avg - (b.transportCost ?? 0) / 1000) - (a.avg - (a.transportCost ?? 0) / 1000))[0];
  const totalArrivals = mandis.reduce((sum, m) => sum + (m.arrivals ?? 0), 0);
  const highDemand = mandis.filter((m) => m.demand === "High").length;
  const priceUp = stats.weeklyChange >= 0;
  const bestNet = best ? best.avg - (best.transportCost ?? 0) / 1000 : stats.avg;

  return (
    <section className="rounded-2xl border border-[#E1E5E1] bg-white p-5 shadow-[0_10px_30px_-18px_rgba(17,17,17,0.12)] sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#2E7D32]">Market intelligence</p>
          <h2 className="mt-1 font-display text-[19px] font-bold text-[#111111]">{cropLabel} — what should I do?</h2>
          <p className="mt-1 text-[12px] text-[#777777]">Price, arrivals, buyer demand and estimated net realization.</p>
        </div>
        <div className="rounded-xl bg-[#F0FAF1] px-3.5 py-2.5 text-right">
          <p className="text-[10px] font-semibold text-[#5B7A63]">AI sale window</p>
          <p className="mt-0.5 font-display text-[14px] font-bold text-[#155B32]">{prediction.days}</p>
          <p className="text-[10px] text-[#5B7A63]">Expected +{prediction.increasePct}</p>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div className="rounded-xl border border-[#E1E5E1] bg-[#FAFBFA] p-3.5">
          <div className="flex items-center gap-2 text-[#777777]"><IndianRupee className="h-4 w-4" /><span className="text-[10.5px] font-semibold">Average price</span></div>
          <p className="mt-2 font-display text-[20px] font-bold text-[#111111]">₹{stats.avg.toFixed(2)}<span className="ml-1 text-[10px] font-medium text-[#888888]">/kg</span></p>
          <p className={`mt-1 flex items-center gap-1 text-[10.5px] font-semibold ${priceUp ? "text-[#2E7D32]" : "text-[#B42318]"}`}>{priceUp ? <ArrowUp className="h-3.5 w-3.5" /> : <ArrowDown className="h-3.5 w-3.5" />}{Math.abs(stats.weeklyChange)}% this week</p>
        </div>
        <div className="rounded-xl border border-[#E1E5E1] bg-[#FAFBFA] p-3.5">
          <div className="flex items-center gap-2 text-[#777777]"><Boxes className="h-4 w-4" /><span className="text-[10.5px] font-semibold">Today's arrivals</span></div>
          <p className="mt-2 font-display text-[20px] font-bold text-[#111111]">{totalArrivals.toLocaleString()}<span className="ml-1 text-[10px] font-medium text-[#888888]">q</span></p>
          <p className="mt-1 text-[10.5px] text-[#777777]">Across shown markets</p>
        </div>
        <div className="rounded-xl border border-[#E1E5E1] bg-[#FAFBFA] p-3.5">
          <div className="flex items-center gap-2 text-[#777777]"><ShoppingCart className="h-4 w-4" /><span className="text-[10.5px] font-semibold">Buyer demand</span></div>
          <p className="mt-2 font-display text-[20px] font-bold text-[#111111]">{highDemand}/{mandis.length}</p>
          <p className="mt-1 text-[10.5px] font-semibold text-[#2E7D32]">markets show high demand</p>
        </div>
        <div className="rounded-xl border border-[#BFE3C5] bg-[#F0FAF1] p-3.5">
          <div className="flex items-center gap-2 text-[#5B7A63]"><Truck className="h-4 w-4" /><span className="text-[10.5px] font-semibold">Best net realization</span></div>
          <p className="mt-2 font-display text-[20px] font-bold text-[#155B32]">₹{bestNet.toFixed(2)}<span className="ml-1 text-[10px] font-medium">/kg*</span></p>
          <p className="mt-1 text-[10.5px] font-semibold text-[#2E7D32]">{best?.market ?? "Nearby market"}</p>
        </div>
      </div>

      <div className="mt-5 overflow-x-auto rounded-xl border border-[#E1E5E1]">
        <table className="w-full min-w-[620px] text-left">
          <thead className="bg-[#F7F9F7] text-[10.5px] font-bold uppercase tracking-[0.05em] text-[#7A827A]">
            <tr><th className="px-3.5 py-3">Market</th><th className="px-3.5 py-3">Avg price</th><th className="px-3.5 py-3">Arrivals</th><th className="px-3.5 py-3">Demand</th><th className="px-3.5 py-3">Transport</th><th className="px-3.5 py-3">Est. net*</th></tr>
          </thead>
          <tbody className="divide-y divide-[#EEF1EE]">
            {mandis.map((m) => {
              const net = m.avg - (m.transportCost ?? 0) / 1000;
              return <tr key={m.market} className="text-[11.5px] text-[#555555]">
                <td className="px-3.5 py-3 font-semibold text-[#111111]">{m.market}</td>
                <td className="px-3.5 py-3 font-bold text-[#2E7D32]">₹{m.avg.toFixed(2)}</td>
                <td className="px-3.5 py-3">{(m.arrivals ?? 0).toLocaleString()} q</td>
                <td className="px-3.5 py-3"><DemandBadge value={m.demand} /></td>
                <td className="px-3.5 py-3">₹{(m.transportCost ?? 0).toLocaleString()}</td>
                <td className="px-3.5 py-3 font-bold text-[#155B32]">₹{net.toFixed(2)}</td>
              </tr>;
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-[10px] text-[#999999]">*Demo net realization subtracts estimated transport for 1 tonne; storage, commission and other costs are not yet included.</p>
    </section>
  );
}
