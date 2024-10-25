class User :

    @staticmethod
    def bulk_from_dict(data: dict) -> list['User']:
        return [User(**item) for item in data]

    def __init__(self, username: str,email: str,password: str,_id: int = None,_isActive: bool = True) -> None:  
        self.username = username
        self.email = email
        self.password = password
        self._id = _id
        self.isActive = _isActive

    def to_dict(self) -> dict:
        return {
        'username': self.username,
        'email': self.email,
        'password': self.password,
        '_isActive': self.isActive
        } 
    
