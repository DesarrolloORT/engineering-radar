import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { environment } from '../../../environments/environment';
import { NewsFeedService } from './news-feed.service';
import { TechnologyFeedItem } from './technology-feed-item.model';

const SAMPLE_ITEM: TechnologyFeedItem = {
  id: 'sig-1',
  type: 'technology',
  category: 'development',
  title: 't',
  summary: 's',
  why_it_matters: 'w',
  priority: 0.7,
  confidence: 0.8,
  sources_count: 2,
  source_urls: [],
  first_seen: new Date().toISOString(),
  published_at: new Date().toISOString(),
  expires_at: new Date(Date.now() + 3_600_000).toISOString(),
  impact: null,
};

describe('NewsFeedService', () => {
  let service: NewsFeedService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(NewsFeedService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('populates items on a successful fetch', () => {
    service.start();

    const req = httpMock.expectOne(`${environment.apiUrl}/api/v1/feed/news`);
    req.flush([SAMPLE_ITEM]);

    expect(service.items()).toEqual([SAMPLE_ITEM]);
    expect(service.hasError()).toBe(false);
    expect(service.hasEverLoaded()).toBe(true);
  });

  it('starts only one polling loop when routes reuse the service', () => {
    vi.useFakeTimers();
    try {
      service.start();
      service.start();
      httpMock.expectOne(`${environment.apiUrl}/api/v1/feed/news`).flush([]);
      vi.advanceTimersByTime(environment.rotation.pollIntervalMs);
      httpMock.expectOne(`${environment.apiUrl}/api/v1/feed/news`).flush([]);
    } finally {
      vi.useRealTimers();
    }
  });

  it('expires cached signals during an outage and recovers on the next poll', () => {
    vi.useFakeTimers();
    try {
      service.start();
      const item = {
        ...SAMPLE_ITEM,
        expires_at: new Date(Date.now() + environment.rotation.pollIntervalMs + 1000).toISOString(),
      };
      httpMock.expectOne(`${environment.apiUrl}/api/v1/feed/news`).flush([item]);
      vi.advanceTimersByTime(environment.rotation.pollIntervalMs);
      httpMock.expectOne(`${environment.apiUrl}/api/v1/feed/news`)
        .flush('boom', { status: 503, statusText: 'Unavailable' });
      expect(service.items()).toEqual([item]);
      vi.advanceTimersByTime(1000);
      expect(service.items()).toEqual([]);
      vi.advanceTimersByTime(environment.rotation.pollIntervalMs - 1000);
      httpMock.expectOne(`${environment.apiUrl}/api/v1/feed/news`).flush([SAMPLE_ITEM]);
      expect(service.items()).toEqual([SAMPLE_ITEM]);
      expect(service.hasError()).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });

  it('keeps the last known-good items and flags an error on failure', () => {
    vi.useFakeTimers();
    try {
      service.start();
      httpMock.expectOne(`${environment.apiUrl}/api/v1/feed/news`).flush([SAMPLE_ITEM]);

      vi.advanceTimersByTime(environment.rotation.pollIntervalMs);

      httpMock
        .expectOne(`${environment.apiUrl}/api/v1/feed/news`)
        .flush('boom', { status: 500, statusText: 'Server Error' });

      expect(service.items()).toEqual([SAMPLE_ITEM]);
      expect(service.hasError()).toBe(true);
    } finally {
      vi.useRealTimers();
    }
  });
});
