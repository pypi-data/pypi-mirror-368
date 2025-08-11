from pathlib import Path
from typing import List, ClassVar
from pydantic import BaseModel, Field, computed_field, ConfigDict
from pydantic_partial import create_partial_model
from utilities import compute_sha1
from wombat.multiprocessing.tasks import RetryableTask, RequiresProps
from constants import BASE_API_URL
# ======================================================================== #
# Task models
# ======================================================================== #

class AsyncFetchUrlTask(RetryableTask, RequiresProps):
    """Task for asynchronous URL fetching."""
    action: str = "async_fetch_url"
    requires_props: List[str] = ["aiohttp_session"]

###############################################################################
# Indicator Data Models & State Transitions
###############################################################################
class ParametrizedIndicator(BaseModel):
    """
    Represents an indicator from the WHO GHO API with injected parameters
    (download URL and output path). State: PARAMETRIZED (ready for acquisition)
    """
    model_config = ConfigDict(populate_by_name=True)
    code: str = Field(alias="IndicatorCode")
    name: str = Field(alias="IndicatorName")
    url: str
    language: str = Field(alias="Language", default="EN")
    output_path: Path

# Raw API responses are missing the URL/output_path. Use a partial model.
UnparametrizedIndicator = create_partial_model(
    ParametrizedIndicator,
    "url",
    "output_path"
)

class UnparametrizedIndicatorList(BaseModel):
    """
    Represents a list of raw indicators from the WHO GHO API,
    prior to parameter injection.
    """
    url: ClassVar[str] = f"{BASE_API_URL}/Indicator/"
    context: ClassVar[str] = Field(alias="@odata.context")
    value: List[UnparametrizedIndicator]


class ParametrizedIndicatorList(BaseModel):
    """
    Represents a list of parametrized indicators, ready for acquisition.
    """
    url: ClassVar[str] = f"{BASE_API_URL}/Indicator/"
    context: ClassVar[str] = Field(alias="@odata.context")
    value: List[ParametrizedIndicator]

class ConcreteIndicator(ParametrizedIndicator):
    """
    Represents an indicator that has been downloaded.
    State: CONCRETE (acquired)
    """
    @computed_field
    @property
    def sha1(self) -> str:
        return compute_sha1(self.output_path).hexdigest()

    @computed_field
    @property
    def exists(self) -> bool:
        return self.output_path.exists()
