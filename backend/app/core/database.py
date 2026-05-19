from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings


async def init_db(app):
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.mongo_client = client

    from app.models.business import Business
    from app.models.appointment import Appointment
    from app.models.customer import Customer
    from app.models.conversation import Conversation
    from app.models.otp_code import OtpCode
    from app.models.staff_member import StaffMember
    from app.models.demo_request import DemoRequest
    from app.models.knowledge import KnowledgeDocument, KnowledgeGap

    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            Business,
            Appointment,
            Customer,
            Conversation,
            OtpCode,
            StaffMember,
            DemoRequest,
            KnowledgeDocument,
            KnowledgeGap,
        ],
    )


async def close_db(app):
    app.state.mongo_client.close()
