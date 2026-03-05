# Next.js Production Checklist

Applies to: **Lotify Web**, **Lotify Admin**, **Courio Admin**

---

## Build & Deploy

- [ ] Standalone output mode for Docker
- [ ] Environment variables at build time vs runtime separated
- [ ] ISR/SSG where possible, SSR only when needed
- [ ] Image optimization (next/image with proper loader)

## Performance

- [ ] Core Web Vitals passing (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] Bundle size analysis (no large unused dependencies)
- [ ] Code splitting / dynamic imports for heavy components
- [ ] Font optimization (next/font)
- [ ] CDN for static assets

## Security

- [ ] CSP headers configured
- [ ] No sensitive data in client bundles
- [ ] API routes protected with auth middleware
- [ ] CSRF protection on forms
- [ ] Sanitized user-generated content (XSS prevention)

## SEO & Accessibility (Lotify Web)

- [ ] Proper meta tags and Open Graph
- [ ] Sitemap generation
- [ ] Structured data for auction listings
- [ ] Accessibility audit (axe-core)
- [ ] Semantic HTML (proper heading hierarchy, landmarks)
- [ ] Alt text on all images
- [ ] Keyboard navigation support

## Internationalization

- [ ] Georgian (ka) and English (en) locales tested
- [ ] RTL not needed (Georgian is LTR) but locale switching works
- [ ] Currency formatting (GEL) consistent across pages
- [ ] Date/time formatting respects locale

## Error Handling

- [ ] Custom 404 page
- [ ] Custom 500 page
- [ ] Error boundary components for client-side crashes
- [ ] Graceful fallback when API is unavailable
