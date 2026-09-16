using System.Net.Http.Headers;
using System.Net.Http.Json;
using RadarApi.Api.Contracts;

namespace RadarApi.Tests;

public class FeedEndpointTests
{
    private static HttpClient AuthedClient(RadarApiFactory factory)
    {
        var client = factory.CreateClient();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", RadarApiFactory.TestApiKey);
        return client;
    }

    [Fact]
    public async Task Re_publishing_the_same_signal_id_upserts_instead_of_duplicating()
    {
        using var factory = new RadarApiFactory();
        var client = AuthedClient(factory);

        await client.PostAsJsonAsync("/api/v1/internal/news-signals", TestData.FeedItem(id: "sig-1", publishedAt: new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero)));
        await client.PostAsJsonAsync("/api/v1/internal/news-signals",
            TestData.FeedItem(id: "sig-1", publishedAt: new DateTimeOffset(2026, 1, 2, 0, 0, 0, TimeSpan.Zero)));

        var feed = await client.GetFromJsonAsync<List<TechnologyFeedItemDto>>("/api/v1/feed/news");

        Assert.NotNull(feed);
        Assert.Single(feed!, i => i.Id == "sig-1");
    }

    [Fact]
    public async Task An_older_republish_does_not_overwrite_a_newer_stored_signal()
    {
        using var factory = new RadarApiFactory();
        var client = AuthedClient(factory);

        await client.PostAsJsonAsync("/api/v1/internal/news-signals",
            TestData.FeedItem(id: "sig-1", publishedAt: new DateTimeOffset(2026, 1, 5, 0, 0, 0, TimeSpan.Zero)));
        var staleResponse = await client.PostAsJsonAsync("/api/v1/internal/news-signals",
            TestData.FeedItem(id: "sig-1", publishedAt: new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero)));

        var body = await staleResponse.Content.ReadFromJsonAsync<Dictionary<string, string>>();
        Assert.Equal("IgnoredStale", body!["outcome"]);

        var feed = await client.GetFromJsonAsync<List<TechnologyFeedItemDto>>("/api/v1/feed/news");
        var stored = feed!.Single(i => i.Id == "sig-1");
        Assert.Equal(new DateTimeOffset(2026, 1, 5, 0, 0, 0, TimeSpan.Zero), stored.PublishedAt);
    }

    [Fact]
    public async Task Expired_signals_are_excluded_from_the_feed()
    {
        using var factory = new RadarApiFactory();
        var client = AuthedClient(factory);
        var published = new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero);

        await client.PostAsJsonAsync("/api/v1/internal/news-signals",
            TestData.FeedItem(id: "sig-1", publishedAt: published, expiresAt: published.AddHours(48)));

        factory.Clock.UtcNow = published.AddHours(49);

        var feed = await client.GetFromJsonAsync<List<TechnologyFeedItemDto>>("/api/v1/feed/news");

        Assert.DoesNotContain(feed!, i => i.Id == "sig-1");
    }

    [Fact]
    public async Task Feed_never_returns_more_than_the_configured_max_even_if_more_are_active()
    {
        using var factory = new RadarApiFactory();
        var client = AuthedClient(factory);
        var published = new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero);

        for (var i = 0; i < 8; i++)
        {
            await client.PostAsJsonAsync("/api/v1/internal/news-signals",
                TestData.FeedItem(id: $"sig-{i}", priority: 0.1 * i, publishedAt: published));
        }

        var feed = await client.GetFromJsonAsync<List<TechnologyFeedItemDto>>("/api/v1/feed/news");

        Assert.Equal(5, feed!.Count); // configured Radar:MaxActiveItems in RadarApiFactory
        Assert.Equal("sig-7", feed[0].Id); // highest priority first
    }
}
