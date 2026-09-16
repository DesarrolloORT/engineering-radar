using RadarApi.Api.Auth;
using RadarApi.Api.Contracts;
using RadarApi.Application;

namespace RadarApi.Api.Endpoints;

public static class NewsSignalsEndpoints
{
    public static void MapNewsSignalsEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapPost("/api/v1/internal/news-signals", async (TechnologyFeedItemDto dto, NewsFeedService feedService, CancellationToken ct) =>
        {
            var errors = TechnologyFeedItemMapper.Validate(dto);
            if (errors.Count > 0)
            {
                return Results.ValidationProblem(errors.ToDictionary(e => "body", e => new[] { e }));
            }

            var outcome = await feedService.UpsertAsync(TechnologyFeedItemMapper.ToDomain(dto), ct);
            return Results.Ok(new { id = dto.Id, outcome = outcome.ToString() });
        })
        .AddEndpointFilter<ApiKeyEndpointFilter>()
        .WithName("UpsertNewsSignal");
    }
}
