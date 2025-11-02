from app.api.schema import CommonBase,Base



class UserBase(Base):
    username: str
    password: str

class UserCreate(UserBase):
    pass

class UserRead(CommonBase):
    username:str

    class Config:
        orm_mode = True


class LoginRead(Base):
    access_token:str
    token_type:str
    