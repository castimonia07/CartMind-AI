import React from 'react';
import { ShoppingCart, Lightbulb, TrendingDown } from 'lucide-react';
import { useStore } from '../store/useStore';

const SmartBasket = (props) => {
  const store = useStore();

  // Props se le ya direct store se fallback uthaye
  const items = props.items || store.basket || [];
  const budget = props.budget ?? store.budget ?? 10000;
  
  // Calculate total if not provided
  const calculatedTotal = items.reduce((acc, item) => {
    const p = item.price || item.product?.price || 0;
    const q = item.quantity || 1;
    return acc + (p * q);
  }, 0);

  const total = props.total ?? calculatedTotal ?? 0;
  const remaining = budget - total;

  return (
    <div className="flex flex-col h-full">
      <div className="rounded-2xl p-6 mb-4 flex-1 bg-zinc-900 border border-zinc-800">
        <h2 className="text-xl font-medium mb-4 flex items-center gap-2 text-zinc-100">
          <ShoppingCart size={20} className="text-indigo-400" />
          Smart Basket
        </h2>

        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <ShoppingCart size={32} className="text-zinc-700 mb-4" />
            <p className="text-zinc-400">Your smart basket is empty.</p>
            <p className="text-zinc-600 text-sm mt-1">Tell CartMind what you're planning to buy.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((item, idx) => {
              const name = item.product?.title || item.name || item.raw_query || 'Item';
              const price = item.price || item.product?.price;
              const qty = item.quantity || 1;

              return (
                <div key={item.id || idx} className="flex justify-between items-center py-2 border-b border-zinc-800/50 last:border-0">
                  <div>
                    <div className="font-medium text-zinc-200">{name}</div>
                    <div className="text-sm text-zinc-500">Qty: {qty} {item.unit || ''}</div>
                  </div>
                  <div className="font-medium text-zinc-300">
                    {price ? `₹${(price * qty).toLocaleString()}` : 'Added'}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="rounded-2xl p-6 bg-zinc-900 border border-zinc-800">
        <div className="flex justify-between items-center mb-2 text-sm text-zinc-400">
          <span>Estimated Total</span>
          <span className="text-white text-lg font-bold">₹{total.toLocaleString()}</span>
        </div>
        <div className="flex justify-between items-center text-sm mb-4">
          <span className="text-zinc-500">Budget: ₹{budget.toLocaleString()}</span>
          <span className={remaining >= 0 ? "text-green-400" : "text-red-400"}>
            {remaining >= 0 ? `Remaining: ₹${remaining.toLocaleString()}` : `Over by: ₹${Math.abs(remaining).toLocaleString()}`}
          </span>
        </div>

        {items.length > 0 && remaining < 0 && (
          <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-4 text-sm mt-4">
            <div className="flex gap-2 text-indigo-400 font-medium mb-1">
              <Lightbulb size={16} /> AI Insight
            </div>
            <p className="text-zinc-300">
              You are over budget. Want me to optimize the basket and find cheaper alternatives?
            </p>
            <button className="mt-3 w-full bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 py-2 rounded-lg transition-colors flex items-center justify-center gap-2">
              <TrendingDown size={16} /> Optimize Basket
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SmartBasket;