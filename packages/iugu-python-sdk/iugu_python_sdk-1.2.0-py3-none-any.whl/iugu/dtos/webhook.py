from dataclasses import dataclass, asdict
from typing import Optional
from fmconsult.utils.object import CustomObject

@dataclass
class Webhook(CustomObject):
  event: str
  url: str
  authorization: str

  def to_dict(self):
    data = asdict(self)
    return data