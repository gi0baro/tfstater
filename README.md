# TFStater

An HTTP Terraform state backend with locking support.

TFStater requires a PostgreSQL database and an S3-compatible object storage endpoint.

## Installation

TFStater can be installed to any Kubernetes >= 1.14 cluster using the Helm 3 chart:

```
helm repo add tfstater https://gi0baro.github.io/tfstater
helm install --generate-name --atomic tfstater/tfstater
```

TFStater includes support to also deploy its dependencies, just enable them in the values:

```yaml
postgresql:
  enabled: true
  postgresqlPassword: your-super-strong-password

minio:
  enabled: true
  rootPassword: another-super-strong-password
```

## Configuration

### Minimal configuration

TFStater requires a minimal configuration in order to work. Add the following to your Helm values:

```yaml
config:
  auth:
    hmac_key: a-very-strong-key
    cookies_key: another-strong-key
    allow_email_login: true
    registration_approval: true

adminUser:
  create: true
  email: admin@my.tld
  password: your-super-secret-password
```

In order to expose your TFStater instance you also need to enable the Ingress resource:

```yaml
ingress:
  enabled: true

  hosts:
    - tf-states.my-domain.tld
```

### Using external PostgreSQL instances

You can customise the `config.db` values:

```yaml
config:
  db:
    host: my-postgres-endpoint
    database: tfstater
    user: tfstater
    password: super-secret-password
```

### Using external object storage

You can customise the `config.object_storage` values:

```yaml
config:
  object_storage:
    region: eu-central-1
    bucket: my-s3-bucket
    access_key: ""
    secret_key: ""
    # path_prefix: terraform/states
```

For S3-compatible providers, you might need to specify the endpoint:

```yaml
config:
  object_storage:
    endpoint: http://my-minio.tld:5000
```

### Encrypt state contents

TFStater has the capability to encrypt your state contents:

```yaml
config:
  object_storage:
    encrypt_data: true
```

this might become handy in case you share the bucket with other applications/users.

### Authentication

TFStater is primarly designed for teams. Users in TFStater might have one of the following roles:

- maintainer
- member

Only users with `maintainer` role are allowed to lock states and – consequentially – push changes.

This is why we suggest to use an external Identity Provider to handle users:

```yaml
config:
  auth:
    allow_email_login: false

  idp:
    provider:
      # provider specific configuration
```

#### Github OIDC

Create an OAuth application within your Github organization. Set the callback url to `http|https://{tfstater-instance}/account/github/exchange` and use the Github login:

```yaml
config:
  auth:
    allow_email_login: false

  idp:
    github:
      client_id: your-gh-app-client-id
      client_secret: your-gh-app-secret
      organization: your-organization

      ## (optionally) require specific github roles
      claim_roles:
        - admin
      ## (optionally) require specific github team membership
      claim_teams:
        - sre
      ## (optionally) match github roles with TFStater ones
      match_roles:
        admin: maintainer
      ## (optionally) match github teams with TFStater roles
      match_teams:
        sre: maintainer
```

#### Use email login

TFStater provides also a standard email signup flow. In order to verify new signups, you have 2 options: manual approval, and email verification.

In order to setup manual approval, you also need to create your fist user:

```yaml
config:
  auth:
    allow_email_login: true
    registration_approval: true

adminUser:
  create: true
  email: admin@my.tld
  password: your-super-secret-password
```

using this configuration, you can manually approve users through the settings page.

The email verification flow requires domain restriction and to setup an smtp server to allow TFStater to send verifications:

```yaml
config:
  auth:
    allow_email_login: true
    registration_verification: true
    restrict_email_domain: "@my.tld"

  smtp:
    sender: tfstater@my.tld
    server: smtp.my.tld
    username: tfstater
    password: super-secret-password
    # port: 25
    # use_tls: false
    # use_ssl: false
```

## Usage

Login to your TFStater instance and through the settings view obtain your Api-Key. Then you just need define the `backend` block in you Terraform code:

```terraform
terraform {
  backend "http" {
    address = "https://{tfstater-instance}/terraform/{state-name}"
    lock_address = "https://{tfstater-instance}/terraform/{state-name}/lock"
    unlock_address = "https://{tfstater-instance}/terraform/{state-name}/lock"
    lock_method = "POST"
    unlock_method = "DELETE"
  }
}
```

and initialise your configuration using *token* as username and your Api-Key as password.

## License

TFStater is released under the BSD License.
