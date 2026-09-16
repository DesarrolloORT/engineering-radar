using System.Net;

namespace RadarApi.Tests;

public class HealthEndpointTests
{
    [Fact]
    public async Task Health_returns_ok_when_database_is_reachable()
    {
        using var factory = new RadarApiFactory();
        var client = factory.CreateClient();

        var response = await client.GetAsync("/api/v1/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }
}
