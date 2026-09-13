import { useState, useEffect } from 'react';
import { type TraceCard, type DiffResult, type VerifyStatus } from './types';
import { TraceCardItem } from './components/TraceCardItem';

function VerifyBadge({
  status,
  onReverify,
  loading,
}: {
  status: VerifyStatus | null;
  onReverify: () => void;
  loading: boolean;
}) {
  return (
    <div className="flex items-center gap-3">
      <span className={status?.valid ? 'text-emerald-400' : 'text-rose-400'}>
        {status === null ? 'Not verified' : status.valid ? 'Verified' : 'Invalid'}
      </span>
      <button
        type="button"
        onClick={onReverify}
        disabled={loading}
        className="rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? 'Verifying...' : 'Reverify'}
      </button>
    </div>
  );
}

function DiffPanel({ diff }: { diff: DiffResult | null }) {
  if (!diff) {
    return (
      <div className="p-8 text-center text-slate-500 bg-slate-900 rounded-xl border border-slate-800">
        No diff data available.
      </div>
    );
  }

  return (
    <div className="p-4 bg-slate-900 rounded-xl border border-slate-800">
      <pre className="whitespace-pre-wrap break-words text-xs text-slate-300">
        {JSON.stringify(diff, null, 2)}
      </pre>
    </div>
  );
}

export default function App() {
  const [cards, setCards] = useState<TraceCard[]>([]);
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [verifyStatus, setVerifyStatus] = useState<VerifyStatus | null>(null);
  const [loadingVerify, setLoadingVerify] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const traceRes = await fetch('http://localhost:8000/api/trace');
      if (traceRes.ok) {
        const data: TraceCard[] = await traceRes.json();
        setCards(data);
      }

      const diffRes = await fetch('http://localhost:8000/api/diff');
      if (diffRes.ok) {
        const diffData: DiffResult = await diffRes.json();
        setDiff(diffData);
      }
    } catch (err) {
      console.error('Error connecting to backend:', err);
    }
  };

  const handleReverify = async () => {
    setLoadingVerify(true);
    try {
      const res = await fetch('http://localhost:8000/api/verify');
      const data: VerifyStatus = await res.json();
      setVerifyStatus(data);
    } catch (err) {
      setVerifyStatus({ valid: false, card_count: 0, error: 'Failed to communicate with verify server' });
    } finally {
      setLoadingVerify(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    handleReverify();
    const interval = setInterval(fetchDashboardData, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      <header className="max-w-6xl mx-auto flex items-center justify-between pb-6 mb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            SIPA TRACE Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Deterministic Audit Trail for AI Infrastructure</p>
        </div>
        <VerifyBadge status={verifyStatus} onReverify={handleReverify} loading={loadingVerify} />
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Trace Stream ({cards.length})</h2>
          {cards.length === 0 ? (
            <div className="p-8 text-center text-slate-500 bg-slate-900 rounded-xl border border-slate-800">
              No trace cards logged yet. Start running pipeline demo script.
            </div>
          ) : (
            cards.map((card, idx) => (
              <TraceCardItem key={card.seq} card={card} isLatest={idx === cards.length - 1} />
            ))
          )}
        </section>

        <section className="space-y-4">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Live Inspection</h2>
          <DiffPanel diff={diff} />
        </section>
      </main>
    </div>
  );
}