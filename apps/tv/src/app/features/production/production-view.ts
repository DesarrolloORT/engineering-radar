import { ChangeDetectionStrategy, Component } from '@angular/core';

import { ProductionPulse } from './production-pulse';

/** Standalone /tv/production route for the kiosk-URL rotation fallback (docs/03). */
@Component({
  selector: 'app-production-view',
  imports: [ProductionPulse],
  template: `
    <main class="production-view">
      <app-production-pulse />
    </main>
  `,
  styles: `
    .production-view {
      height: 100vh;
      width: 100vw;
      overflow: hidden;
      background: var(--tv-bg);
      color: var(--tv-fg);
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProductionView {}
