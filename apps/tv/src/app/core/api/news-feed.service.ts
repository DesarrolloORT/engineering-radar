import { HttpClient } from '@angular/common/http';
import { DestroyRef, Injectable, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { catchError, interval, of, startWith, switchMap, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { TechnologyFeedItem } from './technology-feed-item.model';

/**
 * Polls the Radar's public read endpoint only (GET /api/v1/feed/news) — no
 * LLM, no scraping, no auth from the browser (docs/06-operacion-seguridad.md).
 * On failure, the last known-good items are kept so the TV never blanks out
 * (docs/04-tv-experience.md, "Estado degradado").
 */
@Injectable({ providedIn: 'root' })
export class NewsFeedService {
  private readonly http = inject(HttpClient);
  private readonly destroyRef = inject(DestroyRef);

  readonly items = signal<TechnologyFeedItem[]>([]);
  readonly lastUpdatedAt = signal<number | null>(null);
  readonly hasError = signal(false);

  readonly hasEverLoaded = computed(() => this.lastUpdatedAt() !== null);

  start(): void {
    interval(environment.rotation.pollIntervalMs)
      .pipe(
        startWith(0),
        switchMap(() => this.fetch()),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe();
  }

  isStale(nowMs: number): boolean {
    const last = this.lastUpdatedAt();
    if (last === null) return false;
    return nowMs - last > environment.rotation.feedStaleThresholdMs;
  }

  private fetch() {
    return this.http.get<TechnologyFeedItem[]>(`${environment.apiUrl}/api/v1/feed/news`).pipe(
      tap(items => {
        this.items.set(items);
        this.lastUpdatedAt.set(Date.now());
        this.hasError.set(false);
      }),
      catchError(() => {
        this.hasError.set(true);
        return of(null);
      })
    );
  }
}
