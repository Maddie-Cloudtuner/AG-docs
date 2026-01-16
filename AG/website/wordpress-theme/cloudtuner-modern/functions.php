<?php

function cloudtuner_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'cloudtuner'),
        'footer' => __('Footer Menu', 'cloudtuner'),
    ));
}
add_action('after_setup_theme', 'cloudtuner_setup');

function cloudtuner_scripts() {
    wp_enqueue_style('cloudtuner-style', get_stylesheet_uri());
    
    // Tailwind CDN
    wp_enqueue_script('tailwindcss', 'https://cdn.tailwindcss.com', array(), '3.4.0', false);
    
    // Tailwind Config
    wp_add_inline_script('tailwindcss', "
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        background: '#0F172A',
                        surface: '#1E293B',
                        primary: '#3B82F6',
                        secondary: '#10B981',
                    },
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        heading: ['Plus Jakarta Sans', 'sans-serif'],
                    }
                }
            }
        }
    ");
    
    // Google Fonts: Inter + Plus Jakarta Sans
    wp_enqueue_style('google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap', array(), null);
}
add_action('wp_enqueue_scripts', 'cloudtuner_scripts');
