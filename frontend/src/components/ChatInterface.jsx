import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, Sparkles, User, Bot, Cpu, Clock, Terminal, ChevronRight } from 'lucide-react';
import { askQuestion } from '../services/api';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import ReactMarkdown from 'react-markdown';

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await askQuestion(input);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.answer,
                tool_calls: response.tool_calls,
                execution_time: response.execution_time,
                timestamp: new Date().toISOString()
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'error',
                content: 'Failed to access the graph. Check your connection.',
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex-1 flex flex-col min-h-0">
            {/* Messages Feed */}
            <div className="flex-1 overflow-y-auto px-2 space-y-10 no-scrollbar py-8">
                {messages.length === 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex flex-col items-center justify-center h-full text-center py-20"
                    >
                        <div className="w-16 h-16 bg-blue-600/10 rounded-3xl flex items-center justify-center mb-8 shadow-inner shadow-blue-500/10">
                            <Sparkles className="text-blue-400 w-8 h-8" />
                        </div>
                        <h2 className="text-3xl font-extrabold text-white mb-3">Cinema Intelligence</h2>
                        <p className="text-slate-400 max-w-sm text-sm leading-relaxed mb-10">
                            Ask about plots, actors, or complex graph connections in the movie universe.
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md px-4">
                            {['Highest rated 90s sci-fi', 'Who did Christopher Nolan direct?', 'Movies like Inception', 'Cast of The Matrix'].map((hint) => (
                                <button
                                    key={hint}
                                    onClick={() => setInput(hint)}
                                    className="flex items-center justify-between p-4 glass-card rounded-2xl hover:bg-white/5 transition-all group text-left"
                                >
                                    <span className="text-xs font-semibold text-slate-300">{hint}</span>
                                    <ChevronRight size={14} className="text-slate-500 group-hover:text-blue-400 transition-colors" />
                                </button>
                            ))}
                        </div>
                    </motion.div>
                )}

                <AnimatePresence initial={false}>
                    {messages.map((msg, i) => (
                        <MessageItem key={i} msg={msg} />
                    ))}
                </AnimatePresence>

                {loading && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3 pl-4">
                        <div className="w-8 h-8 bg-blue-600/10 rounded-lg flex items-center justify-center">
                            <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                        </div>
                        <span className="text-xs font-bold text-slate-500 tracking-wider">THINKING...</span>
                    </motion.div>
                )}
                <div ref={messagesEndRef} className="h-20" />
            </div>

            {/* Input Dock */}
            <div className="sticky bottom-0 pb-8 pt-4 bg-gradient-to-t from-[#020203] via-[#020203] to-transparent">
                <form
                    onSubmit={handleSubmit}
                    className="glass-card rounded-2xl p-1.5 flex items-center gap-2 border border-white/10 shadow-2xl focus-within:border-blue-500/50 transition-colors"
                >
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask anything about movies..."
                        className="flex-1 bg-transparent border-none focus:ring-0 text-white placeholder-slate-500 px-4 text-sm font-medium"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim()}
                        className={cn(
                            "px-5 py-2.5 rounded-xl transition-all duration-300 flex items-center justify-center font-bold text-sm",
                            input.trim()
                                ? "bg-blue-600 text-white hover:bg-blue-500 shadow-lg shadow-blue-500/20"
                                : "bg-slate-800 text-slate-500"
                        )}
                    >
                        {loading ? <Loader2 size={16} className="animate-spin" /> : <><Send size={16} className="mr-2" /> Send</>}
                    </button>
                </form>
            </div>
        </div>
    );
};

const MessageItem = ({ msg }) => {
    const isUser = msg.role === 'user';
    const isError = msg.role === 'error';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn("flex gap-5", isUser ? "flex-row-reverse" : "flex-row")}
        >
            <div className={cn(
                "w-10 h-10 rounded-2xl flex-shrink-0 flex items-center justify-center shadow-lg",
                isUser ? "bg-gradient-to-tr from-blue-600 to-indigo-600" : "glass-card border-white/5"
            )}>
                {isUser ? <User size={18} className="text-white" /> : <Bot size={18} className="text-blue-400" />}
            </div>

            <div className={cn("flex flex-col max-w-[85%]", isUser ? "items-end" : "items-start")}>
                <div className={cn(
                    "px-5 py-4 rounded-2xl text-[14px] leading-relaxed shadow-xl",
                    isUser
                        ? "bg-blue-600 text-white rounded-tr-none"
                        : isError
                            ? "bg-red-950/30 text-red-200 border border-red-500/20 rounded-tl-none"
                            : "glass-card text-slate-100 rounded-tl-none"
                )}>
                    <div className="prose prose-invert max-w-none text-slate-100">
                        <ReactMarkdown
                            components={{
                                ul: ({ node, ...props }) => <ul className="list-disc ml-5 mt-3 space-y-2" {...props} />,
                                li: ({ node, ...props }) => <li className="text-[13px] leading-relaxed mb-1" {...props} />,
                                strong: ({ node, ...props }) => <strong className="text-blue-400 font-bold" {...props} />,
                                p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
                            }}
                        >
                            {msg.content}
                        </ReactMarkdown>
                    </div>

                    {!isUser && msg.execution_time && (
                        <div className="mt-4 pt-4 border-t border-white/5 flex items-center gap-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                            <span className="flex items-center gap-1.5"><Clock size={12} /> {msg.execution_time}s</span>
                            <span className="flex items-center gap-1.5 text-blue-400"><Cpu size={12} /> Agentic GraphRAG</span>
                        </div>
                    )}
                </div>

                {!isUser && msg.tool_calls && msg.tool_calls.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3 cursor-default">
                        {msg.tool_calls.map((call, i) => (
                            <div key={i} className="px-3 py-1.5 glass-card rounded-lg flex items-center gap-2 border border-white/5">
                                <Terminal size={10} className="text-blue-500" />
                                <span className="text-[10px] font-black text-slate-300 uppercase tracking-tighter">{call.tool}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </motion.div>
    );
};

export default ChatInterface;
