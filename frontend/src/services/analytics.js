/**
 * Google Analytics 4 (GA4) Integration for FormMind AI
 * 
 * Supports both VITE_GA_ID and NEXT_PUBLIC_GA_ID environment variables,
 * with fallback to the configured measurement ID: G-SPWVNPXRQZ.
 */

export const GA_MEASUREMENT_ID =
  import.meta.env.VITE_GA_ID ||
  import.meta.env.NEXT_PUBLIC_GA_ID ||
  'G-SPWVNPXRQZ';

/**
 * Initialize Google Analytics 4 (gtag.js)
 * Guarantees single idempotent initialization without duplicate script tags.
 */
export const initGA = () => {
  if (typeof window === 'undefined') return;
  if (!GA_MEASUREMENT_ID) return;

  // Prevent duplicate initialization
  if (window.gtagInitialized || document.getElementById('ga-gtag-script')) {
    return;
  }

  // Setup dataLayer and window.gtag queue
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () {
    window.dataLayer.push(arguments);
  };
  window.gtag('js', new Date());

  // Configure GA4 measurement ID
  // send_page_view: false allows SPA to cleanly manage exact page/view transitions
  window.gtag('config', GA_MEASUREMENT_ID, {
    send_page_view: false,
  });

  // Inject gtag.js script asynchronously into head
  const script = document.createElement('script');
  script.id = 'ga-gtag-script';
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
  document.head.appendChild(script);

  window.gtagInitialized = true;
};

/**
 * Track page / screen view across SPA client-side navigation
 * @param {string} [path] - Virtual or physical path (e.g., '/', '/demo', '/forms/123')
 * @param {string} [title] - Page or view title
 */
export const trackPageView = (path, title) => {
  if (typeof window === 'undefined') return;

  // Ensure GA is initialized
  if (!window.gtagInitialized) {
    initGA();
  }

  const pagePath = path || (window.location.pathname + window.location.search);
  const pageTitle = title || document.title;
  const pageLocation = window.location.origin + pagePath;

  if (typeof window.gtag === 'function') {
    window.gtag('event', 'page_view', {
      page_path: pagePath,
      page_title: pageTitle,
      page_location: pageLocation,
    });
  }
};

/**
 * Track custom user events in GA4
 * @param {string} action - Event action name (e.g. 'start_demo', 'analyze_form', 'export_report')
 * @param {Record<string, any>} [params] - Custom event parameters
 */
export const trackEvent = (action, params = {}) => {
  if (typeof window === 'undefined') return;

  if (!window.gtagInitialized) {
    initGA();
  }

  if (typeof window.gtag === 'function') {
    window.gtag('event', action, params);
  }
};
