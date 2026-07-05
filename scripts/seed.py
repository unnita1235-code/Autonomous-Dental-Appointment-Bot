import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionFactory
from app.models.appointment import AppointmentSourceChannel, AppointmentStatus
from app.models.dentist import Dentist
from app.models.patient import Patient
from app.models.service import Service
from app.models.staff_user import StaffUser, StaffRole
from app.models.time_slot import TimeSlot


async def seed_services(db: AsyncSession) -> None:
    """Seed dental services."""
    services_data = [
        {
            "name": "Dental Cleaning",
            "duration_minutes": 30,
            "price": Decimal("75.00"),
            "description": "Professional teeth cleaning and polishing",
            "requires_dentist_specialization": None,
        },
        {
            "name": "Teeth Whitening",
            "duration_minutes": 60,
            "price": Decimal("199.00"),
            "description": "Professional teeth whitening treatment",
            "requires_dentist_specialization": "Cosmetic Dentistry",
        },
        {
            "name": "Composite Filling",
            "duration_minutes": 45,
            "price": Decimal("150.00"),
            "description": "Tooth-colored filling for cavities",
            "requires_dentist_specialization": "General Dentistry",
        },
        {
            "name": "Root Canal",
            "duration_minutes": 90,
            "price": Decimal("450.00"),
            "description": "Root canal therapy for infected teeth",
            "requires_dentist_specialization": "Endodontics",
        },
        {
            "name": "Dental Crown",
            "duration_minutes": 60,
            "price": Decimal("800.00"),
            "description": "Porcelain crown placement",
            "requires_dentist_specialization": "Prosthodontics",
        },
        {
            "name": "Dental Extraction",
            "duration_minutes": 30,
            "price": Decimal("120.00"),
            "description": "Simple tooth extraction",
            "requires_dentist_specialization": "Oral Surgery",
        },
        {
            "name": "Orthodontic Consultation",
            "duration_minutes": 30,
            "price": Decimal("100.00"),
            "description": "Initial braces or Invisalign consultation",
            "requires_dentist_specialization": "Orthodontics",
        },
        {
            "name": "Dental Implant Consultation",
            "duration_minutes": 45,
            "price": Decimal("150.00"),
            "description": "Consultation for dental implant placement",
            "requires_dentist_specialization": "Oral Surgery",
        },
    ]

    for service_data in services_data:
        result = await db.execute(select(Service).where(Service.name == service_data["name"]))
        if result.scalar_one_or_none() is None:
            service = Service(**service_data)
            db.add(service)
            print(f"Created service: {service_data['name']}")

    await db.commit()
    print("✓ Services seeded successfully")


async def seed_dentists(db: AsyncSession) -> None:
    """Seed dentist accounts."""
    dentists_data = [
        {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah.johnson@clinic.com",
            "phone": "+15551234567",
            "specializations": ["General Dentistry", "Cosmetic Dentistry"],
            "bio": "Dr. Johnson has over 15 years of experience in general and cosmetic dentistry.",
            "calendar_id": "sarah.johnson@clinic.com",
        },
        {
            "first_name": "Michael",
            "last_name": "Chen",
            "email": "michael.chen@clinic.com",
            "phone": "+15551234568",
            "specializations": ["Endodontics", "Oral Surgery"],
            "bio": "Dr. Chen specializes in root canals and oral surgery procedures.",
            "calendar_id": "michael.chen@clinic.com",
        },
        {
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "email": "emily.rodriguez@clinic.com",
            "phone": "+15551234569",
            "specializations": ["Orthodontics", "Pediatric Dentistry"],
            "bio": "Dr. Rodriguez focuses on orthodontics and pediatric dental care.",
            "calendar_id": "emily.rodriguez@clinic.com",
        },
    ]

    for dentist_data in dentists_data:
        result = await db.execute(select(Dentist).where(Dentist.email == dentist_data["email"]))
        if result.scalar_one_or_none() is None:
            dentist = Dentist(**dentist_data)
            db.add(dentist)
            print(f"Created dentist: {dentist_data['first_name']} {dentist_data['last_name']}")

    await db.commit()
    print("✓ Dentists seeded successfully")


async def seed_staff(db: AsyncSession) -> None:
    """Seed staff user accounts."""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    staff_data = [
        {
            "email": "admin@clinic.com",
            "hashed_password": pwd_context.hash("admin123"),
            "first_name": "Admin",
            "last_name": "User",
            "role": StaffRole.MANAGER,
        },
        {
            "email": "receptionist@clinic.com",
            "hashed_password": pwd_context.hash("reception123"),
            "first_name": "Jane",
            "last_name": "Smith",
            "role": StaffRole.RECEPTIONIST,
        },
        {
            "email": "dentist_view@clinic.com",
            "hashed_password": pwd_context.hash("dentist123"),
            "first_name": "Dr",
            "last_name": "View",
            "role": StaffRole.DENTIST_VIEW,
        },
    ]

    for staff_member in staff_data:
        result = await db.execute(select(StaffUser).where(StaffUser.email == staff_member["email"]))
        if result.scalar_one_or_none() is None:
            staff = StaffUser(**staff_member)
            db.add(staff)
            print(f"Created staff: {staff_member['email']}")

    await db.commit()
    print("✓ Staff accounts seeded successfully")


async def seed_patients(db: AsyncSession) -> None:
    """Seed sample patient accounts for testing."""
    patients_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+15559876543",
            "date_of_birth": datetime(1985, 5, 15).date(),
            "gender": "Male",
            "insurance_provider": "Delta Dental",
            "insurance_member_id": "DD123456789",
            "is_returning": True,
            "no_show_count": 0,
            "requires_deposit": False,
            "channel_preference": "web",
            "notes": "Prefers morning appointments",
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "+15559876544",
            "date_of_birth": datetime(1990, 8, 22).date(),
            "gender": "Female",
            "insurance_provider": "Aetna",
            "insurance_member_id": "AE987654321",
            "is_returning": False,
            "no_show_count": 1,
            "requires_deposit": False,
            "channel_preference": "whatsapp",
            "notes": "New patient",
        },
        {
            "first_name": "Robert",
            "last_name": "Williams",
            "email": "robert.williams@example.com",
            "phone": "+15559876545",
            "date_of_birth": datetime(1978, 3, 10).date(),
            "gender": "Male",
            "insurance_provider": "Cigna",
            "insurance_member_id": "CG456789123",
            "is_returning": True,
            "no_show_count": 2,
            "requires_deposit": True,
            "channel_preference": "sms",
            "notes": "Requires deposit due to previous no-shows",
        },
    ]

    for patient_data in patients_data:
        result = await db.execute(select(Patient).where(Patient.email == patient_data["email"]))
        if result.scalar_one_or_none() is None:
            patient = Patient(**patient_data)
            db.add(patient)
            print(f"Created patient: {patient_data['first_name']} {patient_data['last_name']}")

    await db.commit()
    print("✓ Patients seeded successfully")


async def seed_time_slots(db: AsyncSession) -> None:
    """Seed time slots for the next 30 days."""
    # Get all active dentists and services
    dentists_result = await db.execute(select(Dentist).where(Dentist.is_active == True))
    dentists = dentists_result.scalars().all()

    services_result = await db.execute(select(Service).where(Service.is_active == True))
    services = services_result.scalars().all()

    if not dentists or not services:
        print("⚠ No dentists or services found, skipping time slot creation")
        return

    # Create slots for next 30 days
    start_date = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=30)

    current_date = start_date
    slots_created = 0

    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            for dentist in dentists:
                # Create slots from 9 AM to 5 PM with 30-minute intervals
                slot_time = current_date.replace(hour=9, minute=0)
                while slot_time.hour < 17:
                    # Check if slot already exists
                    existing = await db.execute(
                        select(TimeSlot).where(
                            TimeSlot.dentist_id == dentist.id,
                            TimeSlot.start_time == slot_time,
                        )
                    )
                    if existing.scalar_one_or_none() is None:
                        slot = TimeSlot(
                            dentist_id=dentist.id,
                            start_time=slot_time,
                            end_time=slot_time + timedelta(minutes=30),
                            is_available=True,
                        )
                        db.add(slot)
                        slots_created += 1
                    slot_time += timedelta(minutes=30)

        current_date += timedelta(days=1)

    await db.commit()
    print(f"✓ Time slots seeded successfully ({slots_created} slots created)")


async def seed() -> None:
    """Main seed function."""
    print("Starting database seeding...")
    print("=" * 50)

    async with AsyncSessionFactory() as db:
        await seed_services(db)
        await seed_dentists(db)
        await seed_staff(db)
        await seed_patients(db)
        await seed_time_slots(db)

    print("=" * 50)
    print("✅ Database seeding completed successfully!")
    print("\nDefault credentials:")
    print("  Admin: admin@clinic.com / admin123")
    print("  Receptionist: receptionist@clinic.com / reception123")
    print("  Dentist View: dentist_view@clinic.com / dentist123")


if __name__ == "__main__":
    asyncio.run(seed())
