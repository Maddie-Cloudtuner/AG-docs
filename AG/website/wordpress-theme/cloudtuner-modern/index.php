<?php get_header(); ?>

<div class="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="text-center max-w-4xl mx-auto">
            <h1 class="text-5xl md:text-6xl lg:text-7xl font-heading font-bold tracking-tight mb-8 text-white leading-tight">
                Cloud costs, <br />
                <span class="text-primary">clarified.</span>
            </h1>
            
            <p class="text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                The FinOps platform designed for real teams. Balance your budget, empower your engineers, and drive innovation without the financial surprise.
            </p>
            
            <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
                <a href="https://dev.dashboard.cloudtuner.ai/public" class="w-full sm:w-auto px-8 py-4 rounded-full bg-primary hover:bg-blue-600 text-white font-bold text-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary/20">
                    Start Optimizing Free
                </a>
                <a href="/demo" class="w-full sm:w-auto px-8 py-4 rounded-full bg-surface hover:bg-slate-700 border border-white/10 text-white font-medium text-lg transition-all flex items-center justify-center">
                    Book a Demo
                </a>
            </div>
        </div>
    </div>
</div>

<section class="py-24 px-4 max-w-7xl mx-auto">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class('p-8 rounded-2xl bg-surface border border-white/10 hover:border-primary/50 transition-colors'); ?>>
                <h2 class="text-xl font-heading font-bold text-white mb-3"><a href="<?php the_permalink(); ?>" class="hover:text-primary transition-colors"><?php the_title(); ?></a></h2>
                <div class="text-slate-400 leading-relaxed">
                    <?php the_excerpt(); ?>
                </div>
            </article>
        <?php endwhile; endif; ?>
    </div>
</section>

<?php get_footer(); ?>
