namespace ProIn.Backend;

using Npgsql;

public sealed class AppDatabase(IConfiguration configuration)
{
    public bool IsConfigured => !string.IsNullOrWhiteSpace(GetConnectionString());

    public async Task<NpgsqlConnection> OpenConnectionAsync(CancellationToken cancellationToken)
    {
        var connectionString = GetConnectionString();

        if (string.IsNullOrWhiteSpace(connectionString))
        {
            throw new InvalidOperationException(
                "Set ConnectionStrings:DefaultConnection or DATABASE_URL for the Supabase Postgres connection.");
        }

        var connection = new NpgsqlConnection(connectionString);
        await connection.OpenAsync(cancellationToken);

        return connection;
    }

    private string? GetConnectionString()
    {
        return configuration.GetConnectionString("DefaultConnection")
            ?? configuration["DATABASE_URL"];
    }
}
