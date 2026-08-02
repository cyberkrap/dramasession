# Obsession UI redesign

## Direction

The redesign keeps the current Obsession colors, backgrounds, user customisation, board CSS, badges, username effects, and content hierarchy. It replaces the inconsistent visual treatment around that content.

The visual reference is application UI rather than a marketing landing page:

- GitHub and Primer for dense navigation, border-led hierarchy, tables, menus, and predictable page widths
- Supabase for dashboard layout, compact forms, sidebars, and reusable page patterns
- shadcn/ui for small radius scales, composition, focus states, and restrained surfaces

## Foundation rules

### Radius

- 3px for checkboxes and tiny controls
- 5px for buttons, inputs, menu items, tabs, and pagination
- 7px for cards, sidebars, dropdowns, and panels
- 9px only for large dialogs
- Circular treatment remains reserved for avatars, roulette balls, radio controls, and status pills

### Surfaces

- One-pixel borders create hierarchy
- Shadows are subtle and reserved for floating layers
- Gradients are removed from controls
- Glass blur is removed from standard application panels
- Hover states change border or background rather than moving the component

### Spacing

- 36px standard control height
- 30px compact control height
- 42px large control height
- 12 to 14px panel padding
- 10 to 14px vertical form rhythm
- Desktop sidebar fixed to 320px
- Main shell capped at 1480px

### Interaction

- Red remains the primary action colour
- Focus rings remain visible and consistent
- Tabs use an underline rather than rounded pills
- Destructive, success, and warning states keep their semantic colours
- Reduced-motion preferences disable nonessential transitions

## Rollout

### Phase 1: global foundation

- App shell and desktop sidebar width
- Header, search, and icon controls
- Buttons and form fields
- Cards, panels, modals, dropdowns, and popovers
- Tabs, tables, pagination, alerts, lists, and toasts
- Generic settings layout
- Shared utility classes for future templates

### Phase 2: high-traffic pages

- Front page post cards and feed controls
- Post page and comment hierarchy
- Profile pages
- Notifications and inbox
- Submission forms
- Casino landing and game wrappers

### Phase 3: administration and edge cases

- Admin dashboards and moderation forms
- Directory and search pages
- Mobile navigation drawer
- Empty, loading, and error states
- Board-specific compatibility review

## Review checklist

- No page should depend on a radius larger than 9px for a normal panel
- Primary actions must remain visually distinct
- Board custom CSS must still override the foundation where intended
- Patron plates, username colours, badges, hats, and avatars must not be flattened
- Forms must remain keyboard accessible
- Mobile pages must not gain horizontal overflow
- Roulette cells and other custom game controls must retain their own geometry

Preview environment trigger refreshed on 2026-08-02.
