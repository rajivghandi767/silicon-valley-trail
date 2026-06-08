import { render, screen, waitFor } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import App from './App';
import * as api from './utils/api';

vi.mock('./utils/api', () => ({
  apiFetch: vi.fn()
}));

vi.mock('./components/ProjectSwitcher', () => ({
  ProjectSwitcher: () => <div data-testid="project-switcher" />
}));

describe('Silicon Valley Trail App', () => {
  test('renders loading state initially', () => {
    // Return a promise that doesn't resolve immediately
    (api.apiFetch as any).mockImplementation(() => new Promise(() => {}));
    render(<App />);
    expect(screen.getByText('Loading IDE...')).toBeDefined();
  });

  test('renders error state if fetch fails', async () => {
    (api.apiFetch as any).mockRejectedValue(new Error('Network Error'));
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/Error: Network Error/i)).toBeDefined();
    });
  });
});
