import { BarChart3, Cloud, Layers, Leaf, Zap, ArrowRight } from "lucide-react";

export default function FeatureShowcase() {
    return (
        <section className="section-padding px-4 max-w-7xl mx-auto">
            <div className="text-center mb-20">
                <h2 className="text-3xl md:text-4xl font-heading font-bold mb-6 text-white">
                    Built for teams who care about <br />
                    <span className="text-primary">every dollar and every deployment.</span>
                </h2>
                <p className="text-muted text-lg max-w-2xl mx-auto">
                    CloudTuner bridges the gap between Finance and Engineering with actionable data, not just dashboards.
                </p>
            </div>

            {/* Core Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-24">
                {[
                    {
                        icon: Cloud,
                        title: "Multi-Cloud Analytics",
                        desc: "See your AWS, Azure, GCP, and Kubernetes spend in one unified view. No more jumping between portals.",
                    },
                    {
                        icon: Layers,
                        title: "Resource Visibility",
                        desc: "Tag, track, and allocate costs to specific teams or projects. Know exactly who owns what.",
                    },
                    {
                        icon: BarChart3,
                        title: "Actionable Savings",
                        desc: "Get automated recommendations to right-size instances and eliminate idle resources.",
                    },
                ].map((feature, idx) => (
                    <div key={idx} className="p-8 rounded-2xl bg-surface border border-border hover:border-primary/50 transition-colors group">
                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-6 text-primary group-hover:scale-110 transition-transform">
                            <feature.icon className="w-6 h-6" />
                        </div>
                        <h3 className="text-xl font-heading font-bold text-white mb-3">{feature.title}</h3>
                        <p className="text-slate-400 leading-relaxed">{feature.desc}</p>
                    </div>
                ))}
            </div>

            {/* Deep Dive / Advanced Features */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center bg-surface/30 rounded-3xl p-8 md:p-12 border border-border">
                <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-sm font-medium mb-6">
                        <Leaf className="w-4 h-4" />
                        <span>Sustainable & Future-Proof</span>
                    </div>
                    <h3 className="text-3xl font-heading font-bold text-white mb-6">
                        Innovation without the overhead.
                    </h3>
                    <div className="space-y-8">
                        <div className="flex gap-4">
                            <div className="mt-1">
                                <Zap className="w-6 h-6 text-amber-400" />
                            </div>
                            <div>
                                <h4 className="text-lg font-bold text-white mb-2">Web3 & Gas Analysis</h4>
                                <p className="text-slate-400">
                                    Running blockchain infrastructure? We track gas fees and deployment costs alongside your traditional cloud spend.
                                </p>
                            </div>
                        </div>
                        <div className="flex gap-4">
                            <div className="mt-1">
                                <Leaf className="w-6 h-6 text-emerald-400" />
                            </div>
                            <div>
                                <h4 className="text-lg font-bold text-white mb-2">Carbon Footprint Tracking</h4>
                                <p className="text-slate-400">
                                    Measure the environmental impact of your infrastructure. Optimize for sustainability as easily as you optimize for cost.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Visual/Mockup Area */}
                <div className="relative h-full min-h-[300px] rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 border border-border p-6 flex items-center justify-center">
                    <div className="text-center">
                        <div className="text-5xl font-bold text-white mb-2">24%</div>
                        <div className="text-slate-400">Average Savings in Month 1</div>
                    </div>
                </div>
            </div>
        </section>
    );
}
