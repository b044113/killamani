"""
Seed Data Script

Creates initial data for the AstroJoy platform:
- Admin user
- Sample consultant user
- Sample client
"""
import sys
from pathlib import Path

# Add backend src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from uuid import uuid4

from src.infrastructure.database.connection import get_db_context
from src.infrastructure.database.models import UserModel, ClientModel
from src.domain.entities.user import UserRole
from src.application.services.password_service import PasswordService

password_service = PasswordService()


def create_admin_user(db):
    """Create initial admin user."""
    # Check if admin already exists
    existing_admin = db.query(UserModel).filter(
        UserModel.email == "admin@astrojoy.com"
    ).first()

    if existing_admin:
        print("[OK] Admin user already exists")
        return existing_admin

    # Create admin user
    admin = UserModel(
        id=uuid4(),
        email="admin@astrojoy.com",
        hashed_password=password_service.hash_password("Admin123!"),
        role=UserRole.ADMIN,
        is_active=True,
        is_first_login=False,
        preferred_language="en",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(admin)
    db.flush()
    print(f"[OK] Created admin user: {admin.email}")
    return admin


def create_consultant_user(db):
    """Create sample consultant user."""
    # Check if consultant already exists
    existing_consultant = db.query(UserModel).filter(
        UserModel.email == "consultant@astrojoy.com"
    ).first()

    if existing_consultant:
        print("[OK] Consultant user already exists")
        return existing_consultant

    # Create consultant user
    consultant = UserModel(
        id=uuid4(),
        email="consultant@astrojoy.com",
        hashed_password=password_service.hash_password("Consultant123!"),
        role=UserRole.CONSULTANT,
        is_active=True,
        is_first_login=False,
        preferred_language="en",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(consultant)
    db.flush()
    print(f"[OK] Created consultant user: {consultant.email}")
    return consultant


def create_sample_client(db, consultant_id):
    """Create sample client."""
    # Check if client already exists
    existing_client = db.query(ClientModel).filter(
        ClientModel.email == "client@example.com"
    ).first()

    if existing_client:
        print("[OK] Sample client already exists")
        return existing_client

    # Create sample client
    client = ClientModel(
        id=uuid4(),
        consultant_id=consultant_id,
        user_id=None,
        first_name="John",
        last_name="Doe",
        email="client@example.com",
        birth_date=datetime(1990, 5, 15, 14, 30),
        birth_city="Buenos Aires",
        birth_country="AR",
        birth_timezone="America/Argentina/Buenos_Aires",
        birth_latitude=-34.6037,
        birth_longitude=-58.3816,
        notes="Sample client for testing",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(client)
    db.flush()
    print(f"[OK] Created sample client: {client.first_name} {client.last_name}")
    return client


def main():
    """Run seed data script."""
    print("Starting seed data script...")
    print("-" * 50)

    try:
        with get_db_context() as db:
            # Create users
            admin = create_admin_user(db)
            consultant = create_consultant_user(db)

            # Create sample client
            client = create_sample_client(db, consultant.id)

            # Commit all changes
            db.commit()

        print("-" * 50)
        print("Seed data created successfully!")
        print("\nCreated accounts:")
        print(f"   Admin:      admin@astrojoy.com / Admin123!")
        print(f"   Consultant: consultant@astrojoy.com / Consultant123!")
        print(f"   Client:     {client.first_name} {client.last_name}")

    except Exception as e:
        print(f"\nError creating seed data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
