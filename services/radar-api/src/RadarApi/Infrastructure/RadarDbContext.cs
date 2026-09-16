using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using RadarApi.Domain;

namespace RadarApi.Infrastructure;

public class RadarDbContext(DbContextOptions<RadarDbContext> options) : DbContext(options)
{
    public DbSet<TechnologySignal> TechnologySignals => Set<TechnologySignal>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<TechnologySignal>(entity =>
        {
            entity.HasKey(s => s.Id);

            entity.Property(s => s.SourceUrls)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, JsonOptions),
                    v => JsonSerializer.Deserialize<List<string>>(v, JsonOptions) ?? new List<string>())
                .Metadata.SetValueComparer(ListStringComparer);

            entity.Property(s => s.Impact)
                .HasConversion(
                    v => v == null ? null : JsonSerializer.Serialize(v, JsonOptions),
                    v => v == null ? null : JsonSerializer.Deserialize<ImpactAssessment>(v, JsonOptions));
        });
    }

    private static readonly JsonSerializerOptions JsonOptions = new();

    private static readonly Microsoft.EntityFrameworkCore.ChangeTracking.ValueComparer<List<string>> ListStringComparer =
        new(
            (a, b) => (a ?? new List<string>()).SequenceEqual(b ?? new List<string>()),
            v => v.Aggregate(0, (hash, item) => HashCode.Combine(hash, item.GetHashCode())),
            v => v.ToList());
}
