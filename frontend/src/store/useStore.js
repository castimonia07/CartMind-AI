import { create } from 'zustand';

export const useStore = create((set) => ({
  basket: [],
  budget: 80000,
  recommendations: [],
  processingState: 'idle', // idle, listening, processing, completed, error
  conversation: [],
  
  setBasket: (basket) => set({ basket }),
  setBudget: (budget) => set({ budget }),
  setRecommendations: (recommendations) => set({ recommendations }),
  setProcessingState: (state) => set({ processingState: state }),
  addMessage: (msg) => set((state) => ({ conversation: [...state.conversation, msg] })),
  
  // Actions to interact with API
  addItem: (item) => set((state) => ({ basket: [...state.basket, item] })),
  removeItem: (id) => set((state) => ({ basket: state.basket.filter(i => i.id !== id) })),
}));
