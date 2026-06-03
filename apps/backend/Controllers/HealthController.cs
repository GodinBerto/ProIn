namespace ProIn.Backend.Controllers;

using Microsoft.AspNetCore.Mvc;

[Route("api/health")]
public sealed class HealthController : ApiControllerBase
{
    [HttpGet(Name = "GetHealth")]
    public ActionResult<ApiHealthResponse> Get()
    {
        return Ok(new ApiHealthResponse("healthy", DateTimeOffset.UtcNow));
    }
}
