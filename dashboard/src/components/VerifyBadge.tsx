import React from 'react';
import type { VerifyStatus } from '../types';

interface Props {
  status: VerifyStatus | null;
  onReverify: () => void;
  loading: boolean;
}

export const VerifyBadge: React.FC<Props> = ({ status, onReverify, loading }) => {
  const isValid = status?.valid ?? true;

  return (
    <div className="flex items-center space-x-3">
      <div
        className={`px-3 py-1.5 rounded-lg border font-mono text-xs flex items-center space-x-2 ${
          isValid
            ? 'bg-emerald-950/90 border-emerald-600 text-emerald-300'
            : 'bg-red-950/90 border-red-600 text-red-300 animate-pulse'
        }`}
      >
        <span className={`w-2 h-2 rounded-full ${isValid ? 'bg-emerald-400' : 'bg-red-500'}`} />
        <span>{isValid ? 'CHAIN VERIFIED (VALID)' : 'TAMPER DETECTED!'}</span>
      </div>

      <button
        onClick={onReverify}
        disabled={loading}
        className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-colors disabled:opacity-50"
      >
        {loading ? 'Verifying...' : 'Re-verify Live'}
      </button>
    </div>
  );
};