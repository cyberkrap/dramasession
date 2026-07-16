# Obsession Fan Club Mobile UI Specification

## Breakpoints

- Compact mobile: up to 374px
- Normal mobile: 375px to 767px
- Tablet: 768px to 1023px
- Desktop: 1024px and above

## Shared measurements

- Mobile page gutter: obs-mobile-gutter (14px)
- Touch target: obs-touch-target (44px minimum)
- Mobile control height: obs-control-height (44px)
- Bottom navigation: obs-mobile-bottom-height (76px including safe-area padding)
- Header: ticker plus navigation, obs-header-total-height (86px)
- Card gap: obs-card-gap (12px)
- Section gap: obs-section-gap (20px)

## Navigation shell

The mobile header stays fixed below the live-user ticker. The hamburger opens the navbarResponsive element as a fixed, independently scrollable drawer. The drawer uses a dark backdrop, closes from the backdrop, close control, Escape, or navigation, and locks document scrolling while open. The drawer uses 100dvh sizing and safe-area-aware padding.

The bottom navigation is visible only below the tablet breakpoint. It uses real Obsession routes, provides an icon and short label for each destination, marks the active route with aria-current=page, and reserves body space so content and composers are not hidden behind it.

## Shared responsive patterns

- app-shell provides the common mobile gutter.
- mobile-toolbar, mobile-card-grid, mobile-form-row, responsive-media, and mobile-sticky-offset are the shared patterns for later pages.
- obs-mobile-bottom-nav and obs-mobile-bottom-nav__item define the fixed mobile navigation.
- mobile-nav-icon is the shared 44px header action target.
- mobile-drawer-open locks the page while the drawer is open.
- Media uses max-width: 100%; long text uses safe wrapping instead of page-wide overflow.
- Form controls use at least 16px text on mobile to avoid iOS input zoom.
- Tables and wide content should use responsive wrappers rather than forcing the page wider.

## Accessibility

Icon-only controls have labels, the drawer exposes expanded and hidden state, focus-visible outlines remain visible, Escape closes the drawer, and reduced-motion users receive minimal transitions.
