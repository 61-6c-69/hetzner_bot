from tortoise.backends.base.client import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Add user_id to tickets table
        ALTER TABLE "tickets" ADD COLUMN IF NOT EXISTS "user_id" INTEGER;
        UPDATE "tickets" SET "user_id" = (
            SELECT "user_id" FROM "users" 
            WHERE "users"."id" = "tickets"."user_id"
        );
        ALTER TABLE "tickets" ALTER COLUMN "user_id" SET NOT NULL;
        CREATE INDEX "idx_ticket_user_id" ON "tickets" ("user_id");
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_ticket_user_id";
        ALTER TABLE "tickets" DROP COLUMN IF EXISTS "user_id";
    """ 