"""initial_schema

Revision ID: 20260427_1419
Revises:
Create Date: 2026-04-27 14:19:00.000000
"""

# Command to create this migration:
# alembic revision --autogenerate -m "initial_schema"

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260427_1419"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("performed_by_type", sa.Enum("BOT", "PATIENT", "STAFF", name="performed_by_type"), nullable=False),
        sa.Column("performed_by_id", sa.String(length=255), nullable=True),
        sa.Column("before_state", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_state", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"], unique=False)

    op.create_table(
        "dentists",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("specializations", postgresql.ARRAY(sa.String(length=120)), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("calendar_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dentists_email", "dentists", ["email"], unique=True)
    op.create_index("ix_dentists_phone", "dentists", ["phone"], unique=True)

    op.create_table(
        "patients",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=50), nullable=True),
        sa.Column("insurance_provider", sa.String(length=255), nullable=True),
        sa.Column("insurance_member_id", sa.String(length=255), nullable=True),
        sa.Column("is_returning", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("no_show_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("requires_deposit", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("channel_preference", sa.Enum("web", "whatsapp", "sms", "voice", name="channel_preference"), server_default="web", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patients_email", "patients", ["email"], unique=True)
    op.create_index("ix_patients_phone", "patients", ["phone"], unique=True)

    op.create_table(
        "services",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requires_dentist_specialization", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "staff_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.Enum("RECEPTIONIST", "MANAGER", "DENTIST_VIEW", name="staff_role"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_staff_users_email", "staff_users", ["email"], unique=True)

    op.create_table(
        "dentist_services",
        sa.Column("dentist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["dentist_id"], ["dentists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("dentist_id", "service_id"),
    )

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.Enum("web", "whatsapp", "sms", "voice", name="conversation_channel"), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "WAITING_HUMAN", "HUMAN_TAKEOVER", "COMPLETED", "ABANDONED", name="conversation_status"), server_default="ACTIVE", nullable=False),
        sa.Column("assigned_staff_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("intent_history", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assigned_staff_id"], ["staff_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_patient_id", "conversations", ["patient_id"], unique=False)
    op.create_index("ix_conversations_session_id", "conversations", ["session_id"], unique=True)

    op.create_table(
        "time_slots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dentist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_available", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("locked_by", sa.String(length=255), nullable=True),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("appointment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dentist_id"], ["dentists.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appointment_id"),
    )
    op.create_index("ix_time_slots_dentist_id", "time_slots", ["dentist_id"], unique=False)
    op.create_index(
        "ix_time_slots_dentist_start_available",
        "time_slots",
        ["dentist_id", "start_time", "is_available"],
        unique=False,
    )

    op.create_table(
        "appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dentist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("time_slot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "CONFIRMED", "CANCELLED", "COMPLETED", "NO_SHOW", name="appointment_status"), server_default="PENDING", nullable=False),
        sa.Column("source_channel", sa.Enum("web", "whatsapp", "sms", "voice", "staff", name="appointment_source_channel"), server_default="web", nullable=False),
        sa.Column("deposit_required", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deposit_paid", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reminder_24h_sent", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reminder_2h_sent", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dentist_id"], ["dentists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["time_slot_id"], ["time_slots.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("time_slot_id"),
    )
    op.create_index("ix_appointments_dentist_id", "appointments", ["dentist_id"], unique=False)
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"], unique=False)
    op.create_index("ix_appointments_start_time", "appointments", ["start_time"], unique=False)
    op.create_index("ix_appointments_status", "appointments", ["status"], unique=False)
    op.create_foreign_key(
        "fk_time_slots_appointment_id_appointments",
        "time_slots",
        "appointments",
        ["appointment_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "conversation_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.Enum("user", "assistant", "system", name="conversation_role"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(length=120), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("entities_extracted", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_turns_conversation_id", "conversation_turns", ["conversation_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("appointment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.Enum("CONFIRM", "REMINDER_48H", "REMINDER_24H", "REMINDER_2H", "CANCELLATION", "RESCHEDULE", name="notification_type"), nullable=False),
        sa.Column("channel", sa.Enum("web", "whatsapp", "sms", "voice", name="notification_channel"), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "SENT", "FAILED", "DELIVERED", name="notification_status"), server_default="PENDING", nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_appointment_id", "notifications", ["appointment_id"], unique=False)
    op.create_index("ix_notifications_patient_id", "notifications", ["patient_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notifications_patient_id", table_name="notifications")
    op.drop_index("ix_notifications_appointment_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_conversation_turns_conversation_id", table_name="conversation_turns")
    op.drop_table("conversation_turns")

    op.drop_constraint("fk_time_slots_appointment_id_appointments", "time_slots", type_="foreignkey")
    op.drop_index("ix_time_slots_dentist_start_available", table_name="time_slots")
    op.drop_index("ix_time_slots_dentist_id", table_name="time_slots")
    op.drop_table("time_slots")

    op.drop_index("ix_appointments_status", table_name="appointments")
    op.drop_index("ix_appointments_start_time", table_name="appointments")
    op.drop_index("ix_appointments_patient_id", table_name="appointments")
    op.drop_index("ix_appointments_dentist_id", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_conversations_session_id", table_name="conversations")
    op.drop_index("ix_conversations_patient_id", table_name="conversations")
    op.drop_table("conversations")

    op.drop_table("dentist_services")

    op.drop_index("ix_staff_users_email", table_name="staff_users")
    op.drop_table("staff_users")

    op.drop_table("services")

    op.drop_index("ix_patients_phone", table_name="patients")
    op.drop_index("ix_patients_email", table_name="patients")
    op.drop_table("patients")

    op.drop_index("ix_dentists_phone", table_name="dentists")
    op.drop_index("ix_dentists_email", table_name="dentists")
    op.drop_table("dentists")

    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.execute("DROP TYPE IF EXISTS notification_status")
    op.execute("DROP TYPE IF EXISTS notification_channel")
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.execute("DROP TYPE IF EXISTS conversation_role")
    op.execute("DROP TYPE IF EXISTS appointment_source_channel")
    op.execute("DROP TYPE IF EXISTS appointment_status")
    op.execute("DROP TYPE IF EXISTS conversation_status")
    op.execute("DROP TYPE IF EXISTS conversation_channel")
    op.execute("DROP TYPE IF EXISTS staff_role")
    op.execute("DROP TYPE IF EXISTS channel_preference")
    op.execute("DROP TYPE IF EXISTS performed_by_type")
