from sqlalchemy import Column, String, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from marketing_agent.services.storage.postgres_storage import Base

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False, default="")
    features = Column(JSON, nullable=False, default=list)
    target_audience = Column(String, nullable=False, default="")
    industry = Column(String, nullable=False, default="")
    logo_url = Column(String, nullable=True)
    image_urls = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
