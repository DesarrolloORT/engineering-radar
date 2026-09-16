import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';

import { environment } from '../../../../environments/environment';
import { NewsFeedService } from '../../../core/api/news-feed.service';
import { RotationClockService } from '../../../core/rotation/rotation-clock.service';
import { buildSlides, pickSlideIndex } from '../../../core/rotation/rotation.util';
import { NewsCard } from '../news-card/news-card';

/**
 * News-only rotation, for the kiosk-URL fallback described in
 * docs/03-production-pulse-qlik.md (Option B): the browser itself rotates
 * between this route and the Qlik URL when embedding isn't viable.
 */
@Component({
  selector: 'app-news-view',
  imports: [NewsCard],
  templateUrl: './news-view.html',
  styleUrl: './news-view.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NewsView {
  private readonly feed = inject(NewsFeedService);
  private readonly clock = inject(RotationClockService);

  // No production slide here — just the news items, with a minimum of one
  // "empty" slide so the schedule is never zero-length.
  private readonly slides = computed(() =>
    buildSlides(this.feed.items(), environment.rotation).filter(s => s.kind !== 'production')
  );

  readonly currentSlide = computed(() => {
    const slides = this.slides();
    return slides[pickSlideIndex(this.clock.nowMs(), slides)];
  });

  readonly isUnreachable = computed(() => this.feed.hasError() && !this.feed.hasEverLoaded());

  constructor() {
    this.feed.start();
    this.clock.start();
  }
}
