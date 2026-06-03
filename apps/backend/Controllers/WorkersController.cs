namespace ProIn.Backend.Controllers;

using Microsoft.AspNetCore.Mvc;

[Route("api/workers")]
public sealed class WorkersController(WorkerStatusStore store) : ApiControllerBase
{
    [HttpGet("status", Name = "GetWorkerStatus")]
    public ActionResult<WorkerStatusResponse> GetStatus()
    {
        return Ok(store.GetSnapshot());
    }

    [HttpPost("heartbeat", Name = "RecordWorkerHeartbeat")]
    public IActionResult RecordHeartbeat([FromBody] WorkerHeartbeatRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.WorkerName))
        {
            return BadRequest(new { message = "workerName is required." });
        }

        store.RecordHeartbeat(request.WorkerName);
        return Accepted();
    }
}
