import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

import { environment } from '../../../environments/environment';

/**
 * MVP defers to QlikSense for production data (docs/03-production-pulse-qlik.md,
 * ADR-003) — this component only decides *when* to show the sheet and
 * degrades gracefully when no URL is configured yet (Option A: embed;
 * falls back to the message docs/04-tv-experience.md specifies verbatim
 * when Qlik isn't available).
 */
@Component({
  selector: 'app-production-pulse',
  templateUrl: './production-pulse.html',
  styleUrl: './production-pulse.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProductionPulse {
  private readonly sanitizer = inject(DomSanitizer);

  readonly qlikUrl: SafeResourceUrl | null = environment.qlikUrl
    ? this.sanitizer.bypassSecurityTrustResourceUrl(environment.qlikUrl)
    : null;
}
