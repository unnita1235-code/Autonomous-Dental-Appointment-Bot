/**
 * PostCSS configuration.
 *
 * Next.js only supplies `postcss-flexbugs-fixes` and `postcss-preset-env` by
 * default — it does NOT add Tailwind automatically. Tailwind therefore only
 * runs when it is registered here.
 *
 * The project is on Tailwind v3 (`tailwindcss@3.4.3`), which uses the
 * `@tailwind base / components / utilities` directives present in
 * `src/app/globals.css`. `autoprefixer` is already installed and is added for
 * vendor prefixing only.
 *
 * Module system: this package has no `"type": "module"`, so this file is
 * CommonJS, matching `next.config.js`.
 */
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};