'use client';

import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

function GapMeter({ starScore, sentimentScore }) {
  if (sentimentScore == null) {
    return (
      <p className="font-data mt-3 text-[11px] text-stone-400">
        no review text sampled yet
      </p>
    );
  }
  const starPct = ((starScore - 1) / 4) * 100;
  const sentPct = ((sentimentScore - 1) / 4) * 100;
  const gap = (starScore - sentimentScore).toFixed(2);
  const isWide = Math.abs(starScore - sentimentScore) > 0.5;

  return (
    <div className="mt-3">
      <div className="relative h-1 rounded-full bg-stone-200">
        <span
          className="absolute top-1/2 h-2.5 w-2.5 -translate-y-1/2 -translate-x-1/2 rounded-full border-2 border-[#FAF8F3] bg-[#1B4B43]"
          style={{ left: `${starPct}%` }}
        />
        <span
          className="absolute top-1/2 h-2.5 w-2.5 -translate-y-1/2 -translate-x-1/2 rounded-full border-2 border-[#FAF8F3] bg-[#A8402F]"
          style={{ left: `${sentPct}%` }}
        />
      </div>
      <div className="font-data mt-1.5 flex items-center justify-between text-[11px] text-stone-500">
        <span>★ {starScore.toFixed(2)}</span>
        <span className={isWide ? 'font-medium text-[#A8402F]' : ''}>
          Δ {gap}
        </span>
        <span>text {sentimentScore.toFixed(2)}</span>
      </div>
    </div>
  );
}

function DetailModal({ detail, loading, onClose }) {
  useEffect(() => {
    const handleEscape = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#1C2321]/40 p-6"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-sm border border-stone-300 bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="font-data absolute right-4 top-4 text-stone-400 hover:text-[#1C2321]"
          aria-label="Close"
        >
          ✕
        </button>

        {loading ? (
          <p className="font-data text-xs text-stone-500">loading detail…</p>
        ) : detail ? (
          <>
            <p className="font-data text-[11px] uppercase tracking-[0.2em] text-stone-400">
              Category detail
            </p>
            <h2 className="font-display mt-1 pr-6 text-2xl">
              {detail.category.replace(/_/g, ' ')}
            </h2>
            <dl className="font-data mt-4 space-y-2 text-sm">
              <div className="flex justify-between border-b border-dotted border-stone-200 pb-2">
                <dt className="text-stone-500">star rating</dt>
                <dd>{detail.avg_review_score?.toFixed(2)} / 5</dd>
              </div>
              <div className="flex justify-between border-b border-dotted border-stone-200 pb-2">
                <dt className="text-stone-500">orders</dt>
                <dd>{detail.order_count}</dd>
              </div>
              <div className="flex justify-between border-b border-dotted border-stone-200 pb-2">
                <dt className="text-stone-500">sentiment score</dt>
                <dd>{detail.avg_sentiment_score?.toFixed(2) ?? '—'} / 5</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-stone-500">reviews sampled</dt>
                <dd>{detail.review_count ?? 0}</dd>
              </div>
            </dl>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default function Home() {
  const [categories, setCategories] = useState([]);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/insights/categories`)
      .then((res) => res.json())
      .then((data) => setCategories(data.categories));
  }, []);

  const handleSelect = async (category) => {
    setSelected(category);
    setModalOpen(true);
    setLoading(true);
    setDetail(null);
    try {
      const res = await fetch(`${API_BASE}/insights/categories/${category.category}`);
      setDetail(await res.json());
    } catch (err) {
      console.error('Error fetching category detail:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#FAF8F3] px-6 py-12 text-[#1C2321] sm:px-12">
      <div className="mx-auto max-w-5xl">
        <div className="mb-10 border-b border-stone-300 pb-6">
          <p className="font-data text-[11px] uppercase tracking-[0.2em] text-[#1B4B43]">
            AI Category Ledger
          </p>
          <h1 className="font-display mt-2 text-4xl font-medium tracking-tight">
            Smart Shop Assistant
          </h1>
          <p className="mt-2 max-w-xl text-sm text-stone-600">
            Every category, ranked by how far customer sentiment in written
            reviews diverges from the star rating they gave.
          </p>
          
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((cat, i) => (
            <button
              key={cat.category}
              onClick={() => handleSelect(cat)}
              className={`rounded-md border bg-white p-4 text-left transition-colors ${
                selected?.category === cat.category
                  ? 'border-[#1B4B43] ring-1 ring-[#1B4B43]'
                  : 'border-stone-200 hover:border-stone-300'
              }`}
            >
              <div className="font-data flex items-baseline justify-between text-[11px] text-stone-400">
                <span>{String(i + 1).padStart(2, '0')}</span>
                <span>{cat.order_count} orders</span>
              </div>
              <h3 className="font-display mt-1 truncate text-lg">
                {cat.category.replace(/_/g, ' ')}
              </h3>
              <GapMeter
                starScore={cat.avg_review_score}
                sentimentScore={cat.avg_sentiment_score}
              />
            </button>
          ))}
        </div>
      </div>

      {modalOpen && (
        <DetailModal
          detail={detail}
          loading={loading}
          onClose={() => setModalOpen(false)}
        />
      )}
    </main>
  );
}