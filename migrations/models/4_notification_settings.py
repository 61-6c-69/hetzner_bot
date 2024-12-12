from tortoise.backends.base.client import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Create notification_settings table
        CREATE TABLE "notification_settings" (
            "id" SERIAL PRIMARY KEY,
            "server_notifications" BOOLEAN NOT NULL DEFAULT TRUE,
            "payment_notifications" BOOLEAN NOT NULL DEFAULT TRUE,
            "ticket_notifications" BOOLEAN NOT NULL DEFAULT TRUE,
            "low_balance_threshold" INTEGER NOT NULL DEFAULT 50000,
            "user_id" INTEGER NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
        );
        
        -- Add user_id to tickets table
        ALTER TABLE "tickets" ADD COLUMN "user_id" INTEGER;
        UPDATE "tickets" SET "user_id" = (SELECT "id" FROM "users" WHERE "users"."id" = "tickets"."user_id");
        ALTER TABLE "tickets" ALTER COLUMN "user_id" SET NOT NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE "notification_settings";
        ALTER TABLE "tickets" DROP COLUMN "user_id";
    """
