r'''
# cdk-library-certbot

[![build](https://github.com/RenovoSolutions/cdk-library-certbot/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-certbotactions/workflows/build.yml)

A CDK Construct Library to automate the creation and renewal of Let's Encrypt certificates.

## Features

* Creates a lambda function that utilizes Certbot to request a certificate from Let's Encrypt
* Uploads the resulting certificate data to S3 for later retrieval
* Imports the certificate to AWS Certificate Manager for tracking expiration
* Creates a trigger to re-run and re-new if the cert will expire in the next 30 days (customizable)

## API Doc

See [API](API.md)

## References

Original [gist](# Modified from original gist https://gist.github.com/arkadiyt/5d764c32baa43fc486ca16cb8488169a) that was modified for the Lambda code

## Examples

This construct utilizes a Route 53 hosted zone lookup so it will require that your stack has [environment variables set for account and region](See https://docs.aws.amazon.com/cdk/latest/guide/environments.html for more details.).

## Typescript

### Typescript with Default Setup

```python
import * as cdk from '@aws-cdk/core';
import { Certbot } from '@renovosolutions/cdk-library-certbot';
import { Architecture } from '@aws-cdk/aws-lambda';

export class CdkExampleCertsStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    let domains = [
      'example.com',
      'www.example.com'
    ]

    new Certbot(this, 'cert', {
      letsencryptDomains: domains.join(','),
      letsencryptEmail: 'webmaster+letsencrypt@example.com',
      hostedZoneNames: [
        'example.com'
      ]
    })
  }
}
```

### Typescript with alternate storage location (Secrets Manager)

```python
import * as cdk from '@aws-cdk/core';
import { Certbot, CertificateStorageType } from '@renovosolutions/cdk-library-certbot';
import { Architecture } from '@aws-cdk/aws-lambda';

export class CdkExampleCertsStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    let domains = [
      'example.com',
      'www.example.com'
    ]

    new Certbot(this, 'cert', {
      letsencryptDomains: domains.join(','),
      letsencryptEmail: 'webmaster+letsencrypt@example.com',
      hostedZoneNames: [
        'example.com'
      ]
      certificateStorage: CertificateStorageType.SECRETS_MANAGER
      // Optional path
      secretsManagerPath: '/path/to/secret/'
    })
  }
}
```

### Typescript with alternate storage location (Parameter Store)

```python
import * as cdk from '@aws-cdk/core';
import { Certbot, CertificateStorageType } from '@renovosolutions/cdk-library-certbot';
import { Architecture } from '@aws-cdk/aws-lambda';

export class CdkExampleCertsStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    let domains = [
      'example.com',
      'www.example.com'
    ]

    new Certbot(this, 'cert', {
      letsencryptDomains: domains.join(','),
      letsencryptEmail: 'webmaster+letsencrypt@example.com',
      hostedZoneNames: [
        'example.com'
      ]
      certificateStorage: CertificateStorageType.SSM_SECURE
      // Optional path
      ssmSecurePath: '/path/to/secret/'
    })
  }
}
```

### Typescript with zone creation in the same stack

```python
import * as cdk from '@aws-cdk/core';
import * as route53 from '@aws-cdk/aws_route53';
import { Certbot } from '@renovosolutions/cdk-library-certbot';
import { Architecture } from '@aws-cdk/aws-lambda';

export class CdkExampleCertsStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const hostedZone = new r53.HostedZone(this, 'authZone', {
      zoneName: 'auth.example.com',
    });

    let domains = [
      'example.com',
      'www.example.com',
      'auth.example.com'
    ]

    new Certbot(this, 'cert', {
      letsencryptDomains: domains.join(','),
      letsencryptEmail: 'webmaster+letsencrypt@example.com',
      hostedZoneNames: [
        'example.com'
      ],
      hostedZones: [
        hostedZone,
      ]
    })
  }
}
```

## Python

```python
from aws_cdk import (
    core as cdk
)
from certbot import Certbot

class CdkExampleCertsStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Certbot(self, "certbot",
            letsencrypt_email="webmaster+letsencrypt@example.com",
            letsencrypt_domains="example.com",
            hosted_zone_names=["example.com"]
        )
```

## Testing the handler in this project

* Set up a python virtual env with `python3.10 -m venv .venv`
* Use the virtual env with `source .venv/bin/activate`
* Install dependencies with `pip install -r function/tests/requirements.txt`
* Run `pytest -v`

The testing using `moto` to mock AWS services and verify the function does what is expected for each given storage type.
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_efs as _aws_cdk_aws_efs_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


class Certbot(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-certbot.Certbot",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        letsencrypt_domains: builtins.str,
        letsencrypt_email: builtins.str,
        architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        certificate_storage: typing.Optional["CertificateStorageType"] = None,
        efs_access_point: typing.Optional[_aws_cdk_aws_efs_ceddda9d.AccessPoint] = None,
        enable_insights: typing.Optional[builtins.bool] = None,
        enable_object_deletion: typing.Optional[builtins.bool] = None,
        function_description: typing.Optional[builtins.str] = None,
        function_name: typing.Optional[builtins.str] = None,
        hosted_zone_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        hosted_zones: typing.Optional[typing.Sequence[_aws_cdk_aws_route53_ceddda9d.IHostedZone]] = None,
        insights_arn: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        kms_key_alias: typing.Optional[builtins.str] = None,
        layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
        object_prefix: typing.Optional[builtins.str] = None,
        preferred_chain: typing.Optional[builtins.str] = None,
        re_issue_days: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        run_on_deploy: typing.Optional[builtins.bool] = None,
        run_on_deploy_wait_minutes: typing.Optional[jsii.Number] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        secrets_manager_path: typing.Optional[builtins.str] = None,
        sns_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
        ssm_secure_path: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param letsencrypt_domains: The comma delimited list of domains for which the Let's Encrypt certificate will be valid. Primary domain should be first.
        :param letsencrypt_email: The email to associate with the Let's Encrypt certificate request.
        :param architecture: The architecture for the Lambda function. This property allows you to specify the architecture type for your Lambda function. Supported values are 'x86_64' for the standard architecture and 'arm64' for the ARM architecture. Default: lambda.Architecture.X86_64
        :param bucket: The S3 bucket to place the resulting certificates in. If no bucket is given one will be created automatically.
        :param certificate_storage: The method of storage for the resulting certificates. Default: CertificateStorageType.S3
        :param efs_access_point: The EFS access point to store the certificates.
        :param enable_insights: Whether or not to enable Lambda Insights. Default: false
        :param enable_object_deletion: Whether or not to enable automatic object deletion if the provided bucket is deleted. Has no effect if a bucket is given as a property Default: false
        :param function_description: The description for the resulting Lambda function.
        :param function_name: The name of the resulting Lambda function.
        :param hosted_zone_names: Hosted zone names that will be required for DNS verification with certbot.
        :param hosted_zones: The hosted zones that will be required for DNS verification with certbot.
        :param insights_arn: Insights layer ARN for your region. Defaults to layer for US-EAST-1
        :param key_type: Set the key type for the certificate. Default: 'ecdsa'
        :param kms_key_alias: The KMS key to use for encryption of the certificates in Secrets Manager or Systems Manager Parameter Store. Default: AWS managed key
        :param layers: Any additional Lambda layers to use with the created function. For example Lambda Extensions
        :param object_prefix: The prefix to apply to the final S3 key name for the certificates. Default is no prefix. Also used for EFS.
        :param preferred_chain: Set the preferred certificate chain. Default: 'None'
        :param re_issue_days: The numbers of days left until the prior cert expires before issuing a new one. Default: 30
        :param removal_policy: The removal policy for the S3 bucket that is automatically created. Has no effect if a bucket is given as a property Default: RemovalPolicy.RETAIN
        :param run_on_deploy: Whether or not to schedule a trigger to run the function after each deployment. Default: true
        :param run_on_deploy_wait_minutes: How many minutes to wait before running the post deployment Lambda trigger. Default: 10
        :param schedule: The schedule for the certificate check trigger. Default: events.Schedule.cron({ minute: '0', hour: '0', weekDay: '1' })
        :param secrets_manager_path: The path to store the certificates in AWS Secrets Manager. Default: ``/certbot/certificates/${letsencryptDomains.split(',')[0]}/``
        :param sns_topic: The SNS topic to notify when a new cert is issued. If no topic is given one will be created automatically.
        :param ssm_secure_path: The path to store the certificates in AWS Systems Manager Parameter Store. Default: ``/certbot/certificates/${letsencryptDomains.split(',')[0]}/``
        :param timeout: The timeout duration for Lambda function. Default: Duraction.seconds(180)
        :param vpc: The VPC to run the Lambda function in. This is needed if you are using EFS. It should be the same VPC as the EFS filesystem Default: none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a97c57094adcc5a6d82e25accd2d32cc4403f75edfb6bdf2875a72fc23b1f8b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CertbotProps(
            letsencrypt_domains=letsencrypt_domains,
            letsencrypt_email=letsencrypt_email,
            architecture=architecture,
            bucket=bucket,
            certificate_storage=certificate_storage,
            efs_access_point=efs_access_point,
            enable_insights=enable_insights,
            enable_object_deletion=enable_object_deletion,
            function_description=function_description,
            function_name=function_name,
            hosted_zone_names=hosted_zone_names,
            hosted_zones=hosted_zones,
            insights_arn=insights_arn,
            key_type=key_type,
            kms_key_alias=kms_key_alias,
            layers=layers,
            object_prefix=object_prefix,
            preferred_chain=preferred_chain,
            re_issue_days=re_issue_days,
            removal_policy=removal_policy,
            run_on_deploy=run_on_deploy,
            run_on_deploy_wait_minutes=run_on_deploy_wait_minutes,
            schedule=schedule,
            secrets_manager_path=secrets_manager_path,
            sns_topic=sns_topic,
            ssm_secure_path=ssm_secure_path,
            timeout=timeout,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="handler")
    def handler(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "handler"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-certbot.CertbotProps",
    jsii_struct_bases=[],
    name_mapping={
        "letsencrypt_domains": "letsencryptDomains",
        "letsencrypt_email": "letsencryptEmail",
        "architecture": "architecture",
        "bucket": "bucket",
        "certificate_storage": "certificateStorage",
        "efs_access_point": "efsAccessPoint",
        "enable_insights": "enableInsights",
        "enable_object_deletion": "enableObjectDeletion",
        "function_description": "functionDescription",
        "function_name": "functionName",
        "hosted_zone_names": "hostedZoneNames",
        "hosted_zones": "hostedZones",
        "insights_arn": "insightsARN",
        "key_type": "keyType",
        "kms_key_alias": "kmsKeyAlias",
        "layers": "layers",
        "object_prefix": "objectPrefix",
        "preferred_chain": "preferredChain",
        "re_issue_days": "reIssueDays",
        "removal_policy": "removalPolicy",
        "run_on_deploy": "runOnDeploy",
        "run_on_deploy_wait_minutes": "runOnDeployWaitMinutes",
        "schedule": "schedule",
        "secrets_manager_path": "secretsManagerPath",
        "sns_topic": "snsTopic",
        "ssm_secure_path": "ssmSecurePath",
        "timeout": "timeout",
        "vpc": "vpc",
    },
)
class CertbotProps:
    def __init__(
        self,
        *,
        letsencrypt_domains: builtins.str,
        letsencrypt_email: builtins.str,
        architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        certificate_storage: typing.Optional["CertificateStorageType"] = None,
        efs_access_point: typing.Optional[_aws_cdk_aws_efs_ceddda9d.AccessPoint] = None,
        enable_insights: typing.Optional[builtins.bool] = None,
        enable_object_deletion: typing.Optional[builtins.bool] = None,
        function_description: typing.Optional[builtins.str] = None,
        function_name: typing.Optional[builtins.str] = None,
        hosted_zone_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        hosted_zones: typing.Optional[typing.Sequence[_aws_cdk_aws_route53_ceddda9d.IHostedZone]] = None,
        insights_arn: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        kms_key_alias: typing.Optional[builtins.str] = None,
        layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
        object_prefix: typing.Optional[builtins.str] = None,
        preferred_chain: typing.Optional[builtins.str] = None,
        re_issue_days: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        run_on_deploy: typing.Optional[builtins.bool] = None,
        run_on_deploy_wait_minutes: typing.Optional[jsii.Number] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        secrets_manager_path: typing.Optional[builtins.str] = None,
        sns_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
        ssm_secure_path: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param letsencrypt_domains: The comma delimited list of domains for which the Let's Encrypt certificate will be valid. Primary domain should be first.
        :param letsencrypt_email: The email to associate with the Let's Encrypt certificate request.
        :param architecture: The architecture for the Lambda function. This property allows you to specify the architecture type for your Lambda function. Supported values are 'x86_64' for the standard architecture and 'arm64' for the ARM architecture. Default: lambda.Architecture.X86_64
        :param bucket: The S3 bucket to place the resulting certificates in. If no bucket is given one will be created automatically.
        :param certificate_storage: The method of storage for the resulting certificates. Default: CertificateStorageType.S3
        :param efs_access_point: The EFS access point to store the certificates.
        :param enable_insights: Whether or not to enable Lambda Insights. Default: false
        :param enable_object_deletion: Whether or not to enable automatic object deletion if the provided bucket is deleted. Has no effect if a bucket is given as a property Default: false
        :param function_description: The description for the resulting Lambda function.
        :param function_name: The name of the resulting Lambda function.
        :param hosted_zone_names: Hosted zone names that will be required for DNS verification with certbot.
        :param hosted_zones: The hosted zones that will be required for DNS verification with certbot.
        :param insights_arn: Insights layer ARN for your region. Defaults to layer for US-EAST-1
        :param key_type: Set the key type for the certificate. Default: 'ecdsa'
        :param kms_key_alias: The KMS key to use for encryption of the certificates in Secrets Manager or Systems Manager Parameter Store. Default: AWS managed key
        :param layers: Any additional Lambda layers to use with the created function. For example Lambda Extensions
        :param object_prefix: The prefix to apply to the final S3 key name for the certificates. Default is no prefix. Also used for EFS.
        :param preferred_chain: Set the preferred certificate chain. Default: 'None'
        :param re_issue_days: The numbers of days left until the prior cert expires before issuing a new one. Default: 30
        :param removal_policy: The removal policy for the S3 bucket that is automatically created. Has no effect if a bucket is given as a property Default: RemovalPolicy.RETAIN
        :param run_on_deploy: Whether or not to schedule a trigger to run the function after each deployment. Default: true
        :param run_on_deploy_wait_minutes: How many minutes to wait before running the post deployment Lambda trigger. Default: 10
        :param schedule: The schedule for the certificate check trigger. Default: events.Schedule.cron({ minute: '0', hour: '0', weekDay: '1' })
        :param secrets_manager_path: The path to store the certificates in AWS Secrets Manager. Default: ``/certbot/certificates/${letsencryptDomains.split(',')[0]}/``
        :param sns_topic: The SNS topic to notify when a new cert is issued. If no topic is given one will be created automatically.
        :param ssm_secure_path: The path to store the certificates in AWS Systems Manager Parameter Store. Default: ``/certbot/certificates/${letsencryptDomains.split(',')[0]}/``
        :param timeout: The timeout duration for Lambda function. Default: Duraction.seconds(180)
        :param vpc: The VPC to run the Lambda function in. This is needed if you are using EFS. It should be the same VPC as the EFS filesystem Default: none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f0249540cbe176a86db839408b6a98feffc11711859731e9b41a932bc4ef767)
            check_type(argname="argument letsencrypt_domains", value=letsencrypt_domains, expected_type=type_hints["letsencrypt_domains"])
            check_type(argname="argument letsencrypt_email", value=letsencrypt_email, expected_type=type_hints["letsencrypt_email"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument certificate_storage", value=certificate_storage, expected_type=type_hints["certificate_storage"])
            check_type(argname="argument efs_access_point", value=efs_access_point, expected_type=type_hints["efs_access_point"])
            check_type(argname="argument enable_insights", value=enable_insights, expected_type=type_hints["enable_insights"])
            check_type(argname="argument enable_object_deletion", value=enable_object_deletion, expected_type=type_hints["enable_object_deletion"])
            check_type(argname="argument function_description", value=function_description, expected_type=type_hints["function_description"])
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument hosted_zone_names", value=hosted_zone_names, expected_type=type_hints["hosted_zone_names"])
            check_type(argname="argument hosted_zones", value=hosted_zones, expected_type=type_hints["hosted_zones"])
            check_type(argname="argument insights_arn", value=insights_arn, expected_type=type_hints["insights_arn"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument kms_key_alias", value=kms_key_alias, expected_type=type_hints["kms_key_alias"])
            check_type(argname="argument layers", value=layers, expected_type=type_hints["layers"])
            check_type(argname="argument object_prefix", value=object_prefix, expected_type=type_hints["object_prefix"])
            check_type(argname="argument preferred_chain", value=preferred_chain, expected_type=type_hints["preferred_chain"])
            check_type(argname="argument re_issue_days", value=re_issue_days, expected_type=type_hints["re_issue_days"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument run_on_deploy", value=run_on_deploy, expected_type=type_hints["run_on_deploy"])
            check_type(argname="argument run_on_deploy_wait_minutes", value=run_on_deploy_wait_minutes, expected_type=type_hints["run_on_deploy_wait_minutes"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument secrets_manager_path", value=secrets_manager_path, expected_type=type_hints["secrets_manager_path"])
            check_type(argname="argument sns_topic", value=sns_topic, expected_type=type_hints["sns_topic"])
            check_type(argname="argument ssm_secure_path", value=ssm_secure_path, expected_type=type_hints["ssm_secure_path"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "letsencrypt_domains": letsencrypt_domains,
            "letsencrypt_email": letsencrypt_email,
        }
        if architecture is not None:
            self._values["architecture"] = architecture
        if bucket is not None:
            self._values["bucket"] = bucket
        if certificate_storage is not None:
            self._values["certificate_storage"] = certificate_storage
        if efs_access_point is not None:
            self._values["efs_access_point"] = efs_access_point
        if enable_insights is not None:
            self._values["enable_insights"] = enable_insights
        if enable_object_deletion is not None:
            self._values["enable_object_deletion"] = enable_object_deletion
        if function_description is not None:
            self._values["function_description"] = function_description
        if function_name is not None:
            self._values["function_name"] = function_name
        if hosted_zone_names is not None:
            self._values["hosted_zone_names"] = hosted_zone_names
        if hosted_zones is not None:
            self._values["hosted_zones"] = hosted_zones
        if insights_arn is not None:
            self._values["insights_arn"] = insights_arn
        if key_type is not None:
            self._values["key_type"] = key_type
        if kms_key_alias is not None:
            self._values["kms_key_alias"] = kms_key_alias
        if layers is not None:
            self._values["layers"] = layers
        if object_prefix is not None:
            self._values["object_prefix"] = object_prefix
        if preferred_chain is not None:
            self._values["preferred_chain"] = preferred_chain
        if re_issue_days is not None:
            self._values["re_issue_days"] = re_issue_days
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if run_on_deploy is not None:
            self._values["run_on_deploy"] = run_on_deploy
        if run_on_deploy_wait_minutes is not None:
            self._values["run_on_deploy_wait_minutes"] = run_on_deploy_wait_minutes
        if schedule is not None:
            self._values["schedule"] = schedule
        if secrets_manager_path is not None:
            self._values["secrets_manager_path"] = secrets_manager_path
        if sns_topic is not None:
            self._values["sns_topic"] = sns_topic
        if ssm_secure_path is not None:
            self._values["ssm_secure_path"] = ssm_secure_path
        if timeout is not None:
            self._values["timeout"] = timeout
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def letsencrypt_domains(self) -> builtins.str:
        '''The comma delimited list of domains for which the Let's Encrypt certificate will be valid.

        Primary domain should be first.
        '''
        result = self._values.get("letsencrypt_domains")
        assert result is not None, "Required property 'letsencrypt_domains' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def letsencrypt_email(self) -> builtins.str:
        '''The email to associate with the Let's Encrypt certificate request.'''
        result = self._values.get("letsencrypt_email")
        assert result is not None, "Required property 'letsencrypt_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def architecture(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture]:
        '''The architecture for the Lambda function.

        This property allows you to specify the architecture type for your Lambda function.
        Supported values are 'x86_64' for the standard architecture and 'arm64' for the
        ARM architecture.

        :default: lambda.Architecture.X86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture], result)

    @builtins.property
    def bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''The S3 bucket to place the resulting certificates in.

        If no bucket is given one will be created automatically.
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    @builtins.property
    def certificate_storage(self) -> typing.Optional["CertificateStorageType"]:
        '''The method of storage for the resulting certificates.

        :default: CertificateStorageType.S3
        '''
        result = self._values.get("certificate_storage")
        return typing.cast(typing.Optional["CertificateStorageType"], result)

    @builtins.property
    def efs_access_point(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.AccessPoint]:
        '''The EFS access point to store the certificates.'''
        result = self._values.get("efs_access_point")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.AccessPoint], result)

    @builtins.property
    def enable_insights(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable Lambda Insights.

        :default: false
        '''
        result = self._values.get("enable_insights")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_object_deletion(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable automatic object deletion if the provided bucket is deleted.

        Has no effect if a bucket is given as a property

        :default: false
        '''
        result = self._values.get("enable_object_deletion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def function_description(self) -> typing.Optional[builtins.str]:
        '''The description for the resulting Lambda function.'''
        result = self._values.get("function_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''The name of the resulting Lambda function.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosted_zone_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Hosted zone names that will be required for DNS verification with certbot.'''
        result = self._values.get("hosted_zone_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def hosted_zones(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_route53_ceddda9d.IHostedZone]]:
        '''The hosted zones that will be required for DNS verification with certbot.'''
        result = self._values.get("hosted_zones")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_route53_ceddda9d.IHostedZone]], result)

    @builtins.property
    def insights_arn(self) -> typing.Optional[builtins.str]:
        '''Insights layer ARN for your region.

        Defaults to layer for US-EAST-1
        '''
        result = self._values.get("insights_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_type(self) -> typing.Optional[builtins.str]:
        '''Set the key type for the certificate.

        :default: 'ecdsa'
        '''
        result = self._values.get("key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_alias(self) -> typing.Optional[builtins.str]:
        '''The KMS key to use for encryption of the certificates in Secrets Manager or Systems Manager Parameter Store.

        :default: AWS managed key
        '''
        result = self._values.get("kms_key_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]]:
        '''Any additional Lambda layers to use with the created function.

        For example Lambda Extensions
        '''
        result = self._values.get("layers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]], result)

    @builtins.property
    def object_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix to apply to the final S3 key name for the certificates.

        Default is no prefix.
        Also used for EFS.
        '''
        result = self._values.get("object_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_chain(self) -> typing.Optional[builtins.str]:
        '''Set the preferred certificate chain.

        :default: 'None'
        '''
        result = self._values.get("preferred_chain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def re_issue_days(self) -> typing.Optional[jsii.Number]:
        '''The numbers of days left until the prior cert expires before issuing a new one.

        :default: 30
        '''
        result = self._values.get("re_issue_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for the S3 bucket that is automatically created.

        Has no effect if a bucket is given as a property

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def run_on_deploy(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to schedule a trigger to run the function after each deployment.

        :default: true
        '''
        result = self._values.get("run_on_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def run_on_deploy_wait_minutes(self) -> typing.Optional[jsii.Number]:
        '''How many minutes to wait before running the post deployment Lambda trigger.

        :default: 10
        '''
        result = self._values.get("run_on_deploy_wait_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The schedule for the certificate check trigger.

        :default: events.Schedule.cron({ minute: '0', hour: '0', weekDay: '1' })
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def secrets_manager_path(self) -> typing.Optional[builtins.str]:
        '''The path to store the certificates in AWS Secrets Manager.

        :default: ``/certbot/certificates/${letsencryptDomains.split(',')[0]}/``
        '''
        result = self._values.get("secrets_manager_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sns_topic(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic]:
        '''The SNS topic to notify when a new cert is issued.

        If no topic is given one will be created automatically.
        '''
        result = self._values.get("sns_topic")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic], result)

    @builtins.property
    def ssm_secure_path(self) -> typing.Optional[builtins.str]:
        '''The path to store the certificates in AWS Systems Manager Parameter Store.

        :default: ``/certbot/certificates/${letsencryptDomains.split(',')[0]}/``
        '''
        result = self._values.get("ssm_secure_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The timeout duration for Lambda function.

        :default: Duraction.seconds(180)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC to run the Lambda function in.

        This is needed if you are using EFS.
        It should be the same VPC as the EFS filesystem

        :default: none
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertbotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@renovosolutions/cdk-library-certbot.CertificateStorageType")
class CertificateStorageType(enum.Enum):
    SECRETS_MANAGER = "SECRETS_MANAGER"
    '''Store the certificate in AWS Secrets Manager.'''
    S3 = "S3"
    '''Store the certificates in S3.'''
    SSM_SECURE = "SSM_SECURE"
    '''Store the certificates as a parameter in AWS Systems Manager Parameter Store  with encryption.'''
    EFS = "EFS"
    '''Store the certificates in EFS, mounted to the Lambda function.'''


__all__ = [
    "Certbot",
    "CertbotProps",
    "CertificateStorageType",
]

publication.publish()

def _typecheckingstub__0a97c57094adcc5a6d82e25accd2d32cc4403f75edfb6bdf2875a72fc23b1f8b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    letsencrypt_domains: builtins.str,
    letsencrypt_email: builtins.str,
    architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    certificate_storage: typing.Optional[CertificateStorageType] = None,
    efs_access_point: typing.Optional[_aws_cdk_aws_efs_ceddda9d.AccessPoint] = None,
    enable_insights: typing.Optional[builtins.bool] = None,
    enable_object_deletion: typing.Optional[builtins.bool] = None,
    function_description: typing.Optional[builtins.str] = None,
    function_name: typing.Optional[builtins.str] = None,
    hosted_zone_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    hosted_zones: typing.Optional[typing.Sequence[_aws_cdk_aws_route53_ceddda9d.IHostedZone]] = None,
    insights_arn: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    kms_key_alias: typing.Optional[builtins.str] = None,
    layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
    object_prefix: typing.Optional[builtins.str] = None,
    preferred_chain: typing.Optional[builtins.str] = None,
    re_issue_days: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    run_on_deploy: typing.Optional[builtins.bool] = None,
    run_on_deploy_wait_minutes: typing.Optional[jsii.Number] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    secrets_manager_path: typing.Optional[builtins.str] = None,
    sns_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
    ssm_secure_path: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f0249540cbe176a86db839408b6a98feffc11711859731e9b41a932bc4ef767(
    *,
    letsencrypt_domains: builtins.str,
    letsencrypt_email: builtins.str,
    architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    certificate_storage: typing.Optional[CertificateStorageType] = None,
    efs_access_point: typing.Optional[_aws_cdk_aws_efs_ceddda9d.AccessPoint] = None,
    enable_insights: typing.Optional[builtins.bool] = None,
    enable_object_deletion: typing.Optional[builtins.bool] = None,
    function_description: typing.Optional[builtins.str] = None,
    function_name: typing.Optional[builtins.str] = None,
    hosted_zone_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    hosted_zones: typing.Optional[typing.Sequence[_aws_cdk_aws_route53_ceddda9d.IHostedZone]] = None,
    insights_arn: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    kms_key_alias: typing.Optional[builtins.str] = None,
    layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
    object_prefix: typing.Optional[builtins.str] = None,
    preferred_chain: typing.Optional[builtins.str] = None,
    re_issue_days: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    run_on_deploy: typing.Optional[builtins.bool] = None,
    run_on_deploy_wait_minutes: typing.Optional[jsii.Number] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    secrets_manager_path: typing.Optional[builtins.str] = None,
    sns_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
    ssm_secure_path: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass
