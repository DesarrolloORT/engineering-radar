using System.Text.Json.Serialization;

namespace RadarApi.Api.Contracts;

/// <summary>
/// Wire DTO matching contracts/technology-feed.schema.json field-for-field.
/// Kept separate from Domain.TechnologySignal so the HTTP contract never
/// accidentally drifts when the storage model changes.
/// </summary>
public class TechnologyFeedItemDto
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = "";

    [JsonPropertyName("type")]
    public string Type { get; set; } = "technology";

    [JsonPropertyName("category")]
    public string Category { get; set; } = "";

    [JsonPropertyName("title")]
    public string Title { get; set; } = "";

    [JsonPropertyName("summary")]
    public string Summary { get; set; } = "";

    [JsonPropertyName("why_it_matters")]
    public string WhyItMatters { get; set; } = "";

    [JsonPropertyName("priority")]
    public double Priority { get; set; }

    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }

    [JsonPropertyName("sources_count")]
    public int SourcesCount { get; set; }

    [JsonPropertyName("source_urls")]
    public List<string> SourceUrls { get; set; } = [];

    [JsonPropertyName("first_seen")]
    public DateTimeOffset FirstSeen { get; set; }

    [JsonPropertyName("published_at")]
    public DateTimeOffset PublishedAt { get; set; }

    [JsonPropertyName("expires_at")]
    public DateTimeOffset ExpiresAt { get; set; }

    [JsonPropertyName("impact")]
    public ImpactDto? Impact { get; set; }
}

public class ImpactDto
{
    [JsonPropertyName("status")]
    public string Status { get; set; } = "unknown";

    [JsonPropertyName("repositories")]
    public List<ImpactRepositoryDto> Repositories { get; set; } = [];
}

public class ImpactRepositoryDto
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("reason")]
    public string Reason { get; set; } = "";

    [JsonPropertyName("evidence")]
    public string? Evidence { get; set; }
}
