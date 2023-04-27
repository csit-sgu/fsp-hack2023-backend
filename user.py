@dataclass
class User:
    guid : int
    claims : list
    date_reg : str
    date_login : str
    salt : bytes
    hashed_password : bytes
    athlete_FK : int
    representative_FK : int
    administator_FK : int
    parthner_FK : int
    email : str
