import asyncio
import typer
from tortoise import Tortoise, run_async
from aerich import Command
from config import TORTOISE_ORM

app = typer.Typer()


@app.command()
def init_db():
    """Initialize database and create tables"""

    async def run():
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await Tortoise.close_connections()

    run_async(run())
    typer.echo("Database initialized successfully!")


@app.command()
def migrate():
    """Run migrations"""

    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, app="models")
        await command.init()
        await command.migrate()
        await command.upgrade()

    run_async(run())
    typer.echo("Migrations completed successfully!")


@app.command()
def makemigrations(message: str = ""):
    """Create new migration"""

    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, app="models")
        await command.init()
        await command.migrate(message)

    run_async(run())
    typer.echo("New migration created successfully!")


@app.command()
def upgrade():
    """Upgrade to latest migration"""

    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, app="models")
        await command.init()
        await command.upgrade()

    run_async(run())
    typer.echo("Database upgraded successfully!")


@app.command()
def downgrade():
    """Downgrade to previous migration"""

    async def run():
        command = Command(tortoise_config=TORTOISE_ORM, app="models")
        await command.init()
        await command.downgrade()

    run_async(run())
    typer.echo("Database downgraded successfully!")


if __name__ == "__main__":
    app()
