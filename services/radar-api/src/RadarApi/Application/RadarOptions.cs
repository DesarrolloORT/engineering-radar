namespace RadarApi.Application;

public class RadarOptions
{
    public const string SectionName = "Radar";

    /// <summary>Shared secret the news-intelligence publisher sends as "Authorization: Bearer {ApiKey}". Must come from an env var / secret store, never committed.</summary>
    public string? ApiKey { get; set; }

    /// <summary>Hard cap on how many active signals /feed/news ever returns (docs/09-decisiones.md ADR-007: 3-5 señales).</summary>
    public int MaxActiveItems { get; set; } = 5;
}
