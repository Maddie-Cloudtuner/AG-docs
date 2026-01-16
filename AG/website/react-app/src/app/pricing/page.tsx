import PricingTable from "../../components/PricingTable";

export default function PricingPage() {
    return (
        <div className="py-24">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16 text-center">
                <h1 className="text-4xl md:text-5xl font-heading font-bold text-white mb-6">
                    Choose Your Plan
                </h1>
                <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                    Whether you're a solo developer auditing a single contract or an enterprise managing multi-cloud infrastructure, we have a plan for you.
                </p>
            </div>
            <PricingTable />

            <div className="max-w-3xl mx-auto mt-24 px-4">
                <h2 className="text-2xl font-bold text-white mb-8 text-center">Frequently Asked Questions</h2>
                <div className="space-y-6">
                    {[
                        { q: "Can I switch plans later?", a: "Yes, you can upgrade or downgrade at any time. Prorated charges will apply." },
                        { q: "Do you support custom enterprise contracts?", a: "Absolutely. Contact our sales team for custom SLAs and volume discounts." },
                        { q: "Is the Audit tool included in the Free plan?", a: "Yes, the Free plan includes 1 smart contract audit per month." },
                    ].map((faq, idx) => (
                        <div key={idx} className="border-b border-white/10 pb-6">
                            <h3 className="text-lg font-medium text-white mb-2">{faq.q}</h3>
                            <p className="text-slate-400">{faq.a}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
