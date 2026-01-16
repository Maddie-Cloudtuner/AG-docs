import { ArrowUpRight, ShieldCheck, Coins, Cpu, Zap, Lock } from "lucide-react";
import Link from "next/link";

export default function BentoGrid() {
    return (
        <section className="py-24 px-4 max-w-7xl mx-auto">
            <div className="mb-16 text-center">
                <h2 className="text-3xl md:text-5xl font-heading font-bold mb-6">
                    Total Control. <span className="text-gradient">Zero Compromise.</span>
                </h2>
                <p className="text-muted text-lg max-w-2xl mx-auto">
                    The only platform that unifies deep infrastructure intelligence with automated security enforcement.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[300px]">

                {/* Card 1: Large - Cost Intelligence */}
                <div className="md:col-span-2 glass-card rounded-3xl p-8 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:opacity-40 transition-opacity">
                        <Coins className="w-32 h-32" />
                    </div>
                    <div className="relative z-10 h-full flex flex-col justify-between">
                        <div>
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-success/10 border border-success/20 text-success text-xs font-mono mb-4">
                                <ArrowUpRight className="w-3 h-3" /> SAVED $1.2M YTD
                            </div>
                            <h3 className="text-3xl font-heading font-bold mb-2">Kubernetes Cost Intelligence</h3>
                            <p className="text-muted max-w-md">
                                Granular allocation down to the pod level. Identify idle resources, right-size workloads, and eliminate waste automatically.
                            </p>
                        </div>
                        <div className="bg-black/40 rounded-xl p-4 border border-white/5 font-mono text-sm text-slate-300">
                            <div className="flex justify-between mb-2">
                                <span>cluster-prod-01</span>
                                <span className="text-success">-24% cost</span>
                            </div>
                            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                                <div className="bg-success h-full w-[76%]"></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Card 2: Tall - Security Audit */}
                <div className="md:row-span-2 glass-card rounded-3xl p-8 relative overflow-hidden group bg-gradient-to-b from-surface to-primary/5">
                    <div className="absolute inset-0 bg-grid-pattern opacity-[0.03]"></div>
                    <div className="relative z-10 h-full flex flex-col">
                        <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center mb-6 text-primary">
                            <ShieldCheck className="w-6 h-6" />
                        </div>
                        <h3 className="text-3xl font-heading font-bold mb-4">AI Security Auditor</h3>
                        <p className="text-muted mb-8">
                            Instant smart contract analysis powered by advanced LLMs. Detect reentrancy, overflow, and logic errors before deployment.
                        </p>

                        <div className="mt-auto space-y-3">
                            {["Reentrancy Attack", "Integer Overflow", "Unchecked Call", "Gas Optimization"].map((item, i) => (
                                <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-black/20 border border-white/5">
                                    <Lock className="w-4 h-4 text-secondary" />
                                    <span className="font-mono text-sm text-slate-300">{item}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Card 3: Standard - Gas Fees */}
                <div className="glass-card rounded-3xl p-8 flex flex-col justify-between group hover:bg-white/5 transition-colors">
                    <Zap className="w-10 h-10 text-yellow-400 mb-4" />
                    <div>
                        <h3 className="text-xl font-heading font-bold mb-2">Real-time Gas Tracker</h3>
                        <p className="text-muted text-sm">Monitor network congestion and optimize transaction timing.</p>
                    </div>
                </div>

                {/* Card 4: Standard - Multi-Cloud */}
                <div className="glass-card rounded-3xl p-8 flex flex-col justify-between group hover:bg-white/5 transition-colors">
                    <Cpu className="w-10 h-10 text-blue-400 mb-4" />
                    <div>
                        <h3 className="text-xl font-heading font-bold mb-2">Multi-Cloud Native</h3>
                        <p className="text-muted text-sm">Unified view across AWS, GCP, Azure, and on-premise clusters.</p>
                    </div>
                </div>

            </div>
        </section>
    );
}
