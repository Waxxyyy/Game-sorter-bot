# support_db.py
from sqlalchemy import Column, Integer, Text, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()


class SupportTicket(Base):
    __tablename__ = 'support_tickets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    issue_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine('sqlite:///support_tickets.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def add_support_ticket(user_id, issue_description):
    ticket = SupportTicket(user_id=user_id, issue_description=issue_description)
    session.add(ticket)
    session.commit()


def get_user_support_tickets(user_id):
    tickets = session.query(SupportTicket).filter_by(user_id=user_id).all()
    return tickets
