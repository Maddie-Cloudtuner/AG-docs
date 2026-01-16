import { Check } from "lucide-react";
import Link from "next/link";

const tiers = [
    {
        name: "Free",
        price: "$0",
        description: "For individuals and small projects.",
        features: [
            "Basic Cloud Cost Monitoring",
            "1 Smart Contract Audit / Month",
            "Community Support",
            "Gas Fees Tracker",
        ],
        cta: "Get Started",
        href: "https://dev.dashboard.cloudtuner.ai/public",
        featured: false,
    },
    {
        name: "Pro",
        price: "$49",
        period: "/mo",
        description: "For growing teams and startups.",
        features: [
            "Advanced Kubernetes Cost Allocation",
            "10 Smart Contract Audits / Month",
            "Priority Email Support",
            "Custom Alerts & Reports",
            "API Access",
        ],
        cta: "Start Free Trial",
        href: "https://dev.dashboard.cloudtuner.ai/public",
        featured: true,
    },
    {
        name: "Enterprise",
        price: "Custom",
        description: "For large organizations with complex needs.",
        features: [
            "Unlimited Audits & Cost Monitoring",
            "Dedicated Account Manager",
            "24/7 Phone & Slack Support",
            "On-premise Deployment Option",
            "Custom SLA",
        ],
        cta: "Contact Sales",
        href: "/contact",
        featured: false,
    },
];

export default function PricingTable() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {tiers.map((tier) => (
                <div
                    key={tier.name}
                    className={`relative rounded-2xl p-8 border ${tier.featured
                            ? "bg-dark-800 border-primary shadow-2xl shadow-primary/10"
                            : "bg-dark-900/50 border-white/10 hover:border-white/20 transition-colors"
                        }`}
                >
                    {tier.featured && (
                        <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-dark-900 px-4 py-1 rounded-full text-sm font-bold">
                            Most Popular
                        </div>
                    )}
                    <h3 className="text-xl font-bold text-white mb-2">{tier.name}</h3>
                    <div className="flex items-baseline mb-4">
                        <span className="text-4xl font-bold text-white">{tier.price}</span>
                        {tier.period && <span className="text-slate-400 ml-1">{tier.period}</span>}
                    </div>
                    <p className="text-slate-400 text-sm mb-6">{tier.description}</p>
                    <ul className="space-y-4 mb-8">
                        {tier.features.map((feature) => (
                            <li key={feature} className="flex items-start gap-3">
                                <Check className="w-5 h-5 text-primary flex-shrink-0" />
                                <span className="text-slate-300 text-sm">{feature}</span>
                            </li>
                        ))}
                    </ul>
                    <Link
                        href={tier.href}
                        className={`block w-full py-3 rounded-lg text-center font-bold transition-all ${tier.featured
                                ? "bg-primary hover:bg-primary-dark text-dark-900"
                                : "bg-white/10 hover:bg-white/20 text-white"
                            }`}
                    >
                        {tier.cta}
                    </Link>
                </div>
            ))}
        </div>
    );
}
