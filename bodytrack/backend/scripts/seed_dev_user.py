"""
Cria um usuário de desenvolvimento local, só para testar os endpoints
de projeto (Etapa 3) via o header temporário X-User-Id, antes de
existir um fluxo de login de verdade (Etapa 4).

Uso (com o Postgres de docker-compose no ar e as migrations aplicadas):
    python -m scripts.seed_dev_user
"""
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User

DEV_EMAIL = "dev@bodytrack.local"
DEV_PASSWORD = "dev12345"


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == DEV_EMAIL).first()
        if existing:
            print(f"Usuário de desenvolvimento já existe. ID: {existing.id}")
            return

        user = User(
            email=DEV_EMAIL,
            hashed_password=hash_password(DEV_PASSWORD),
            name="Usuário de Desenvolvimento",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print("Usuário de desenvolvimento criado.")
        print(f"  ID:    {user.id}")
        print(f"  Email: {user.email}")
        print("Use este ID no header 'X-User-Id' ao chamar a API (ex.: via /docs).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
