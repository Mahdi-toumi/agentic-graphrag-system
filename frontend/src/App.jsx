import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, BarChart3, Film, Sparkles } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import GraphVisualization from './components/GraphVisualization';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

function App() {
    const [activeTab, setActiveTab] = useState('chat');

    return (
        <div className="relative min-h-screen bg-[#020203] text-slate-100 flex flex-col font-sans selection:bg-blue-500/30">
            {/* Background Orbs */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-600/10 blur-[120px] rounded-full" />
            </div>

            {/* Main Container */}
            <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full px-6 relative z-10">

                {/* Navigation Bar */}
                <header className="py-8 flex flex-col sm:flex-row items-center justify-between gap-6 border-b border-white/5 mb-8">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-3.5"
                    >
                        <div className="p-2.5 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-2xl shadow-xl shadow-blue-500/20">
                            <Film className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black tracking-tight flex items-center gap-1.5">
                                <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">Movie</span>
                                <span className="text-white">Assistant</span>
                            </h1>
                            <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500 tracking-[0.2em] uppercase">
                                <Sparkles size={10} className="text-blue-500" />
                                GraphRAG powered
                            </div>
                        </div>
                    </motion.div>

                    <nav className="flex items-center p-1 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl">
                        <TabButton
                            active={activeTab === 'chat'}
                            onClick={() => setActiveTab('chat')}
                            icon={<MessageSquare size={16} />}
                            label="Assistant"
                        />
                        <TabButton
                            active={activeTab === 'graph'}
                            onClick={() => setActiveTab('graph')}
                            icon={<BarChart3 size={16} />}
                            label="Data Hub"
                        />
                    </nav>
                </header>

                {/* Dynamic Content */}
                <main className="flex-1 min-h-0 flex flex-col relative">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeTab}
                            initial={{ opacity: 0, y: 15 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -15 }}
                            transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
                            className="flex-1 flex flex-col"
                        >
                            {activeTab === 'chat' ? (
                                <ChatInterface />
                            ) : (
                                <GraphVisualization />
                            )}
                        </motion.div>
                    </AnimatePresence>
                </main>

                <footer className="py-8 mt-auto flex items-center justify-between text-[11px] font-semibold text-slate-500 uppercase tracking-widest border-t border-white/5">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                            Node Service Active
                        </div>
                    </div>
                    <div className="opacity-60">© 2025 AI GraphRAG · Cinematic Intelligence</div>
                </footer>
            </div>
        </div>
    );
}

const TabButton = ({ active, onClick, icon, label }) => (
    <button
        onClick={onClick}
        className={cn(
            "relative flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-500",
            active
                ? "text-white"
                : "text-slate-400 hover:text-slate-200"
        )}
    >
        {active && (
            <motion.div
                layoutId="pill"
                className="absolute inset-0 bg-gradient-to-r from-blue-600/90 to-indigo-600/90 rounded-xl shadow-lg shadow-blue-500/10 -z-10"
                transition={{ type: "spring", bounce: 0.25, duration: 0.6 }}
            />
        )}
        <span className={cn("transition-transform duration-300", active && "scale-110")}>{icon}</span>
        {label}
    </button>
);

export default App;
