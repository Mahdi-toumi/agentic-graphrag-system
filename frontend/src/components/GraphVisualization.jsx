import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getGraphInfo } from '../services/api';
import { Database, Film, Users, Languages, Share2, Activity, Zap } from 'lucide-react';

const GraphVisualization = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const data = await getGraphInfo();
            setStats(data);
        } catch (error) {
            console.error('Failed to load graph stats:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return (
        <div className="flex-1 flex flex-col items-center justify-center py-40">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }} className="w-12 h-12 border-2 border-blue-500/20 border-t-blue-500 rounded-full" />
            <span className="mt-6 text-[11px] font-black text-slate-500 uppercase tracking-[0.3em]">Querying Knowledge Graph...</span>
        </div>
    );

    if (!stats) return (
        <div className="flex-1 flex flex-col items-center justify-center py-40 text-center px-6">
            <div className="w-20 h-20 bg-red-500/10 rounded-3xl flex items-center justify-center mb-8">
                <Database className="text-red-500 w-10 h-10" />
            </div>
            <h3 className="text-2xl font-black text-white mb-2">Sync Interrupted</h3>
            <p className="text-slate-400 text-sm max-w-xs">The cinematic database is currently unavailable. Ensure Neo4j is online.</p>
        </div>
    );

    return (
        <div className="flex-1 py-4 space-y-12">
            {/* Metrics Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                <StatItem label="Movies" value={stats.total_movies} icon={<Film size={20} />} color="blue" />
                <StatItem label="Entities" value={stats.total_people} icon={<Users size={20} />} color="indigo" />
                <StatItem label="Genres" value={stats.total_genres} icon={<Languages size={20} />} color="emerald" />
                <StatItem label="Connections" value={stats.total_relationships} icon={<Share2 size={20} />} color="amber" />
            </div>

            {/* Insight Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 glass-card p-10 rounded-[2.5rem] relative overflow-hidden group">
                    <div className="relative z-10">
                        <div className="flex items-center gap-3 mb-8">
                            <Activity className="text-blue-500 w-5 h-5" />
                            <h4 className="text-xl font-black text-white uppercase tracking-tight">Graph Network Strategy</h4>
                        </div>
                        <p className="text-slate-300 text-sm leading-relaxed mb-10 max-w-xl font-medium">
                            We leverage an <span className="text-blue-400">Atomic Movie-Centered Model</span>. Every connection represents a semantic or professional link, indexed via <span className="text-indigo-400">HNSW Vector Space</span> for sub-millisecond similarity retrieval.
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="p-5 rounded-2xl bg-white/5 border border-white/5 group-hover:border-blue-500/20 transition-colors">
                                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">Semantic Indexing</div>
                                <div className="text-xs text-slate-200 font-bold leading-relaxed">OpenAI-grade embeddings mapped to graph nodes.</div>
                            </div>
                            <div className="p-5 rounded-2xl bg-white/5 border border-white/5 group-hover:border-indigo-500/20 transition-colors">
                                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">Schema Consistency</div>
                                <div className="text-xs text-slate-200 font-bold leading-relaxed">Rigid node typing for precise Cypher traversal.</div>
                            </div>
                        </div>
                    </div>
                    <div className="absolute -top-12 -right-12 w-48 h-48 bg-blue-600/10 blur-[80px] rounded-full group-hover:bg-blue-600/20 transition-colors duration-1000" />
                </div>

                <div className="glass-card p-10 rounded-[2.5rem] flex flex-col items-center justify-center text-center group">
                    <div className="w-20 h-20 bg-gradient-to-tr from-slate-900 to-[#020203] rounded-3xl flex items-center justify-center mb-8 border border-white/5 shadow-2xl group-hover:scale-110 transition-transform duration-500">
                        <Zap className="text-blue-400 w-10 h-10 drop-shadow-lg" />
                    </div>
                    <p className="text-[11px] font-black text-slate-500 uppercase tracking-[0.2em] mb-2 uppercase">Real-time Pulse</p>
                    <div className="text-xl font-black text-white mb-2 tracking-tight">Sync Optimized</div>
                    <p className="text-xs text-slate-400 font-medium">Network latency: &lt; 15ms</p>
                </div>
            </div>
        </div>
    );
};

const StatItem = ({ label, value, icon, color }) => {
    const colors = {
        blue: "from-blue-600 to-indigo-600 shadow-blue-500/20",
        indigo: "from-indigo-600 to-violet-600 shadow-indigo-500/20",
        emerald: "from-emerald-600 to-teal-600 shadow-emerald-500/20",
        amber: "from-amber-600 to-orange-600 shadow-amber-500/20"
    };

    return (
        <motion.div
            whileHover={{ y: -6 }}
            className="glass-card p-8 rounded-[2.5rem] border-white/5 space-y-4 group overflow-hidden relative"
        >
            <div className={cn("w-12 h-12 rounded-2xl flex items-center justify-center text-white bg-gradient-to-tr shadow-lg drop-shadow-md", colors[color])}>
                {icon}
            </div>
            <div>
                <div className="text-4xl font-black text-white tracking-tighter mb-1">{value}</div>
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">{label}</div>
            </div>
            <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        </motion.div>
    );
};

function cn(...inputs) {
    return inputs.filter(Boolean).join(' ');
}

export default GraphVisualization;
