export type ThemeMode = 'light' | 'dark';

export const getStoredTheme = (): ThemeMode => {
  const stored = localStorage.getItem('theme');
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  // Default to system preference
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
};

export const setStoredTheme = (theme: ThemeMode): void => {
  localStorage.setItem('theme', theme);
};

export const getSystemTheme = (): ThemeMode => {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}; 