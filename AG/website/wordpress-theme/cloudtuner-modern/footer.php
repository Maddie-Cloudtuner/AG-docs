</main>

<footer class="bg-dark-900 border-t border-white/10 pt-16 pb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-12">
            <div class="col-span-1 md:col-span-1">
                <a href="<?php echo home_url(); ?>" class="flex-shrink-0">
                    <span class="font-heading text-2xl font-bold text-white">
                        Cloud<span class="text-primary">Tuner</span>
                    </span>
                </a>
                <p class="mt-4 text-slate-400 text-sm leading-relaxed">
                    Empowering enterprises with AI-driven cloud cost optimization and smart contract security auditing.
                </p>
            </div>
            
            <!-- Dynamic Footer Widgets would go here, hardcoded for demo -->
            <div>
                <h3 class="text-sm font-semibold text-white tracking-wider uppercase mb-4">Platform</h3>
                <ul class="space-y-3 text-sm text-slate-400">
                    <li><a href="#" class="hover:text-primary">Kubernetes Cost</a></li>
                    <li><a href="#" class="hover:text-primary">Security Audit</a></li>
                </ul>
            </div>
            
            <div>
                <h3 class="text-sm font-semibold text-white tracking-wider uppercase mb-4">Company</h3>
                <ul class="space-y-3 text-sm text-slate-400">
                    <li><a href="#" class="hover:text-primary">About Us</a></li>
                    <li><a href="#" class="hover:text-primary">Contact</a></li>
                </ul>
            </div>
        </div>
        
        <div class="mt-16 pt-8 border-t border-white/5 text-center">
            <p class="text-slate-500 text-sm">
                &copy; <?php echo date('Y'); ?> CloudTuner AI. All rights reserved.
            </p>
        </div>
    </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
