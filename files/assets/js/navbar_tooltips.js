document.addEventListener('DOMContentLoaded', () => {
  const navbar = document.getElementById('navbar');
  if (!navbar || typeof bootstrap === 'undefined' || !bootstrap.Tooltip) return;

  const triggers = navbar.querySelectorAll('[data-bs-toggle="tooltip"]');
  triggers.forEach((trigger) => {
    const existing = bootstrap.Tooltip.getInstance(trigger);
    if (existing) existing.dispose();

    bootstrap.Tooltip.getOrCreateInstance(trigger, {
      container: document.body,
      placement: trigger.getAttribute('data-bs-placement') || 'bottom',
      boundary: 'viewport',
      fallbackPlacements: ['bottom', 'top'],
      offset: [0, 8],
      popperConfig(defaultConfig) {
        return {
          ...defaultConfig,
          strategy: 'fixed',
          modifiers: [
            ...(defaultConfig.modifiers || []),
            { name: 'preventOverflow', options: { boundary: 'viewport', padding: 8 } },
            { name: 'flip', options: { fallbackPlacements: ['bottom', 'top'] } }
          ]
        };
      }
    });
  });
});
