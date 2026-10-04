"""Seeds the database with one tenant + one user per role. Idempotent."""
import os, sys
from dotenv import load_dotenv; load_dotenv()
import structlog
from db import tx, Tenant, User, Business, new_id, audit
from auth import hash_password, VALID_ROLES

log = structlog.get_logger("sanad.seed")

DEMO_USERS = [
    ("rm@sanad.demo",         "rm",             "sanad-rm-2026"),
    ("credit@sanad.demo",     "credit_analyst", "sanad-credit-2026"),
    ("scu@sanad.demo",        "scu",            "sanad-scu-2026"),
    ("verifier@sanad.demo",   "verifier",       "sanad-verifier-2026"),
    ("admin@sanad.demo",      "admin",          "sanad-admin-2026"),
    ("committee@sanad.demo",  "committee",      "sanad-committee-2026"),
]

def seed():
    with tx() as s:
        # Tenant
        tenant = s.query(Tenant).filter(Tenant.name == "Warba Bank").first()
        if not tenant:
            tenant = Tenant(id=new_id(), name="Warba Bank")
            s.add(tenant); s.flush()
            log.info("tenant_created", id=tenant.id)
        else:
            log.info("tenant_exists", id=tenant.id)

        # Users
        for email, role, password in DEMO_USERS:
            existing = s.query(User).filter(User.email == email).first()
            if existing:
                log.info("user_exists", email=email)
                continue
            u = User(id=new_id(), tenant_id=tenant.id, email=email,
                     password_hash=hash_password(password), role=role)
            s.add(u); s.flush()
            audit(s, tenant.id, u.id, "seed_user", target_type="user", target_id=u.id,
                  detail={"role": role, "email": email})
            log.info("user_seeded", email=email, role=role)

        # Demo business
        biz = s.query(Business).filter(Business.name == "Gulf Pearl Foods Trading W.L.L.").first()
        if not biz:
            biz = Business(id=new_id(), tenant_id=tenant.id,
                           name="Gulf Pearl Foods Trading W.L.L.",
                           sector="Import & distribution of frozen and dry foods",
                           cr_number="214457-2019", status="active", data_quality=80)
            s.add(biz); s.flush()
            log.info("business_seeded", id=biz.id)

        print("✔ seed complete:")
        print(f"   tenant : {tenant.name} ({tenant.id})")
        print(f"   users  : {len(DEMO_USERS)} seeded")
        print(f"   business: Gulf Pearl Foods Trading W.L.L.")
        print()
        print("Login credentials (email / password):")
        for email, role, pw in DEMO_USERS:
            print(f"   {role:16s}  {email:28s}  {pw}")

if __name__ == "__main__":
    seed()