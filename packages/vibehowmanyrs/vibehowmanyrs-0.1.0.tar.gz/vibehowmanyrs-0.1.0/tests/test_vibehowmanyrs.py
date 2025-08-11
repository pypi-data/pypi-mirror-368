from vibehowmanyrs import vibehowmanyrs
from dotenv import load_dotenv

load_dotenv()


def test_vibehowmanyrs():
    assert vibehowmanyrs("strawberry") == 3
    assert vibehowmanyrs("strawberrry") == 4