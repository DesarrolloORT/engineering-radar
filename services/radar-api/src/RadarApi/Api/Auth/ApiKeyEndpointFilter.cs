using Microsoft.Extensions.Options;
using RadarApi.Application;

namespace RadarApi.Api.Auth;

/// <summary>
/// Protects internal endpoints with a shared-secret bearer token
/// (docs/06-operacion-seguridad.md: "API key almacenada en Key Vault como
/// MVP" — the browser/TV never receives or sends this key).
/// </summary>
public class ApiKeyEndpointFilter(IOptions<RadarOptions> options) : IEndpointFilter
{
    public async ValueTask<object?> InvokeAsync(EndpointFilterInvocationContext context, EndpointFilterDelegate next)
    {
        var configuredKey = options.Value.ApiKey;
        if (string.IsNullOrEmpty(configuredKey))
        {
            return TypedResults.Problem("Internal endpoint is not configured with an API key.", statusCode: StatusCodes.Status500InternalServerError);
        }

        var header = context.HttpContext.Request.Headers.Authorization.ToString();
        if (!header.StartsWith("Bearer ", StringComparison.Ordinal) || header["Bearer ".Length..] != configuredKey)
        {
            return TypedResults.Unauthorized();
        }

        return await next(context);
    }
}
