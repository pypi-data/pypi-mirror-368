import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-certbot",
    "version": "2.9.0",
    "description": "AWS CDK Construct Library to manage Lets Encrypt certificate renewals with Certbot",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-certbot.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-certbot.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "renovosolutions_certbot",
        "renovosolutions_certbot._jsii"
    ],
    "package_data": {
        "renovosolutions_certbot._jsii": [
            "cdk-library-certbot@2.9.0.jsii.tgz"
        ],
        "renovosolutions_certbot": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.210.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "publication>=0.0.3",
        "renovosolutions.aws-cdk-one-time-event>=2.1.125, <3.0.0",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
