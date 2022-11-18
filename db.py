from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Shortcut(Base):
    __tablename__ = "shortcut"
    id = Column(Integer, primary_key=True)
    hotkey = Column(String(255))
    replacement = Column(String)


def init_db():
    engine = create_engine("sqlite:///data.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    current_session = Session()
    return current_session


def add_record(hotkey, replacement):
    session = init_db()
    s = Shortcut(hotkey=hotkey, replacement=replacement)
    row_id = s.id
    session.add(s)
    session.commit()
    session.close()
    return row_id


def remove_record(record_id):
    session = init_db()
    session.query(Shortcut).filter_by(id=record_id).delete()
    session.commit()
    session.close()


def get_records():
    session = init_db()
    return_dict = {}
    for row in session.query(Shortcut).all():
        return_dict[row.id] = {"hotkey": row.hotkey, "replacement": row.replacement}
    session.close()
    return return_dict
