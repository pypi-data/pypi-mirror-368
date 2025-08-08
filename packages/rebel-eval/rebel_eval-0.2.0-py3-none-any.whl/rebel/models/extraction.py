from pydantic import BaseModel
from typing import List, Optional

from rebel.models import RetryParams, Metric


class TestGroup(BaseModel):
    """Represents a configuration for a group of related tests.

    This class is used to apply common settings such as metrics, tags, and retry
    policies to a collection of tests, often generated from a single source like
    a decorated function.

    Attributes:
        metrics (List[Metric]): A list of metrics to be applied to all tests
            within this group.
        tags (Optional[List[str]]): A list of tags for categorizing and filtering
            the tests in this group. Defaults to an empty list.
        retry_params (Optional[RetryParams]): Configuration for retrying failed
            tests. By default, tests are run once with no retries.
        postfix (Optional[str]): An optional string to be appended to the base
            name of each test in the group, helping to create unique and
            descriptive test names. Defaults to None.
    """
    metrics: List[Metric]
    tags: Optional[List[str]] = []
    retry_params: Optional[RetryParams] = RetryParams(count=1)  # do not retry by default
    postfix: Optional[str] = None  # postfix to basic name of the test (name of the function)
