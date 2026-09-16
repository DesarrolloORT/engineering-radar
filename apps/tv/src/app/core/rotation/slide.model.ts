import { TechnologyFeedItem } from '../api/technology-feed-item.model';

export type Slide =
  | { kind: 'news'; item: TechnologyFeedItem; durationMs: number }
  | { kind: 'empty-news'; durationMs: number }
  | { kind: 'production'; durationMs: number };

export interface RotationConfig {
  newsDurationMs: number;
  productionDurationMs: number;
}
