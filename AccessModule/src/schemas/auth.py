from pydantic import BaseModel
from typing import Optional, Dict, Any

import config
import utils

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str

class UserRequest(User):
    password: str
    company: str

class UserDB(User):
    company: str
    hashed_password: str
    @staticmethod
    def from_fiware(fiware: dict[str, str]):
        return UserDB(
            username=utils.get_user_from_fiware_id(fiware["id"]),
            company=fiware["company"]["value"],
            hashed_password=fiware["hashed_password"]["value"],
        )
    def user_to_fiware(self) -> dict[str, str]:
        try:
            fiware_obj: Dict[str, Any] = {}
            fiware_obj["@context"] = config.FIWARE_CONTEXT
            fiware_obj["id"] = utils.get_full_user_id(self.username)
            fiware_obj["type"] = config.USER_ENTITY
            fiware_obj["company"] = utils.get_property(
                self.company
            )
            fiware_obj["hashed_password"] = utils.get_property(
                self.hashed_password
            )
            return fiware_obj
        except Exception as e:
            raise ValueError(f"Error converting User to Fiware format: {str(e)}")


class ChangePassword(BaseModel):
    old_password: str
    new_password: str