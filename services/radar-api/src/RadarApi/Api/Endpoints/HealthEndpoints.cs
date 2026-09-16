using Microsoft.EntityFrameworkCore;
using RadarApi.Infrastructure;

namespace RadarApi.Api.Endpoints;

public static class HealthEndpoints
{
    public static void MapHealthEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapGet("/api/v1/health", async (RadarDbContext db, CancellationToken ct) =>
        {
            var dbReachable = await db.Database.CanConnectAsync(ct);
            var status = dbReachable ? "ok" : "degraded";
            return Results.Json(new { status, database = dbReachable ? "ok" : "unreachable" },
                statusCode: dbReachable ? StatusCodes.Status200OK : StatusCodes.Status503ServiceUnavailable);
        })
        .WithName("Health");
    }
}
