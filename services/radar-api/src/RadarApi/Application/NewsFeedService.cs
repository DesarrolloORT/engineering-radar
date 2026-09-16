using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using RadarApi.Domain;
using RadarApi.Infrastructure;

namespace RadarApi.Application;

public enum UpsertOutcome
{
    Created,
    Updated,
    IgnoredStale,
}

public class NewsFeedService(RadarDbContext db, IClock clock, IOptions<RadarOptions> options, ILogger<NewsFeedService> logger)
{
    private readonly RadarOptions _options = options.Value;

    /// <summary>
    /// Upsert by signal id. Newer publish wins (docs/02-news-radar.md: "PUT/UPSERT semantics
    /// ... newer generated_at wins") — re-publishing the same or an older snapshot is a no-op,
    /// so a retried/duplicated publish never regresses the stored signal.
    /// </summary>
    public async Task<UpsertOutcome> UpsertAsync(TechnologySignal incoming, CancellationToken ct = default)
    {
        var existing = await db.TechnologySignals.FindAsync([incoming.Id], ct);

        if (existing is null)
        {
            db.TechnologySignals.Add(incoming);
            await db.SaveChangesAsync(ct);
            logger.LogInformation("Published new signal {SignalId} (category={Category})", incoming.Id, incoming.Category);
            return UpsertOutcome.Created;
        }

        if (incoming.PublishedAt < existing.PublishedAt)
        {
            logger.LogInformation(
                "Ignored stale publish for {SignalId}: incoming published_at={IncomingPublishedAt} older than stored {StoredPublishedAt}",
                incoming.Id, incoming.PublishedAt, existing.PublishedAt);
            return UpsertOutcome.IgnoredStale;
        }

        existing.Category = incoming.Category;
        existing.Title = incoming.Title;
        existing.Summary = incoming.Summary;
        existing.WhyItMatters = incoming.WhyItMatters;
        existing.Priority = incoming.Priority;
        existing.Confidence = incoming.Confidence;
        existing.SourcesCount = incoming.SourcesCount;
        existing.SourceUrls = incoming.SourceUrls;
        existing.FirstSeen = incoming.FirstSeen;
        existing.PublishedAt = incoming.PublishedAt;
        existing.ExpiresAt = incoming.ExpiresAt;
        existing.Impact = incoming.Impact;

        await db.SaveChangesAsync(ct);
        logger.LogInformation("Updated existing signal {SignalId} (category={Category})", incoming.Id, incoming.Category);
        return UpsertOutcome.Updated;
    }

    /// <summary>Active, non-expired signals ordered by priority, capped at the configured max regardless of what the caller asks for.</summary>
    public async Task<List<TechnologySignal>> GetActiveFeedAsync(int? requestedMax, CancellationToken ct = default)
    {
        var now = clock.UtcNow.UtcDateTime;
        var max = Math.Clamp(requestedMax ?? _options.MaxActiveItems, 1, _options.MaxActiveItems);

        return await db.TechnologySignals
            .Where(s => s.ExpiresAt > now)
            .OrderByDescending(s => s.Priority)
            .ThenBy(s => s.FirstSeen)
            .Take(max)
            .ToListAsync(ct);
    }
}
