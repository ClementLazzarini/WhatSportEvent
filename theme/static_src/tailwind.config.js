/**
 * This is a minimal config.
 * If using the Tailwind app from django-tailwind, it might look like this:
 */
module.exports = {
    darkMode: "class", // Permet d'activer le dark mode
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
                "background": "#131315",
                "surface": "#131315",
                "surface-container-lowest": "#0e0e10",
                "surface-container-low": "#1b1b1d",
                "surface-container": "#201f21",
                "surface-container-high": "#2a2a2c",
                "surface-container-highest": "#353437",
                "on-surface": "#e5e1e4",
                "on-surface-variant": "#c4c5d9",
                "primary": "#b8c3ff",
                "on-primary": "#002388",
                "primary-container": "#2e5bff",
                "secondary-container": "#ff5e07",
                "error": "#ffb4ab",
                "inverse-primary": "#124af0",
            },
            fontFamily: {
                "headline-lg": ["Sora", "sans-serif"],
                "headline-md": ["Sora", "sans-serif"],
                "headline-xl": ["Sora", "sans-serif"],
                "body-md": ["Inter", "sans-serif"],
                "body-lg": ["Inter", "sans-serif"],
                "label-md": ["Inter", "sans-serif"],
                "label-bold": ["Inter", "sans-serif"]
            },
            spacing: {
                "container-margin-mobile": "20px",
                "container-margin-desktop": "40px",
                "section-gap": "80px",
                "gutter": "24px",
            }
        }
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}