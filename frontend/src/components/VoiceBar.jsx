import React, { useState, useRef } from 'react';
import { Mic, MicOff, Send, Loader2 } from 'lucide-react';
import { useStore } from '../store/useStore';
import axios from 'axios';

const API = 'http://localhost:8000';

export default function VoiceBar() {
  const { processingState, setProcessingState, addMessage, setRecommendations, setBasket } = useStore();
  const [text, setText] = useState('');
  const recognitionRef = useRef(null);

  const handleSend = async (command) => {
    const cmd = (command || text).trim();
    if (!cmd) return;

    setText('');
    setProcessingState('processing');
    addMessage({ sender: 'USER', text: cmd });

    try {
      const res = await axios.post(`${API}/api/conversation/message`, { 
        text: cmd, 
        session_id: 'demo' 
      });
      const data = res.data;

      // Show AI response in conversation
      if (data.message) {
        addMessage({ sender: 'AI', text: data.message });
      }

      // Fast path: Update basket
      if (data.mode === 'fast') {
        const listRes = await axios.get(`${API}/api/shopping/list`);
        if (listRes.data?.items) {
          setBasket(listRes.data.items);
        }
      }

      // Decision path: Show product recommendations
      if (data.mode === 'decision' && data.recommendations) {
        setRecommendations(data.recommendations);
      } else if (data.mode === 'decision' && data.intent === 'RECOMMEND') {
        try {
          const cat = data.extracted_category || 'Laptops';
          const recRes = await axios.post(`${API}/api/recommendations`, {
            category: cat,
            hard_constraints: data.extracted_constraints || {},
            soft_preferences: data.extracted_preferences || {},
          });
          setRecommendations(recRes.data);
        } catch (e) {
          console.error('Rec fetch error:', e.message);
        }
      }

      setProcessingState('completed');
      setTimeout(() => setProcessingState('idle'), 2000);
    } catch (err) {
      console.error('API Error:', err.message);
      addMessage({ 
        sender: 'AI', 
        text: 'Sorry, I could not reach the backend. Please check backend server.' 
      });
      setProcessingState('error');
      setTimeout(() => setProcessingState('idle'), 3000);
    }
  };

  const handleVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      addMessage({ 
        sender: 'AI', 
        text: 'Voice recognition is not supported in this browser. Please use Google Chrome.' 
      });
      return;
    }

    if (processingState === 'listening') {
      recognitionRef.current?.stop();
      setProcessingState('idle');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-IN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setProcessingState('listening');

      recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        setText(transcript);
        handleSend(transcript);
      };

      recognition.onerror = (e) => {
        console.error('Speech recognition error:', e.error);
        setProcessingState('idle');
      };

      recognition.onend = () => {
        setProcessingState('idle');
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('Failed to start voice recognition:', err);
      setProcessingState('idle');
    }
  };

  const isListening = processingState === 'listening';
  const isProcessing = processingState === 'processing';

  return (
    <div className="w-full max-w-3xl mx-auto my-4">
      <div className={`flex items-center gap-3 rounded-2xl border px-4 py-3 transition-all ${
        isListening
          ? 'border-red-500 bg-red-500/10'
          : isProcessing
          ? 'border-blue-500 bg-blue-500/10'
          : 'border-zinc-800 bg-zinc-900 hover:border-zinc-700'
      }`}>
        {/* Mic Button */}
        <button
          type="button"
          onClick={handleVoice}
          disabled={isProcessing}
          className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all shrink-0 ${
            isListening
              ? 'bg-red-500 shadow-lg animate-pulse'
              : isProcessing
              ? 'bg-blue-500 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-500'
          }`}
        >
          {isProcessing ? (
            <Loader2 size={20} className="text-white animate-spin" />
          ) : isListening ? (
            <MicOff size={20} className="text-white" />
          ) : (
            <Mic size={20} className="text-white" />
          )}
        </button>

        {/* Text Input */}
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend(text)}
          placeholder={
            isListening
              ? 'Listening... speak now'
              : isProcessing
              ? 'Processing your request...'
              : 'Type or speak — e.g. "Add 2kg rice" or "I need a laptop under 80000"'
          }
          disabled={isListening || isProcessing}
          className="flex-1 bg-transparent text-zinc-100 placeholder:text-zinc-500 outline-none text-base"
        />

        {/* Send Button */}
        {text.trim() && !isProcessing && (
          <button
            type="button"
            onClick={() => handleSend(text)}
            className="w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center shrink-0 transition-all text-white"
          >
            <Send size={16} />
          </button>
        )}
      </div>

      {/* Quick Suggestion Chips */}
      <div className="flex flex-wrap gap-2 mt-3">
        {[
          'Add 2kg oats',
          'I need a laptop under 80000',
          'Find headphones under 5000',
          'Remove milk',
          'Clear basket',
        ].map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => handleSend(s)}
            className="text-xs px-3 py-1.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700 transition-all"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}