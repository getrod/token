from render_token import render_token

token_file = 'tokens_300.json'
tokens = [
    "t_78",
    "t_79",
    "t_80",
    "t_81",
    "t_82",
    "t_94",
    "t_121",
    "t_123",
    "t_186",
    "t_187",
    "t_188",
    "t_189",
    "t_190",
    "t_191",
    "t_210",
    "t_211",
    "t_212",
    "t_213",
    "t_214",
    "t_215",
    "t_300"
]

for token in tokens:
    render_token(token_file, token)
