using ProIn.Backend;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddOpenApi();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddCors(options =>
{
    options.AddPolicy("Frontend", policy =>
    {
        var frontendOrigin = builder.Configuration["Frontend:Origin"] ?? "http://localhost:3000";

        policy.WithOrigins(frontendOrigin)
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});
builder.Services.AddSingleton<WorkerStatusStore>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "ProIn Backend API v1");
    });
}

app.UseCors("Frontend");
app.MapControllers();

app.Run();
