class DepagError(Exception):
    """Errore generico del client DEPAG."""


class DepagServiceError(DepagError):
    """Errore SOAP a livello applicativo."""
