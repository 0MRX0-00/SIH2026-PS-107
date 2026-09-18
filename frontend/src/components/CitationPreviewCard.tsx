import React from "react";
import { BookMarked, ExternalLink, CheckCircle2 } from "lucide-react";
import { Citation } from "@/types";

interface CitationPreviewCardProps {
  citation: Citation;
}

export function CitationPreviewCard({ citation }: CitationPreviewCardProps) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 hover:border-blue-300 transition-all text-xs space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <BookMarked className="w-4 h-4 text-bis-blue" />
          <span className="font-bold text-slate-800">{citation.standard_number}</span>
          {citation.clause_ref && (
            <span className="bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded text-[10px] font-semibold">
              {citation.clause_ref}
            </span>
          )}
        </div>
        {citation.confidence_score && (
          <div className="flex items-center space-x-1 text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 text-[10px]">
            <CheckCircle2 className="w-3 h-3" />
            <span>{(citation.confidence_score * 100).toFixed(0)}% Match</span>
          </div>
        )}
      </div>

      {citation.snippet_text && (
        <blockquote className="text-slate-600 italic border-l-2 border-slate-300 pl-2 text-[11px] leading-relaxed">
          &quot;{citation.snippet_text}&quot;
        </blockquote>
      )}

      <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-200">
        <span>Page: {citation.page_number ?? "N/A"}</span>
        {citation.source_url && (
          <a
            href={citation.source_url}
            target="_blank"
            rel="noreferrer"
            className="text-bis-blue hover:underline flex items-center space-x-1"
          >
            <span>Official Gazette</span>
            <ExternalLink className="w-2.5 h-2.5" />
          </a>
        )}
      </div>
    </div>
  );
}
