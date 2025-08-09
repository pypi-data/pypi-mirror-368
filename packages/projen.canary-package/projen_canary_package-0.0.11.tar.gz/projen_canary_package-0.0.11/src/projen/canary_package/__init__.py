r'''
# @projen/canary-testing

:warning: Do not use! :warning:

This package is used to integration test certain [projen](https://github.com/projen/projen) features that cannot be tested otherwise.
For example:

* Publishing
* Backports
* GitHub Workflows

# Note on vendoring

When vendoring a projen tarball into this repository, be sure to remove the `@`
character from the file name, or you will get the following very confusing
error:

```
error Error: ENOTDIR: not a directory, scandir /some/cache/path/projen-0.0.0-<guid>
```
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *


class CustomTypeScriptProject(
    metaclass=jsii.JSIIMeta,
    jsii_type="@projen/canary-package.CustomTypeScriptProject",
):
    '''Creates a custom TypeScript Project.

    :pjid: custom-ts-project
    '''

    def __init__(self, options: typing.Any) -> None:
        '''
        :param options: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b0efe38cc461c4178651aa27985753b521330f7b542c4a386f9134c2c14886f)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="prettier")
    def prettier(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "prettier"))


__all__ = [
    "CustomTypeScriptProject",
]

publication.publish()

def _typecheckingstub__7b0efe38cc461c4178651aa27985753b521330f7b542c4a386f9134c2c14886f(
    options: typing.Any,
) -> None:
    """Type checking stubs"""
    pass
