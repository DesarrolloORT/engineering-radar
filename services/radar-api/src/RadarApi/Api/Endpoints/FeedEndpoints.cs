using RadarApi.Api.Contracts;
using RadarApi.Application;

namespace RadarApi.Api.Endpoints;

public static class FeedEndpoints
{
    public static void MapFeedEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapGet("/api/v1/feed/news", async (NewsFeedService feedService, int? max, CancellationToken ct) =>
        {
            var signals = await feedService.GetActiveFeedAsync(max, ct);
            return Results.Ok(signals.Select(TechnologyFeedItemMapper.ToDto));
        })
        .WithName("GetNewsFeed");
    }
}
