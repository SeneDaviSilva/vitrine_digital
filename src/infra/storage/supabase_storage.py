from supabase import Client


class SupabaseStorageRepository:
    def __init__(self, client: Client, bucket: str = "produtos") -> None:
        self._client = client
        self._bucket = bucket

    def upload(self, caminho: str, conteudo: bytes, content_type: str) -> str:
        self._client.storage.from_(self._bucket).upload(
            path=caminho,
            file=conteudo,
            file_options={"content-type": content_type},
        )
        return self._client.storage.from_(self._bucket).get_public_url(caminho)