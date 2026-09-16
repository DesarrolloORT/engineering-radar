import { provideZonelessChangeDetection } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { TechnologyFeedItem } from '../../../core/api/technology-feed-item.model';
import { NewsCard } from './news-card';

const ITEM: TechnologyFeedItem = {
  id: 'sig-1',
  type: 'technology',
  category: 'security',
  title: 'Título de prueba',
  summary: 'Resumen de prueba',
  why_it_matters: 'Importa porque sí',
  priority: 0.9,
  confidence: 0.87,
  sources_count: 3,
  source_urls: [],
  first_seen: new Date(Date.now() - 2 * 3_600_000).toISOString(),
  published_at: new Date().toISOString(),
  expires_at: new Date().toISOString(),
  impact: null,
};

describe('NewsCard', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideZonelessChangeDetection()],
    });
  });

  it('renders the category label, title, summary and why-it-matters text', async () => {
    const fixture = TestBed.createComponent(NewsCard);
    fixture.componentRef.setInput('item', ITEM);
    await fixture.whenStable();

    const text = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(text).toContain('Seguridad');
    expect(text).toContain('Título de prueba');
    expect(text).toContain('Resumen de prueba');
    expect(text).toContain('Importa porque sí');
    expect(text).toContain('87%');
    expect(text).toContain('3 fuentes');
  });

  it('formats the age of a two-hour-old signal', async () => {
    const fixture = TestBed.createComponent(NewsCard);
    fixture.componentRef.setInput('item', ITEM);
    await fixture.whenStable();

    expect((fixture.nativeElement as HTMLElement).textContent).toContain('hace 2 h');
  });
});
