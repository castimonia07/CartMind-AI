import React from 'react';
import { Check, Plus } from 'lucide-react';

const RecommendationCard = ({ 
  product = {}, 
  tag, 
  matchScore = 90, 
  explanation = "Best match for your requirements.",
  onAdd,
  onCompare 
}) => {
  // Safe fallbacks for title, brand, and price
  const title = product?.title || product?.name || 'Recommended Product';
  const brand = product?.brand || 'Top Pick';
  const price = product?.price ? Number(product.price).toLocaleString() : 'N/A';
  const attributes = product?.attributes || product?.specs || {};

  return (
    <div className="rounded-2xl p-5 bg-zinc-900 border border-zinc-800 flex flex-col relative overflow-hidden group hover:border-zinc-700 transition-colors">
      {/* Glow effect */}
      <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-indigo-500/20 blur-2xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
      
      {tag && (
        <div className="inline-block self-start mb-2 bg-indigo-500/20 text-indigo-400 text-xs font-bold px-3 py-1 rounded-md border border-indigo-500/30">
          {tag}
        </div>
      )}

      <div className="mt-1 mb-2 flex justify-between items-start gap-2">
        <div>
          <p className="text-zinc-500 text-xs uppercase tracking-wider mb-1">{brand}</p>
          <h3 className="text-base font-semibold text-zinc-100 leading-tight">{title}</h3>
        </div>
        <div className="text-right shrink-0">
          <div className="text-lg font-bold text-white">₹{price}</div>
          <div className="text-green-400 font-medium text-xs flex items-center justify-end gap-1 mt-1">
            <Check size={12} /> {matchScore}% Match
          </div>
        </div>
      </div>

      <div className="flex-1 my-3">
        <ul className="space-y-1.5 text-xs text-zinc-400">
          {Object.entries(attributes).slice(0, 4).map(([key, value]) => (
            <li key={key} className="flex items-center gap-2">
              <Check size={12} className="text-indigo-400 shrink-0" />
              <span className="capitalize">{String(key).replace('_', ' ')}: {String(value)}</span>
            </li>
          ))}
        </ul>
      </div>

      {explanation && (
        <div className="bg-zinc-800/60 rounded-lg p-2.5 text-xs text-zinc-300 mb-4 border border-zinc-700/40">
          <span className="font-semibold text-indigo-300 mb-0.5 block">Why this?</span>
          {explanation}
        </div>
      )}

      <div className="flex gap-2 mt-auto">
        <button 
          type="button"
          onClick={onAdd}
          className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-xl text-xs font-medium transition-colors flex items-center justify-center gap-1.5"
        >
          <Plus size={14} /> Add to Basket
        </button>
        <button 
          type="button"
          onClick={onCompare}
          className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white py-2 rounded-xl text-xs font-medium transition-colors border border-zinc-700"
        >
          Compare
        </button>
      </div>
    </div>
  );
};

export default RecommendationCard;