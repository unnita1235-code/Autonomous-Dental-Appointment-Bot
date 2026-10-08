import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Patient Experience Colors
        patient: {
          primary: {
            DEFAULT: "#004ac6",
            container: "#2563eb",
            fixed: "#dbe1ff",
            "fixed-dim": "#b4c5ff",
            "on-primary": "#ffffff",
            "on-primary-fixed": "#00174b",
            "on-primary-fixed-variant": "#003ea8",
          },
          secondary: {
            DEFAULT: "#006c49",
            container: "#6cf8bb",
            fixed: "#6ffbbe",
            "fixed-dim": "#4edea3",
            "on-secondary": "#ffffff",
            "on-secondary-fixed": "#002113",
            "on-secondary-fixed-variant": "#005236",
          },
          tertiary: {
            DEFAULT: "#784b00",
            container: "#996100",
            fixed: "#ffddb8",
            "fixed-dim": "#ffb95f",
            "on-tertiary": "#ffffff",
            "on-tertiary-fixed": "#2a1700",
            "on-tertiary-fixed-variant": "#653e00",
          },
          error: {
            DEFAULT: "#ba1a1a",
            container: "#ffdad6",
            "on-error": "#ffffff",
            "on-error-container": "#93000a",
          },
          surface: {
            lowest: "#ffffff",
            low: "#f2f3ff",
            DEFAULT: "#eaedff",
            high: "#e2e7ff",
            highest: "#dae2fd",
          },
          "surface-variant": "#dae2fd",
          "on-surface": "#131b2e",
          "on-surface-variant": "#434655",
          "outline": "#737686",
          "outline-variant": "#c3c6d7",
          background: "#faf8ff",
          "on-background": "#131b2e",
          "inverse-surface": "#283044",
          "inverse-on-surface": "#eef0ff",
          "inverse-primary": "#b4c5ff",
          "surface-tint": "#0053db",

          // -------------------------------------------------------------
          // Compatibility aliases (flat Stitch-style names)
          // -------------------------------------------------------------
          // Phase 1 grouped these values under nested objects (for example
          // `patient.primary.on-primary`), but the frontend components
          // reference the flat names (for example `text-patient-on-primary`).
          // These aliases expose the SAME design-system values under the flat
          // names so existing class usage resolves. No component is rewritten
          // and no visual semantics are changed.
          "primary-hover": "#003ea8",      // = patient.primary.on-primary-fixed-variant
          "on-primary": "#ffffff",         // = patient.primary.on-primary
          "on-primary-container": "#eeefff",
          "on-secondary-fixed": "#002113", // = patient.secondary.on-secondary-fixed
          "on-tertiary-fixed": "#2a1700",  // = patient.tertiary.on-tertiary-fixed
          "success": "#006c49",            // = patient.secondary.DEFAULT
          "success-container": "#6cf8bb",  // = patient.secondary.container
          "on-success": "#ffffff",
          "on-success-container": "#00714d",
          "warning": "#784b00",            // = patient.tertiary.DEFAULT
          "on-error-container": "#93000a", // = patient.error.on-error-container
          "error-hover": "#93000a",        // darker error state
        },

        // Staff Command Colors
        staff: {
          primary: {
            DEFAULT: "#2563EB",
            hover: "#1D4ED8",
            container: "#DBEAFE",
            "on-primary": "#ffffff",
            "on-container": "#1E3A8A",
          },
          ai: {
            DEFAULT: "#7C3AED",
            hover: "#6D28D9",
            container: "#F5F3FF",
            "on-ai": "#ffffff",
            "on-container": "#4C1D95",
            cyan: "#06B6D4",
            "cyan-container": "#ECFEFF",
            "on-cyan": "#164E63",
          },
          background: {
            DEFAULT: "#F8FAFC",
            dark: "#0F172A",
            rail: "#0F172A",
            card: "#FFFFFF",
          },
          surface: {
            DEFAULT: "#FFFFFF",
            variant: "#F1F5F9",
            rail: "#0F172A",
          },
          "on-surface": "#0F172A",
          "on-surface-variant": "#475569",
          "on-surface-muted": "#94A3B8",
          border: {
            DEFAULT: "#E2E8F0",
            dark: "#1E293B",
            focus: "#2563EB",
            "focus-ring": "rgba(37, 99, 235, 0.2)",
          },
          success: {
            DEFAULT: "#10B981",
            container: "#ECFDF5",
            border: "#A7F3D0",
            "on-success": "#ffffff",
            "on-container": "#065F46",
          },
          warning: {
            DEFAULT: "#F59E0B",
            container: "#FFFBEB",
            border: "#FDE68A",
            "on-warning": "#ffffff",
            "on-container": "#92400E",
          },
          error: {
            DEFAULT: "#EF4444",
            container: "#FEF2F2",
            border: "#FECACA",
            "on-error": "#ffffff",
            "on-container": "#991B1B",
          },
          urgent: {
            DEFAULT: "#EF4444",
            container: "#FEF2F2",
            "on-urgent": "#ffffff",
          },
          info: {
            DEFAULT: "#3B82F6",
            container: "#EFF6FF",
            "on-info": "#ffffff",
          },

          // -------------------------------------------------------------
          // Compatibility aliases (flat Stitch-style names)
          // -------------------------------------------------------------
          // Same rationale as the `patient` aliases above: expose the
          // nested design-system values under the flat names already used
          // across the staff UI, without editing any component.
          "on-primary": "#ffffff",          // = staff.primary.on-primary
          "on-primary-container": "#1E3A8A", // = staff.primary.on-container
          "on-ai": "#ffffff",              // = staff.ai.on-ai
          "on-ai-container": "#4C1D95",    // = staff.ai.on-container
          "on-ai-cyan": "#164E63",         // = staff.ai.on-cyan
          "on-error": "#ffffff",           // = staff.error.on-error
          "on-error-container": "#991B1B", // = staff.error.on-container
          "on-info": "#ffffff",            // = staff.info.on-info
          "on-success": "#ffffff",         // = staff.success.on-success
          "on-success-container": "#065F46", // = staff.success.on-container
          "on-warning": "#ffffff",         // = staff.warning.on-warning
          "on-warning-container": "#92400E", // = staff.warning.on-container
        },

        // Semantic tokens (alias to patient/staff for backward compatibility)
        primary: {
          DEFAULT: "#004ac6",
          hover: "#003ea8",
          light: "#dbe1ff",
        },
        accent: {
          DEFAULT: "#006c49",
          hover: "#005236",
        },
        surface: "#faf8ff",
        success: "#006c49",
        warning: "#784b00",
        error: "#ba1a1a",
        muted: "#434655",
      },
      fontFamily: {
        heading: ["Plus Jakarta Sans", "sans-serif"],
        body: ["Plus Jakarta Sans", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        // Stitch Patient Typography Scale
        "display-hero": ["3rem", { lineHeight: "3.5rem", letterSpacing: "-0.025em", fontWeight: "700" }],
        "display-hero-mobile": ["2rem", { lineHeight: "2.5rem", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-xl": ["48px", { lineHeight: "58px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-xl-mobile": ["34px", { lineHeight: "42px", letterSpacing: "-0.01em", fontWeight: "700" }],
        "headline-lg": ["36px", { lineHeight: "46px", letterSpacing: "-0.01em", fontWeight: "700" }],
        "headline-lg-mobile": ["28px", { lineHeight: "36px", fontWeight: "700" }],
        "headline-md": ["28px", { lineHeight: "38px", fontWeight: "600" }],
        "headline-sm": ["22px", { lineHeight: "32px", fontWeight: "600" }],
        "body-xl": ["20px", { lineHeight: "32px", fontWeight: "400" }],
        "body-lg": ["18px", { lineHeight: "28px", fontWeight: "400" }],
        "body-md": ["17px", { lineHeight: "27px", fontWeight: "400" }],
        "body-sm": ["15px", { lineHeight: "24px", fontWeight: "400" }],
        "label-lg": ["18px", { lineHeight: "24px", fontWeight: "600" }],
        "label-md": ["16px", { lineHeight: "22px", fontWeight: "600" }],
        "label-sm": ["14px", { lineHeight: "20px", fontWeight: "600" }],
        "caption": ["14px", { lineHeight: "21px", fontWeight: "500" }],
        // Staff Compact Scale
        "label-dense": ["11px", { lineHeight: "14px", fontWeight: "600", letterSpacing: "0.04em" }],
        "label-mono-stat": ["12px", { lineHeight: "16px", fontWeight: "500", letterSpacing: "0.02em" }],
      },
      spacing: {
        // Stitch Spacing Scale
        "space-xs": "0.25rem",   // 4px
        "space-sm": "0.5rem",    // 8px
        "space-md": "1rem",      // 16px
        "space-lg": "1.5rem",    // 24px
        "space-xl": "2.5rem",    // 40px
        "gutter": "1.5rem",      // 24px
        "gutter-mobile": "1rem", // 16px
        "gutter-staff": "0.75rem", // 12px
        "margin": "2rem",        // 32px
        "margin-mobile": "1rem", // 16px
        "margin-patient": "2rem", // 32px
      },
      borderWidth: {
        // Stitch inputs use a 1.5px hairline border. Tailwind's default scale
        // only ships 0/1/2/4/8, so `border-1.5` could not resolve.
        "1.5": "1.5px",
      },
      borderRadius: {
        DEFAULT: "0.5rem",      // 8px
        sm: "0.25rem",          // 4px
        md: "0.5rem",           // 8px
        lg: "1rem",             // 16px
        xl: "1.5rem",           // 24px
        "2xl": "2rem",          // 32px
        full: "9999px",
      },
      boxShadow: {
        // Stitch Elevation Levels
        "elevation-0": "0 1px 3px 0 rgba(15, 23, 42, 0.04)",
        "elevation-1": "0 4px 20px rgba(15, 23, 42, 0.06)",
        "elevation-hover": "0 8px 24px rgba(15, 23, 42, 0.09)",
        "elevation-2": "0 12px 36px rgba(15, 23, 42, 0.12)",
        "elevation-3": "0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.04)",
        // Used by the chat panel/launcher for the strongest surface lift.
        // Aliased to the deepest defined elevation so no new design value
        // is introduced.
        "elevation-4": "0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.04)",
        // AI Agentic Layer
        "ai-glow": "0 0 0 1px rgba(124, 58, 237, 0.25), 0 4px 20px -2px rgba(99, 102, 241, 0.12)",
        // Focus rings
        "focus-ring": "0 0 0 2px #2563EB, 0 0 0 4px rgba(37, 99, 235, 0.15)",
        "focus-ring-ai": "0 0 0 2px #7C3AED, 0 0 0 4px rgba(124, 58, 237, 0.15)",
      },
      keyframes: {
        "typing-dot": {
          "0%, 80%, 100%": { opacity: "0.3", transform: "translateY(0)" },
          "40%": { opacity: "1", transform: "translateY(-2px)" }
        },
        "checkmark-draw": {
          "0%": { "stroke-dashoffset": "40" },
          "100%": { "stroke-dashoffset": "0" }
        },
        "glow-pulse": {
          "0%, 100%": { opacity: "0.4", transform: "scale(1)" },
          "50%": { opacity: "0.6", transform: "scale(1.1)" }
        },
        "fab-pulse": {
          "0%": { transform: "scale(1)", opacity: "0.5" },
          "50%": { transform: "scale(1.1)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "0" }
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        },
        "slide-down": {
          "0%": { opacity: "0", transform: "translateY(-16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" }
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" }
        },
        "shimmer": {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" }
        }
      },
      animation: {
        "typing-dot": "typing-dot 1.2s infinite ease-in-out",
        "checkmark-draw": "checkmark-draw 600ms cubic-bezier(0.2, 0.8, 0.2, 1) forwards",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "fab-pulse": "fab-pulse 6s ease-out infinite",
        "slide-up": "slide-up 400ms ease-out",
        "slide-down": "slide-down 300ms ease-out",
        "fade-in": "fade-in 200ms ease-out",
        "scale-in": "scale-in 200ms ease-out",
        "shimmer": "shimmer 2s linear infinite",
      },
      transitionTimingFunction: {
        "ease-spring": "cubic-bezier(0.16, 1, 0.3, 1)",
        "ease-out-expo": "cubic-bezier(0.16, 1, 0.3, 1)",
      },
      minHeight: {
        "touch-target": "48px",
        "touch-target-lg": "52px",
        "touch-target-sm": "36px",
      },
      minWidth: {
        "touch-target": "48px",
        "touch-target-lg": "52px",
        "touch-target-sm": "36px",
      },
    }
  },
  plugins: [
    require("tailwindcss-animate")
  ],
};

export default config;