import logging


class MaxLevelFilter(logging.Filter):
    def __init__(self, level: str) -> None:
        # O argumento agora se chama 'level' para corresponder à configuração JSON
        super().__init__()

        # self.max_level terá o número do level
        self.max_level = logging.getLevelNamesMapping().get(level.upper(), 50)

    def filter(self, record: logging.LogRecord) -> bool:
        # record é o LogRecord que eu disse antes
        # record.levelno é o número do level do log
        # se o número do level do log for menor ou igual ao max_level que
        # definimos no filter o log passa.
        # INFO 20 só aceitará logs INFO e DEBUG.
        return record.levelno <= self.max_level
