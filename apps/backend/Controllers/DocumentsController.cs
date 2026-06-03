namespace ProIn.Backend.Controllers;

using Microsoft.AspNetCore.Mvc;

[Route("api/documents")]
public sealed class DocumentsController(AppDatabase database)
    : DatabaseTableControllerBase(database, DatabaseTables.Documents);
