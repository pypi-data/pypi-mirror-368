<a id="types-aiobotocore-lite"></a>

# types-aiobotocore-lite

[![PyPI - types-aiobotocore-lite](https://img.shields.io/pypi/v/types-aiobotocore-lite.svg?color=blue)](https://pypi.org/project/types-aiobotocore-lite/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-aiobotocore-lite.svg?color=blue)](https://pypi.org/project/types-aiobotocore-lite/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/types_aiobotocore_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/types-aiobotocore-lite)](https://pypistats.org/packages/types-aiobotocore-lite)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for
[aiobotocore 2.24.0](https://pypi.org/project/aiobotocore/) compatible with
[VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found on
[types-aiobotocore](https://pypi.org/project/types-aiobotocore/) page and in
[types-aiobotocore-lite docs](https://youtype.github.io/types_aiobotocore_docs/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [types-aiobotocore-lite](#types-aiobotocore-lite)
  - [How to install](#how-to-install)
    - [Generate locally (recommended)](<#generate-locally-(recommended)>)
    - [From PyPI with pip](#from-pypi-with-pip)
  - [How to uninstall](#how-to-uninstall)
  - [Usage](#usage)
    - [VSCode](#vscode)
    - [PyCharm](#pycharm)
    - [Emacs](#emacs)
    - [Sublime Text](#sublime-text)
    - [Other IDEs](#other-ides)
    - [mypy](#mypy)
    - [pyright](#pyright)
    - [Pylint compatibility](#pylint-compatibility)
  - [How it works](#how-it-works)
  - [What's new](#what's-new)
    - [Implemented features](#implemented-features)
    - [Latest changes](#latest-changes)
  - [Versioning](#versioning)
  - [Thank you](#thank-you)
  - [Documentation](#documentation)
  - [Support and contributing](#support-and-contributing)
  - [Submodules](#submodules)

<a id="how-to-install"></a>

## How to install

<a id="generate-locally-(recommended)"></a>

### Generate locally (recommended)

You can generate type annotations for `aiobotocore` package locally with
`mypy-boto3-builder`. Use
[uv](https://docs.astral.sh/uv/getting-started/installation/) for build
isolation.

1. Run mypy-boto3-builder in your package root directory:
   `uvx --with 'aiobotocore==2.24.0' mypy-boto3-builder`
2. Select `aiobotocore` AWS SDK.
3. Select services you use in the current project.
4. Use provided commands to install generated packages.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `types-aiobotocore` to add type checking for `aiobotocore` package.

```bash
# install type annotations only for aiobotocore
python -m pip install types-aiobotocore

# install aiobotocore type annotations
# for cloudformation, dynamodb, ec2, lambda, rds, s3, sqs
python -m pip install 'types-aiobotocore[essential]'

# or install annotations for services you use
python -m pip install 'types-aiobotocore[acm,apigateway]'

# or install annotations in sync with aiobotocore version
python -m pip install 'types-aiobotocore[aiobotocore]'

# or install all-in-one annotations for all services
python -m pip install 'types-aiobotocore[full]'
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
# uninstall types-aiobotocore-lite
python -m pip uninstall -y types-aiobotocore-lite
```

<a id="usage"></a>

## Usage

<a id="vscode"></a>

### VSCode

- Install
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- Install
  [Pylance extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- Set `Pylance` as your Python Language Server
- Install `types-aiobotocore-lite[essential]` in your environment:

```bash
python -m pip install 'types-aiobotocore-lite[essential]'
```

Both type checking and code completion should now work. No explicit type
annotations required, write your `aiobotocore` code as usual.

<a id="pycharm"></a>

### PyCharm

Install `types-aiobotocore-lite[essential]` in your environment:

```bash
python -m pip install 'types-aiobotocore-lite[essential]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `types-aiobotocore-lite` with services you use in your environment:

```bash
python -m pip install 'types-aiobotocore-lite[essential]'
```

- Install [use-package](https://github.com/jwiegley/use-package),
  [lsp](https://github.com/emacs-lsp/lsp-mode/),
  [company](https://github.com/company-mode/company-mode) and
  [flycheck](https://github.com/flycheck/flycheck) packages
- Install [lsp-pyright](https://github.com/emacs-lsp/lsp-pyright) package

```elisp
(use-package lsp-pyright
  :ensure t
  :hook (python-mode . (lambda ()
                          (require 'lsp-pyright)
                          (lsp)))  ; or lsp-deferred
  :init (when (executable-find "python3")
          (setq lsp-pyright-python-executable-cmd "python3"))
  )
```

- Make sure emacs uses the environment where you have installed
  `types-aiobotocore-lite`

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="sublime-text"></a>

### Sublime Text

- Install `types-aiobotocore-lite[essential]` with services you use in your
  environment:

```bash
python -m pip install 'types-aiobotocore-lite[essential]'
```

- Install [LSP-pyright](https://github.com/sublimelsp/LSP-pyright) package

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="other-ides"></a>

### Other IDEs

Not tested, but as long as your IDE supports `mypy` or `pyright`, everything
should work.

<a id="mypy"></a>

### mypy

- Install `mypy`: `python -m pip install mypy`
- Install `types-aiobotocore-lite[essential]` in your environment:

```bash
python -m pip install 'types-aiobotocore-lite[essential]'
```

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `types-aiobotocore-lite[essential]` in your environment:

```bash
python -m pip install 'types-aiobotocore-lite[essential]'
```

Optionally, you can install `types-aiobotocore-lite` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid
`types-aiobotocore-lite` dependency in production. However, there is an issue
in `pylint` that it complains about undefined variables. To fix it, set all
types to `object` in non-`TYPE_CHECKING` mode.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types_aiobotocore_ec2 import EC2Client, EC2ServiceResource
    from types_aiobotocore_ec2.waiters import BundleTaskCompleteWaiter
    from types_aiobotocore_ec2.paginators import DescribeVolumesPaginator
else:
    EC2Client = object
    EC2ServiceResource = object
    BundleTaskCompleteWaiter = object
    DescribeVolumesPaginator = object

...
```

<a id="how-it-works"></a>

## How it works

Fully automated
[mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder) carefully
generates type annotations for each service, patiently waiting for
`aiobotocore` updates. It delivers drop-in type annotations for you and makes
sure that:

- All available `aiobotocore` services are covered.
- Each public class and method of every `aiobotocore` service gets valid type
  annotations extracted from `botocore` schemas.
- Type annotations include up-to-date documentation.
- Link to documentation is provided for every method.
- Code is processed by [ruff](https://docs.astral.sh/ruff/) for readability.

<a id="what's-new"></a>

## What's new

<a id="implemented-features"></a>

### Implemented features

- Fully type annotated `boto3`, `botocore`, `aiobotocore` and `aioboto3`
  libraries
- `mypy`, `pyright`, `VSCode`, `PyCharm`, `Sublime Text` and `Emacs`
  compatibility
- `Client`, `ServiceResource`, `Resource`, `Waiter` `Paginator` type
  annotations for each service
- Generated `TypeDefs` for each service
- Generated `Literals` for each service
- Auto discovery of types for `boto3.client` and `boto3.resource` calls
- Auto discovery of types for `session.client` and `session.resource` calls
- Auto discovery of types for `client.get_waiter` and `client.get_paginator`
  calls
- Auto discovery of types for `ServiceResource` and `Resource` collections
- Auto discovery of types for `aiobotocore.Session.create_client` calls

<a id="latest-changes"></a>

### Latest changes

Builder changelog can be found in
[Releases](https://github.com/youtype/mypy_boto3_builder/releases).

<a id="versioning"></a>

## Versioning

`types-aiobotocore-lite` version is the same as related `aiobotocore` version
and follows
[Python Packaging version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/).

<a id="thank-you"></a>

## Thank you

- [Allie Fitter](https://github.com/alliefitter) for
  [boto3-type-annotations](https://pypi.org/project/boto3-type-annotations/),
  this package is based on top of his work
- [black](https://github.com/psf/black) developers for an awesome formatting
  tool
- [Timothy Edmund Crosley](https://github.com/timothycrosley) for
  [isort](https://github.com/PyCQA/isort) and how flexible it is
- [mypy](https://github.com/python/mypy) developers for doing all dirty work
  for us
- [pyright](https://github.com/microsoft/pyright) team for the new era of typed
  Python

<a id="documentation"></a>

## Documentation

All services type annotations can be found in
[aiobotocore docs](https://youtype.github.io/types_aiobotocore_docs/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.

<a id="submodules"></a>

## Submodules

- `types-aiobotocore-lite[full]` - Type annotations for all 412 services in one
  package (recommended).
- `types-aiobotocore-lite[all]` - Type annotations for all 412 services in
  separate packages.
- `types-aiobotocore-lite[essential]` - Type annotations for
  [CloudFormation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudformation/),
  [DynamoDB](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dynamodb/),
  [EC2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ec2/),
  [Lambda](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lambda/),
  [RDS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_rds/),
  [S3](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_s3/)
  and
  [SQS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sqs/)
  services.
- `types-aiobotocore-lite[aiobotocore]` - Install annotations in sync with
  `aiobotocore` version.
- `types-aiobotocore-lite[accessanalyzer]` - Type annotations for
  [AccessAnalyzer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_accessanalyzer/)
  service.
- `types-aiobotocore-lite[account]` - Type annotations for
  [Account](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_account/)
  service.
- `types-aiobotocore-lite[acm]` - Type annotations for
  [ACM](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_acm/)
  service.
- `types-aiobotocore-lite[acm-pca]` - Type annotations for
  [ACMPCA](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_acm_pca/)
  service.
- `types-aiobotocore-lite[aiops]` - Type annotations for
  [AIOps](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_aiops/)
  service.
- `types-aiobotocore-lite[amp]` - Type annotations for
  [PrometheusService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_amp/)
  service.
- `types-aiobotocore-lite[amplify]` - Type annotations for
  [Amplify](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_amplify/)
  service.
- `types-aiobotocore-lite[amplifybackend]` - Type annotations for
  [AmplifyBackend](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_amplifybackend/)
  service.
- `types-aiobotocore-lite[amplifyuibuilder]` - Type annotations for
  [AmplifyUIBuilder](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_amplifyuibuilder/)
  service.
- `types-aiobotocore-lite[apigateway]` - Type annotations for
  [APIGateway](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_apigateway/)
  service.
- `types-aiobotocore-lite[apigatewaymanagementapi]` - Type annotations for
  [ApiGatewayManagementApi](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_apigatewaymanagementapi/)
  service.
- `types-aiobotocore-lite[apigatewayv2]` - Type annotations for
  [ApiGatewayV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_apigatewayv2/)
  service.
- `types-aiobotocore-lite[appconfig]` - Type annotations for
  [AppConfig](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_appconfig/)
  service.
- `types-aiobotocore-lite[appconfigdata]` - Type annotations for
  [AppConfigData](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_appconfigdata/)
  service.
- `types-aiobotocore-lite[appfabric]` - Type annotations for
  [AppFabric](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_appfabric/)
  service.
- `types-aiobotocore-lite[appflow]` - Type annotations for
  [Appflow](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_appflow/)
  service.
- `types-aiobotocore-lite[appintegrations]` - Type annotations for
  [AppIntegrationsService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_appintegrations/)
  service.
- `types-aiobotocore-lite[application-autoscaling]` - Type annotations for
  [ApplicationAutoScaling](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_autoscaling/)
  service.
- `types-aiobotocore-lite[application-insights]` - Type annotations for
  [ApplicationInsights](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_insights/)
  service.
- `types-aiobotocore-lite[application-signals]` - Type annotations for
  [CloudWatchApplicationSignals](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/)
  service.
- `types-aiobotocore-lite[applicationcostprofiler]` - Type annotations for
  [ApplicationCostProfiler](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_applicationcostprofiler/)
  service.
- `types-aiobotocore-lite[appmesh]` - Type annotations for
  [AppMesh](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_appmesh/)
  service.
- `types-aiobotocore-lite[apprunner]` - Type annotations for
  [AppRunner](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_apprunner/)
  service.
- `types-aiobotocore-lite[appstream]` - Type annotations for
  [AppStream](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_appstream/)
  service.
- `types-aiobotocore-lite[appsync]` - Type annotations for
  [AppSync](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_appsync/)
  service.
- `types-aiobotocore-lite[apptest]` - Type annotations for
  [MainframeModernizationApplicationTesting](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_apptest/)
  service.
- `types-aiobotocore-lite[arc-zonal-shift]` - Type annotations for
  [ARCZonalShift](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_arc_zonal_shift/)
  service.
- `types-aiobotocore-lite[artifact]` - Type annotations for
  [Artifact](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_artifact/)
  service.
- `types-aiobotocore-lite[athena]` - Type annotations for
  [Athena](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_athena/)
  service.
- `types-aiobotocore-lite[auditmanager]` - Type annotations for
  [AuditManager](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_auditmanager/)
  service.
- `types-aiobotocore-lite[autoscaling]` - Type annotations for
  [AutoScaling](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_autoscaling/)
  service.
- `types-aiobotocore-lite[autoscaling-plans]` - Type annotations for
  [AutoScalingPlans](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_autoscaling_plans/)
  service.
- `types-aiobotocore-lite[b2bi]` - Type annotations for
  [B2BI](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_b2bi/)
  service.
- `types-aiobotocore-lite[backup]` - Type annotations for
  [Backup](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backup/)
  service.
- `types-aiobotocore-lite[backup-gateway]` - Type annotations for
  [BackupGateway](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backup_gateway/)
  service.
- `types-aiobotocore-lite[backupsearch]` - Type annotations for
  [BackupSearch](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/)
  service.
- `types-aiobotocore-lite[batch]` - Type annotations for
  [Batch](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_batch/)
  service.
- `types-aiobotocore-lite[bcm-data-exports]` - Type annotations for
  [BillingandCostManagementDataExports](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bcm_data_exports/)
  service.
- `types-aiobotocore-lite[bcm-pricing-calculator]` - Type annotations for
  [BillingandCostManagementPricingCalculator](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bcm_pricing_calculator/)
  service.
- `types-aiobotocore-lite[bedrock]` - Type annotations for
  [Bedrock](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock/)
  service.
- `types-aiobotocore-lite[bedrock-agent]` - Type annotations for
  [AgentsforBedrock](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agent/)
  service.
- `types-aiobotocore-lite[bedrock-agent-runtime]` - Type annotations for
  [AgentsforBedrockRuntime](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agent_runtime/)
  service.
- `types-aiobotocore-lite[bedrock-agentcore]` - Type annotations for
  [BedrockAgentCoreDataPlaneFrontingLayer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore/)
  service.
- `types-aiobotocore-lite[bedrock-agentcore-control]` - Type annotations for
  [BedrockAgentCoreControlPlaneFrontingLayer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/)
  service.
- `types-aiobotocore-lite[bedrock-data-automation]` - Type annotations for
  [DataAutomationforBedrock](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_data_automation/)
  service.
- `types-aiobotocore-lite[bedrock-data-automation-runtime]` - Type annotations
  for
  [RuntimeforBedrockDataAutomation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_data_automation_runtime/)
  service.
- `types-aiobotocore-lite[bedrock-runtime]` - Type annotations for
  [BedrockRuntime](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_runtime/)
  service.
- `types-aiobotocore-lite[billing]` - Type annotations for
  [Billing](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_billing/)
  service.
- `types-aiobotocore-lite[billingconductor]` - Type annotations for
  [BillingConductor](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_billingconductor/)
  service.
- `types-aiobotocore-lite[braket]` - Type annotations for
  [Braket](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_braket/)
  service.
- `types-aiobotocore-lite[budgets]` - Type annotations for
  [Budgets](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_budgets/)
  service.
- `types-aiobotocore-lite[ce]` - Type annotations for
  [CostExplorer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ce/)
  service.
- `types-aiobotocore-lite[chatbot]` - Type annotations for
  [Chatbot](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_chatbot/)
  service.
- `types-aiobotocore-lite[chime]` - Type annotations for
  [Chime](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_chime/)
  service.
- `types-aiobotocore-lite[chime-sdk-identity]` - Type annotations for
  [ChimeSDKIdentity](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_chime_sdk_identity/)
  service.
- `types-aiobotocore-lite[chime-sdk-media-pipelines]` - Type annotations for
  [ChimeSDKMediaPipelines](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_chime_sdk_media_pipelines/)
  service.
- `types-aiobotocore-lite[chime-sdk-meetings]` - Type annotations for
  [ChimeSDKMeetings](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_chime_sdk_meetings/)
  service.
- `types-aiobotocore-lite[chime-sdk-messaging]` - Type annotations for
  [ChimeSDKMessaging](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_chime_sdk_messaging/)
  service.
- `types-aiobotocore-lite[chime-sdk-voice]` - Type annotations for
  [ChimeSDKVoice](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_chime_sdk_voice/)
  service.
- `types-aiobotocore-lite[cleanrooms]` - Type annotations for
  [CleanRoomsService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cleanrooms/)
  service.
- `types-aiobotocore-lite[cleanroomsml]` - Type annotations for
  [CleanRoomsML](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cleanroomsml/)
  service.
- `types-aiobotocore-lite[cloud9]` - Type annotations for
  [Cloud9](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloud9/)
  service.
- `types-aiobotocore-lite[cloudcontrol]` - Type annotations for
  [CloudControlApi](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudcontrol/)
  service.
- `types-aiobotocore-lite[clouddirectory]` - Type annotations for
  [CloudDirectory](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_clouddirectory/)
  service.
- `types-aiobotocore-lite[cloudformation]` - Type annotations for
  [CloudFormation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudformation/)
  service.
- `types-aiobotocore-lite[cloudfront]` - Type annotations for
  [CloudFront](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/)
  service.
- `types-aiobotocore-lite[cloudfront-keyvaluestore]` - Type annotations for
  [CloudFrontKeyValueStore](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront_keyvaluestore/)
  service.
- `types-aiobotocore-lite[cloudhsm]` - Type annotations for
  [CloudHSM](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudhsm/)
  service.
- `types-aiobotocore-lite[cloudhsmv2]` - Type annotations for
  [CloudHSMV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudhsmv2/)
  service.
- `types-aiobotocore-lite[cloudsearch]` - Type annotations for
  [CloudSearch](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudsearch/)
  service.
- `types-aiobotocore-lite[cloudsearchdomain]` - Type annotations for
  [CloudSearchDomain](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudsearchdomain/)
  service.
- `types-aiobotocore-lite[cloudtrail]` - Type annotations for
  [CloudTrail](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudtrail/)
  service.
- `types-aiobotocore-lite[cloudtrail-data]` - Type annotations for
  [CloudTrailDataService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudtrail_data/)
  service.
- `types-aiobotocore-lite[cloudwatch]` - Type annotations for
  [CloudWatch](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudwatch/)
  service.
- `types-aiobotocore-lite[codeartifact]` - Type annotations for
  [CodeArtifact](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codeartifact/)
  service.
- `types-aiobotocore-lite[codebuild]` - Type annotations for
  [CodeBuild](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codebuild/)
  service.
- `types-aiobotocore-lite[codecatalyst]` - Type annotations for
  [CodeCatalyst](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codecatalyst/)
  service.
- `types-aiobotocore-lite[codecommit]` - Type annotations for
  [CodeCommit](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codecommit/)
  service.
- `types-aiobotocore-lite[codeconnections]` - Type annotations for
  [CodeConnections](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codeconnections/)
  service.
- `types-aiobotocore-lite[codedeploy]` - Type annotations for
  [CodeDeploy](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codedeploy/)
  service.
- `types-aiobotocore-lite[codeguru-reviewer]` - Type annotations for
  [CodeGuruReviewer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codeguru_reviewer/)
  service.
- `types-aiobotocore-lite[codeguru-security]` - Type annotations for
  [CodeGuruSecurity](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codeguru_security/)
  service.
- `types-aiobotocore-lite[codeguruprofiler]` - Type annotations for
  [CodeGuruProfiler](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codeguruprofiler/)
  service.
- `types-aiobotocore-lite[codepipeline]` - Type annotations for
  [CodePipeline](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codepipeline/)
  service.
- `types-aiobotocore-lite[codestar-connections]` - Type annotations for
  [CodeStarconnections](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codestar_connections/)
  service.
- `types-aiobotocore-lite[codestar-notifications]` - Type annotations for
  [CodeStarNotifications](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_codestar_notifications/)
  service.
- `types-aiobotocore-lite[cognito-identity]` - Type annotations for
  [CognitoIdentity](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cognito_identity/)
  service.
- `types-aiobotocore-lite[cognito-idp]` - Type annotations for
  [CognitoIdentityProvider](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cognito_idp/)
  service.
- `types-aiobotocore-lite[cognito-sync]` - Type annotations for
  [CognitoSync](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cognito_sync/)
  service.
- `types-aiobotocore-lite[comprehend]` - Type annotations for
  [Comprehend](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_comprehend/)
  service.
- `types-aiobotocore-lite[comprehendmedical]` - Type annotations for
  [ComprehendMedical](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_comprehendmedical/)
  service.
- `types-aiobotocore-lite[compute-optimizer]` - Type annotations for
  [ComputeOptimizer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_compute_optimizer/)
  service.
- `types-aiobotocore-lite[config]` - Type annotations for
  [ConfigService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_config/)
  service.
- `types-aiobotocore-lite[connect]` - Type annotations for
  [Connect](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_connect/)
  service.
- `types-aiobotocore-lite[connect-contact-lens]` - Type annotations for
  [ConnectContactLens](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_connect_contact_lens/)
  service.
- `types-aiobotocore-lite[connectcampaigns]` - Type annotations for
  [ConnectCampaignService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_connectcampaigns/)
  service.
- `types-aiobotocore-lite[connectcampaignsv2]` - Type annotations for
  [ConnectCampaignServiceV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_connectcampaignsv2/)
  service.
- `types-aiobotocore-lite[connectcases]` - Type annotations for
  [ConnectCases](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_connectcases/)
  service.
- `types-aiobotocore-lite[connectparticipant]` - Type annotations for
  [ConnectParticipant](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_connectparticipant/)
  service.
- `types-aiobotocore-lite[controlcatalog]` - Type annotations for
  [ControlCatalog](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_controlcatalog/)
  service.
- `types-aiobotocore-lite[controltower]` - Type annotations for
  [ControlTower](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_controltower/)
  service.
- `types-aiobotocore-lite[cost-optimization-hub]` - Type annotations for
  [CostOptimizationHub](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cost_optimization_hub/)
  service.
- `types-aiobotocore-lite[cur]` - Type annotations for
  [CostandUsageReportService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cur/)
  service.
- `types-aiobotocore-lite[customer-profiles]` - Type annotations for
  [CustomerProfiles](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_customer_profiles/)
  service.
- `types-aiobotocore-lite[databrew]` - Type annotations for
  [GlueDataBrew](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_databrew/)
  service.
- `types-aiobotocore-lite[dataexchange]` - Type annotations for
  [DataExchange](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dataexchange/)
  service.
- `types-aiobotocore-lite[datapipeline]` - Type annotations for
  [DataPipeline](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_datapipeline/)
  service.
- `types-aiobotocore-lite[datasync]` - Type annotations for
  [DataSync](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_datasync/)
  service.
- `types-aiobotocore-lite[datazone]` - Type annotations for
  [DataZone](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_datazone/)
  service.
- `types-aiobotocore-lite[dax]` - Type annotations for
  [DAX](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dax/)
  service.
- `types-aiobotocore-lite[deadline]` - Type annotations for
  [DeadlineCloud](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_deadline/)
  service.
- `types-aiobotocore-lite[detective]` - Type annotations for
  [Detective](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_detective/)
  service.
- `types-aiobotocore-lite[devicefarm]` - Type annotations for
  [DeviceFarm](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_devicefarm/)
  service.
- `types-aiobotocore-lite[devops-guru]` - Type annotations for
  [DevOpsGuru](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_devops_guru/)
  service.
- `types-aiobotocore-lite[directconnect]` - Type annotations for
  [DirectConnect](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_directconnect/)
  service.
- `types-aiobotocore-lite[discovery]` - Type annotations for
  [ApplicationDiscoveryService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_discovery/)
  service.
- `types-aiobotocore-lite[dlm]` - Type annotations for
  [DLM](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dlm/)
  service.
- `types-aiobotocore-lite[dms]` - Type annotations for
  [DatabaseMigrationService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dms/)
  service.
- `types-aiobotocore-lite[docdb]` - Type annotations for
  [DocDB](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_docdb/)
  service.
- `types-aiobotocore-lite[docdb-elastic]` - Type annotations for
  [DocDBElastic](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_docdb_elastic/)
  service.
- `types-aiobotocore-lite[drs]` - Type annotations for
  [Drs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_drs/)
  service.
- `types-aiobotocore-lite[ds]` - Type annotations for
  [DirectoryService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ds/)
  service.
- `types-aiobotocore-lite[ds-data]` - Type annotations for
  [DirectoryServiceData](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ds_data/)
  service.
- `types-aiobotocore-lite[dsql]` - Type annotations for
  [AuroraDSQL](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dsql/)
  service.
- `types-aiobotocore-lite[dynamodb]` - Type annotations for
  [DynamoDB](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dynamodb/)
  service.
- `types-aiobotocore-lite[dynamodbstreams]` - Type annotations for
  [DynamoDBStreams](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dynamodbstreams/)
  service.
- `types-aiobotocore-lite[ebs]` - Type annotations for
  [EBS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ebs/)
  service.
- `types-aiobotocore-lite[ec2]` - Type annotations for
  [EC2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ec2/)
  service.
- `types-aiobotocore-lite[ec2-instance-connect]` - Type annotations for
  [EC2InstanceConnect](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ec2_instance_connect/)
  service.
- `types-aiobotocore-lite[ecr]` - Type annotations for
  [ECR](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ecr/)
  service.
- `types-aiobotocore-lite[ecr-public]` - Type annotations for
  [ECRPublic](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ecr_public/)
  service.
- `types-aiobotocore-lite[ecs]` - Type annotations for
  [ECS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ecs/)
  service.
- `types-aiobotocore-lite[efs]` - Type annotations for
  [EFS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_efs/)
  service.
- `types-aiobotocore-lite[eks]` - Type annotations for
  [EKS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_eks/)
  service.
- `types-aiobotocore-lite[eks-auth]` - Type annotations for
  [EKSAuth](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_eks_auth/)
  service.
- `types-aiobotocore-lite[elasticache]` - Type annotations for
  [ElastiCache](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_elasticache/)
  service.
- `types-aiobotocore-lite[elasticbeanstalk]` - Type annotations for
  [ElasticBeanstalk](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_elasticbeanstalk/)
  service.
- `types-aiobotocore-lite[elastictranscoder]` - Type annotations for
  [ElasticTranscoder](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_elastictranscoder/)
  service.
- `types-aiobotocore-lite[elb]` - Type annotations for
  [ElasticLoadBalancing](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_elb/)
  service.
- `types-aiobotocore-lite[elbv2]` - Type annotations for
  [ElasticLoadBalancingv2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_elbv2/)
  service.
- `types-aiobotocore-lite[emr]` - Type annotations for
  [EMR](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_emr/)
  service.
- `types-aiobotocore-lite[emr-containers]` - Type annotations for
  [EMRContainers](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_emr_containers/)
  service.
- `types-aiobotocore-lite[emr-serverless]` - Type annotations for
  [EMRServerless](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_emr_serverless/)
  service.
- `types-aiobotocore-lite[entityresolution]` - Type annotations for
  [EntityResolution](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_entityresolution/)
  service.
- `types-aiobotocore-lite[es]` - Type annotations for
  [ElasticsearchService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_es/)
  service.
- `types-aiobotocore-lite[events]` - Type annotations for
  [EventBridge](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_events/)
  service.
- `types-aiobotocore-lite[evidently]` - Type annotations for
  [CloudWatchEvidently](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_evidently/)
  service.
- `types-aiobotocore-lite[evs]` - Type annotations for
  [EVS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_evs/)
  service.
- `types-aiobotocore-lite[finspace]` - Type annotations for
  [Finspace](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_finspace/)
  service.
- `types-aiobotocore-lite[finspace-data]` - Type annotations for
  [FinSpaceData](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_finspace_data/)
  service.
- `types-aiobotocore-lite[firehose]` - Type annotations for
  [Firehose](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_firehose/)
  service.
- `types-aiobotocore-lite[fis]` - Type annotations for
  [FIS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_fis/)
  service.
- `types-aiobotocore-lite[fms]` - Type annotations for
  [FMS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_fms/)
  service.
- `types-aiobotocore-lite[forecast]` - Type annotations for
  [ForecastService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_forecast/)
  service.
- `types-aiobotocore-lite[forecastquery]` - Type annotations for
  [ForecastQueryService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_forecastquery/)
  service.
- `types-aiobotocore-lite[frauddetector]` - Type annotations for
  [FraudDetector](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_frauddetector/)
  service.
- `types-aiobotocore-lite[freetier]` - Type annotations for
  [FreeTier](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_freetier/)
  service.
- `types-aiobotocore-lite[fsx]` - Type annotations for
  [FSx](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_fsx/)
  service.
- `types-aiobotocore-lite[gamelift]` - Type annotations for
  [GameLift](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_gamelift/)
  service.
- `types-aiobotocore-lite[gameliftstreams]` - Type annotations for
  [GameLiftStreams](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_gameliftstreams/)
  service.
- `types-aiobotocore-lite[geo-maps]` - Type annotations for
  [LocationServiceMapsV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_geo_maps/)
  service.
- `types-aiobotocore-lite[geo-places]` - Type annotations for
  [LocationServicePlacesV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_geo_places/)
  service.
- `types-aiobotocore-lite[geo-routes]` - Type annotations for
  [LocationServiceRoutesV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_geo_routes/)
  service.
- `types-aiobotocore-lite[glacier]` - Type annotations for
  [Glacier](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_glacier/)
  service.
- `types-aiobotocore-lite[globalaccelerator]` - Type annotations for
  [GlobalAccelerator](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_globalaccelerator/)
  service.
- `types-aiobotocore-lite[glue]` - Type annotations for
  [Glue](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_glue/)
  service.
- `types-aiobotocore-lite[grafana]` - Type annotations for
  [ManagedGrafana](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_grafana/)
  service.
- `types-aiobotocore-lite[greengrass]` - Type annotations for
  [Greengrass](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_greengrass/)
  service.
- `types-aiobotocore-lite[greengrassv2]` - Type annotations for
  [GreengrassV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_greengrassv2/)
  service.
- `types-aiobotocore-lite[groundstation]` - Type annotations for
  [GroundStation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_groundstation/)
  service.
- `types-aiobotocore-lite[guardduty]` - Type annotations for
  [GuardDuty](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_guardduty/)
  service.
- `types-aiobotocore-lite[health]` - Type annotations for
  [Health](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_health/)
  service.
- `types-aiobotocore-lite[healthlake]` - Type annotations for
  [HealthLake](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_healthlake/)
  service.
- `types-aiobotocore-lite[iam]` - Type annotations for
  [IAM](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iam/)
  service.
- `types-aiobotocore-lite[identitystore]` - Type annotations for
  [IdentityStore](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_identitystore/)
  service.
- `types-aiobotocore-lite[imagebuilder]` - Type annotations for
  [Imagebuilder](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_imagebuilder/)
  service.
- `types-aiobotocore-lite[importexport]` - Type annotations for
  [ImportExport](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_importexport/)
  service.
- `types-aiobotocore-lite[inspector]` - Type annotations for
  [Inspector](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_inspector/)
  service.
- `types-aiobotocore-lite[inspector-scan]` - Type annotations for
  [Inspectorscan](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_inspector_scan/)
  service.
- `types-aiobotocore-lite[inspector2]` - Type annotations for
  [Inspector2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_inspector2/)
  service.
- `types-aiobotocore-lite[internetmonitor]` - Type annotations for
  [CloudWatchInternetMonitor](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_internetmonitor/)
  service.
- `types-aiobotocore-lite[invoicing]` - Type annotations for
  [Invoicing](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_invoicing/)
  service.
- `types-aiobotocore-lite[iot]` - Type annotations for
  [IoT](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iot/)
  service.
- `types-aiobotocore-lite[iot-data]` - Type annotations for
  [IoTDataPlane](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iot_data/)
  service.
- `types-aiobotocore-lite[iot-jobs-data]` - Type annotations for
  [IoTJobsDataPlane](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iot_jobs_data/)
  service.
- `types-aiobotocore-lite[iot-managed-integrations]` - Type annotations for
  [ManagedintegrationsforIoTDeviceManagement](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iot_managed_integrations/)
  service.
- `types-aiobotocore-lite[iotanalytics]` - Type annotations for
  [IoTAnalytics](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotanalytics/)
  service.
- `types-aiobotocore-lite[iotdeviceadvisor]` - Type annotations for
  [IoTDeviceAdvisor](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotdeviceadvisor/)
  service.
- `types-aiobotocore-lite[iotevents]` - Type annotations for
  [IoTEvents](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotevents/)
  service.
- `types-aiobotocore-lite[iotevents-data]` - Type annotations for
  [IoTEventsData](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotevents_data/)
  service.
- `types-aiobotocore-lite[iotfleethub]` - Type annotations for
  [IoTFleetHub](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotfleethub/)
  service.
- `types-aiobotocore-lite[iotfleetwise]` - Type annotations for
  [IoTFleetWise](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotfleetwise/)
  service.
- `types-aiobotocore-lite[iotsecuretunneling]` - Type annotations for
  [IoTSecureTunneling](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotsecuretunneling/)
  service.
- `types-aiobotocore-lite[iotsitewise]` - Type annotations for
  [IoTSiteWise](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotsitewise/)
  service.
- `types-aiobotocore-lite[iotthingsgraph]` - Type annotations for
  [IoTThingsGraph](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotthingsgraph/)
  service.
- `types-aiobotocore-lite[iottwinmaker]` - Type annotations for
  [IoTTwinMaker](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iottwinmaker/)
  service.
- `types-aiobotocore-lite[iotwireless]` - Type annotations for
  [IoTWireless](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_iotwireless/)
  service.
- `types-aiobotocore-lite[ivs]` - Type annotations for
  [IVS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs/)
  service.
- `types-aiobotocore-lite[ivs-realtime]` - Type annotations for
  [Ivsrealtime](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/)
  service.
- `types-aiobotocore-lite[ivschat]` - Type annotations for
  [Ivschat](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivschat/)
  service.
- `types-aiobotocore-lite[kafka]` - Type annotations for
  [Kafka](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kafka/)
  service.
- `types-aiobotocore-lite[kafkaconnect]` - Type annotations for
  [KafkaConnect](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kafkaconnect/)
  service.
- `types-aiobotocore-lite[kendra]` - Type annotations for
  [Kendra](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kendra/)
  service.
- `types-aiobotocore-lite[kendra-ranking]` - Type annotations for
  [KendraRanking](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kendra_ranking/)
  service.
- `types-aiobotocore-lite[keyspaces]` - Type annotations for
  [Keyspaces](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_keyspaces/)
  service.
- `types-aiobotocore-lite[keyspacesstreams]` - Type annotations for
  [KeyspacesStreams](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_keyspacesstreams/)
  service.
- `types-aiobotocore-lite[kinesis]` - Type annotations for
  [Kinesis](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kinesis/)
  service.
- `types-aiobotocore-lite[kinesis-video-archived-media]` - Type annotations for
  [KinesisVideoArchivedMedia](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kinesis_video_archived_media/)
  service.
- `types-aiobotocore-lite[kinesis-video-media]` - Type annotations for
  [KinesisVideoMedia](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kinesis_video_media/)
  service.
- `types-aiobotocore-lite[kinesis-video-signaling]` - Type annotations for
  [KinesisVideoSignalingChannels](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kinesis_video_signaling/)
  service.
- `types-aiobotocore-lite[kinesis-video-webrtc-storage]` - Type annotations for
  [KinesisVideoWebRTCStorage](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kinesis_video_webrtc_storage/)
  service.
- `types-aiobotocore-lite[kinesisanalytics]` - Type annotations for
  [KinesisAnalytics](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kinesisanalytics/)
  service.
- `types-aiobotocore-lite[kinesisanalyticsv2]` - Type annotations for
  [KinesisAnalyticsV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kinesisanalyticsv2/)
  service.
- `types-aiobotocore-lite[kinesisvideo]` - Type annotations for
  [KinesisVideo](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kinesisvideo/)
  service.
- `types-aiobotocore-lite[kms]` - Type annotations for
  [KMS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_kms/)
  service.
- `types-aiobotocore-lite[lakeformation]` - Type annotations for
  [LakeFormation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lakeformation/)
  service.
- `types-aiobotocore-lite[lambda]` - Type annotations for
  [Lambda](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lambda/)
  service.
- `types-aiobotocore-lite[launch-wizard]` - Type annotations for
  [LaunchWizard](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_launch_wizard/)
  service.
- `types-aiobotocore-lite[lex-models]` - Type annotations for
  [LexModelBuildingService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lex_models/)
  service.
- `types-aiobotocore-lite[lex-runtime]` - Type annotations for
  [LexRuntimeService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lex_runtime/)
  service.
- `types-aiobotocore-lite[lexv2-models]` - Type annotations for
  [LexModelsV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lexv2_models/)
  service.
- `types-aiobotocore-lite[lexv2-runtime]` - Type annotations for
  [LexRuntimeV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lexv2_runtime/)
  service.
- `types-aiobotocore-lite[license-manager]` - Type annotations for
  [LicenseManager](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_license_manager/)
  service.
- `types-aiobotocore-lite[license-manager-linux-subscriptions]` - Type
  annotations for
  [LicenseManagerLinuxSubscriptions](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_license_manager_linux_subscriptions/)
  service.
- `types-aiobotocore-lite[license-manager-user-subscriptions]` - Type
  annotations for
  [LicenseManagerUserSubscriptions](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_license_manager_user_subscriptions/)
  service.
- `types-aiobotocore-lite[lightsail]` - Type annotations for
  [Lightsail](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lightsail/)
  service.
- `types-aiobotocore-lite[location]` - Type annotations for
  [LocationService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_location/)
  service.
- `types-aiobotocore-lite[logs]` - Type annotations for
  [CloudWatchLogs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_logs/)
  service.
- `types-aiobotocore-lite[lookoutequipment]` - Type annotations for
  [LookoutEquipment](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lookoutequipment/)
  service.
- `types-aiobotocore-lite[lookoutmetrics]` - Type annotations for
  [LookoutMetrics](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lookoutmetrics/)
  service.
- `types-aiobotocore-lite[lookoutvision]` - Type annotations for
  [LookoutforVision](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_lookoutvision/)
  service.
- `types-aiobotocore-lite[m2]` - Type annotations for
  [MainframeModernization](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_m2/)
  service.
- `types-aiobotocore-lite[machinelearning]` - Type annotations for
  [MachineLearning](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_machinelearning/)
  service.
- `types-aiobotocore-lite[macie2]` - Type annotations for
  [Macie2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_macie2/)
  service.
- `types-aiobotocore-lite[mailmanager]` - Type annotations for
  [MailManager](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mailmanager/)
  service.
- `types-aiobotocore-lite[managedblockchain]` - Type annotations for
  [ManagedBlockchain](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_managedblockchain/)
  service.
- `types-aiobotocore-lite[managedblockchain-query]` - Type annotations for
  [ManagedBlockchainQuery](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_managedblockchain_query/)
  service.
- `types-aiobotocore-lite[marketplace-agreement]` - Type annotations for
  [AgreementService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_marketplace_agreement/)
  service.
- `types-aiobotocore-lite[marketplace-catalog]` - Type annotations for
  [MarketplaceCatalog](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_marketplace_catalog/)
  service.
- `types-aiobotocore-lite[marketplace-deployment]` - Type annotations for
  [MarketplaceDeploymentService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_marketplace_deployment/)
  service.
- `types-aiobotocore-lite[marketplace-entitlement]` - Type annotations for
  [MarketplaceEntitlementService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_marketplace_entitlement/)
  service.
- `types-aiobotocore-lite[marketplace-reporting]` - Type annotations for
  [MarketplaceReportingService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_marketplace_reporting/)
  service.
- `types-aiobotocore-lite[marketplacecommerceanalytics]` - Type annotations for
  [MarketplaceCommerceAnalytics](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_marketplacecommerceanalytics/)
  service.
- `types-aiobotocore-lite[mediaconnect]` - Type annotations for
  [MediaConnect](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mediaconnect/)
  service.
- `types-aiobotocore-lite[mediaconvert]` - Type annotations for
  [MediaConvert](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mediaconvert/)
  service.
- `types-aiobotocore-lite[medialive]` - Type annotations for
  [MediaLive](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_medialive/)
  service.
- `types-aiobotocore-lite[mediapackage]` - Type annotations for
  [MediaPackage](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mediapackage/)
  service.
- `types-aiobotocore-lite[mediapackage-vod]` - Type annotations for
  [MediaPackageVod](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mediapackage_vod/)
  service.
- `types-aiobotocore-lite[mediapackagev2]` - Type annotations for
  [Mediapackagev2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mediapackagev2/)
  service.
- `types-aiobotocore-lite[mediastore]` - Type annotations for
  [MediaStore](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mediastore/)
  service.
- `types-aiobotocore-lite[mediastore-data]` - Type annotations for
  [MediaStoreData](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mediastore_data/)
  service.
- `types-aiobotocore-lite[mediatailor]` - Type annotations for
  [MediaTailor](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mediatailor/)
  service.
- `types-aiobotocore-lite[medical-imaging]` - Type annotations for
  [HealthImaging](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_medical_imaging/)
  service.
- `types-aiobotocore-lite[memorydb]` - Type annotations for
  [MemoryDB](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_memorydb/)
  service.
- `types-aiobotocore-lite[meteringmarketplace]` - Type annotations for
  [MarketplaceMetering](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_meteringmarketplace/)
  service.
- `types-aiobotocore-lite[mgh]` - Type annotations for
  [MigrationHub](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mgh/)
  service.
- `types-aiobotocore-lite[mgn]` - Type annotations for
  [Mgn](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mgn/)
  service.
- `types-aiobotocore-lite[migration-hub-refactor-spaces]` - Type annotations
  for
  [MigrationHubRefactorSpaces](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_migration_hub_refactor_spaces/)
  service.
- `types-aiobotocore-lite[migrationhub-config]` - Type annotations for
  [MigrationHubConfig](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_migrationhub_config/)
  service.
- `types-aiobotocore-lite[migrationhuborchestrator]` - Type annotations for
  [MigrationHubOrchestrator](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_migrationhuborchestrator/)
  service.
- `types-aiobotocore-lite[migrationhubstrategy]` - Type annotations for
  [MigrationHubStrategyRecommendations](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_migrationhubstrategy/)
  service.
- `types-aiobotocore-lite[mpa]` - Type annotations for
  [MultipartyApproval](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mpa/)
  service.
- `types-aiobotocore-lite[mq]` - Type annotations for
  [MQ](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mq/)
  service.
- `types-aiobotocore-lite[mturk]` - Type annotations for
  [MTurk](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mturk/)
  service.
- `types-aiobotocore-lite[mwaa]` - Type annotations for
  [MWAA](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_mwaa/)
  service.
- `types-aiobotocore-lite[neptune]` - Type annotations for
  [Neptune](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune/)
  service.
- `types-aiobotocore-lite[neptune-graph]` - Type annotations for
  [NeptuneGraph](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/)
  service.
- `types-aiobotocore-lite[neptunedata]` - Type annotations for
  [NeptuneData](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptunedata/)
  service.
- `types-aiobotocore-lite[network-firewall]` - Type annotations for
  [NetworkFirewall](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_network_firewall/)
  service.
- `types-aiobotocore-lite[networkflowmonitor]` - Type annotations for
  [NetworkFlowMonitor](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_networkflowmonitor/)
  service.
- `types-aiobotocore-lite[networkmanager]` - Type annotations for
  [NetworkManager](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_networkmanager/)
  service.
- `types-aiobotocore-lite[networkmonitor]` - Type annotations for
  [CloudWatchNetworkMonitor](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_networkmonitor/)
  service.
- `types-aiobotocore-lite[notifications]` - Type annotations for
  [UserNotifications](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_notifications/)
  service.
- `types-aiobotocore-lite[notificationscontacts]` - Type annotations for
  [UserNotificationsContacts](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_notificationscontacts/)
  service.
- `types-aiobotocore-lite[oam]` - Type annotations for
  [CloudWatchObservabilityAccessManager](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_oam/)
  service.
- `types-aiobotocore-lite[observabilityadmin]` - Type annotations for
  [CloudWatchObservabilityAdminService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_observabilityadmin/)
  service.
- `types-aiobotocore-lite[odb]` - Type annotations for
  [Odb](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_odb/)
  service.
- `types-aiobotocore-lite[omics]` - Type annotations for
  [Omics](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/)
  service.
- `types-aiobotocore-lite[opensearch]` - Type annotations for
  [OpenSearchService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_opensearch/)
  service.
- `types-aiobotocore-lite[opensearchserverless]` - Type annotations for
  [OpenSearchServiceServerless](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_opensearchserverless/)
  service.
- `types-aiobotocore-lite[opsworks]` - Type annotations for
  [OpsWorks](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_opsworks/)
  service.
- `types-aiobotocore-lite[opsworkscm]` - Type annotations for
  [OpsWorksCM](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_opsworkscm/)
  service.
- `types-aiobotocore-lite[organizations]` - Type annotations for
  [Organizations](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_organizations/)
  service.
- `types-aiobotocore-lite[osis]` - Type annotations for
  [OpenSearchIngestion](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_osis/)
  service.
- `types-aiobotocore-lite[outposts]` - Type annotations for
  [Outposts](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_outposts/)
  service.
- `types-aiobotocore-lite[panorama]` - Type annotations for
  [Panorama](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_panorama/)
  service.
- `types-aiobotocore-lite[partnercentral-selling]` - Type annotations for
  [PartnerCentralSellingAPI](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_partnercentral_selling/)
  service.
- `types-aiobotocore-lite[payment-cryptography]` - Type annotations for
  [PaymentCryptographyControlPlane](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography/)
  service.
- `types-aiobotocore-lite[payment-cryptography-data]` - Type annotations for
  [PaymentCryptographyDataPlane](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/)
  service.
- `types-aiobotocore-lite[pca-connector-ad]` - Type annotations for
  [PcaConnectorAd](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pca_connector_ad/)
  service.
- `types-aiobotocore-lite[pca-connector-scep]` - Type annotations for
  [PrivateCAConnectorforSCEP](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pca_connector_scep/)
  service.
- `types-aiobotocore-lite[pcs]` - Type annotations for
  [ParallelComputingService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pcs/)
  service.
- `types-aiobotocore-lite[personalize]` - Type annotations for
  [Personalize](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_personalize/)
  service.
- `types-aiobotocore-lite[personalize-events]` - Type annotations for
  [PersonalizeEvents](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_personalize_events/)
  service.
- `types-aiobotocore-lite[personalize-runtime]` - Type annotations for
  [PersonalizeRuntime](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_personalize_runtime/)
  service.
- `types-aiobotocore-lite[pi]` - Type annotations for
  [PI](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pi/)
  service.
- `types-aiobotocore-lite[pinpoint]` - Type annotations for
  [Pinpoint](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pinpoint/)
  service.
- `types-aiobotocore-lite[pinpoint-email]` - Type annotations for
  [PinpointEmail](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pinpoint_email/)
  service.
- `types-aiobotocore-lite[pinpoint-sms-voice]` - Type annotations for
  [PinpointSMSVoice](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pinpoint_sms_voice/)
  service.
- `types-aiobotocore-lite[pinpoint-sms-voice-v2]` - Type annotations for
  [PinpointSMSVoiceV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pinpoint_sms_voice_v2/)
  service.
- `types-aiobotocore-lite[pipes]` - Type annotations for
  [EventBridgePipes](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pipes/)
  service.
- `types-aiobotocore-lite[polly]` - Type annotations for
  [Polly](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_polly/)
  service.
- `types-aiobotocore-lite[pricing]` - Type annotations for
  [Pricing](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_pricing/)
  service.
- `types-aiobotocore-lite[proton]` - Type annotations for
  [Proton](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_proton/)
  service.
- `types-aiobotocore-lite[qapps]` - Type annotations for
  [QApps](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_qapps/)
  service.
- `types-aiobotocore-lite[qbusiness]` - Type annotations for
  [QBusiness](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_qbusiness/)
  service.
- `types-aiobotocore-lite[qconnect]` - Type annotations for
  [QConnect](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_qconnect/)
  service.
- `types-aiobotocore-lite[qldb]` - Type annotations for
  [QLDB](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_qldb/)
  service.
- `types-aiobotocore-lite[qldb-session]` - Type annotations for
  [QLDBSession](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_qldb_session/)
  service.
- `types-aiobotocore-lite[quicksight]` - Type annotations for
  [QuickSight](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_quicksight/)
  service.
- `types-aiobotocore-lite[ram]` - Type annotations for
  [RAM](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ram/)
  service.
- `types-aiobotocore-lite[rbin]` - Type annotations for
  [RecycleBin](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_rbin/)
  service.
- `types-aiobotocore-lite[rds]` - Type annotations for
  [RDS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_rds/)
  service.
- `types-aiobotocore-lite[rds-data]` - Type annotations for
  [RDSDataService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_rds_data/)
  service.
- `types-aiobotocore-lite[redshift]` - Type annotations for
  [Redshift](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_redshift/)
  service.
- `types-aiobotocore-lite[redshift-data]` - Type annotations for
  [RedshiftDataAPIService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_redshift_data/)
  service.
- `types-aiobotocore-lite[redshift-serverless]` - Type annotations for
  [RedshiftServerless](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_redshift_serverless/)
  service.
- `types-aiobotocore-lite[rekognition]` - Type annotations for
  [Rekognition](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_rekognition/)
  service.
- `types-aiobotocore-lite[repostspace]` - Type annotations for
  [RePostPrivate](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_repostspace/)
  service.
- `types-aiobotocore-lite[resiliencehub]` - Type annotations for
  [ResilienceHub](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_resiliencehub/)
  service.
- `types-aiobotocore-lite[resource-explorer-2]` - Type annotations for
  [ResourceExplorer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_resource_explorer_2/)
  service.
- `types-aiobotocore-lite[resource-groups]` - Type annotations for
  [ResourceGroups](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_resource_groups/)
  service.
- `types-aiobotocore-lite[resourcegroupstaggingapi]` - Type annotations for
  [ResourceGroupsTaggingAPI](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_resourcegroupstaggingapi/)
  service.
- `types-aiobotocore-lite[robomaker]` - Type annotations for
  [RoboMaker](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_robomaker/)
  service.
- `types-aiobotocore-lite[rolesanywhere]` - Type annotations for
  [IAMRolesAnywhere](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_rolesanywhere/)
  service.
- `types-aiobotocore-lite[route53]` - Type annotations for
  [Route53](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_route53/)
  service.
- `types-aiobotocore-lite[route53-recovery-cluster]` - Type annotations for
  [Route53RecoveryCluster](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_route53_recovery_cluster/)
  service.
- `types-aiobotocore-lite[route53-recovery-control-config]` - Type annotations
  for
  [Route53RecoveryControlConfig](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_route53_recovery_control_config/)
  service.
- `types-aiobotocore-lite[route53-recovery-readiness]` - Type annotations for
  [Route53RecoveryReadiness](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_route53_recovery_readiness/)
  service.
- `types-aiobotocore-lite[route53domains]` - Type annotations for
  [Route53Domains](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_route53domains/)
  service.
- `types-aiobotocore-lite[route53profiles]` - Type annotations for
  [Route53Profiles](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_route53profiles/)
  service.
- `types-aiobotocore-lite[route53resolver]` - Type annotations for
  [Route53Resolver](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_route53resolver/)
  service.
- `types-aiobotocore-lite[rum]` - Type annotations for
  [CloudWatchRUM](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_rum/)
  service.
- `types-aiobotocore-lite[s3]` - Type annotations for
  [S3](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_s3/)
  service.
- `types-aiobotocore-lite[s3control]` - Type annotations for
  [S3Control](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_s3control/)
  service.
- `types-aiobotocore-lite[s3outposts]` - Type annotations for
  [S3Outposts](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_s3outposts/)
  service.
- `types-aiobotocore-lite[s3tables]` - Type annotations for
  [S3Tables](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_s3tables/)
  service.
- `types-aiobotocore-lite[s3vectors]` - Type annotations for
  [S3Vectors](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_s3vectors/)
  service.
- `types-aiobotocore-lite[sagemaker]` - Type annotations for
  [SageMaker](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker/)
  service.
- `types-aiobotocore-lite[sagemaker-a2i-runtime]` - Type annotations for
  [AugmentedAIRuntime](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_a2i_runtime/)
  service.
- `types-aiobotocore-lite[sagemaker-edge]` - Type annotations for
  [SagemakerEdgeManager](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_edge/)
  service.
- `types-aiobotocore-lite[sagemaker-featurestore-runtime]` - Type annotations
  for
  [SageMakerFeatureStoreRuntime](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_featurestore_runtime/)
  service.
- `types-aiobotocore-lite[sagemaker-geospatial]` - Type annotations for
  [SageMakergeospatialcapabilities](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_geospatial/)
  service.
- `types-aiobotocore-lite[sagemaker-metrics]` - Type annotations for
  [SageMakerMetrics](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_metrics/)
  service.
- `types-aiobotocore-lite[sagemaker-runtime]` - Type annotations for
  [SageMakerRuntime](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/)
  service.
- `types-aiobotocore-lite[savingsplans]` - Type annotations for
  [SavingsPlans](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_savingsplans/)
  service.
- `types-aiobotocore-lite[scheduler]` - Type annotations for
  [EventBridgeScheduler](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_scheduler/)
  service.
- `types-aiobotocore-lite[schemas]` - Type annotations for
  [Schemas](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_schemas/)
  service.
- `types-aiobotocore-lite[sdb]` - Type annotations for
  [SimpleDB](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sdb/)
  service.
- `types-aiobotocore-lite[secretsmanager]` - Type annotations for
  [SecretsManager](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_secretsmanager/)
  service.
- `types-aiobotocore-lite[security-ir]` - Type annotations for
  [SecurityIncidentResponse](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_security_ir/)
  service.
- `types-aiobotocore-lite[securityhub]` - Type annotations for
  [SecurityHub](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_securityhub/)
  service.
- `types-aiobotocore-lite[securitylake]` - Type annotations for
  [SecurityLake](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_securitylake/)
  service.
- `types-aiobotocore-lite[serverlessrepo]` - Type annotations for
  [ServerlessApplicationRepository](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_serverlessrepo/)
  service.
- `types-aiobotocore-lite[service-quotas]` - Type annotations for
  [ServiceQuotas](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_service_quotas/)
  service.
- `types-aiobotocore-lite[servicecatalog]` - Type annotations for
  [ServiceCatalog](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_servicecatalog/)
  service.
- `types-aiobotocore-lite[servicecatalog-appregistry]` - Type annotations for
  [AppRegistry](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_servicecatalog_appregistry/)
  service.
- `types-aiobotocore-lite[servicediscovery]` - Type annotations for
  [ServiceDiscovery](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_servicediscovery/)
  service.
- `types-aiobotocore-lite[ses]` - Type annotations for
  [SES](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ses/)
  service.
- `types-aiobotocore-lite[sesv2]` - Type annotations for
  [SESV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sesv2/)
  service.
- `types-aiobotocore-lite[shield]` - Type annotations for
  [Shield](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_shield/)
  service.
- `types-aiobotocore-lite[signer]` - Type annotations for
  [Signer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_signer/)
  service.
- `types-aiobotocore-lite[simspaceweaver]` - Type annotations for
  [SimSpaceWeaver](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_simspaceweaver/)
  service.
- `types-aiobotocore-lite[sms]` - Type annotations for
  [SMS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sms/)
  service.
- `types-aiobotocore-lite[snow-device-management]` - Type annotations for
  [SnowDeviceManagement](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_snow_device_management/)
  service.
- `types-aiobotocore-lite[snowball]` - Type annotations for
  [Snowball](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_snowball/)
  service.
- `types-aiobotocore-lite[sns]` - Type annotations for
  [SNS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/)
  service.
- `types-aiobotocore-lite[socialmessaging]` - Type annotations for
  [EndUserMessagingSocial](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_socialmessaging/)
  service.
- `types-aiobotocore-lite[sqs]` - Type annotations for
  [SQS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sqs/)
  service.
- `types-aiobotocore-lite[ssm]` - Type annotations for
  [SSM](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm/)
  service.
- `types-aiobotocore-lite[ssm-contacts]` - Type annotations for
  [SSMContacts](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_contacts/)
  service.
- `types-aiobotocore-lite[ssm-guiconnect]` - Type annotations for
  [SSMGUIConnect](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_guiconnect/)
  service.
- `types-aiobotocore-lite[ssm-incidents]` - Type annotations for
  [SSMIncidents](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_incidents/)
  service.
- `types-aiobotocore-lite[ssm-quicksetup]` - Type annotations for
  [SystemsManagerQuickSetup](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_quicksetup/)
  service.
- `types-aiobotocore-lite[ssm-sap]` - Type annotations for
  [SsmSap](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/)
  service.
- `types-aiobotocore-lite[sso]` - Type annotations for
  [SSO](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sso/)
  service.
- `types-aiobotocore-lite[sso-admin]` - Type annotations for
  [SSOAdmin](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sso_admin/)
  service.
- `types-aiobotocore-lite[sso-oidc]` - Type annotations for
  [SSOOIDC](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sso_oidc/)
  service.
- `types-aiobotocore-lite[stepfunctions]` - Type annotations for
  [SFN](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_stepfunctions/)
  service.
- `types-aiobotocore-lite[storagegateway]` - Type annotations for
  [StorageGateway](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_storagegateway/)
  service.
- `types-aiobotocore-lite[sts]` - Type annotations for
  [STS](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sts/)
  service.
- `types-aiobotocore-lite[supplychain]` - Type annotations for
  [SupplyChain](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_supplychain/)
  service.
- `types-aiobotocore-lite[support]` - Type annotations for
  [Support](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_support/)
  service.
- `types-aiobotocore-lite[support-app]` - Type annotations for
  [SupportApp](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_support_app/)
  service.
- `types-aiobotocore-lite[swf]` - Type annotations for
  [SWF](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_swf/)
  service.
- `types-aiobotocore-lite[synthetics]` - Type annotations for
  [Synthetics](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_synthetics/)
  service.
- `types-aiobotocore-lite[taxsettings]` - Type annotations for
  [TaxSettings](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_taxsettings/)
  service.
- `types-aiobotocore-lite[textract]` - Type annotations for
  [Textract](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_textract/)
  service.
- `types-aiobotocore-lite[timestream-influxdb]` - Type annotations for
  [TimestreamInfluxDB](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_timestream_influxdb/)
  service.
- `types-aiobotocore-lite[timestream-query]` - Type annotations for
  [TimestreamQuery](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_timestream_query/)
  service.
- `types-aiobotocore-lite[timestream-write]` - Type annotations for
  [TimestreamWrite](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_timestream_write/)
  service.
- `types-aiobotocore-lite[tnb]` - Type annotations for
  [TelcoNetworkBuilder](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_tnb/)
  service.
- `types-aiobotocore-lite[transcribe]` - Type annotations for
  [TranscribeService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_transcribe/)
  service.
- `types-aiobotocore-lite[transfer]` - Type annotations for
  [Transfer](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_transfer/)
  service.
- `types-aiobotocore-lite[translate]` - Type annotations for
  [Translate](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_translate/)
  service.
- `types-aiobotocore-lite[trustedadvisor]` - Type annotations for
  [TrustedAdvisorPublicAPI](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_trustedadvisor/)
  service.
- `types-aiobotocore-lite[verifiedpermissions]` - Type annotations for
  [VerifiedPermissions](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_verifiedpermissions/)
  service.
- `types-aiobotocore-lite[voice-id]` - Type annotations for
  [VoiceID](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_voice_id/)
  service.
- `types-aiobotocore-lite[vpc-lattice]` - Type annotations for
  [VPCLattice](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_vpc_lattice/)
  service.
- `types-aiobotocore-lite[waf]` - Type annotations for
  [WAF](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_waf/)
  service.
- `types-aiobotocore-lite[waf-regional]` - Type annotations for
  [WAFRegional](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_waf_regional/)
  service.
- `types-aiobotocore-lite[wafv2]` - Type annotations for
  [WAFV2](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_wafv2/)
  service.
- `types-aiobotocore-lite[wellarchitected]` - Type annotations for
  [WellArchitected](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_wellarchitected/)
  service.
- `types-aiobotocore-lite[wisdom]` - Type annotations for
  [ConnectWisdomService](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_wisdom/)
  service.
- `types-aiobotocore-lite[workdocs]` - Type annotations for
  [WorkDocs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workdocs/)
  service.
- `types-aiobotocore-lite[workmail]` - Type annotations for
  [WorkMail](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workmail/)
  service.
- `types-aiobotocore-lite[workmailmessageflow]` - Type annotations for
  [WorkMailMessageFlow](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workmailmessageflow/)
  service.
- `types-aiobotocore-lite[workspaces]` - Type annotations for
  [WorkSpaces](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces/)
  service.
- `types-aiobotocore-lite[workspaces-instances]` - Type annotations for
  [WorkspacesInstances](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces_instances/)
  service.
- `types-aiobotocore-lite[workspaces-thin-client]` - Type annotations for
  [WorkSpacesThinClient](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces_thin_client/)
  service.
- `types-aiobotocore-lite[workspaces-web]` - Type annotations for
  [WorkSpacesWeb](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces_web/)
  service.
- `types-aiobotocore-lite[xray]` - Type annotations for
  [XRay](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_xray/)
  service.
