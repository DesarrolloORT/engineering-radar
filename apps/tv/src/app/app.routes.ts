import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'tv',
    loadComponent: () => import('./shell/tv-shell/tv-shell').then(m => m.TvShell),
  },
  {
    path: 'tv/news',
    loadComponent: () => import('./features/news/news-view/news-view').then(m => m.NewsView),
  },
  {
    path: 'tv/production',
    loadComponent: () =>
      import('./features/production/production-view').then(m => m.ProductionView),
  },
  { path: '', redirectTo: 'tv', pathMatch: 'full' },
  { path: '**', redirectTo: 'tv' },
];
