import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';

import { NewsFeedService } from '../../core/api/news-feed.service';
import { RotationClockService } from '../../core/rotation/rotation-clock.service';
import { buildSlides, pickSlideIndex } from '../../core/rotation/rotation.util';
import { NewsCard } from '../../features/news/news-card/news-card';
import { ProductionPulse } from '../../features/production/production-pulse';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-tv-shell',
  imports: [NewsCard, ProductionPulse],
  templateUrl: './tv-shell.html',
  styleUrl: './tv-shell.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TvShell {
  private readonly feed = inject(NewsFeedService);
  private readonly clock = inject(RotationClockService);

  private readonly slides = computed(() => buildSlides(this.feed.items(), environment.rotation));
  readonly currentSlide = computed(() => {
    const slides = this.slides();
    return slides[pickSlideIndex(this.clock.nowMs(), slides)];
  });

  readonly isStale = computed(
    () => this.feed.hasEverLoaded() && this.feed.isStale(this.clock.nowMs())
  );
  readonly isUnreachable = computed(() => this.feed.hasError() && !this.feed.hasEverLoaded());

  constructor() {
    this.feed.start();
    this.clock.start();
  }
}
