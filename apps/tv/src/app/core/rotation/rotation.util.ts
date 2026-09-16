import { TechnologyFeedItem } from '../api/technology-feed-item.model';
import { RotationConfig, Slide } from './slide.model';

/**
 * Interleaves a production slide after every 2 news items (and after the
 * last one), matching the example sequence in docs/04-tv-experience.md:
 * News#1, News#2, Production, News#3, Production, repeat. Production is
 * always shown periodically even when stable — it never disappears just
 * because there are 0 or 1 news items.
 */
export function buildSlides(items: TechnologyFeedItem[], cfg: RotationConfig): Slide[] {
  if (items.length === 0) {
    return [
      { kind: 'empty-news', durationMs: cfg.newsDurationMs },
      { kind: 'production', durationMs: cfg.productionDurationMs },
    ];
  }

  const slides: Slide[] = [];
  items.forEach((item, index) => {
    slides.push({ kind: 'news', item, durationMs: cfg.newsDurationMs });
    const isLast = index === items.length - 1;
    if ((index + 1) % 2 === 0 || isLast) {
      slides.push({ kind: 'production', durationMs: cfg.productionDurationMs });
    }
  });
  return slides;
}

/**
 * Picks the slide active at `nowMs`, purely from wall-clock time — no
 * mutable rotation state to lose on refresh/reboot
 * (docs/04-tv-experience.md, "recuperación tras refresh/reinicio").
 */
export function pickSlideIndex(nowMs: number, slides: Slide[]): number {
  const totalMs = slides.reduce((sum, slide) => sum + slide.durationMs, 0);
  if (totalMs <= 0) return 0;

  let elapsed = nowMs % totalMs;
  for (let i = 0; i < slides.length; i++) {
    if (elapsed < slides[i].durationMs) return i;
    elapsed -= slides[i].durationMs;
  }
  return slides.length - 1;
}
