from sqlalchemy import Column, Integer, String, Text
from src.database import Base

class Advogado(Base):
    __tablename__ = "advogados"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    especialidade = Column(String, nullable=True)
    oab = Column(String, nullable=True)
    email = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
