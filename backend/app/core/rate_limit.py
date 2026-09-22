"""
Rate limiter compartido.
Vive en su propio módulo para evitar import circular
(antes vivía en main.py, pero auth.py lo importaba y rompía).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)
