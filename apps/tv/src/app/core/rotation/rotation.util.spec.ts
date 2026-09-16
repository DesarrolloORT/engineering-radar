import { TechnologyFeedItem } from '../api/technology-feed-item.model';
import { buildSlides, pickSlideIndex } from './rotation.util';

function item(id: string): TechnologyFeedItem {
  return {
    id,
    type: 'technology',
    category: 'development',
    title: id,
    summary: '',
    why_it_matters: '',
    priority: 0.5,
    confidence: 0.5,
    sources_count: 1,
    source_urls: [],
    first_seen: new Date().toISOString(),
    published_at: new Date().toISOString(),
    expires_at: new Date().toISOString(),
    impact: null,
  };
}

describe('buildSlides', () => {
  it('returns an empty-news slide plus a production slide when there are no items', () => {
    const slides = buildSlides([], { newsDurationMs: 1000, productionDurationMs: 2000 });
    expect(slides.map(s => s.kind)).toEqual(['empty-news', 'production']);
  });

  it('inserts a production slide after every 2 news items and after the last one', () => {
    const slides = buildSlides([item('a'), item('b'), item('c')], {
      newsDurationMs: 1000,
      productionDurationMs: 2000,
    });
    expect(slides.map(s => s.kind)).toEqual([
      'news',
      'news',
      'production',
      'news',
      'production',
    ]);
  });
});

describe('pickSlideIndex', () => {
  const slides = buildSlides([item('a'), item('b')], {
    newsDurationMs: 1000,
    productionDurationMs: 2000,
  });
  // slides: [news(1000), news(1000), production(2000)] => total 4000

  it('picks the first slide at time 0', () => {
    expect(pickSlideIndex(0, slides)).toBe(0);
  });

  it('picks the second slide once the first has elapsed', () => {
    expect(pickSlideIndex(1000, slides)).toBe(1);
  });

  it('picks the production slide for the remainder of the cycle', () => {
    expect(pickSlideIndex(2500, slides)).toBe(2);
  });

  it('wraps around to the first slide after a full cycle', () => {
    expect(pickSlideIndex(4000, slides)).toBe(0);
    expect(pickSlideIndex(4200, slides)).toBe(0);
  });
});
