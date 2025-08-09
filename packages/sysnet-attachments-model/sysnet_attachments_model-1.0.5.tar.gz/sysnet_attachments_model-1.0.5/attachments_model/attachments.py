from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from sysnet_pyutils.models.general import AclType, ListTypeBase
from sysnet_pyutils.utils import uuid_factory

from attachments_model.domino import DominoAttachmentType


class AttachmentBaseType(BaseModel):
    uuid_external: Optional[str] = Field(
        default=None,
        description='Externí identifikátor')
    title: Optional[str] = Field(
        default=None,
        description='Attachment title for display',
        examples=['Rámcová smlouva se společností XY'], )
    attachment_type: Optional[str] = Field(
        default=None,
        description='Typ přílohy - z číselníku typů',
        examples=['Evidenční list'])
    attachment_subtype: Optional[str] = Field(
        default=None,
        description='Typ přílohy - z číselníku typů',
        examples=['Podepsaný evidenční list'], )
    container_id: Optional[str] = Field(
        default=None,
        description='Container unique identifier',
        examples=['123e4567-e89b-12d3-a456-426614174000'], )
    document_id: Optional[str] = Field(
        default=None,
        description='Document unique identifier',
        examples=['123e4567-e89b-12d3-a456-426614174000'], )
    comment: Optional[str] = Field(default=None, title='Libovolný komentář'),
    date_created: Optional[datetime] = Field(default=None, title='Datum vytvoření zdrojového dokumentu')


class AttachmentType(AttachmentBaseType):
    identifier: str = Field(
        default_factory=uuid_factory,
        description='Attachment unique identifier',
        examples=['123e4567-e89b-12d3-a456-426614174000'])
    name: Optional[str] = Field(
        default=None,
        description='Attachment name for display',
        examples=['smlouva.pdf'])
    creator: Optional[str] = Field(
        default=None,
        description='Osoba, která uploadovala přílohu',
        examples=['Jan Novák'])
    date_uploaded: Optional[datetime] = Field(
        default=None,
        description='Datum uploadu přílohy',
        examples=['2021-08-30T23:01:14.274085491+15:55'], )
    mime_type: Optional[str] = Field(
        default=None,
        description='Attachment mime type',
        examples=['application/pdf'])
    size: Optional[int] = Field(
        default=None,
        description='File size',
        examples=[1456879475])
    storage: Optional[str] = Field(
        default=None,
        description='Identifikátor úložiště souborů (např. Replica ID)',
        examples=['C1257BFF00563DB0'], )
    domino: Optional[DominoAttachmentType] = Field(
        default=None,
        description='Metadata domino přílohy')
    acl: Optional[List[AclType]] = Field(default=None, description='seznam přístupových práv')

class AttachmentOutType(AttachmentType):
    file_exists: Optional[bool] = Field(default=False, description='Soubor existuje v úložišti')


class AttachmentListType(ListTypeBase):
    key: Optional[Union[str, dict]] = Field(
        default=None,
        description='Může být identifikátor nebo jiný textový klíč (např. čj.)',
        examples=['114/22'])
    search: Optional[str] = Field(default=None, description='Text pro fulltextové vyhledávání', examples=['MŠMT'])
    category: Optional[str] = Field(default=None, description='Vrácená kategorie', examples=['Návrhy'])
    container_id: Optional[str] = Field(
        default=None,
        description='Identifikátor kontejneru',
        examples=['451893da-28ea-46ab-b8b2-374530b5cb2b'])
    document_id: Optional[str] = Field(
        default=None,
        description='Identifikátor dokumentu',
        examples=['451893da-28ea-46ab-b8b2-374530b5cb2b'])
    hits: Optional[int] = Field(default=0, description='Hits')
    entries: Optional[List[AttachmentOutType]] = Field(default=None, description='Položky seznamu')


class AttachmentExtType(AttachmentType):
    file_path: Optional[str] = Field(default=None, description='Cesta k souboru do FS')
    file_name_original: Optional[str] = Field(default=None, description='Původní název souboru')
    file_name_slugified: Optional[str] = Field(default=None, description='Uložitelný název souboru')
    ft_indexed: Optional[bool] = Field(default=False, description='Soubor je FT indexován')
    file_exists: Optional[bool] = Field(default=False, description='Soubor existuje v úložišti')
