<?php get_header(); ?>

<div class="py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <header class="mb-12 text-center">
                    <h1 class="text-4xl md:text-5xl font-heading font-bold text-white mb-6"><?php the_title(); ?></h1>
                </header>
                
                <div class="prose prose-invert prose-lg max-w-4xl mx-auto text-slate-300">
                    <?php the_content(); ?>
                </div>
            </article>
        <?php endwhile; endif; ?>
    </div>
</div>

<?php get_footer(); ?>
