namespace ProIn.Backend.Controllers;

using ProIn.Database;

using Microsoft.AspNetCore.Mvc;

[Route("api/document-shares")]
public sealed class DocumentSharesController(AppDatabase database)
    : DatabaseTableControllerBase(database, DatabaseTables.DocumentShares);
