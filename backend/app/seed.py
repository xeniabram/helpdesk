from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ticket, TicketStatus

SEED_TICKETS = [
    {
        "title": "Login page returns 500 error",
        "description": "Users are reporting a 500 Internal Server Error when trying to log in. The issue started after the latest deployment on Friday. The error occurs for all users regardless of browser. Server logs show a database connection timeout. The connection pool seems to be exhausted during peak hours.",
        "status": TicketStatus.open,
    },
    {
        "title": "Update user profile avatar",
        "description": "Users want the ability to upload and change their profile avatar. Currently the system only shows a default placeholder. We need to support JPEG and PNG uploads up to 5MB, with automatic resizing to 200x200. The avatar should appear in the navbar and on the profile page.",
        "status": TicketStatus.open,
    },
    {
        "title": "CSV export includes deleted records",
        "description": "When exporting the transactions report as CSV, deleted (soft-deleted) records are included in the output. The export query is missing a WHERE deleted_at IS NULL filter. This affects compliance reporting and several clients have raised concerns about incorrect totals in their monthly statements.",
        "status": TicketStatus.in_progress,
    },
    {
        "title": "Migrate email service to SendGrid",
        "description": "Our current email provider is being deprecated. We need to migrate all transactional emails (welcome, password reset, notifications) to SendGrid. API keys have been provisioned. The templates need to be recreated in SendGrid's template engine. Estimated 15 email templates to migrate.",
        "status": TicketStatus.in_progress,
    },
    {
        "title": "Search results not returning recent items",
        "description": "The search index appears to be stale. Items added in the last 48 hours do not appear in search results. The Elasticsearch reindex cron job has been failing silently since Tuesday. The disk on the search node is at 95% capacity which is preventing new index writes.",
        "status": TicketStatus.open,
    },
    {
        "title": "Add two-factor authentication",
        "description": "Implement TOTP-based two-factor authentication for user accounts. Users should be able to enable 2FA from security settings, scan a QR code with their authenticator app, and enter a verification code on login. Backup codes should be generated for account recovery. Admin users should have 2FA enforced.",
        "status": TicketStatus.open,
    },
    {
        "title": "Fix timezone display in dashboard",
        "description": "All timestamps in the analytics dashboard are displayed in UTC regardless of the user's local timezone setting. The issue is in the frontend date formatting - the API correctly returns ISO 8601 timestamps with timezone info but the chart library strips it. Affects all date-based charts and tables.",
        "status": TicketStatus.resolved,
    },
    {
        "title": "Optimize slow product listing query",
        "description": "The /api/products endpoint takes over 3 seconds to respond when filtering by category with more than 10,000 products. The query is doing a sequential scan instead of using the category index. Adding EXPLAIN ANALYZE shows the planner choosing a seq scan due to outdated table statistics. Need to run ANALYZE and consider a composite index on (category_id, created_at).",
        "status": TicketStatus.resolved,
    },
]


async def seed_tickets(session: AsyncSession) -> int:
    stmt = (
        insert(Ticket)
        .values(SEED_TICKETS)
        .on_conflict_do_nothing(index_elements=["title"])
        .returning(Ticket.id)
    )
    result = await session.execute(stmt)
    return len(result.all())
