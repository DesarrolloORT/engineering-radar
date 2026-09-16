using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;

namespace RadarApi.Tests;

public class NewsSignalsEndpointTests
{
    [Fact]
    public async Task Publishing_without_a_key_is_rejected()
    {
        using var factory = new RadarApiFactory();
        var client = factory.CreateClient();

        var response = await client.PostAsJsonAsync("/api/v1/internal/news-signals", TestData.FeedItem());

        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }

    [Fact]
    public async Task Publishing_with_the_wrong_key_is_rejected()
    {
        using var factory = new RadarApiFactory();
        var client = factory.CreateClient();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "wrong-key");

        var response = await client.PostAsJsonAsync("/api/v1/internal/news-signals", TestData.FeedItem());

        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }

    [Fact]
    public async Task Publishing_with_the_correct_key_and_a_valid_payload_succeeds()
    {
        using var factory = new RadarApiFactory();
        var client = factory.CreateClient();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", RadarApiFactory.TestApiKey);

        var response = await client.PostAsJsonAsync("/api/v1/internal/news-signals", TestData.FeedItem());

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }

    [Fact]
    public async Task Invalid_category_is_rejected_with_bad_request()
    {
        using var factory = new RadarApiFactory();
        var client = factory.CreateClient();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", RadarApiFactory.TestApiKey);

        var response = await client.PostAsJsonAsync("/api/v1/internal/news-signals", TestData.FeedItem(category: "not-a-real-category"));

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }
}
