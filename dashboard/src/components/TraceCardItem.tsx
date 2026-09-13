import React from 'react';
import { RiskClass } from '../types';
import type { TraceCard } from '../types';

const RISK_CONFIG: Record<RiskClass, { label: string; badgeClass: string; borderClass: string }> = {
  [RiskClass.NONE]: { label: 'NONE', badgeClass: 'bg-gray-700 text-gray-200', borderClass: 'border-gray-700' },
  [RiskClass.LOW]: { label: 'LOW', badgeClass: 'bg-emerald-950 text-emerald-300 border border-emerald-700', borderClass: 'border-emerald-700/50' },
  [RiskClass.MEDIUM]: { label: 'MEDIUM', badgeClass: 'bg-amber-950 text-amber-300 border border-amber-700', borderClass: 'border-amber-700/50' },
  [RiskClass.HIGH]: { label: 'HIGH', badgeClass: 'bg-orange-950 text-orange-300 border border-orange-700', borderClass: 'border-orange-700/50' },
  [RiskClass.CRITICAL]: { label: 'CRITICAL', badgeClass: 'bg-rose-950 text-rose-300 border border-rose-700 animate-pulse', borderClass: 'border-rose-600' },
};

interface Props {
  card: TraceCard;
  isLatest?: boolean;
}

export const TraceCardItem: React.FC<Props> = ({ card, isLatest }) => {
  const risk = RISK_CONFIG[card.risk_class] || RISK_CONFIG[RiskClass.NONE];

  return (
    <div className={`p-4 rounded-xl bg-slate-900 border ${risk.borderClass} transition-all duration-200 shadow-md ${isLatest ? 'ring-2 ring-blue-500/50' : ''}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          <span className="font-mono text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded">#{card.seq}</span>
          <h3 className="font-semibold text-slate-100 text-base">{card.stage}</h3>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${risk.badgeClass}`}>
            {risk.label}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded font-mono ${card.reversible ? 'bg-slate-800 text-slate-300' : 'bg-red-950 text-red-300 font-bold'}`}>
            {card.reversible ? 'Reversible' : 'Irreversible'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs font-mono mb-3 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 text-slate-300">
        <div><span className="text-slate-500">Action:</span> {card.action_type}</div>
        <div><span className="text-slate-500">Hash:</span> {card.hash ? card.hash.substring(0, 10) + '...' : 'N/A'}</div>
        <div><span className="text-slate-500">In Digest:</span> {card.inputs_digest}</div>
        <div><span className="text-slate-500">Out Digest:</span> {card.outputs_digest}</div>
      </div>

      {Object.keys(card.state_delta).length > 0 && (
        <div className="mt-2 text-xs">
          <span className="text-slate-400 font-medium">State Delta:</span>
          <div className="mt-1 flex flex-wrap gap-1.5">
            {Object.entries(card.state_delta).map(([k, v]) => (
              <span key={k} className="bg-slate-800 text-slate-200 px-2 py-0.5 rounded font-mono">
                {k}: <strong className="text-blue-400">{String(v)}</strong>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};