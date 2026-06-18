// Setup file for Vitest tests
export {};
// Mock IntersectionObserver
class IntersectionObserverMock {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() { return []; }
  unobserve() {}
}
import { vi } from 'vitest';
vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

