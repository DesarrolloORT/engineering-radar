namespace RadarApi.Tests;

public static class TestData
{
    public static object FeedItem(
        string id = "sig-test-1",
        string category = "development",
        double priority = 0.7,
        DateTimeOffset? publishedAt = null,
        DateTimeOffset? expiresAt = null)
    {
        var published = publishedAt ?? new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero);
        var expires = expiresAt ?? published.AddHours(48);

        return new
        {
            id,
            type = "technology",
            category,
            title = "Sample signal",
            summary = "Sample summary",
            why_it_matters = "Sample why it matters",
            priority,
            confidence = 0.8,
            sources_count = 2,
            source_urls = new[] { "https://example.org/1", "https://example.org/2" },
            first_seen = published.AddHours(-1),
            published_at = published,
            expires_at = expires,
            impact = (object?)null,
        };
    }
}
