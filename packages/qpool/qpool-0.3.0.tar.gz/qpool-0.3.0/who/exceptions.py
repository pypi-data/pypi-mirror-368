
class BHIVEException(Exception):
    """Base exception for bhive things."""
    pass

class EmptyDataPullException(BHIVEException):
    def __init__(self, url: str, indicator: str) -> None:
        self.url = url
        self.indicator = indicator
        super().__init__(f"Received no data when pulling {self.indicator} from {self.url}")

class TransferInterruptException(BHIVEException):
    def __init__(self, url: str, indicator: str) -> None:
        self.url = url
        self.indicator = indicator
        super().__init__(f"Transfer interrupted when pulling {self.indicator} from {self.url}")
