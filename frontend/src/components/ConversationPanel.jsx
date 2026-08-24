import React, { useEffect, useRef } from 'react';
import { useStore } from '../store/useStore';
import { cn } from '../utils/cn';
import { Bot, User as UserIcon } from 'lucide-react';

const ConversationPanel = () => {
  const { conversation } = useStore();
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  if (conversation.length === 0) return null;

  return (
    <div className="glass rounded-2xl p-4 max-h-[300px] overflow-y-auto mb-8 flex flex-col gap-4 border-zinc-800/50">
      {conversation.map((msg, i) => (
        <div key={i} className={cn("flex gap-3", msg.sender === 'USER' ? 'flex-row-reverse' : '')}>
          <div className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
            msg.sender === 'USER' ? 'bg-indigo-500' : 'bg-zinc-800'
          )}>
            {msg.sender === 'USER' ? <UserIcon size={16} className="text-white" /> : <Bot size={16} className="text-indigo-400" />}
          </div>
          <div className={cn(
            "px-4 py-2 rounded-2xl max-w-[80%]",
            msg.sender === 'USER' 
              ? 'bg-indigo-500 text-white rounded-tr-none' 
              : 'bg-zinc-800/50 text-zinc-200 border border-zinc-700/50 rounded-tl-none'
          )}>
            {msg.text}
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
};

export default ConversationPanel;
