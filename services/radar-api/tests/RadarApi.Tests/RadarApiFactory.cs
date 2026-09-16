using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using RadarApi.Application;

namespace RadarApi.Tests;

/// <summary>
/// Each instance gets its own SQLite file (so tests never see each other's
/// data) and a controllable clock (so expiration logic can be tested
/// without sleeping).
/// </summary>
public class RadarApiFactory : WebApplicationFactory<Program>
{
    public const string TestApiKey = "test-api-key";
    public readonly TestClock Clock = new();

    private readonly string _dbPath = Path.Combine(Path.GetTempPath(), $"radar-api-tests-{Guid.NewGuid():N}.db");

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureAppConfiguration((_, config) =>
        {
            config.AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["ConnectionStrings:Radar"] = $"Data Source={_dbPath}",
                ["Radar:ApiKey"] = TestApiKey,
                ["Radar:MaxActiveItems"] = "5",
            });
        });

        builder.ConfigureServices(services =>
        {
            services.RemoveAll<IClock>();
            services.AddSingleton<IClock>(Clock);
        });
    }

    protected override void Dispose(bool disposing)
    {
        base.Dispose(disposing);
        try
        {
            File.Delete(_dbPath);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }
}
