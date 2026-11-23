import hashlib


class Sha256PasswordHasher:
    """Mantém compatibilidade com os hashes migrados do banco legado."""

    def hash(self, senha: str) -> str:
        return hashlib.sha256(senha.encode("utf-8")).hexdigest()

    def verificar(self, senha: str, senha_hash: str) -> bool:
        return self.hash(senha) == senha_hash