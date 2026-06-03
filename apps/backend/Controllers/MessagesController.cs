namespace ProIn.Backend.Controllers;

using ProIn.Database;

using Microsoft.AspNetCore.Mvc;

[Route("api/messages")]
public sealed class MessagesController(AppDatabase database)
    : DatabaseTableControllerBase(database, DatabaseTables.Messages);
