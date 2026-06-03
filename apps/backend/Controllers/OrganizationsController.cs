namespace ProIn.Backend.Controllers;

using ProIn.Database;

using Microsoft.AspNetCore.Mvc;

[Route("api/organizations")]
public sealed class OrganizationsController(AppDatabase database)
    : DatabaseTableControllerBase(database, DatabaseTables.Organizations);
