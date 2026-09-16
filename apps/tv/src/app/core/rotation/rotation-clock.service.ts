import { DestroyRef, Injectable, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval, startWith } from 'rxjs';

/**
 * A single shared "now" tick shared by slide rotation and staleness
 * detection, so the TV needs exactly one timer instead of one per feature.
 */
@Injectable({ providedIn: 'root' })
export class RotationClockService {
  private readonly destroyRef = inject(DestroyRef);
  private started = false;
  readonly nowMs = signal(Date.now());

  start(tickMs = 1000): void {
    if (this.started) return;
    this.started = true;
    interval(tickMs)
      .pipe(startWith(0), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.nowMs.set(Date.now()));
  }
}
