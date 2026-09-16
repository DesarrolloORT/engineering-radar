namespace RadarApi.Domain;

/// <summary>
/// The Radar's stored view of a TechnologyFeedItem (contracts/technology-feed.schema.json).
/// One row per signal_id — publishing again upserts this row, it never appends a new one.
/// </summary>
public class TechnologySignal
{
    public required string Id { get; set; }
    public required string Category { get; set; }
    public required string Title { get; set; }
    public required string Summary { get; set; }
    public required string WhyItMatters { get; set; }
    public required double Priority { get; set; }
    public required double Confidence { get; set; }
    public required int SourcesCount { get; set; }
    public List<string> SourceUrls { get; set; } = [];

    // Stored as UTC DateTime rather than DateTimeOffset: SQLite/EF Core cannot
    // translate DateTimeOffset comparisons server-side, only DateTime ones.
    // The contract is UTC-only (ISO 8601 "Z" timestamps), so no offset is lost.
    public required DateTime FirstSeen { get; set; }
    public required DateTime PublishedAt { get; set; }
    public required DateTime ExpiresAt { get; set; }
    public ImpactAssessment? Impact { get; set; }

    public bool IsActive(DateTime utcNow) => ExpiresAt > utcNow;
}

public class ImpactAssessment
{
    public required string Status { get; set; }
    public List<ImpactRepositoryRef> Repositories { get; set; } = [];
}

public class ImpactRepositoryRef
{
    public required string Name { get; set; }
    public required string Reason { get; set; }
    public string? Evidence { get; set; }
}
