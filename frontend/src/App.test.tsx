import { render, screen, waitFor } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import App from './App';
import * as api from './utils/api';
import { GameState } from './types';

vi.mock('./utils/api', () => ({
  apiFetch: vi.fn()
}));

vi.mock('./components/ProjectSwitcher', () => ({
  ProjectSwitcher: () => <div data-testid="project-switcher" />
}));

describe('Silicon Valley Trail App', () => {
  test('renders loading state initially', () => {
    vi.mocked(api.apiFetch).mockImplementation(
      () =>
        new Promise<GameState>(() => {
          // Intentionally unresolved to test initial loading state
        }),
    );
    render(<App />);
    expect(screen.getByText('Loading IDE...')).toBeDefined();
  });

  test('renders error state if fetch fails', async () => {
    vi.mocked(api.apiFetch).mockRejectedValue(new Error('Network Error'));
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Error: Network Error/i)).toBeDefined();
    });
  });

  test('renders dynamic max_bugs from backend state', async () => {
    vi.mocked(api.apiFetch).mockResolvedValue({
      current_location: 'New York City',
      description: 'The start.',
      sequence_in_journey: 1,
      total_stops: 10,
      cash: 1400,
      award_miles: 3000,
      morale: 100,
      bugs: 12,
      max_bugs: 50,
      days_remaining: 16,
      is_won: false,
      is_lost: false,
      status_summary: 'Active',
      message: 'Welcome!',
      stat_statuses: {
        days: 'good',
        cash: 'good',
        miles: 'blue',
        morale: 'good',
        bugs: 'good',
      },
    });
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('12 / 50')).toBeDefined();
    });
  });
});
