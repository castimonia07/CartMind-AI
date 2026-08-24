import React, { useEffect } from 'react';
import axios from 'axios';
import { Mic, ShoppingCart, Activity, Search, Settings, User, Sparkles, TrendingUp, Zap, Trash2, Plus, ArrowRight } from 'lucide-react';
import VoiceBar from '../components/VoiceBar';
import SmartBasket from '../components/SmartBasket';
import ConversationPanel from '../components/ConversationPanel';
import RecommendationCard from '../components/RecommendationCard';
import { useStore } from '../store/useStore';

const API = 'http://localhost:8000';

const Sidebar = ({ activePage, setActivePage }) => {
  const navItems = [
    { icon: <Activity size={20} />, label: 'Home', key: 'home' },
    { icon: <ShoppingCart size={20} />, label: 'Smart Basket', key: 'basket' },
    { icon: <Search size={20} />, label: 'Discover', key: 'discover' },
    { icon: <TrendingUp size={20} />, label: 'Recommendations', key: 'recs' },
    { icon: <User size={20} />, label: 'Profile', key: 'profile' },
    { icon: <Settings size={20} />, label: 'Settings', key: 'settings' },
  ];

  return (
    <div className="w-64 border-r border-zinc-800 bg-zinc-950 p-6 flex flex-col shrink-0">
      <div className="flex items-center gap-3 mb-10">
        <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
          <Sparkles size={18} className="text-white" />
        </div>
        <div>
          <span className="text-base font-bold tracking-tight text-white">CartMind AI</span>
          <p className="text-xs text-zinc-500">Shopping Agent</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.key}
            onClick={() => setActivePage(item.key)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${
              activePage === item.key
                ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-600/20'
                : 'text-zinc-500 hover:text-zinc-200 hover:bg-zinc-900'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="mt-auto pt-6 border-t border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white">D</div>
          <div>
            <p className="text-sm font-medium text-zinc-200">Demo User</p>
            <p className="text-xs text-zinc-500">demo@cartmind.ai</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProcessingBadge = ({ state }) => {
  if (state === 'idle') return null;
  const config = {
    listening: { label: 'Listening...', color: 'bg-red-500', pulse: true },
    processing: { label: 'CartMind is thinking...', color: 'bg-blue-500', pulse: true },
    completed: { label: 'Done!', color: 'bg-green-500', pulse: false },
    error: { label: 'Something went wrong', color: 'bg-red-600', pulse: false },
  };
  const c = config[state] || config.processing;
  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900 border border-zinc-800 text-sm text-zinc-300 mb-4 w-fit">
      <span className={`w-2 h-2 rounded-full ${c.color} ${c.pulse ? 'animate-pulse' : ''}`}></span>
      {c.label}
    </div>
  );
};

const EmptyRecommendations = () => (
  <div className="rounded-2xl border border-dashed border-zinc-800 bg-zinc-950/50 flex flex-col items-center justify-center text-center min-h-[240px] p-8">
    <div className="w-14 h-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-3">
      <Zap size={24} className="text-zinc-600" />
    </div>
    <p className="text-zinc-300 font-medium text-base mb-1">No recommendations yet</p>
    <p className="text-zinc-600 text-xs max-w-xs">
      Try saying: <span className="text-zinc-400 italic">"I need a laptop under 80000"</span> or <span className="text-zinc-400 italic">"Find headphones under 5000"</span>
    </p>
  </div>
);

export default function Dashboard() {
  const { basket, budget, setBasket, recommendations, processingState, addToBasket } = useStore();
  const [activePage, setActivePage] = React.useState('home');

  const total = (basket || []).reduce((acc, item) => {
    const price = item.price || item.product?.price || 0;
    const qty = item.quantity || 1;
    return acc + price * qty;
  }, 0);

  const fetchBasket = async () => {
    try {
      const res = await axios.get(`${API}/api/shopping/list`);
      if (res.data?.items) setBasket(res.data.items);
    } catch (err) {
      console.error('Failed to fetch basket:', err.message);
    }
  };

  useEffect(() => {
    fetchBasket();
  }, []);

  return (
    <div className="flex h-screen w-full bg-zinc-950 text-zinc-100 overflow-hidden">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-8">
          
          {/* Top Header */}
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">
                Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}.
              </h1>
              <p className="text-zinc-500 text-sm">What are you shopping for today?</p>
            </div>
            {activePage !== 'home' && (
              <button 
                onClick={() => setActivePage('home')}
                className="text-xs bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3 py-1.5 rounded-lg text-zinc-300 transition-colors"
              >
                ← Back to Home
              </button>
            )}
          </div>

          <ProcessingBadge state={processingState} />

          {/* PAGE SWITCHER */}
          {activePage === 'home' && (
            <>
              <VoiceBar />
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mt-8">
                {/* Left: Chat + Recommendations */}
                <div className="xl:col-span-2 space-y-6">
                  <ConversationPanel />

                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <Sparkles size={18} className="text-indigo-400" />
                      <h2 className="text-lg font-semibold text-white">AI Recommendations</h2>
                      {recommendations?.length > 0 && (
                        <span className="ml-auto text-xs text-zinc-500 bg-zinc-900 px-2.5 py-1 rounded-full border border-zinc-800">
                          {recommendations.length} result{recommendations.length !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>

                    {recommendations?.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {recommendations.map((rec, i) => (
                          <RecommendationCard
                            key={rec.id || i}
                            product={rec.product || rec}
                            tag={rec.tag || (i === 0 ? "Top Pick" : null)}
                            matchScore={rec.match_score || rec.matchScore || 92}
                            explanation={rec.explanation || rec.reason || "Recommended based on your query."}
                            onAdd={() => addToBasket && addToBasket(rec.product || rec)}
                          />
                        ))}
                      </div>
                    ) : (
                      <EmptyRecommendations />
                    )}
                  </div>
                </div>

                {/* Right: Smart Basket */}
                <div>
                  <SmartBasket items={basket} budget={budget} total={total} />
                </div>
              </div>
            </>
          )}

          {activePage === 'basket' && (
            <div className="max-w-3xl">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <ShoppingCart className="text-indigo-400" /> My Shopping Basket
              </h2>
              <SmartBasket items={basket} budget={budget} total={total} />
            </div>
          )}

          {activePage === 'discover' && (
            <div>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Search className="text-indigo-400" /> Discover Categories & Products
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {['Laptops & Tech', 'Groceries & Staples', 'Audio & Accessories', 'Fitness & Nutrition'].map((cat, i) => (
                  <div key={i} className="p-5 bg-zinc-900 border border-zinc-800 rounded-2xl hover:border-zinc-700 transition-all cursor-pointer">
                    <h3 className="font-semibold text-zinc-200">{cat}</h3>
                    <p className="text-xs text-zinc-500 mt-1">Explore top rated products and AI insights</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activePage === 'recs' && (
            <div>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="text-indigo-400" /> Personalized Recommendations
              </h2>
              {recommendations?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations.map((rec, i) => (
                    <RecommendationCard
                      key={rec.id || i}
                      product={rec.product || rec}
                      tag={rec.tag || "Best Match"}
                      matchScore={rec.match_score || 95}
                      explanation={rec.explanation || "Selected based on requirements."}
                      onAdd={() => addToBasket && addToBasket(rec.product || rec)}
                    />
                  ))}
                </div>
              ) : (
                <EmptyRecommendations />
              )}
            </div>
          )}

          {activePage === 'profile' && (
            <div className="max-w-xl bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <User className="text-indigo-400" /> User Profile
              </h2>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between py-2 border-b border-zinc-800">
                  <span className="text-zinc-500">Name</span>
                  <span className="text-zinc-200 font-medium">Demo User</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-800">
                  <span className="text-zinc-500">Email</span>
                  <span className="text-zinc-200 font-medium">demo@cartmind.ai</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-zinc-500">Monthly Budget</span>
                  <span className="text-indigo-400 font-bold">₹{budget?.toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          {activePage === 'settings' && (
            <div className="max-w-xl bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Settings className="text-indigo-400" /> Preferences & Settings
              </h2>
              <div className="space-y-4 text-sm text-zinc-300">
                <label className="flex items-center justify-between p-3 bg-zinc-950 rounded-xl border border-zinc-800">
                  <span>Voice Auto-Submit</span>
                  <input type="checkbox" defaultChecked className="accent-indigo-600 w-4 h-4" />
                </label>
                <label className="flex items-center justify-between p-3 bg-zinc-950 rounded-xl border border-zinc-800">
                  <span>Auto-optimize Budget</span>
                  <input type="checkbox" defaultChecked className="accent-indigo-600 w-4 h-4" />
                </label>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}