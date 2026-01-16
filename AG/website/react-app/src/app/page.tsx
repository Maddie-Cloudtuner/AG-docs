import Hero from "../components/Hero";
import FeatureShowcase from "../components/FeatureShowcase";
import PricingTable from "../components/PricingTable";

export default function Home() {
    return (
        <>
            <Hero />
            <FeatureShowcase />

            {/* Social Proof / Trust Section */}
            <section className="py-16 border-y border-border bg-surface/30">
                <div className="max-w-7xl mx-auto px-4 text-center">
                    <p className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-8">Trusted by forward-thinking finance & engineering teams</p>
                    <div className="flex flex-wrap justify-center items-center gap-12 opacity-50 grayscale">
                        {/* Placeholders for logos */}
                        <div className="h-8 w-32 bg-white/10 rounded"></div>
                        <div className="h-8 w-32 bg-white/10 rounded"></div>
                        <div className="h-8 w-32 bg-white/10 rounded"></div>
                        <div className="h-8 w-32 bg-white/10 rounded"></div>
                    </div>
                </div>
            </section>

            <section className="section-padding">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16 text-center">
                    <h2 className="text-3xl md:text-4xl font-heading font-bold text-white mb-6">
                        Simple pricing for complex infrastructure.
                    </h2>
                    <p className="text-muted text-lg">Scale your savings as you scale your cloud.</p>
                </div>
                <PricingTable />
            </section>
        </>
    );
}
