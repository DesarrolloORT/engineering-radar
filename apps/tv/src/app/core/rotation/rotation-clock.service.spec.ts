import { TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { RotationClockService } from './rotation-clock.service';

describe('RotationClockService', () => {
  it('reuses one timer across starts and stops it when the app is destroyed', () => {
    vi.useFakeTimers();
    try {
      TestBed.configureTestingModule({});
      const clock = TestBed.inject(RotationClockService);
      clock.start();
      clock.start();
      expect(vi.getTimerCount()).toBe(1);
      vi.advanceTimersByTime(1000);
      expect(clock.nowMs()).toBe(Date.now());
      TestBed.resetTestingModule();
      expect(vi.getTimerCount()).toBe(0);
    } finally {
      vi.useRealTimers();
    }
  });
});
