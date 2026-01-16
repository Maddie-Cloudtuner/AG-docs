<!DOCTYPE html>
<html <?php language_attributes(); ?> class="scroll-smooth">
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
</head>
<body <?php body_class('bg-background text-slate-50 antialiased'); ?>>

<nav class="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-white/10">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-20">
            <a href="<?php echo home_url(); ?>" class="flex items-center gap-2">
                <div class="w-8 h-8 rounded bg-primary flex items-center justify-center text-white font-bold font-heading text-lg">C</div>
                <span class="font-heading text-xl font-bold text-white">CloudTuner</span>
            </a>
            
            <div class="hidden md:block">
                <?php
                wp_nav_menu(array(
                    'theme_location' => 'primary',
                    'container' => false,
                    'menu_class' => 'flex items-center space-x-8',
                    'add_li_class' => 'text-sm font-medium text-slate-300 hover:text-primary transition-colors'
                ));
                ?>
            </div>

            <div class="hidden md:flex items-center gap-4">
                <a href="https://dev.dashboard.cloudtuner.ai/public" class="text-sm font-medium text-white hover:text-primary transition-colors">Log In</a>
                <a href="/demo" class="px-5 py-2.5 rounded-lg bg-primary hover:bg-blue-600 text-white font-bold text-sm transition-colors">Get Started</a>
            </div>
        </div>
    </div>
</nav>

<main class="min-h-screen">
