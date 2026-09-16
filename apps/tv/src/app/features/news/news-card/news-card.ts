import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { TechnologyFeedItem } from '../../../core/api/technology-feed-item.model';

const CATEGORY_LABELS: Record<TechnologyFeedItem['category'], string> = {
  ai: 'IA',
  development: 'Desarrollo',
  cloud: 'Cloud',
  security: 'Seguridad',
  'dev-tooling': 'Herramientas',
  other: 'Otros',
};

@Component({
  selector: 'app-news-card',
  templateUrl: './news-card.html',
  styleUrl: './news-card.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NewsCard {
  readonly item = input.required<TechnologyFeedItem>();

  readonly categoryLabel = computed(() => CATEGORY_LABELS[this.item().category]);
  readonly confidencePercent = computed(() => Math.round(this.item().confidence * 100));
  readonly ageLabel = computed(() => formatAge(this.item().first_seen));
}

function formatAge(isoDate: string): string {
  const ms = Date.now() - new Date(isoDate).getTime();
  const hours = Math.floor(ms / 3_600_000);
  if (hours < 1) return 'hace menos de 1 hora';
  if (hours < 24) return `hace ${hours} h`;
  const days = Math.floor(hours / 24);
  return `hace ${days} d`;
}
