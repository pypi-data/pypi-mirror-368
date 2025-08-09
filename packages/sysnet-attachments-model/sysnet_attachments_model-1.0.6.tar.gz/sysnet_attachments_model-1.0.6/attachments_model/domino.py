from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class DominoAttachmentType(BaseModel):
    database: Optional[str] = Field(default=None, description='ReplicaID databáze s uloženou přílohou', examples=['C1257BFF00563DB0'])
    document: Optional[str] = Field(default=None, description='UNID dokumentu s přílohou', examples=['C1257B7F0058E304C125704A001AED45'])
    filename: Optional[str] = Field(default=None, description='Název souboru', examples=['2020_03_26_OZO_CENIA.pdf'])
    token: Optional[str] = Field(default=None, description='uploadToken', examples=['CIT08OR5N6GK_pdf'])
    pid: Optional[str] = Field(default=None, description='PID dokumentu s přílohou', examples=['CIT28YH17I75'])
    pid_source: Optional[str] = Field(default=None, description='PID zdrojového dokumentu', examples=['CIT08OR5N6GK'])
    comments: Optional[str] = Field(default=None, description='Poznámky')
