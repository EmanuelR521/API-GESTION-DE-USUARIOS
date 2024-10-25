import yaml

class Config:
    def __init__(self) -> None:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
            self.jwt_secret = config['jwt']['secret']
            self.db_name = config['mongo']['db']
            self.uri = config['mongo']['uri']