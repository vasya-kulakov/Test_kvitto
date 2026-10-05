from fastapi import APIRouter

router = APIRouter()

@router.get("/admin/reset")
def reset_database():
    """
    Endpoint to reset the database.
    This will drop all tables and recreate them.
    """
    from ..database import reset_db
    import asyncio
    # Run the reset_db function in an event loop
    asyncio.run(reset_db(drop_sqlite_file=True))
    
    return {"message": "Database has been reset."}