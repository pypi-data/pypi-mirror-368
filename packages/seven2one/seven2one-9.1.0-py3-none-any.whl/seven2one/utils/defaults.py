from dataclasses import dataclass

@dataclass
class Defaults():
    timeZone: str = 'UTC'
    useDateTimeOffset: bool = True
    copyGraphQLString: bool = False