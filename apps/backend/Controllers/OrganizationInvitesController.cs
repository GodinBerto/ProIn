namespace ProIn.Backend.Controllers;

using Microsoft.AspNetCore.Mvc;

[Route("api/organization-invites")]
public sealed class OrganizationInvitesController(AppDatabase database)
    : DatabaseTableControllerBase(database, DatabaseTables.OrganizationInvites);
