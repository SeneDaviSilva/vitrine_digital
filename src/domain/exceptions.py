class DomainError(Exception):
    """Exceção base para erros de regra de negócio no domínio."""
    pass


class DadosInvalidosError(DomainError):
    """Lançada quando uma entidade recebe dados fora do formato esperado."""
    pass


class EntidadeNaoEncontradaError(DomainError):
    """Lançada quando um registro solicitado não existe."""
    pass


class DuplicidadeError(DomainError):
    """Lançada quando e-mail, WhatsApp ou nome de loja já estão em uso."""
    pass


class CredenciaisInvalidasError(DomainError):
    """Lançada quando e-mail ou senha não conferem na autenticação."""
    pass