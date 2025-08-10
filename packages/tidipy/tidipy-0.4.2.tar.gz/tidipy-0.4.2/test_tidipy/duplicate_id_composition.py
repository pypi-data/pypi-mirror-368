from tidipy import composer


@composer(id='this')
def hey() -> str:
    return 'a'


@composer(id='this')
def other() -> str:
    return 'b'
