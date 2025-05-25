"""
Services - Logiche business complesse

I servizi implementano logiche business di alto livello che combinano
più repository e manager per fornire funzionalità complete:

- ZeroTrustService: Valutazione accessi, report sicurezza, analisi trust

I servizi sono opzionali e pensati per sviluppi futuri o per logiche
business complesse che vanno oltre le singole policy.

Utilizzo:
    from utils.services.zero_trust_service import ZeroTrustService
    
    service = ZeroTrustService()
    access_result = service.evaluate_user_access("cliente1", 1, "lettura")
    security_report = service.get_network_security_report()
"""

from .zero_trust_service import ZeroTrustService

__all__ = [
    'ZeroTrustService'
]