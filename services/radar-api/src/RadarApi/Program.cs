using Microsoft.EntityFrameworkCore;
using RadarApi.Api.Auth;
using RadarApi.Api.Endpoints;
using RadarApi.Application;
using RadarApi.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();

builder.Services.Configure<RadarOptions>(builder.Configuration.GetSection(RadarOptions.SectionName));
// The API key is a secret and must come from the environment, never appsettings.json.
builder.Services.PostConfigure<RadarOptions>(options =>
    options.ApiKey ??= builder.Configuration["RADAR_API_KEY"] ?? Environment.GetEnvironmentVariable("RADAR_API_KEY"));

builder.Services.AddDbContext<RadarDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("Radar") ?? "Data Source=radar.db"));

builder.Services.AddScoped<NewsFeedService>();
builder.Services.AddScoped<ApiKeyEndpointFilter>();
builder.Services.AddSingleton<IClock, SystemClock>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<RadarDbContext>();
    db.Database.EnsureCreated();
}

app.MapHealthEndpoints();
app.MapNewsSignalsEndpoints();
app.MapFeedEndpoints();

app.Run();

public partial class Program;
