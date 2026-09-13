import React from 'react';
import type { DiffResult } from '../types';

interface Props {
  diff: DiffResult | null;
}

export const DiffPanel: React.FC<Props> = ({ diff }) => {
  if (!diff) {
    return (
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 text-slate-500 text-center text-sm">
        Waiting for at least 2 cards to compute state delta...
      </div>
    );
  }

  return (
    <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
      <h2 className="text-lg font-bold text-slate-100 mb-3 flex items-center justify-between">
        <span>Live State Delta (Diff)</span>
        {diff.risk_escalated && (
          <span className="text-xs bg-red-600 text-white font-bold px-2 py-0.5 rounded animate-bounce">
            RISK ESCALATED ⚠️
          </span>
        )}
      </h2>

      {diff.became_irreversible && (
        <div className="mb-3 p-2 bg-rose-950/80 border border-rose-800 text-rose-200 text-xs rounded-lg font-semibold">
          🚨 Action became IRREVERSIBLE in this step.
        </div>
      )}

      {diff.changed_fields.length > 0 && (
        <div className="mb-3 text-xs">
          <span className="text-slate-400 font-medium">Changed Fields:</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {diff.changed_fields.map((field) => (
              <span key={field} className="bg-slate-800 text-yellow-300 font-mono px-2 py-0.5 rounded">
                {field}
              </span>
            ))}
          </div>
        </div>
      )}

      {Object.keys(diff.state_delta_changed).length > 0 && (
        <div className="mt-3">
          <span className="text-xs text-slate-400 font-medium">State Key Changes:</span>
          <div className="mt-1 space-y-1 font-mono text-xs">
            {Object.entries(diff.state_delta_changed).map(([key, [oldVal, newVal]]) => (
              <div key={key} className="p-2 rounded bg-slate-950 flex justify-between items-center border border-slate-800">
                <span className="text-slate-300">{key}:</span>
                <span className="text-slate-400">
                  <span className="line-through text-red-400 mr-1">{String(oldVal)}</span>
                  →
                  <span className="text-emerald-400 font-bold ml-1">{String(newVal)}</span>
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};