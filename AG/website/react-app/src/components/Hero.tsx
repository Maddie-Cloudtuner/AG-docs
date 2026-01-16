import Link from "next/link";
import { ArrowRight, CheckCircle2 } from "lucide-react";

export default function Hero() {
    return (
        <div className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="text-center max-w-4xl mx-auto">
                    <h1 className="text-5xl md:text-6xl lg:text-7xl font-heading font-bold tracking-tight mb-8 text-white leading-tight">
                        Cloud costs, <br />
                        <span className="text-primary">clarified.</span>
                    </h1>

                    <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                        The FinOps platform designed for real teams. Balance your budget, empower your engineers, and drive innovation without the financial surprise.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
                        <Link href="https://dev.dashboard.cloudtuner.ai/public" className="w-full sm:w-auto px-8 py-4 rounded-full bg-primary hover:bg-primary-hover text-white font-bold text-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary/20">
                            Start Optimizing Free
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                        <Link href="/demo" className="w-full sm:w-auto px-8 py-4 rounded-full bg-surface hover:bg-surface-hover border border-border text-white font-medium text-lg transition-all flex items-center justify-center">
                            Book a Demo
                        </Link>
                    </div>

                    <div className="flex flex-wrap justify-center gap-x-8 gap-y-4 text-sm text-slate-400">
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                            <span>SOC2 Compliant</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                            <span>15-min Setup</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                            <span>No Credit Card Required</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Background Gradient */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl opacity-30 pointer-events-none">
                <div className="absolute top-20 left-20 w-96 h-96 bg-primary/20 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-20 right-20 w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px]"></div>
            </div>
        </div>
    );
}
