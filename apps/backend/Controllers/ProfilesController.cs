namespace ProIn.Backend.Controllers;

using Microsoft.AspNetCore.Mvc;

[Route("api/profiles")]
public sealed class ProfilesController(AppDatabase database)
    : DatabaseTableControllerBase(database, DatabaseTables.Profiles);
