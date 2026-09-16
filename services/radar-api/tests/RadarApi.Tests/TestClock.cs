using RadarApi.Application;

namespace RadarApi.Tests;

public class TestClock : IClock
{
    public DateTimeOffset UtcNow { get; set; } = new(2026, 1, 1, 0, 0, 0, TimeSpan.Zero);
}
