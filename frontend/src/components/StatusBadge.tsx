import React from "react";

interface StatusBadgeProps {
  status: "ACTIVE" | "UNDER_REVISION" | "WITHDRAWN" | "MANDATORY_QCO" | "VOLUNTARY";
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const styles: Record<string, string> = {
    ACTIVE: "bg-emerald-100 text-emerald-800 border-emerald-300",
    UNDER_REVISION: "bg-amber-100 text-amber-800 border-amber-300",
    WITHDRAWN: "bg-rose-100 text-rose-800 border-rose-300",
    MANDATORY_QCO: "bg-red-100 text-red-800 border-red-300 font-bold",
    VOLUNTARY: "bg-slate-100 text-slate-800 border-slate-300",
  };

  const labels: Record<string, string> = {
    ACTIVE: "Active Standard",
    UNDER_REVISION: "Under Revision",
    WITHDRAWN: "Withdrawn",
    MANDATORY_QCO: "Mandatory QCO",
    VOLUNTARY: "Voluntary Standard",
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${
        styles[status] || "bg-slate-100 text-slate-800 border-slate-300"
      }`}
    >
      {labels[status] || status}
    </span>
  );
}
