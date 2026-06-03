namespace ProIn.Backend.Controllers;

using ProIn.Database;

using Microsoft.AspNetCore.Mvc;

[Route("api/organization-members")]
public sealed class OrganizationMembersController(AppDatabase database)
    : DatabaseTableControllerBase(database, DatabaseTables.OrganizationMembers);
