/**
 * Mirrors contracts/technology-feed.schema.json field-for-field (snake_case
 * kept on purpose — this is the wire contract, not an internal model).
 */
export interface TechnologyFeedItem {
  id: string;
  type: 'technology';
  category: 'ai' | 'development' | 'cloud' | 'security' | 'dev-tooling' | 'other';
  title: string;
  summary: string;
  why_it_matters: string;
  priority: number;
  confidence: number;
  sources_count: number;
  source_urls: string[];
  first_seen: string;
  published_at: string;
  expires_at: string;
  impact: ImpactAssessment | null;
}

export interface ImpactAssessment {
  status: 'confirmed' | 'potential' | 'not_affected' | 'unknown';
  repositories: { name: string; reason: string; evidence: string | null }[];
}
