/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',


        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
      screens: {
        sm: '480px',
        md: '768px',
        lg: '976px',
        xl: '1440px',
      },
      fontFamily: {
        courgette: ['Courgette', 'cursive'],
        poppins: ['Poppins', 'sans-serif'],
      },
      gridTemplateColumns: {
        '70/30': '70% 28%'
      },
      colors: {
        "darkBrown": "#161616",
        "lytBrown": "#b58863",
        "rose": "#CAA98B",
        "paraColor": "#d3c3b9",
        "signColor": "#a79e9c",
        "lytBlue": "#3d4d55",
        "rifleBlue": "#10232a",
        "rifleBlue-50": "#f0fafb",
        "rifleBlue-100": "#d9f2f4",
        "rifleBlue-500": "#3398a7",
        "rifleBlue-600": "#2d7c8d",
        "rifleBlue-700": "#2a6574",
        "backgroundColor": "#f7fcff",
        "backgroundColor2": "rgba(175,193,199,0.56)"
      }
    },
    },
    variants: {
        extend: {
            borderColor: ['hover', 'focus'],
            ringColor: ['focus'],
        },
    },
    plugins: [
        /**
         * '@tailwindcss/all_forms' is the all_forms plugin that provides a minimal styling
         * for all_forms. If you don't like it or have own styling for all_forms,
         * comment the line below to disable '@tailwindcss/all_forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
