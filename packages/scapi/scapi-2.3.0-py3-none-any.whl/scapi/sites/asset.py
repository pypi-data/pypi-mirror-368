import datetime
from enum import Enum
import re
from typing import TYPE_CHECKING
import warnings

import bs4
from . import base
from ..others import common,error as exception

if TYPE_CHECKING:
    from .session import Session

class Backpacktype(Enum):
    unknown=0
    Sprite=1
    Script=2
    BitmapCostume=3
    VectorCostume=4
    Sound=5

_backpacktype = {
    Backpacktype.Sprite:("sprite","application/zip"),
    Backpacktype.Script:("script","application/json"),
    Backpacktype.BitmapCostume:("costume","image/png"),
    Backpacktype.VectorCostume:("costume","image/svg+xml"),
    Backpacktype.Sound:("sound","audio/x-wav"),
}


class Backpack(base._BaseSiteAPI):
    id_name = "id"

    def __repr__(self):
        return f"<Backpack id:{self.id} name:{self.name} session:{self.Session}>"

    def __init__(
        self,
        ClientSession:common.ClientSession,
        id:str,
        scratch_session:"Session|None"=None,
        **entries
    ):
        super().__init__("get","",ClientSession,scratch_session)

        self.id:str=id
        self.type:Backpacktype=Backpacktype.unknown
        self.name:str=None
        self._body:str=None
        self._thumbnail:str=None

    async def update(self):
        self.has_session_raise()
        async for i in self.Session.backpack():
            if i.id == self.id:
                self.type,self.name,self._body,self._thumbnail = i.type,i.name,i._body,i._thumbnail
                return
        raise exception.ObjectNotFound(Backpack)
    
    def _update_from_dict(self, data:dict):
        self.id = data.get("id",self.id)
        self.name = data.get("name",self.name)
        self._body = data.get("body",self._body)
        self._thumbnail = data.get("thumbnail",self._thumbnail)
        if data.get("type",None) == "sprite": self.type = Backpacktype.Sprite
        elif data.get("type",None) == "script": self.type = Backpacktype.Script
        elif data.get("type",None) == "costume" and data.get("mime",None) == "image/svg+xml":
            self.type = Backpacktype.VectorCostume
        elif data.get("type",None) == "costume" and data.get("mime",None) == "image/png":
            self.type = Backpacktype.BitmapCostume
        elif data.get("type",None) == "sound": self.type = Backpacktype.Sound
        else: self.type = Backpacktype.unknown
    
    @property
    def download_url(self) -> str:
        return "https://backpack.scratch.mit.edu/" + self._body
    
    @property
    def thumbnail_url(self) -> str:
        return "https://backpack.scratch.mit.edu/" + self._thumbnail
    
    async def download(self,path:str) -> None:
        await common.downloader(self.ClientSession,self.download_url,path)

    async def delete(self) -> None:
        self.has_session_raise()
        r = await self.ClientSession.delete(f"https://backpack.scratch.mit.edu/{self.Session.username}/{self.id}")
        if not r.json().get("ok",False):
            raise exception.BadResponse(r)
        
async def download_asset(id:str,path:str,ClientSession:common.ClientSession):
    await common.downloader(ClientSession,f"https://assets.scratch.mit.edu/internalapi/asset/{id}/get/",path)