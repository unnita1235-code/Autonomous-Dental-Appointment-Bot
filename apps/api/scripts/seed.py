from __future__ import annotations

import asyncio
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import AsyncSessionFactory
from app.models.dentist import Dentist
from app.models.patient import ChannelPreference, Patient
from app.models.service import Service
from app.models.staff_user import StaffRole, StaffUser
from app.models.time_slot import TimeSlot

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def generate_time_slots(start_day: date, days: int) -> list[tuple[datetime, datetime]]:
    slots: list[tuple[datetime, datetime]] = []
    for day_offset in range(days):
        current_date = start_day + timedelta(days=day_offset)
        if current_date.weekday() > 4:
            continue

        slot_start = datetime.combine(current_date, time(hour=9, minute=0), tzinfo=timezone.utc)
        slot_end_boundary = datetime.combine(current_date, time(hour=17, minute=0), tzinfo=timezone.utc)
        while slot_start < slot_end_boundary:
            slot_end = slot_start + timedelta(minutes=30)
            slots.append((slot_start, slot_end))
            slot_start = slot_end
    return slots


async def seed() -> None:
    async with AsyncSessionFactory() as session:
        try:
            existing_dentist = await session.scalar(select(Dentist.id).limit(1))
            if existing_dentist is not None:
                print("Seed data already exists; skipping.")
                return

            dentists = [
                Dentist(
                    first_name="Ava",
                    last_name="Sharma",
                    email="ava.sharma@clinic.example",
                    phone="+15551000001",
                    specializations=["general", "cosmetic"],
                    bio="Experienced in cosmetic smile redesigns and preventive care.",
                    calendar_id="ava.sharma@clinic-calendar.local",
                ),
                Dentist(
                    first_name="Liam",
                    last_name="Patel",
                    email="liam.patel@clinic.example",
                    phone="+15551000002",
                    specializations=["orthodontics", "general"],
                    bio="Focuses on braces, aligners, and long-term bite correction.",
                    calendar_id="liam.patel@clinic-calendar.local",
                ),
                Dentist(
                    first_name="Mia",
                    last_name="Rao",
                    email="mia.rao@clinic.example",
                    phone="+15551000003",
                    specializations=["endodontics", "surgery"],
                    bio="Specialist in root canal care and complex restorative procedures.",
                    calendar_id="mia.rao@clinic-calendar.local",
                ),
            ]
            session.add_all(dentists)
            await session.flush()

            services = [
                Service(name="Dental Cleaning", duration_minutes=30, price=Decimal("80.00"), description="Routine cleaning and plaque removal."),
                Service(name="Comprehensive Checkup", duration_minutes=30, price=Decimal("60.00"), description="Consultation, oral exam, and treatment plan."),
                Service(name="Teeth Whitening", duration_minutes=60, price=Decimal("220.00"), description="In-clinic cosmetic whitening treatment.", requires_dentist_specialization="cosmetic"),
                Service(name="Root Canal Therapy", duration_minutes=90, price=Decimal("650.00"), description="Root canal procedure for infected teeth.", requires_dentist_specialization="endodontics"),
                Service(name="Orthodontic Consultation", duration_minutes=45, price=Decimal("120.00"), description="Braces/aligner assessment and planning.", requires_dentist_specialization="orthodontics"),
            ]
            session.add_all(services)
            await session.flush()

            services_by_name = {service.name: service for service in services}
            dentists[0].services.extend(
                [
                    services_by_name["Dental Cleaning"],
                    services_by_name["Comprehensive Checkup"],
                    services_by_name["Teeth Whitening"],
                ]
            )
            dentists[1].services.extend(
                [
                    services_by_name["Dental Cleaning"],
                    services_by_name["Comprehensive Checkup"],
                    services_by_name["Orthodontic Consultation"],
                ]
            )
            dentists[2].services.extend(
                [
                    services_by_name["Dental Cleaning"],
                    services_by_name["Comprehensive Checkup"],
                    services_by_name["Root Canal Therapy"],
                ]
            )

            staff_users = [
                StaffUser(
                    email="admin@clinic.example",
                    hashed_password=hash_password("Admin@12345"),
                    first_name="Clinic",
                    last_name="Admin",
                    role=StaffRole.MANAGER,
                ),
                StaffUser(
                    email="reception@clinic.example",
                    hashed_password=hash_password("Reception@12345"),
                    first_name="Front",
                    last_name="Desk",
                    role=StaffRole.RECEPTIONIST,
                ),
            ]
            session.add_all(staff_users)

            patients = [
                Patient(
                    first_name="Noah",
                    last_name="Mehta",
                    email="noah.mehta@example.com",
                    phone="+15551000101",
                    date_of_birth=date(1992, 3, 21),
                    gender="male",
                    is_returning=True,
                    channel_preference=ChannelPreference.WHATSAPP,
                ),
                Patient(
                    first_name="Emma",
                    last_name="Iyer",
                    email="emma.iyer@example.com",
                    phone="+15551000102",
                    date_of_birth=date(1988, 11, 9),
                    gender="female",
                    insurance_provider="SmileHealth",
                    insurance_member_id="SMH-883201",
                    channel_preference=ChannelPreference.SMS,
                ),
                Patient(
                    first_name="Oliver",
                    last_name="Singh",
                    email="oliver.singh@example.com",
                    phone="+15551000103",
                    date_of_birth=date(2001, 6, 14),
                    gender="male",
                    channel_preference=ChannelPreference.WEB,
                ),
                Patient(
                    first_name="Sophia",
                    last_name="Nair",
                    email="sophia.nair@example.com",
                    phone="+15551000104",
                    date_of_birth=date(1995, 1, 30),
                    gender="female",
                    requires_deposit=True,
                    channel_preference=ChannelPreference.VOICE,
                ),
                Patient(
                    first_name="Ethan",
                    last_name="Reddy",
                    email="ethan.reddy@example.com",
                    phone="+15551000105",
                    date_of_birth=date(1985, 8, 18),
                    gender="male",
                    no_show_count=1,
                    channel_preference=ChannelPreference.WHATSAPP,
                ),
            ]
            session.add_all(patients)

            slot_ranges = generate_time_slots(date.today(), days=30)
            time_slots: list[TimeSlot] = []
            for dentist in dentists:
                for start_time, end_time in slot_ranges:
                    time_slots.append(
                        TimeSlot(
                            dentist_id=dentist.id,
                            start_time=start_time,
                            end_time=end_time,
                            is_available=True,
                        )
                    )
            session.add_all(time_slots)

            await session.commit()
            print("Seed completed successfully.")
        except SQLAlchemyError:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed())
