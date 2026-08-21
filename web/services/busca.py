from sqlalchemy import or_

from web.modules.model import Contato


def buscar_contatos(termo):
    termo = (termo or '').strip()
    if not termo:
        return []

    return Contato.query.filter(
        or_(
            Contato.nome.ilike(f"%{termo}%"),
            Contato.empresa.ilike(f"%{termo}%"),
            Contato.email.ilike(f"%{termo}%"),
        )
    ).order_by(Contato.nome).all()


def serializar_contato(contato):
    return {
        "id": contato.id,
        "nome": contato.nome,
        "empresa": contato.empresa,
        "email": contato.email,
        "telefone": contato.telefone,
        "etapa": contato.etapa.nome,
    }