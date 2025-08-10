from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Union
from dataclasses import dataclass, field
from queue import Queue
from threading import Thread

from py_return_success_or_error.core.return_success_or_error import (
    ReturnSuccessOrError, 
    SuccessReturn, 
    ErrorReturn
)
from py_return_success_or_error.interfaces.parameters_return_result import (
    ParametersReturnResult,
)

from py_return_success_or_error.interfaces.datasource import Datasource
from py_return_success_or_error.mixins.repository_mixin import RepositoryMixin
from py_return_success_or_error.mixins.thread_mixin import ThreadMixin
from py_return_success_or_error.interfaces.datasource import Datasource
