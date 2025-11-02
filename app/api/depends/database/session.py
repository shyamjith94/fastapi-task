from typing import Generator
from app.core import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from app.logs import logger

class Database:
    def __init__(self,check_connection: bool=False):
        self._create_engine = create_engine(
            str(settings.SQLALCHEMY_DATABASE_URI),
            echo=settings.DATABASE_ECHO,
            future=True,
            
        )
        
        self._local_session =  sessionmaker(
           autoflush=False,
           autocommit=False,
           bind=self._create_engine,
           class_=Session,
           future=True
       )
        
        if check_connection:
            self._test_connection_once()

    def _test_connection_once(self):
        """Run once at initialization to confirm DB connectivity."""
        try:
            current_db = ""
            with self._create_engine.connect() as conn:
                current_db = conn.execute(text("SELECT current_database();")).scalar()
            logger.info(f"Database connection successful! Connected to: {current_db}")
        except OperationalError as e:
            logger.error(f"Database connection failed - could not connect: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed - SQLAlchemy error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database connection failed - unexpected error: {str(e)}")
            raise

    def get_db(self,)->Generator[Session,None, None]:
        db = self._local_session()
        try:
            yield db
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            db.rollback()
            raise
        except OperationalError as e:
            logger.error(f"Database operational error: {str(e)}")
            db.rollback()
            raise
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error: {str(e)}")
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected database error: {str(e)}")
            db.rollback()
            raise
        finally:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
                
        
    
