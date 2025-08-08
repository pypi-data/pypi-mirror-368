from collections.abc import Mapping

__all__ = ['cxd_exceptions', 'cxd_token_url']

cxd_exceptions: Mapping[int, type[Exception]]

def cxd_token_url(target: str) -> str: ...
