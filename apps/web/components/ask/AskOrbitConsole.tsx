"use client";

import React, { useState } from "react";
import { Terminal, Send, Sparkles, Copy, Check, Eye, Database, BarChart2 } from "lucide-react";
import { postAskOrbit } from "@/lib/api";
import { useOrbitStore } from "@/lib/store";

const PRESET_QUERIES = [
  "why did revenue data go stale at 3am?",
  "Show logistics carrier SLA performance",
  "Check pipeline data quality distribution"
];

export function AskOrbitConsole() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const { setHighlightedNodes } = useOrbitStore();

  const handleAsk = async (text: string) => {
    if (!text.trim() || loading) return;
    setLoading(true);
    try {
      const res = await postAskOrbit(text);
      setResponse(res);
      if (res.highlighted_lineage_nodes?.length > 0) {
        setHighlightedNodes(res.highlighted_lineage_nodes);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const copySQL = () => {
    if (!response?.generated_sql) return;
    navigator.clipboard.writeText(response.generated_sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const jumpToLineage = () => {
    const el = document.getElementById("galaxy");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section id="ask" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-gold/30 bg-surface/60 text-gold text-xs font-mono uppercase tracking-widest mb-4">
          <Terminal className="w-3.5 h-3.5" />
          Natural Language Ops Assistant
        </div>
        <h2 className="text-3xl sm:text-5xl font-serif text-white">
          Ask ORBIT
        </h2>
        <p className="text-neutral-400 text-sm sm:text-base mt-3 leading-relaxed">
          Ask complex operational questions in plain English. ORBIT synthesizes an analytical postmortem, executes grounded DuckDB SQL, and spotlights the affected 3D lineage nodes.
        </p>
      </div>

      {/* Console Input Container */}
      <div className="max-w-4xl mx-auto">
        <div className="glass-panel p-3 rounded-2xl border-hairline shadow-2xl flex flex-col gap-3">
          {/* Preset Suggestion Chips */}
          <div className="flex flex-wrap items-center gap-2 px-2 pt-1">
            <span className="text-[11px] font-mono text-neutral-500 uppercase">Suggested:</span>
            {PRESET_QUERIES.map((q) => (
              <button
                key={q}
                onClick={() => {
                  setQuery(q);
                  handleAsk(q);
                }}
                className="text-xs font-mono px-3 py-1 rounded-full bg-surface border border-white/10 text-neutral-300 hover:text-gold hover:border-gold/40 transition-colors"
              >
                "{q}"
              </button>
            ))}
          </div>

          {/* Prompt Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAsk(query);
            }}
            className="flex items-center gap-3 bg-[#050608] px-4 py-3 rounded-xl border border-white/5 focus-within:border-gold/50 transition-colors"
          >
            <Sparkles className="w-5 h-5 text-gold flex-shrink-0" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. why did revenue data go stale at 3am?"
              className="w-full bg-transparent text-white font-mono text-sm focus:outline-none placeholder:text-neutral-600"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2 rounded-lg bg-gold hover:bg-gold-light text-background font-mono text-xs uppercase font-semibold tracking-wider flex items-center gap-2 disabled:opacity-40 transition-all hover:shadow-gold-glow"
            >
              <span>{loading ? "Analyzing..." : "Ask"}</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>

        {/* Structured Response Box */}
        {response && (
          <div className="mt-8 glass-panel p-6 sm:p-8 rounded-2xl border-hairline space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Top row: Answer + Lineage Spotlight Button */}
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div>
                <div className="text-xs font-mono uppercase tracking-wider text-gold flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-gold" />
                  <span>Synthesized Operational Answer</span>
                </div>
                <p className="text-white text-base leading-relaxed font-sans">
                  {response.natural_language_answer}
                </p>
              </div>

              {response.highlighted_lineage_nodes?.length > 0 && (
                <button
                  onClick={jumpToLineage}
                  className="flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-xl bg-ice/15 hover:bg-ice/25 border border-ice/40 text-ice text-xs font-mono uppercase tracking-wider transition-all hover:shadow-ice-glow"
                >
                  <Eye className="w-4 h-4" />
                  <span>Spotlight on 3D Galaxy ({response.highlighted_lineage_nodes.length} Nodes)</span>
                </button>
              )}
            </div>

            {/* Generated Executable SQL Code Block */}
            {response.generated_sql && (
              <div>
                <div className="flex items-center justify-between text-xs font-mono text-neutral-400 mb-2">
                  <div className="flex items-center gap-1.5">
                    <Database className="w-3.5 h-3.5 text-ice" />
                    <span>Grounded DuckDB Analytical SQL</span>
                  </div>
                  <button
                    onClick={copySQL}
                    className="flex items-center gap-1 text-neutral-400 hover:text-white transition-colors"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? "Copied" : "Copy SQL"}</span>
                  </button>
                </div>

                <pre className="bg-[#050608] p-4 rounded-xl border border-white/5 font-mono text-xs text-neutral-300 overflow-x-auto leading-relaxed">
                  <code>{response.generated_sql}</code>
                </pre>
              </div>
            )}

            {/* Live SQL Results Table */}
            {response.sql_result && response.sql_result.length > 0 && (
              <div>
                <div className="text-xs font-mono uppercase text-neutral-400 mb-3 flex items-center gap-1.5">
                  <BarChart2 className="w-3.5 h-3.5 text-gold" />
                  <span>Live Execution Records ({response.sql_result.length} Rows)</span>
                </div>
                <div className="overflow-x-auto rounded-xl border border-white/5">
                  <table className="w-full text-left font-mono text-xs">
                    <thead className="bg-surface/80 border-b border-white/5 text-neutral-400 uppercase text-[10px]">
                      <tr>
                        {Object.keys(response.sql_result[0]).map((col) => (
                          <th key={col} className="p-3">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 bg-[#050608]">
                      {response.sql_result.map((row: any, i: number) => (
                        <tr key={i} className="hover:bg-white/[0.02]">
                          {Object.values(row).map((val: any, j: number) => (
                            <td key={j} className="p-3 text-neutral-300">
                              {typeof val === "number" ? val.toLocaleString() : String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
