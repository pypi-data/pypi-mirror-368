from enum import Enum, StrEnum


class EnvironmentMode(Enum):
    TESTING = "testing"
    PRODUCTION = "production"


class AIModel(StrEnum):
    GPT_4_1_NANO = "gpt-4.1-nano"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1 = "gpt-4.1"


GPT_4_1_NANO = AIModel.GPT_4_1_NANO
GPT_4_1_MINI = AIModel.GPT_4_1_MINI
GPT_4_1 = AIModel.GPT_4_1
TESTING_MODE = EnvironmentMode.TESTING
PRODUCTION_MODE = EnvironmentMode.PRODUCTION
