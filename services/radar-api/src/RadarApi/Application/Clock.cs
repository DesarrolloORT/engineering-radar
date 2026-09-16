namespace RadarApi.Application;

/// <summary>Testable indirection over "now" — expiration/health checks must not depend on wall-clock time in tests.</summary>
public interface IClock
{
    DateTimeOffset UtcNow { get; }
}

public class SystemClock : IClock
{
    public DateTimeOffset UtcNow => DateTimeOffset.UtcNow;
}
