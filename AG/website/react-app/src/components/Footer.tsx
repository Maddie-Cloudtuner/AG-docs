import Link from "next/link";
import { Github, Twitter, Linkedin } from "lucide-react";

export default function Footer() {
    return (
        <footer className="bg-dark-900 border-t border-white/10 pt-16 pb-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
                    <div className="col-span-1 md:col-span-1">
                        <Link href="/" className="flex-shrink-0">
                            <span className="font-heading text-2xl font-bold text-white">
                                Cloud<span className="text-primary">Tuner</span>
                            </span>
                        </Link>
                        <p className="mt-4 text-slate-400 text-sm leading-relaxed">
                            Empowering enterprises with AI-driven cloud cost optimization and smart contract security auditing.
                        </p>
                        <div className="flex space-x-4 mt-6">
                            <Link href="#" className="text-slate-400 hover:text-white transition-colors">
                                <Github className="h-5 w-5" />
                            </Link>
                            <Link href="#" className="text-slate-400 hover:text-white transition-colors">
                                <Twitter className="h-5 w-5" />
                            </Link>
                            <Link href="#" className="text-slate-400 hover:text-white transition-colors">
                                <Linkedin className="h-5 w-5" />
                            </Link>
                        </div>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold text-white tracking-wider uppercase mb-4">Platform</h3>
                        <ul className="space-y-3">
                            <li><Link href="/solutions/kubernetes-cost" className="text-slate-400 hover:text-primary text-sm">Kubernetes Cost</Link></li>
                            <li><Link href="/solutions/cloud-migration" className="text-slate-400 hover:text-primary text-sm">Cloud Migration</Link></li>
                            <li><Link href="/solutions/smart-contract-audit" className="text-slate-400 hover:text-primary text-sm">Security Audit</Link></li>
                            <li><Link href="/tools/gas-fees" className="text-slate-400 hover:text-primary text-sm">Gas Fees Tracker</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold text-white tracking-wider uppercase mb-4">Company</h3>
                        <ul className="space-y-3">
                            <li><Link href="/about" className="text-slate-400 hover:text-primary text-sm">About Us</Link></li>
                            <li><Link href="/careers" className="text-slate-400 hover:text-primary text-sm">Careers</Link></li>
                            <li><Link href="/contact" className="text-slate-400 hover:text-primary text-sm">Contact</Link></li>
                            <li><Link href="/privacy" className="text-slate-400 hover:text-primary text-sm">Privacy Policy</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold text-white tracking-wider uppercase mb-4">Resources</h3>
                        <ul className="space-y-3">
                            <li><Link href="/docs" className="text-slate-400 hover:text-primary text-sm">Documentation</Link></li>
                            <li><Link href="/blog" className="text-slate-400 hover:text-primary text-sm">Blog</Link></li>
                            <li><Link href="/case-studies" className="text-slate-400 hover:text-primary text-sm">Case Studies</Link></li>
                            <li><Link href="/status" className="text-slate-400 hover:text-primary text-sm">System Status</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="mt-16 pt-8 border-t border-white/5 text-center">
                    <p className="text-slate-500 text-sm">
                        &copy; {new Date().getFullYear()} CloudTuner AI. All rights reserved.
                    </p>
                </div>
            </div>
        </footer>
    );
}
