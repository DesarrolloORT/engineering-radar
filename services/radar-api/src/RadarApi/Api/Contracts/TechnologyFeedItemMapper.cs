using RadarApi.Domain;

namespace RadarApi.Api.Contracts;

public static class TechnologyFeedItemMapper
{
    private static readonly string[] ValidCategories =
        ["ai", "development", "cloud", "security", "dev-tooling", "other"];

    private static readonly string[] ValidImpactStatuses =
        ["confirmed", "potential", "not_affected", "unknown"];

    /// <summary>Returns validation errors; an empty list means the DTO is acceptable.</summary>
    public static List<string> Validate(TechnologyFeedItemDto dto)
    {
        var errors = new List<string>();

        if (string.IsNullOrWhiteSpace(dto.Id)) errors.Add("id is required");
        if (dto.Type != "technology") errors.Add("type must be 'technology'");
        if (!ValidCategories.Contains(dto.Category)) errors.Add($"category must be one of: {string.Join(", ", ValidCategories)}");
        if (string.IsNullOrWhiteSpace(dto.Title)) errors.Add("title is required");
        if (string.IsNullOrWhiteSpace(dto.Summary)) errors.Add("summary is required");
        if (string.IsNullOrWhiteSpace(dto.WhyItMatters)) errors.Add("why_it_matters is required");
        if (dto.Priority is < 0 or > 1) errors.Add("priority must be between 0 and 1");
        if (dto.Confidence is < 0 or > 1) errors.Add("confidence must be between 0 and 1");
        if (dto.SourcesCount < 1) errors.Add("sources_count must be at least 1");
        if (dto.ExpiresAt <= dto.PublishedAt) errors.Add("expires_at must be after published_at");
        if (dto.Impact is not null && !ValidImpactStatuses.Contains(dto.Impact.Status))
            errors.Add($"impact.status must be one of: {string.Join(", ", ValidImpactStatuses)}");

        return errors;
    }

    public static TechnologySignal ToDomain(TechnologyFeedItemDto dto) => new()
    {
        Id = dto.Id,
        Category = dto.Category,
        Title = dto.Title,
        Summary = dto.Summary,
        WhyItMatters = dto.WhyItMatters,
        Priority = dto.Priority,
        Confidence = dto.Confidence,
        SourcesCount = dto.SourcesCount,
        SourceUrls = [.. dto.SourceUrls],
        FirstSeen = dto.FirstSeen.UtcDateTime,
        PublishedAt = dto.PublishedAt.UtcDateTime,
        ExpiresAt = dto.ExpiresAt.UtcDateTime,
        Impact = dto.Impact is null
            ? null
            : new ImpactAssessment
            {
                Status = dto.Impact.Status,
                Repositories =
                [
                    .. dto.Impact.Repositories.Select(r => new ImpactRepositoryRef
                    {
                        Name = r.Name,
                        Reason = r.Reason,
                        Evidence = r.Evidence,
                    }),
                ],
            },
    };

    public static TechnologyFeedItemDto ToDto(TechnologySignal signal) => new()
    {
        Id = signal.Id,
        Type = "technology",
        Category = signal.Category,
        Title = signal.Title,
        Summary = signal.Summary,
        WhyItMatters = signal.WhyItMatters,
        Priority = signal.Priority,
        Confidence = signal.Confidence,
        SourcesCount = signal.SourcesCount,
        SourceUrls = [.. signal.SourceUrls],
        FirstSeen = new DateTimeOffset(signal.FirstSeen, TimeSpan.Zero),
        PublishedAt = new DateTimeOffset(signal.PublishedAt, TimeSpan.Zero),
        ExpiresAt = new DateTimeOffset(signal.ExpiresAt, TimeSpan.Zero),
        Impact = signal.Impact is null
            ? null
            : new ImpactDto
            {
                Status = signal.Impact.Status,
                Repositories =
                [
                    .. signal.Impact.Repositories.Select(r => new ImpactRepositoryDto
                    {
                        Name = r.Name,
                        Reason = r.Reason,
                        Evidence = r.Evidence,
                    }),
                ],
            },
    };
}
