#  Copyright 2024 Palantir Technologies, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from __future__ import annotations

import decimal
import typing
from datetime import date

import pydantic
import typing_extensions

from foundry_sdk import _core as core
from foundry_sdk.v2.core import models as core_models
from foundry_sdk.v2.datasets import models as datasets_models
from foundry_sdk.v2.filesystem import models as filesystem_models


class ApiKeyAuthentication(pydantic.BaseModel):
    """
    The API key used to authenticate to the external system.
    This can be configured as a header or query parameter.
    """

    location: RestRequestApiKeyLocation
    """The location of the API key in the request."""

    api_key: EncryptedProperty = pydantic.Field(alias=str("apiKey"))  # type: ignore[literal-required]
    """The value of the API key."""

    type: typing.Literal["apiKey"] = "apiKey"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class AsPlaintextValue(pydantic.BaseModel):
    """AsPlaintextValue"""

    value: PlaintextValue
    type: typing.Literal["asPlaintextValue"] = "asPlaintextValue"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class AsSecretName(pydantic.BaseModel):
    """AsSecretName"""

    value: SecretName
    type: typing.Literal["asSecretName"] = "asSecretName"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class AwsAccessKey(pydantic.BaseModel):
    """
    [Access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) are long-term
    credentials for an IAM user or the AWS account root user.
    Access keys consist of two parts: an access key ID (for example, AKIAIOSFODNN7EXAMPLE) and a secret access
    key (for example, wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY). You must use both the access key ID and
    secret access key together to authenticate your requests.
    """

    access_key_id: str = pydantic.Field(alias=str("accessKeyId"))  # type: ignore[literal-required]
    secret_access_key: EncryptedProperty = pydantic.Field(alias=str("secretAccessKey"))  # type: ignore[literal-required]
    type: typing.Literal["awsAccessKey"] = "awsAccessKey"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class AwsOidcAuthentication(pydantic.BaseModel):
    """
    [OpenID Connect (OIDC)](https://palantir.com/docs/foundry/data-connection/oidc/) is an open authentication protocol that allows
    you to authenticate to external system resources without the use of static credentials.
    """

    audience: str
    """The configured audience that identifies the external system."""

    issuer_url: str = pydantic.Field(alias=str("issuerUrl"))  # type: ignore[literal-required]
    """The URL that identifies Foundry as an OIDC identity provider."""

    subject: ConnectionRid
    """The RID of the Connection that is connecting to the external system."""

    type: typing.Literal["oidc"] = "oidc"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class BasicCredentials(pydantic.BaseModel):
    """BasicCredentials"""

    username: str
    password: EncryptedProperty
    type: typing.Literal["basic"] = "basic"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class BearerToken(pydantic.BaseModel):
    """The bearer token used to authenticate to the external system."""

    bearer_token: EncryptedProperty = pydantic.Field(alias=str("bearerToken"))  # type: ignore[literal-required]
    type: typing.Literal["bearerToken"] = "bearerToken"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CloudIdentity(pydantic.BaseModel):
    """
    [Cloud identities](https://palantir.com/docs/foundry/administration/configure-cloud-identities/) allow you to authenticate to
    cloud provider resources without the use of static credentials.
    """

    cloud_identity_rid: CloudIdentityRid = pydantic.Field(alias=str("cloudIdentityRid"))  # type: ignore[literal-required]
    type: typing.Literal["cloudIdentity"] = "cloudIdentity"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


CloudIdentityRid = core.RID
"""The Resource Identifier (RID) of a Cloud Identity."""


class Connection(pydantic.BaseModel):
    """Connection"""

    rid: ConnectionRid
    parent_folder_rid: filesystem_models.FolderRid = pydantic.Field(alias=str("parentFolderRid"))  # type: ignore[literal-required]
    display_name: ConnectionDisplayName = pydantic.Field(alias=str("displayName"))  # type: ignore[literal-required]
    """The display name of the Connection. The display name must not be blank."""

    export_settings: ConnectionExportSettings = pydantic.Field(alias=str("exportSettings"))  # type: ignore[literal-required]
    configuration: ConnectionConfiguration
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


ConnectionConfiguration = typing_extensions.Annotated[
    typing.Union[
        "S3ConnectionConfiguration",
        "RestConnectionConfiguration",
        "SnowflakeConnectionConfiguration",
        "DatabricksConnectionConfiguration",
        "JdbcConnectionConfiguration",
    ],
    pydantic.Field(discriminator="type"),
]
"""ConnectionConfiguration"""


ConnectionDisplayName = str
"""The display name of the Connection. The display name must not be blank."""


class ConnectionExportSettings(pydantic.BaseModel):
    """The [export settings of a Connection](https://palantir.com/docs/foundry/data-connection/export-overview/#enable-exports-for-source)."""

    exports_enabled: bool = pydantic.Field(alias=str("exportsEnabled"))  # type: ignore[literal-required]
    """Allow exporting datasets from Foundry to this Connection."""

    export_enabled_without_markings_validation: bool = pydantic.Field(alias=str("exportEnabledWithoutMarkingsValidation"))  # type: ignore[literal-required]
    """
    In certain interactive workflows the Connection can be used in, it is not currently possible to validate the 
    security markings of the data being exported. 
    By enabling exports without markings validation, you acknowledge that you are responsible for ensuring 
    that the data being exported is compliant with your organization's policies.
    """

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


ConnectionRid = core.RID
"""The Resource Identifier (RID) of a Connection (also known as a source)."""


class CreateConnectionRequestAsPlaintextValue(pydantic.BaseModel):
    """CreateConnectionRequestAsPlaintextValue"""

    value: PlaintextValue
    type: typing.Literal["asPlaintextValue"] = "asPlaintextValue"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestAsSecretName(pydantic.BaseModel):
    """CreateConnectionRequestAsSecretName"""

    value: SecretName
    type: typing.Literal["asSecretName"] = "asSecretName"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestBasicCredentials(pydantic.BaseModel):
    """CreateConnectionRequestBasicCredentials"""

    password: CreateConnectionRequestEncryptedProperty
    username: str
    type: typing.Literal["basic"] = "basic"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


CreateConnectionRequestConnectionConfiguration = typing_extensions.Annotated[
    typing.Union[
        "CreateConnectionRequestS3ConnectionConfiguration",
        "CreateConnectionRequestRestConnectionConfiguration",
        "CreateConnectionRequestSnowflakeConnectionConfiguration",
        "CreateConnectionRequestDatabricksConnectionConfiguration",
        "CreateConnectionRequestJdbcConnectionConfiguration",
    ],
    pydantic.Field(discriminator="type"),
]
"""CreateConnectionRequestConnectionConfiguration"""


CreateConnectionRequestDatabricksAuthenticationMode = typing_extensions.Annotated[
    typing.Union[
        "CreateConnectionRequestWorkflowIdentityFederation",
        "CreateConnectionRequestOauthMachineToMachineAuth",
        "CreateConnectionRequestPersonalAccessToken",
        CreateConnectionRequestBasicCredentials,
    ],
    pydantic.Field(discriminator="type"),
]
"""The method of authentication for connecting to an external Databricks system."""


class CreateConnectionRequestDatabricksConnectionConfiguration(pydantic.BaseModel):
    """CreateConnectionRequestDatabricksConnectionConfiguration"""

    host_name: str = pydantic.Field(alias=str("hostName"))  # type: ignore[literal-required]
    """The hostname of the Databricks workspace."""

    http_path: str = pydantic.Field(alias=str("httpPath"))  # type: ignore[literal-required]
    """The Databricks compute resource’s HTTP Path value."""

    jdbc_properties: JdbcProperties = pydantic.Field(alias=str("jdbcProperties"))  # type: ignore[literal-required]
    authentication: CreateConnectionRequestDatabricksAuthenticationMode
    """The method of authentication to use."""

    type: typing.Literal["databricks"] = "databricks"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


CreateConnectionRequestEncryptedProperty = typing_extensions.Annotated[
    typing.Union[CreateConnectionRequestAsSecretName, CreateConnectionRequestAsPlaintextValue],
    pydantic.Field(discriminator="type"),
]
"""
When reading an encrypted property, the secret name representing the encrypted value will be returned.
When writing to an encrypted property:
- If a plaintext value is passed as an input, the plaintext value will be encrypted and saved to the property.
- If a secret name is passed as an input, the secret name must match the existing secret name of the property
  and the property will retain its previously encrypted value.
"""


class CreateConnectionRequestJdbcConnectionConfiguration(pydantic.BaseModel):
    """CreateConnectionRequestJdbcConnectionConfiguration"""

    credentials: typing.Optional[BasicCredentials] = None
    driver_class: str = pydantic.Field(alias=str("driverClass"))  # type: ignore[literal-required]
    """The fully-qualified driver class name that is used to connect to the database."""

    jdbc_properties: JdbcProperties = pydantic.Field(alias=str("jdbcProperties"))  # type: ignore[literal-required]
    url: str
    """The URL that the JDBC driver uses to connect to a database."""

    type: typing.Literal["jdbc"] = "jdbc"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestOauthMachineToMachineAuth(pydantic.BaseModel):
    """CreateConnectionRequestOauthMachineToMachineAuth"""

    client_id: str = pydantic.Field(alias=str("clientID"))  # type: ignore[literal-required]
    """The client ID for the service principal."""

    client_secret: CreateConnectionRequestEncryptedProperty = pydantic.Field(alias=str("clientSecret"))  # type: ignore[literal-required]
    """The value of the client secret."""

    type: typing.Literal["oauthM2M"] = "oauthM2M"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestPersonalAccessToken(pydantic.BaseModel):
    """CreateConnectionRequestPersonalAccessToken"""

    personal_access_token: CreateConnectionRequestEncryptedProperty = pydantic.Field(alias=str("personalAccessToken"))  # type: ignore[literal-required]
    type: typing.Literal["personalAccessToken"] = "personalAccessToken"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestRestConnectionConfiguration(pydantic.BaseModel):
    """CreateConnectionRequestRestConnectionConfiguration"""

    additional_secrets: typing.Optional[RestConnectionAdditionalSecrets] = pydantic.Field(alias=str("additionalSecrets"), default=None)  # type: ignore[literal-required]
    """
    Additional secrets that can be referenced in code and webhook configurations.
    If not provided, no additional secrets will be created.
    """

    oauth2_client_rid: typing.Optional[core.RID] = pydantic.Field(alias=str("oauth2ClientRid"), default=None)  # type: ignore[literal-required]
    """
    The RID of the [Outbound application](https://palantir.com/docs/foundry/administration/configure-outbound-applications) that is used to authenticate to the external system via OAuth2.
    Currently, a connection may use only one outbound application for OAuth 2.0 authentication.
    Selecting a different outbound application will update the configuration for all domains with OAuth 2.0 as the selected authorization.
    """

    domains: typing.List[Domain]
    """
    The domains that the connection is allowed to access.
    At least one domain must be specified.
    """

    type: typing.Literal["rest"] = "rest"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestS3ConnectionConfiguration(pydantic.BaseModel):
    """CreateConnectionRequestS3ConnectionConfiguration"""

    connection_timeout_millis: typing.Optional[core.Long] = pydantic.Field(alias=str("connectionTimeoutMillis"), default=None)  # type: ignore[literal-required]
    """
    The amount of time (in milliseconds) to wait when initially establishing a connection before giving up and timing out.
    If not specified, defaults to 10000 as defined by the [AWS SDK default](https://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/ClientConfiguration.html#DEFAULT_CONNECTION_TIMEOUT).
    """

    max_error_retry: typing.Optional[int] = pydantic.Field(alias=str("maxErrorRetry"), default=None)  # type: ignore[literal-required]
    """
    The maximum number of retry attempts for failed requests to the S3 service.
    If not specified, defaults to 3 as defined by the [AWS SDK default](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/retry-strategy.html#retry-strategies).
    """

    bucket_url: str = pydantic.Field(alias=str("bucketUrl"))  # type: ignore[literal-required]
    """The URL of the S3 bucket. The URL should contain a trailing slash."""

    client_kms_configuration: typing.Optional[S3KmsConfiguration] = pydantic.Field(alias=str("clientKmsConfiguration"), default=None)  # type: ignore[literal-required]
    """
    The client-side KMS key to use for encryption and decryption of data in the S3 bucket.
    If not specified, the default KMS key for the bucket is used.
    """

    match_subfolder_exactly: typing.Optional[bool] = pydantic.Field(alias=str("matchSubfolderExactly"), default=None)  # type: ignore[literal-required]
    """
    If true, only files in the subfolder specified in the bucket URL will be synced.
    If false, all files in the bucket will be synced.
    If not specified, defaults to false.
    """

    sts_role_configuration: typing.Optional[StsRoleConfiguration] = pydantic.Field(alias=str("stsRoleConfiguration"), default=None)  # type: ignore[literal-required]
    """The configuration needed to assume a role to connect to the S3 external system."""

    s3_endpoint: typing.Optional[str] = pydantic.Field(alias=str("s3Endpoint"), default=None)  # type: ignore[literal-required]
    """
    The endpoint of the S3 service. This is used to connect to a custom S3 service that is not AWS S3.
    If not specified, defaults to the [AWS S3 endpoint](https://docs.aws.amazon.com/general/latest/gr/s3.html).
    Warning: Specifying a region and a custom endpoint containing a region can lead to unexpected behavior.
    """

    socket_timeout_millis: typing.Optional[core.Long] = pydantic.Field(alias=str("socketTimeoutMillis"), default=None)  # type: ignore[literal-required]
    """
    The amount of time (in milliseconds) to wait for data to be transferred over an established, open connection.
    If not specified, defaults to 50000 as defined by the [AWS SDK default](https://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/ClientConfiguration.html#DEFAULT_SOCKET_TIMEOUT).
    """

    enable_requester_pays: typing.Optional[bool] = pydantic.Field(alias=str("enableRequesterPays"), default=None)  # type: ignore[literal-required]
    """
    Defaults to false, unless set and overwritten.
    If true, includes the [requester pays header](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html)
    in requests, allowing reads from requester pays buckets.
    """

    s3_endpoint_signing_region: typing.Optional[Region] = pydantic.Field(alias=str("s3EndpointSigningRegion"), default=None)  # type: ignore[literal-required]
    """
    The region used when constructing the S3 client using a custom endpoint.
    This is often not required and would only be needed if you are using the S3 connector with an S3-compliant third-party API,
    and are also setting a custom endpoint that requires a non-default region.
    """

    region: typing.Optional[Region] = None
    """
    The region representing the location of the S3 bucket.
    Warning: Specifying a region and a custom endpoint containing a region can lead to unexpected behavior.
    """

    authentication_mode: typing.Optional[S3AuthenticationMode] = pydantic.Field(alias=str("authenticationMode"), default=None)  # type: ignore[literal-required]
    """
    The authentication mode to use to connect to the S3 external system. No authentication mode is required
    to connect to publicly accessible AWS S3 buckets.
    """

    proxy_configuration: typing.Optional[S3ProxyConfiguration] = pydantic.Field(alias=str("proxyConfiguration"), default=None)  # type: ignore[literal-required]
    """The configuration needed to connect to the S3 external system through a proxy."""

    max_connections: typing.Optional[int] = pydantic.Field(alias=str("maxConnections"), default=None)  # type: ignore[literal-required]
    """
    The maximum number of HTTP connections to the S3 service per sync.
    If not specified, defaults to 50 as defined by the [AWS SDK default](https://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/ClientConfiguration.html#DEFAULT_MAX_CONNECTIONS).
    """

    type: typing.Literal["s3"] = "s3"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


CreateConnectionRequestSnowflakeAuthenticationMode = typing_extensions.Annotated[
    typing.Union[
        "CreateConnectionRequestSnowflakeExternalOauth",
        "CreateConnectionRequestSnowflakeKeyPairAuthentication",
        CreateConnectionRequestBasicCredentials,
    ],
    pydantic.Field(discriminator="type"),
]
"""CreateConnectionRequestSnowflakeAuthenticationMode"""


class CreateConnectionRequestSnowflakeConnectionConfiguration(pydantic.BaseModel):
    """CreateConnectionRequestSnowflakeConnectionConfiguration"""

    schema_: typing.Optional[str] = pydantic.Field(alias=str("schema"), default=None)  # type: ignore[literal-required]
    """
    Specifies the default schema to use for the specified database once connected. If unspecified, 
    defaults to the empty string.
    The specified schema should be an existing schema for which the specified default role has privileges.

    See https://docs.snowflake.com/developer-guide/jdbc/jdbc-parameters#schema
    """

    database: typing.Optional[str] = None
    """
    Specifies the default database to use once connected. If unspecified, defaults to the empty string.
    The specified database should be an existing database for which the specified default role has privileges.

    See https://docs.snowflake.com/developer-guide/jdbc/jdbc-parameters#db
    """

    role: typing.Optional[str] = None
    """
    Specifies the default access control role to use in the Snowflake session initiated by the driver. 
    If unspecified, no role will be used when the session is initiated by the driver.

    The specified role should be an existing role that has already been assigned to the specified user for 
    the driver. If the specified role has not already been assigned to the user, the role is not used when 
    the session is initiated by the driver.

    See https://docs.snowflake.com/developer-guide/jdbc/jdbc-parameters#role
    """

    account_identifier: str = pydantic.Field(alias=str("accountIdentifier"))  # type: ignore[literal-required]
    """
    An [account identifier](https://docs.snowflake.com/en/user-guide/admin-account-identifier) uniquely 
    identifies a Snowflake account within your organization, as well as throughout the global network of 
    Snowflake-supported cloud platforms and cloud regions.

    The URL for an account uses the following format: <account_identifier>.snowflakecomputing.com.
    An example URL is https://acme-test_aws_us_east_2.snowflakecomputing.com.
    """

    jdbc_properties: JdbcProperties = pydantic.Field(alias=str("jdbcProperties"))  # type: ignore[literal-required]
    warehouse: typing.Optional[str] = None
    """
    Specifies the virtual warehouse to use once connected. If unspecified, defaults to the empty string. 
    The specified warehouse should be an existing warehouse for which the specified default role has privileges.

    See https://docs.snowflake.com/developer-guide/jdbc/jdbc-parameters#warehouse
    """

    authentication_mode: CreateConnectionRequestSnowflakeAuthenticationMode = pydantic.Field(alias=str("authenticationMode"))  # type: ignore[literal-required]
    """The authentication mode to use to connect to the Snowflake database."""

    type: typing.Literal["snowflake"] = "snowflake"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestSnowflakeExternalOauth(pydantic.BaseModel):
    """CreateConnectionRequestSnowflakeExternalOauth"""

    type: typing.Literal["externalOauth"] = "externalOauth"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestSnowflakeKeyPairAuthentication(pydantic.BaseModel):
    """CreateConnectionRequestSnowflakeKeyPairAuthentication"""

    private_key: CreateConnectionRequestEncryptedProperty = pydantic.Field(alias=str("privateKey"))  # type: ignore[literal-required]
    user: str
    type: typing.Literal["keyPair"] = "keyPair"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateConnectionRequestWorkflowIdentityFederation(pydantic.BaseModel):
    """CreateConnectionRequestWorkflowIdentityFederation"""

    audience: str
    """
    Identifies the recipients that the access token is intended for as a string URI. 
    This should be the primary host name where the Connection lives.
    """

    service_principal_application_id: typing.Optional[str] = pydantic.Field(alias=str("servicePrincipalApplicationId"), default=None)  # type: ignore[literal-required]
    """
    The ID of the Databricks [service principal](https://docs.databricks.com/aws/en/admin/users-groups/service-principals). 
    If provided, a federated JWT token is exchanged using a
    service principal federation policy. If not provided, a federated JWT token is exchanged using an account
    federation policy.
    """

    type: typing.Literal["workflowIdentityFederation"] = "workflowIdentityFederation"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateTableImportRequestDatabricksTableImportConfig(pydantic.BaseModel):
    """CreateTableImportRequestDatabricksTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["databricksImportConfig"] = "databricksImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateTableImportRequestJdbcTableImportConfig(pydantic.BaseModel):
    """CreateTableImportRequestJdbcTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["jdbcImportConfig"] = "jdbcImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateTableImportRequestMicrosoftAccessTableImportConfig(pydantic.BaseModel):
    """CreateTableImportRequestMicrosoftAccessTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["microsoftAccessImportConfig"] = "microsoftAccessImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateTableImportRequestMicrosoftSqlServerTableImportConfig(pydantic.BaseModel):
    """CreateTableImportRequestMicrosoftSqlServerTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["microsoftSqlServerImportConfig"] = "microsoftSqlServerImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateTableImportRequestOracleTableImportConfig(pydantic.BaseModel):
    """CreateTableImportRequestOracleTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["oracleImportConfig"] = "oracleImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateTableImportRequestPostgreSqlTableImportConfig(pydantic.BaseModel):
    """CreateTableImportRequestPostgreSqlTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["postgreSqlImportConfig"] = "postgreSqlImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class CreateTableImportRequestSnowflakeTableImportConfig(pydantic.BaseModel):
    """CreateTableImportRequestSnowflakeTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["snowflakeImportConfig"] = "snowflakeImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


CreateTableImportRequestTableImportConfig = typing_extensions.Annotated[
    typing.Union[
        CreateTableImportRequestDatabricksTableImportConfig,
        CreateTableImportRequestJdbcTableImportConfig,
        CreateTableImportRequestMicrosoftSqlServerTableImportConfig,
        CreateTableImportRequestPostgreSqlTableImportConfig,
        CreateTableImportRequestMicrosoftAccessTableImportConfig,
        CreateTableImportRequestSnowflakeTableImportConfig,
        CreateTableImportRequestOracleTableImportConfig,
    ],
    pydantic.Field(discriminator="type"),
]
"""The import configuration for a specific [connector type](https://palantir.com/docs/foundry/data-integration/source-type-overview)."""


DatabricksAuthenticationMode = typing_extensions.Annotated[
    typing.Union[
        "WorkflowIdentityFederation",
        "OauthMachineToMachineAuth",
        "PersonalAccessToken",
        BasicCredentials,
    ],
    pydantic.Field(discriminator="type"),
]
"""The method of authentication for connecting to an external Databricks system."""


class DatabricksConnectionConfiguration(pydantic.BaseModel):
    """
    The configuration needed to connect to a [Databricks external system](https://palantir.com/docs/foundry/available-connectors/databricks).
    Refer to the [official Databricks documentation](https://docs.databricks.com/aws/en/integrations/compute-details)
    for more information on how to obtain connection details for your system.
    """

    host_name: str = pydantic.Field(alias=str("hostName"))  # type: ignore[literal-required]
    """The hostname of the Databricks workspace."""

    http_path: str = pydantic.Field(alias=str("httpPath"))  # type: ignore[literal-required]
    """The Databricks compute resource’s HTTP Path value."""

    authentication: DatabricksAuthenticationMode
    """The method of authentication to use."""

    jdbc_properties: JdbcProperties = pydantic.Field(alias=str("jdbcProperties"))  # type: ignore[literal-required]
    type: typing.Literal["databricks"] = "databricks"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class DatabricksTableImportConfig(pydantic.BaseModel):
    """The table import configuration for a [Databricks connection](https://palantir.com/docs/foundry/available-connectors/databricks)."""

    query: TableImportQuery
    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    type: typing.Literal["databricksImportConfig"] = "databricksImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class DateColumnInitialIncrementalState(pydantic.BaseModel):
    """The state for an incremental table import using a column with a date type."""

    column_name: str = pydantic.Field(alias=str("columnName"))  # type: ignore[literal-required]
    current_value: date = pydantic.Field(alias=str("currentValue"))  # type: ignore[literal-required]
    """The initial incremental state value for the date column to reference in the query."""

    type: typing.Literal["dateColumnInitialIncrementalState"] = "dateColumnInitialIncrementalState"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class DecimalColumnInitialIncrementalState(pydantic.BaseModel):
    """The state for an incremental table import using a column with a decimal data type."""

    column_name: str = pydantic.Field(alias=str("columnName"))  # type: ignore[literal-required]
    current_value: decimal.Decimal = pydantic.Field(alias=str("currentValue"))  # type: ignore[literal-required]
    """The initial incremental state value for the decimal column to reference in the query."""

    type: typing.Literal["decimalColumnInitialIncrementalState"] = (
        "decimalColumnInitialIncrementalState"
    )
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class Domain(pydantic.BaseModel):
    """The domain that the connection is allowed to access."""

    scheme: typing.Optional[UriScheme] = None
    """
    The scheme of the domain that the connection is allowed to access.
    If not specified, defaults to HTTPS.
    """

    host: str
    """The domain name, IPv4, or IPv6 address."""

    port: typing.Optional[int] = None
    """The port number of the domain that the connection is allowed to access."""

    auth: typing.Optional[RestAuthenticationMode] = None
    """
    The URI scheme must be HTTPS if using any authentication.
    If not specified, no authentication is required.
    """

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


EncryptedProperty = typing_extensions.Annotated[
    typing.Union[AsSecretName, AsPlaintextValue], pydantic.Field(discriminator="type")
]
"""
When reading an encrypted property, the secret name representing the encrypted value will be returned.
When writing to an encrypted property:
- If a plaintext value is passed as an input, the plaintext value will be encrypted and saved to the property.
- If a secret name is passed as an input, the secret name must match the existing secret name of the property
  and the property will retain its previously encrypted value.
"""


class FileAnyPathMatchesFilter(pydantic.BaseModel):
    """If any file has a relative path matching the regular expression, sync all files in the subfolder that are not otherwise filtered."""

    regex: str
    """The regular expression for the relative path to match against."""

    type: typing.Literal["anyPathMatchesFilter"] = "anyPathMatchesFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class FileAtLeastCountFilter(pydantic.BaseModel):
    """Import all filtered files only if there are at least the specified number of files remaining."""

    min_files_count: int = pydantic.Field(alias=str("minFilesCount"))  # type: ignore[literal-required]
    """
    The minimum number of files remaining expected.
    The value specified must be greater than 0.
    """

    type: typing.Literal["atLeastCountFilter"] = "atLeastCountFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class FileChangedSinceLastUploadFilter(pydantic.BaseModel):
    """
    Only import files that have changed or been added since the last import run. Whether or not a file is considered to be changed is determined by the specified file properties.
    This will exclude files uploaded in any previous imports, regardless of the file import mode used. A SNAPSHOT file import mode does not reset the filter.
    """

    file_properties: typing.List[FileProperty] = pydantic.Field(alias=str("fileProperties"))  # type: ignore[literal-required]
    """
    The criteria on which to determine whether a file has been changed or not since the last import. 
    If any of the specified criteria have changed, the file is consider changed. The criteria include:

    LAST_MODIFIED: The file's last modified timestamp has changed since the last import.
    SIZE: The file's size has changed since the last import.

    If no criteria are specified, only newly added files will be imported.
    """

    type: typing.Literal["changedSinceLastUploadFilter"] = "changedSinceLastUploadFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class FileImport(pydantic.BaseModel):
    """FileImport"""

    rid: FileImportRid
    connection_rid: ConnectionRid = pydantic.Field(alias=str("connectionRid"))  # type: ignore[literal-required]
    """The RID of the Connection (also known as a source) that the File Import uses to import data."""

    dataset_rid: datasets_models.DatasetRid = pydantic.Field(alias=str("datasetRid"))  # type: ignore[literal-required]
    """The RID of the output dataset. Can not be modified after the file import is created."""

    branch_name: typing.Optional[datasets_models.BranchName] = pydantic.Field(alias=str("branchName"), default=None)  # type: ignore[literal-required]
    """The branch name in the output dataset that will contain the imported data. Defaults to `master` for most enrollments. Can not be modified after the file import is created."""

    display_name: FileImportDisplayName = pydantic.Field(alias=str("displayName"))  # type: ignore[literal-required]
    file_import_filters: typing.List[FileImportFilter] = pydantic.Field(alias=str("fileImportFilters"))  # type: ignore[literal-required]
    """Use filters to limit which files should be imported. Filters are applied in the order they are defined. A different ordering of filters may lead to a more optimized import. [Learn more about optimizing file imports.](https://palantir.com/docs/foundry/data-connection/file-based-syncs/#optimize-file-based-syncs)"""

    import_mode: FileImportMode = pydantic.Field(alias=str("importMode"))  # type: ignore[literal-required]
    subfolder: typing.Optional[str] = None
    """A subfolder in the external system that will be imported. If not specified, defaults to the root folder of the external system."""

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class FileImportCustomFilter(pydantic.BaseModel):
    """
    A custom file import filter. Custom file import filters can be fetched but cannot currently be used
    when creating or updating file imports.
    """

    config: typing.Any
    type: typing.Literal["customFilter"] = "customFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


FileImportDisplayName = str
"""FileImportDisplayName"""


FileImportFilter = typing_extensions.Annotated[
    typing.Union[
        "FilePathNotMatchesFilter",
        FileAnyPathMatchesFilter,
        "FilesCountLimitFilter",
        FileChangedSinceLastUploadFilter,
        FileImportCustomFilter,
        "FileLastModifiedAfterFilter",
        "FilePathMatchesFilter",
        FileAtLeastCountFilter,
        "FileSizeFilter",
    ],
    pydantic.Field(discriminator="type"),
]
"""
[Filters](https://palantir.com/docs/foundry/data-connection/file-based-syncs/#filters) allow you to filter source files
before they are imported into Foundry.
"""


FileImportMode = typing.Literal["SNAPSHOT", "APPEND", "UPDATE"]
"""
Import mode governs how raw files are read from an external system, and written into a Foundry dataset. 

SNAPSHOT: Defines a new dataset state consisting only of files from a particular import execution.
APPEND: Purely additive and yields data from previous import executions in addition to newly added files.
UPDATE: Replaces existing files from previous import executions based on file names.
"""


FileImportRid = core.RID
"""The Resource Identifier (RID) of a FileImport (also known as a batch sync)."""


class FileLastModifiedAfterFilter(pydantic.BaseModel):
    """Only import files that have been modified after a specified timestamp"""

    after_timestamp: typing.Optional[core.AwareDatetime] = pydantic.Field(alias=str("afterTimestamp"), default=None)  # type: ignore[literal-required]
    """
    Timestamp threshold, specified in ISO-8601 format.
    If not specified, defaults to the timestamp the filter is added to the file import.
    """

    type: typing.Literal["lastModifiedAfterFilter"] = "lastModifiedAfterFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class FilePathMatchesFilter(pydantic.BaseModel):
    """
    Only import files whose path (relative to the root of the source) matches the regular expression.

    **Example**
    Suppose we are importing files from `relative/subfolder`.
    `relative/subfolder` contains:
    - `relative/subfolder/include-file.txt`
    - `relative/subfolder/exclude-file.txt`
    - `relative/subfolder/other-file.txt`

    With the `relative/subfolder/include-.*.txt` regex, only `relative/subfolder/include-file.txt` will be imported.
    """

    regex: str
    """Must be written to match the paths relative to the root of the source, even if a subfolder is specified."""

    type: typing.Literal["pathMatchesFilter"] = "pathMatchesFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class FilePathNotMatchesFilter(pydantic.BaseModel):
    """
    Only import files whose path (relative to the root of the source) does not match the regular expression.

    **Example**
    Suppose we are importing files from `relative/subfolder`.
    `relative/subfolder` contains:
    - `relative/subfolder/include-file.txt`
    - `relative/subfolder/exclude-file.txt`
    - `relative/subfolder/other-file.txt`

    With the `relative/subfolder/exclude-.*.txt` regex, both `relative/subfolder/include-file.txt` and `relative/subfolder/other-file.txt` will be imported,
    and `relative/subfolder/exclude-file.txt` will be excluded from the import.
    """

    regex: str
    """Must be written to match the paths relative to the root of the source, even if a subfolder is specified."""

    type: typing.Literal["pathNotMatchesFilter"] = "pathNotMatchesFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


FileProperty = typing.Literal["LAST_MODIFIED", "SIZE"]
"""FileProperty"""


class FileSizeFilter(pydantic.BaseModel):
    """
    Only import files whose size is between the specified minimum and maximum values.
    At least one of `gt` or `lt` should be present.
    If both are present, the value specified for `gt` must be strictly less than `lt - 1`.
    """

    gt: typing.Optional[core_models.SizeBytes] = None
    """
    File size must be greater than this number for it to be imported.
    The value specified cannot be a negative number.
    """

    lt: typing.Optional[core_models.SizeBytes] = None
    """
    File size must be less than this number for it to be imported.
    The value specified must be at least 1 byte.
    """

    type: typing.Literal["fileSizeFilter"] = "fileSizeFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class FilesCountLimitFilter(pydantic.BaseModel):
    """
    Only retain `filesCount` number of files in each transaction.
    The choice of files to retain is made without any guarantee of order.
    This option can increase the reliability of incremental syncs.
    """

    files_count: int = pydantic.Field(alias=str("filesCount"))  # type: ignore[literal-required]
    """The number of files to import in the transaction. The value specified must be positive."""

    type: typing.Literal["filesCountLimitFilter"] = "filesCountLimitFilter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class HeaderApiKey(pydantic.BaseModel):
    """HeaderApiKey"""

    header_name: str = pydantic.Field(alias=str("headerName"))  # type: ignore[literal-required]
    """The name of the header that the API key is passed in."""

    type: typing.Literal["header"] = "header"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class IntegerColumnInitialIncrementalState(pydantic.BaseModel):
    """The state for an incremental table import using a numeric integer datatype."""

    column_name: str = pydantic.Field(alias=str("columnName"))  # type: ignore[literal-required]
    current_value: int = pydantic.Field(alias=str("currentValue"))  # type: ignore[literal-required]
    """The initial incremental state value for the integer column to reference in the query."""

    type: typing.Literal["integerColumnInitialIncrementalState"] = (
        "integerColumnInitialIncrementalState"
    )
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class JdbcConnectionConfiguration(pydantic.BaseModel):
    """The configuration needed to connect to an external system using the JDBC protocol."""

    url: str
    """The URL that the JDBC driver uses to connect to a database."""

    driver_class: str = pydantic.Field(alias=str("driverClass"))  # type: ignore[literal-required]
    """The fully-qualified driver class name that is used to connect to the database."""

    jdbc_properties: JdbcProperties = pydantic.Field(alias=str("jdbcProperties"))  # type: ignore[literal-required]
    credentials: typing.Optional[BasicCredentials] = None
    type: typing.Literal["jdbc"] = "jdbc"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


JdbcProperties = typing.Dict[str, str]
"""
A map of [properties](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/Properties.html) passed 
to the JDBC driver to configure behavior. Refer to the documentation of your specific connection type for additional 
available JDBC properties to add to your connection configuration.
This should only contain unencrypted properties, all values specified here are sent unencrypted to Foundry.
"""


class JdbcTableImportConfig(pydantic.BaseModel):
    """The import configuration for a [custom JDBC connection](https://palantir.com/docs/foundry/available-connectors/custom-jdbc-sources)."""

    query: TableImportQuery
    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    type: typing.Literal["jdbcImportConfig"] = "jdbcImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ListFileImportsResponse(pydantic.BaseModel):
    """ListFileImportsResponse"""

    data: typing.List[FileImport]
    next_page_token: typing.Optional[core_models.PageToken] = pydantic.Field(alias=str("nextPageToken"), default=None)  # type: ignore[literal-required]
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ListTableImportsResponse(pydantic.BaseModel):
    """ListTableImportsResponse"""

    data: typing.List[TableImport]
    next_page_token: typing.Optional[core_models.PageToken] = pydantic.Field(alias=str("nextPageToken"), default=None)  # type: ignore[literal-required]
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class LongColumnInitialIncrementalState(pydantic.BaseModel):
    """The state for an incremental table import using a column with a numeric long datatype."""

    column_name: str = pydantic.Field(alias=str("columnName"))  # type: ignore[literal-required]
    current_value: core.Long = pydantic.Field(alias=str("currentValue"))  # type: ignore[literal-required]
    """The initial incremental state value for the long column to reference in the query."""

    type: typing.Literal["longColumnInitialIncrementalState"] = "longColumnInitialIncrementalState"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class MicrosoftAccessTableImportConfig(pydantic.BaseModel):
    """The import configuration for a [Microsoft Access connection](https://palantir.com/docs/foundry/available-connectors/microsoft-access)."""

    query: TableImportQuery
    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    type: typing.Literal["microsoftAccessImportConfig"] = "microsoftAccessImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class MicrosoftSqlServerTableImportConfig(pydantic.BaseModel):
    """The import configuration for a [Microsoft SQL Server connection](https://palantir.com/docs/foundry/available-connectors/microsoft-sql-server)."""

    query: TableImportQuery
    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    type: typing.Literal["microsoftSqlServerImportConfig"] = "microsoftSqlServerImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class OauthMachineToMachineAuth(pydantic.BaseModel):
    """
    Authenticate as a service principal using OAuth. Create a service principal in Databricks and generate an OAuth secret to obtain a client ID and secret.
    Read the [official Databricks documentation](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m) for more information about OAuth machine-to-machine
    authentication.
    """

    client_id: str = pydantic.Field(alias=str("clientID"))  # type: ignore[literal-required]
    """The client ID for the service principal."""

    client_secret: EncryptedProperty = pydantic.Field(alias=str("clientSecret"))  # type: ignore[literal-required]
    """The value of the client secret."""

    type: typing.Literal["oauthM2M"] = "oauthM2M"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class OracleTableImportConfig(pydantic.BaseModel):
    """The import configuration for an Oracle Database 21 connection."""

    query: TableImportQuery
    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    type: typing.Literal["oracleImportConfig"] = "oracleImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class PersonalAccessToken(pydantic.BaseModel):
    """
    Authenticate as a user or service principal using a personal access token.
    Read the [official Databricks documentation](https://docs.databricks.com/aws/en/dev-tools/auth/pat) for information on generating a personal access token.
    """

    personal_access_token: EncryptedProperty = pydantic.Field(alias=str("personalAccessToken"))  # type: ignore[literal-required]
    type: typing.Literal["personalAccessToken"] = "personalAccessToken"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


PlaintextValue = str
"""PlaintextValue"""


class PostgreSqlTableImportConfig(pydantic.BaseModel):
    """The import configuration for a [PostgreSQL connection](https://palantir.com/docs/foundry/available-connectors/postgresql)."""

    query: TableImportQuery
    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    type: typing.Literal["postgreSqlImportConfig"] = "postgreSqlImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


Protocol = typing.Literal["HTTP", "HTTPS"]
"""Protocol to establish a connection with another system."""


class QueryParameterApiKey(pydantic.BaseModel):
    """QueryParameterApiKey"""

    query_parameter_name: str = pydantic.Field(alias=str("queryParameterName"))  # type: ignore[literal-required]
    """The name of the query parameter that the API key is passed in."""

    type: typing.Literal["queryParameter"] = "queryParameter"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


Region = str
"""The region of the external system."""


class ReplaceTableImportRequestDatabricksTableImportConfig(pydantic.BaseModel):
    """ReplaceTableImportRequestDatabricksTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["databricksImportConfig"] = "databricksImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ReplaceTableImportRequestJdbcTableImportConfig(pydantic.BaseModel):
    """ReplaceTableImportRequestJdbcTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["jdbcImportConfig"] = "jdbcImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ReplaceTableImportRequestMicrosoftAccessTableImportConfig(pydantic.BaseModel):
    """ReplaceTableImportRequestMicrosoftAccessTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["microsoftAccessImportConfig"] = "microsoftAccessImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ReplaceTableImportRequestMicrosoftSqlServerTableImportConfig(pydantic.BaseModel):
    """ReplaceTableImportRequestMicrosoftSqlServerTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["microsoftSqlServerImportConfig"] = "microsoftSqlServerImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ReplaceTableImportRequestOracleTableImportConfig(pydantic.BaseModel):
    """ReplaceTableImportRequestOracleTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["oracleImportConfig"] = "oracleImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ReplaceTableImportRequestPostgreSqlTableImportConfig(pydantic.BaseModel):
    """ReplaceTableImportRequestPostgreSqlTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["postgreSqlImportConfig"] = "postgreSqlImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ReplaceTableImportRequestSnowflakeTableImportConfig(pydantic.BaseModel):
    """ReplaceTableImportRequestSnowflakeTableImportConfig"""

    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    query: TableImportQuery
    type: typing.Literal["snowflakeImportConfig"] = "snowflakeImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


ReplaceTableImportRequestTableImportConfig = typing_extensions.Annotated[
    typing.Union[
        ReplaceTableImportRequestDatabricksTableImportConfig,
        ReplaceTableImportRequestJdbcTableImportConfig,
        ReplaceTableImportRequestMicrosoftSqlServerTableImportConfig,
        ReplaceTableImportRequestPostgreSqlTableImportConfig,
        ReplaceTableImportRequestMicrosoftAccessTableImportConfig,
        ReplaceTableImportRequestSnowflakeTableImportConfig,
        ReplaceTableImportRequestOracleTableImportConfig,
    ],
    pydantic.Field(discriminator="type"),
]
"""The import configuration for a specific [connector type](https://palantir.com/docs/foundry/data-integration/source-type-overview)."""


RestAuthenticationMode = typing_extensions.Annotated[
    typing.Union[BearerToken, ApiKeyAuthentication, BasicCredentials, "RestConnectionOAuth2"],
    pydantic.Field(discriminator="type"),
]
"""The method of authentication for connecting to an external REST system."""


RestConnectionAdditionalSecrets = typing_extensions.Annotated[
    typing.Union["SecretsWithPlaintextValues", "SecretsNames"], pydantic.Field(discriminator="type")
]
"""
When creating or updating additional secrets, use SecretsWithPlaintextValues.
When fetching the RestConnectionConfiguration, SecretsNames will be provided.
"""


class RestConnectionConfiguration(pydantic.BaseModel):
    """The configuration needed to connect to a [REST external system](https://palantir.com/docs/foundry/available-connectors/rest-apis)."""

    domains: typing.List[Domain]
    """
    The domains that the connection is allowed to access.
    At least one domain must be specified.
    """

    additional_secrets: typing.Optional[RestConnectionAdditionalSecrets] = pydantic.Field(alias=str("additionalSecrets"), default=None)  # type: ignore[literal-required]
    """
    Additional secrets that can be referenced in code and webhook configurations.
    If not provided, no additional secrets will be created.
    """

    oauth2_client_rid: typing.Optional[core.RID] = pydantic.Field(alias=str("oauth2ClientRid"), default=None)  # type: ignore[literal-required]
    """
    The RID of the [Outbound application](https://palantir.com/docs/foundry/administration/configure-outbound-applications) that is used to authenticate to the external system via OAuth2.
    Currently, a connection may use only one outbound application for OAuth 2.0 authentication.
    Selecting a different outbound application will update the configuration for all domains with OAuth 2.0 as the selected authorization.
    """

    type: typing.Literal["rest"] = "rest"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class RestConnectionOAuth2(pydantic.BaseModel):
    """
    In order to use OAuth2 you must have an Outbound application configured in the [Foundry Control Panel Organization settings](https://palantir.com/docs/foundry/administration/configure-outbound-applications#create-an-outbound-application).
    The RID of the Outbound application must be configured in the RestConnectionConfiguration in the `oauth2ClientRid` field.
    """

    type: typing.Literal["oauth2"] = "oauth2"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


RestRequestApiKeyLocation = typing_extensions.Annotated[
    typing.Union[HeaderApiKey, QueryParameterApiKey], pydantic.Field(discriminator="type")
]
"""The location of the API key in the request."""


S3AuthenticationMode = typing_extensions.Annotated[
    typing.Union[AwsAccessKey, CloudIdentity, AwsOidcAuthentication],
    pydantic.Field(discriminator="type"),
]
"""S3AuthenticationMode"""


class S3ConnectionConfiguration(pydantic.BaseModel):
    """
    The configuration needed to connect to an [AWS S3 external system (or any other S3-like external systems that
    implement the s3a protocol)](https://palantir.com/docs/foundry/available-connectors/amazon-s3/#amazon-s3).
    """

    bucket_url: str = pydantic.Field(alias=str("bucketUrl"))  # type: ignore[literal-required]
    """The URL of the S3 bucket. The URL should contain a trailing slash."""

    s3_endpoint: typing.Optional[str] = pydantic.Field(alias=str("s3Endpoint"), default=None)  # type: ignore[literal-required]
    """
    The endpoint of the S3 service. This is used to connect to a custom S3 service that is not AWS S3.
    If not specified, defaults to the [AWS S3 endpoint](https://docs.aws.amazon.com/general/latest/gr/s3.html).
    Warning: Specifying a region and a custom endpoint containing a region can lead to unexpected behavior.
    """

    region: typing.Optional[Region] = None
    """
    The region representing the location of the S3 bucket.
    Warning: Specifying a region and a custom endpoint containing a region can lead to unexpected behavior.
    """

    authentication_mode: typing.Optional[S3AuthenticationMode] = pydantic.Field(alias=str("authenticationMode"), default=None)  # type: ignore[literal-required]
    """
    The authentication mode to use to connect to the S3 external system. No authentication mode is required
    to connect to publicly accessible AWS S3 buckets.
    """

    s3_endpoint_signing_region: typing.Optional[Region] = pydantic.Field(alias=str("s3EndpointSigningRegion"), default=None)  # type: ignore[literal-required]
    """
    The region used when constructing the S3 client using a custom endpoint.
    This is often not required and would only be needed if you are using the S3 connector with an S3-compliant third-party API,
    and are also setting a custom endpoint that requires a non-default region.
    """

    client_kms_configuration: typing.Optional[S3KmsConfiguration] = pydantic.Field(alias=str("clientKmsConfiguration"), default=None)  # type: ignore[literal-required]
    """
    The client-side KMS key to use for encryption and decryption of data in the S3 bucket.
    If not specified, the default KMS key for the bucket is used.
    """

    sts_role_configuration: typing.Optional[StsRoleConfiguration] = pydantic.Field(alias=str("stsRoleConfiguration"), default=None)  # type: ignore[literal-required]
    """The configuration needed to assume a role to connect to the S3 external system."""

    proxy_configuration: typing.Optional[S3ProxyConfiguration] = pydantic.Field(alias=str("proxyConfiguration"), default=None)  # type: ignore[literal-required]
    """The configuration needed to connect to the S3 external system through a proxy."""

    max_connections: typing.Optional[int] = pydantic.Field(alias=str("maxConnections"), default=None)  # type: ignore[literal-required]
    """
    The maximum number of HTTP connections to the S3 service per sync.
    If not specified, defaults to 50 as defined by the [AWS SDK default](https://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/ClientConfiguration.html#DEFAULT_MAX_CONNECTIONS).
    """

    connection_timeout_millis: typing.Optional[core.Long] = pydantic.Field(alias=str("connectionTimeoutMillis"), default=None)  # type: ignore[literal-required]
    """
    The amount of time (in milliseconds) to wait when initially establishing a connection before giving up and timing out.
    If not specified, defaults to 10000 as defined by the [AWS SDK default](https://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/ClientConfiguration.html#DEFAULT_CONNECTION_TIMEOUT).
    """

    socket_timeout_millis: typing.Optional[core.Long] = pydantic.Field(alias=str("socketTimeoutMillis"), default=None)  # type: ignore[literal-required]
    """
    The amount of time (in milliseconds) to wait for data to be transferred over an established, open connection.
    If not specified, defaults to 50000 as defined by the [AWS SDK default](https://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/ClientConfiguration.html#DEFAULT_SOCKET_TIMEOUT).
    """

    max_error_retry: typing.Optional[int] = pydantic.Field(alias=str("maxErrorRetry"), default=None)  # type: ignore[literal-required]
    """
    The maximum number of retry attempts for failed requests to the S3 service.
    If not specified, defaults to 3 as defined by the [AWS SDK default](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/retry-strategy.html#retry-strategies).
    """

    match_subfolder_exactly: typing.Optional[bool] = pydantic.Field(alias=str("matchSubfolderExactly"), default=None)  # type: ignore[literal-required]
    """
    If true, only files in the subfolder specified in the bucket URL will be synced.
    If false, all files in the bucket will be synced.
    If not specified, defaults to false.
    """

    enable_requester_pays: typing.Optional[bool] = pydantic.Field(alias=str("enableRequesterPays"), default=None)  # type: ignore[literal-required]
    """
    Defaults to false, unless set and overwritten.
    If true, includes the [requester pays header](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html)
    in requests, allowing reads from requester pays buckets.
    """

    type: typing.Literal["s3"] = "s3"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class S3KmsConfiguration(pydantic.BaseModel):
    """S3KmsConfiguration"""

    kms_key: str = pydantic.Field(alias=str("kmsKey"))  # type: ignore[literal-required]
    """
    The client-side KMS key to use for encryption and decryption of data in the S3 bucket.
    If not specified, the default KMS key for the bucket is used.
    """

    kms_region: typing.Optional[Region] = pydantic.Field(alias=str("kmsRegion"), default=None)  # type: ignore[literal-required]
    """
    The region of the client-side KMS key to use for encryption and decryption of data in the S3 bucket.
    If not specified, the default KMS key region for the bucket is used.
    """

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class S3ProxyConfiguration(pydantic.BaseModel):
    """S3ProxyConfiguration"""

    host: str
    """
    Domain name, IPv4, or IPv6 address. 
    `protocol` and `port` must be specified separately.
    """

    port: int
    non_proxy_hosts: typing.Optional[typing.List[str]] = pydantic.Field(alias=str("nonProxyHosts"), default=None)  # type: ignore[literal-required]
    """A list of hosts that can bypass the proxy, such as those used for STS Role. You can also use "*" wildcards."""

    protocol: typing.Optional[Protocol] = None
    """If defined, must be "HTTP" or "HTTPS". Defaults to "HTTPS"."""

    credentials: typing.Optional[BasicCredentials] = None
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


SecretName = str
"""SecretName"""


class SecretsNames(pydantic.BaseModel):
    """
    A list of secret names that can be referenced in code and webhook configurations.
    This will be provided to the client when fetching the RestConnectionConfiguration.
    """

    secret_names: typing.List[SecretName] = pydantic.Field(alias=str("secretNames"))  # type: ignore[literal-required]
    """The names of the additional secrets that can be referenced in code and webhook configurations."""

    type: typing.Literal["asSecretsNames"] = "asSecretsNames"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class SecretsWithPlaintextValues(pydantic.BaseModel):
    """
    A map representing secret name to plaintext secret value pairs.
    This should be used when creating or updating additional secrets for a REST connection.
    """

    secrets: typing.Dict[SecretName, PlaintextValue]
    """The additional secrets that can be referenced in code and webhook configurations."""

    type: typing.Literal["asSecretsWithPlaintextValues"] = "asSecretsWithPlaintextValues"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


SnowflakeAuthenticationMode = typing_extensions.Annotated[
    typing.Union["SnowflakeExternalOauth", "SnowflakeKeyPairAuthentication", BasicCredentials],
    pydantic.Field(discriminator="type"),
]
"""SnowflakeAuthenticationMode"""


class SnowflakeConnectionConfiguration(pydantic.BaseModel):
    """The configuration needed to connect to a Snowflake database."""

    account_identifier: str = pydantic.Field(alias=str("accountIdentifier"))  # type: ignore[literal-required]
    """
    An [account identifier](https://docs.snowflake.com/en/user-guide/admin-account-identifier) uniquely 
    identifies a Snowflake account within your organization, as well as throughout the global network of 
    Snowflake-supported cloud platforms and cloud regions.

    The URL for an account uses the following format: <account_identifier>.snowflakecomputing.com.
    An example URL is https://acme-test_aws_us_east_2.snowflakecomputing.com.
    """

    database: typing.Optional[str] = None
    """
    Specifies the default database to use once connected. If unspecified, defaults to the empty string.
    The specified database should be an existing database for which the specified default role has privileges.

    See https://docs.snowflake.com/developer-guide/jdbc/jdbc-parameters#db
    """

    role: typing.Optional[str] = None
    """
    Specifies the default access control role to use in the Snowflake session initiated by the driver. 
    If unspecified, no role will be used when the session is initiated by the driver.

    The specified role should be an existing role that has already been assigned to the specified user for 
    the driver. If the specified role has not already been assigned to the user, the role is not used when 
    the session is initiated by the driver.

    See https://docs.snowflake.com/developer-guide/jdbc/jdbc-parameters#role
    """

    schema_: typing.Optional[str] = pydantic.Field(alias=str("schema"), default=None)  # type: ignore[literal-required]
    """
    Specifies the default schema to use for the specified database once connected. If unspecified, 
    defaults to the empty string.
    The specified schema should be an existing schema for which the specified default role has privileges.

    See https://docs.snowflake.com/developer-guide/jdbc/jdbc-parameters#schema
    """

    warehouse: typing.Optional[str] = None
    """
    Specifies the virtual warehouse to use once connected. If unspecified, defaults to the empty string. 
    The specified warehouse should be an existing warehouse for which the specified default role has privileges.

    See https://docs.snowflake.com/developer-guide/jdbc/jdbc-parameters#warehouse
    """

    authentication_mode: SnowflakeAuthenticationMode = pydantic.Field(alias=str("authenticationMode"))  # type: ignore[literal-required]
    """The authentication mode to use to connect to the Snowflake database."""

    jdbc_properties: JdbcProperties = pydantic.Field(alias=str("jdbcProperties"))  # type: ignore[literal-required]
    type: typing.Literal["snowflake"] = "snowflake"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class SnowflakeExternalOauth(pydantic.BaseModel):
    """
    Use an External OAuth security integration to connect and authenticate to Snowflake.

    See https://docs.snowflake.com/en/user-guide/oauth-ext-custom
    """

    audience: str
    """Identifies the recipients that the access token is intended for as a string URI."""

    issuer_url: str = pydantic.Field(alias=str("issuerUrl"))  # type: ignore[literal-required]
    """Identifies the principal that issued the access token as a string URI."""

    subject: ConnectionRid
    """The RID of the Connection that is connecting to the external system."""

    type: typing.Literal["externalOauth"] = "externalOauth"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class SnowflakeKeyPairAuthentication(pydantic.BaseModel):
    """
    Use a key-pair to connect and authenticate to Snowflake.

    See https://docs.snowflake.com/en/user-guide/key-pair-auth
    """

    user: str
    private_key: EncryptedProperty = pydantic.Field(alias=str("privateKey"))  # type: ignore[literal-required]
    type: typing.Literal["keyPair"] = "keyPair"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class SnowflakeTableImportConfig(pydantic.BaseModel):
    """The table import configuration for a [Snowflake connection](https://palantir.com/docs/foundry/available-connectors/snowflake)."""

    query: TableImportQuery
    initial_incremental_state: typing.Optional[TableImportInitialIncrementalState] = pydantic.Field(alias=str("initialIncrementalState"), default=None)  # type: ignore[literal-required]
    type: typing.Literal["snowflakeImportConfig"] = "snowflakeImportConfig"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class StringColumnInitialIncrementalState(pydantic.BaseModel):
    """The state for an incremental table import using a column with a string data type."""

    column_name: str = pydantic.Field(alias=str("columnName"))  # type: ignore[literal-required]
    current_value: str = pydantic.Field(alias=str("currentValue"))  # type: ignore[literal-required]
    """The initial incremental state value for the string column to reference in the query."""

    type: typing.Literal["stringColumnInitialIncrementalState"] = (
        "stringColumnInitialIncrementalState"
    )
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class StsRoleConfiguration(pydantic.BaseModel):
    """StsRoleConfiguration"""

    role_arn: str = pydantic.Field(alias=str("roleArn"))  # type: ignore[literal-required]
    """
    The Amazon Resource Name (ARN) of the role to assume.
    For more information, see the official [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-arn-format).
    """

    role_session_name: str = pydantic.Field(alias=str("roleSessionName"))  # type: ignore[literal-required]
    """
    An identifier for the assumed role session.
    The value can be any string that you assume will be unique within the AWS account.
    For more information, see the official [AWS documentation](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html#API_AssumeRole_RequestParameters).
    """

    role_session_duration: typing.Optional[core_models.Duration] = pydantic.Field(alias=str("roleSessionDuration"), default=None)  # type: ignore[literal-required]
    """
    The duration of the role session.
    The value specified can range from 900 seconds (15 minutes) up to the maximum session duration set for the role.
    The maximum session duration setting can have a value from 1 hour to 12 hours. For more details see the official [AWS documentation](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html#API_AssumeRole_RequestParameters).
    """

    external_id: typing.Optional[str] = pydantic.Field(alias=str("externalId"), default=None)  # type: ignore[literal-required]
    """
    A unique identifier that is used by third parties when assuming roles in their customers' accounts.
    For more information, see the official [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html).
    """

    sts_endpoint: typing.Optional[str] = pydantic.Field(alias=str("stsEndpoint"), default=None)  # type: ignore[literal-required]
    """
    By default, the AWS Security Token Service (AWS STS) is available as a global service, and all AWS STS requests go to a single endpoint at https://sts.amazonaws.com.
    AWS recommends using Regional AWS STS endpoints instead of the global endpoint to reduce latency, build in redundancy, and increase session token validity.
    """

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class TableImport(pydantic.BaseModel):
    """TableImport"""

    rid: TableImportRid
    connection_rid: ConnectionRid = pydantic.Field(alias=str("connectionRid"))  # type: ignore[literal-required]
    """The RID of the Connection (also known as a source) that the Table Import uses to import data."""

    dataset_rid: datasets_models.DatasetRid = pydantic.Field(alias=str("datasetRid"))  # type: ignore[literal-required]
    """The RID of the output dataset. Can not be modified after the table import is created."""

    branch_name: typing.Optional[datasets_models.BranchName] = pydantic.Field(alias=str("branchName"), default=None)  # type: ignore[literal-required]
    """The branch name in the output dataset that will contain the imported data. Defaults to `master` for most enrollments. Can not be modified after the table import is created."""

    display_name: TableImportDisplayName = pydantic.Field(alias=str("displayName"))  # type: ignore[literal-required]
    import_mode: TableImportMode = pydantic.Field(alias=str("importMode"))  # type: ignore[literal-required]
    allow_schema_changes: TableImportAllowSchemaChanges = pydantic.Field(alias=str("allowSchemaChanges"))  # type: ignore[literal-required]
    """Allow the TableImport to succeed if the schema of imported rows does not match the existing dataset's schema. Defaults to false for new table imports."""

    config: TableImportConfig
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


TableImportAllowSchemaChanges = bool
"""Allow the TableImport to succeed if the schema of imported rows does not match the existing dataset's schema. Defaults to false for new table imports."""


TableImportConfig = typing_extensions.Annotated[
    typing.Union[
        DatabricksTableImportConfig,
        JdbcTableImportConfig,
        MicrosoftSqlServerTableImportConfig,
        PostgreSqlTableImportConfig,
        MicrosoftAccessTableImportConfig,
        SnowflakeTableImportConfig,
        OracleTableImportConfig,
    ],
    pydantic.Field(discriminator="type"),
]
"""The import configuration for a specific [connector type](https://palantir.com/docs/foundry/data-integration/source-type-overview)."""


TableImportDisplayName = str
"""TableImportDisplayName"""


TableImportInitialIncrementalState = typing_extensions.Annotated[
    typing.Union[
        StringColumnInitialIncrementalState,
        DateColumnInitialIncrementalState,
        IntegerColumnInitialIncrementalState,
        "TimestampColumnInitialIncrementalState",
        LongColumnInitialIncrementalState,
        DecimalColumnInitialIncrementalState,
    ],
    pydantic.Field(discriminator="type"),
]
"""
The incremental configuration for a table import enables append-style transactions from the same table without duplication of data.
You must provide a monotonically increasing column such as a timestamp or id and an initial value for this column. 
An incremental table import will import rows where the value is greater than the largest already imported.

You can use the '?' character to reference the incremental state value when constructing your query. 
Normally this would be used in a WHERE clause or similar filter applied in order to only sync data with an incremental column value 
larger than the previously observed maximum value stored in the incremental state.
"""


TableImportMode = typing.Literal["SNAPSHOT", "APPEND"]
"""
Import mode governs how data is read from an external system, and written into a Foundry dataset. 

SNAPSHOT: Defines a new dataset state consisting only of data from a particular import execution.
APPEND: Purely additive and yields data from previous import executions in addition to newly added data.
"""


TableImportQuery = str
"""
A single SQL query can be executed per sync, which should output a data table 
and avoid operations like invoking stored procedures. 
The query results are saved to the output dataset in Foundry.
"""


TableImportRid = core.RID
"""The Resource Identifier (RID) of a TableImport (also known as a batch sync)."""


class TimestampColumnInitialIncrementalState(pydantic.BaseModel):
    """TimestampColumnInitialIncrementalState"""

    column_name: str = pydantic.Field(alias=str("columnName"))  # type: ignore[literal-required]
    current_value: core.AwareDatetime = pydantic.Field(alias=str("currentValue"))  # type: ignore[literal-required]
    """The initial incremental state value for the timestamp column in UTC to reference in the query."""

    type: typing.Literal["timestampColumnInitialIncrementalState"] = (
        "timestampColumnInitialIncrementalState"
    )
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


UriScheme = typing.Literal["HTTP", "HTTPS"]
"""Defines supported URI schemes to be used for external connections."""


class WorkflowIdentityFederation(pydantic.BaseModel):
    """
    Authenticate as a service principal using workload identity federation. This is the recommended way to connect to Databricks.
    Workload identity federation allows workloads running in Foundry to access Databricks APIs without the need for Databricks secrets.
    Refer to our [OIDC documentation](https://palantir.com/docs/foundry/data-connection/oidc) for an overview of how OpenID Connect is supported in Foundry.
    A service principal federation policy must exist in Databricks to allow Foundry to act as an identity provider.
    Refer to the [official documentation](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation) for guidance.
    """

    service_principal_application_id: typing.Optional[str] = pydantic.Field(alias=str("servicePrincipalApplicationId"), default=None)  # type: ignore[literal-required]
    """
    The ID of the Databricks [service principal](https://docs.databricks.com/aws/en/admin/users-groups/service-principals). 
    If provided, a federated JWT token is exchanged using a
    service principal federation policy. If not provided, a federated JWT token is exchanged using an account
    federation policy.
    """

    issuer_url: str = pydantic.Field(alias=str("issuerUrl"))  # type: ignore[literal-required]
    """Identifies the principal that issued the access token as a string URI."""

    audience: str
    """
    Identifies the recipients that the access token is intended for as a string URI. 
    This should be the primary host name where the Connection lives.
    """

    subject: ConnectionRid
    """The RID of the Connection that is connecting to the external system."""

    type: typing.Literal["workflowIdentityFederation"] = "workflowIdentityFederation"
    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return the dictionary representation of the model using the field aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


core.resolve_forward_references(ConnectionConfiguration, globalns=globals(), localns=locals())
core.resolve_forward_references(
    CreateConnectionRequestConnectionConfiguration, globalns=globals(), localns=locals()
)
core.resolve_forward_references(
    CreateConnectionRequestDatabricksAuthenticationMode, globalns=globals(), localns=locals()
)
core.resolve_forward_references(
    CreateConnectionRequestEncryptedProperty, globalns=globals(), localns=locals()
)
core.resolve_forward_references(
    CreateConnectionRequestSnowflakeAuthenticationMode, globalns=globals(), localns=locals()
)
core.resolve_forward_references(
    CreateTableImportRequestTableImportConfig, globalns=globals(), localns=locals()
)
core.resolve_forward_references(DatabricksAuthenticationMode, globalns=globals(), localns=locals())
core.resolve_forward_references(EncryptedProperty, globalns=globals(), localns=locals())
core.resolve_forward_references(FileImportFilter, globalns=globals(), localns=locals())
core.resolve_forward_references(JdbcProperties, globalns=globals(), localns=locals())
core.resolve_forward_references(
    ReplaceTableImportRequestTableImportConfig, globalns=globals(), localns=locals()
)
core.resolve_forward_references(RestAuthenticationMode, globalns=globals(), localns=locals())
core.resolve_forward_references(
    RestConnectionAdditionalSecrets, globalns=globals(), localns=locals()
)
core.resolve_forward_references(RestRequestApiKeyLocation, globalns=globals(), localns=locals())
core.resolve_forward_references(S3AuthenticationMode, globalns=globals(), localns=locals())
core.resolve_forward_references(SnowflakeAuthenticationMode, globalns=globals(), localns=locals())
core.resolve_forward_references(TableImportConfig, globalns=globals(), localns=locals())
core.resolve_forward_references(
    TableImportInitialIncrementalState, globalns=globals(), localns=locals()
)

__all__ = [
    "ApiKeyAuthentication",
    "AsPlaintextValue",
    "AsSecretName",
    "AwsAccessKey",
    "AwsOidcAuthentication",
    "BasicCredentials",
    "BearerToken",
    "CloudIdentity",
    "CloudIdentityRid",
    "Connection",
    "ConnectionConfiguration",
    "ConnectionDisplayName",
    "ConnectionExportSettings",
    "ConnectionRid",
    "CreateConnectionRequestAsPlaintextValue",
    "CreateConnectionRequestAsSecretName",
    "CreateConnectionRequestBasicCredentials",
    "CreateConnectionRequestConnectionConfiguration",
    "CreateConnectionRequestDatabricksAuthenticationMode",
    "CreateConnectionRequestDatabricksConnectionConfiguration",
    "CreateConnectionRequestEncryptedProperty",
    "CreateConnectionRequestJdbcConnectionConfiguration",
    "CreateConnectionRequestOauthMachineToMachineAuth",
    "CreateConnectionRequestPersonalAccessToken",
    "CreateConnectionRequestRestConnectionConfiguration",
    "CreateConnectionRequestS3ConnectionConfiguration",
    "CreateConnectionRequestSnowflakeAuthenticationMode",
    "CreateConnectionRequestSnowflakeConnectionConfiguration",
    "CreateConnectionRequestSnowflakeExternalOauth",
    "CreateConnectionRequestSnowflakeKeyPairAuthentication",
    "CreateConnectionRequestWorkflowIdentityFederation",
    "CreateTableImportRequestDatabricksTableImportConfig",
    "CreateTableImportRequestJdbcTableImportConfig",
    "CreateTableImportRequestMicrosoftAccessTableImportConfig",
    "CreateTableImportRequestMicrosoftSqlServerTableImportConfig",
    "CreateTableImportRequestOracleTableImportConfig",
    "CreateTableImportRequestPostgreSqlTableImportConfig",
    "CreateTableImportRequestSnowflakeTableImportConfig",
    "CreateTableImportRequestTableImportConfig",
    "DatabricksAuthenticationMode",
    "DatabricksConnectionConfiguration",
    "DatabricksTableImportConfig",
    "DateColumnInitialIncrementalState",
    "DecimalColumnInitialIncrementalState",
    "Domain",
    "EncryptedProperty",
    "FileAnyPathMatchesFilter",
    "FileAtLeastCountFilter",
    "FileChangedSinceLastUploadFilter",
    "FileImport",
    "FileImportCustomFilter",
    "FileImportDisplayName",
    "FileImportFilter",
    "FileImportMode",
    "FileImportRid",
    "FileLastModifiedAfterFilter",
    "FilePathMatchesFilter",
    "FilePathNotMatchesFilter",
    "FileProperty",
    "FileSizeFilter",
    "FilesCountLimitFilter",
    "HeaderApiKey",
    "IntegerColumnInitialIncrementalState",
    "JdbcConnectionConfiguration",
    "JdbcProperties",
    "JdbcTableImportConfig",
    "ListFileImportsResponse",
    "ListTableImportsResponse",
    "LongColumnInitialIncrementalState",
    "MicrosoftAccessTableImportConfig",
    "MicrosoftSqlServerTableImportConfig",
    "OauthMachineToMachineAuth",
    "OracleTableImportConfig",
    "PersonalAccessToken",
    "PlaintextValue",
    "PostgreSqlTableImportConfig",
    "Protocol",
    "QueryParameterApiKey",
    "Region",
    "ReplaceTableImportRequestDatabricksTableImportConfig",
    "ReplaceTableImportRequestJdbcTableImportConfig",
    "ReplaceTableImportRequestMicrosoftAccessTableImportConfig",
    "ReplaceTableImportRequestMicrosoftSqlServerTableImportConfig",
    "ReplaceTableImportRequestOracleTableImportConfig",
    "ReplaceTableImportRequestPostgreSqlTableImportConfig",
    "ReplaceTableImportRequestSnowflakeTableImportConfig",
    "ReplaceTableImportRequestTableImportConfig",
    "RestAuthenticationMode",
    "RestConnectionAdditionalSecrets",
    "RestConnectionConfiguration",
    "RestConnectionOAuth2",
    "RestRequestApiKeyLocation",
    "S3AuthenticationMode",
    "S3ConnectionConfiguration",
    "S3KmsConfiguration",
    "S3ProxyConfiguration",
    "SecretName",
    "SecretsNames",
    "SecretsWithPlaintextValues",
    "SnowflakeAuthenticationMode",
    "SnowflakeConnectionConfiguration",
    "SnowflakeExternalOauth",
    "SnowflakeKeyPairAuthentication",
    "SnowflakeTableImportConfig",
    "StringColumnInitialIncrementalState",
    "StsRoleConfiguration",
    "TableImport",
    "TableImportAllowSchemaChanges",
    "TableImportConfig",
    "TableImportDisplayName",
    "TableImportInitialIncrementalState",
    "TableImportMode",
    "TableImportQuery",
    "TableImportRid",
    "TimestampColumnInitialIncrementalState",
    "UriScheme",
    "WorkflowIdentityFederation",
]
