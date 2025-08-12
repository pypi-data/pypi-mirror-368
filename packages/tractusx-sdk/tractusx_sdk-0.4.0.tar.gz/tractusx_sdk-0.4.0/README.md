> [!IMPORTANT]
> This Software is still in development. Please consult our [Roadmap](#roadmap)

# Tractus-X Software Development KIT

Eclipse Tractus-X Software Development KIT - The Dataspace &amp; Industry Foundation Libraries

A modular facade with generic microservices that allows you to "provide" and "consume" data from Catena-X with simplified APIs and methods.

It aims to provide a reference implementation for the various interactions between applications and services like the EDC, Digital Twin Registry and Submodel Service.
Is the literal "tool box" you need to provide data and consume data, how you orchestrate it is then up to you and your use case.

This SDK will manage automatically the version updates from the EDC and the Digital Twin Registry, providing a "smart REST API middleware" that will be maintained by the community.

No specific use case logic will be configured here, only the bare minimum for interacting in a Dataspace and developing your own applications with this stack, based on the KITs which adopt the core data exchange functionalities, in concrete the following ones:

- [Connector KIT](https://eclipse-tractusx.github.io/docs-kits/kits/Connector%20Kit/Adoption%20View/connector_kit_adoption_view)
- [Digital Twin KIT](https://eclipse-tractusx.github.io/docs-kits/kits/Digital%20Twin%20Kit/Adoption%20View%20Digital%20Twin%20Kit)
- [Industry Core KIT](https://eclipse-tractusx.github.io/docs-kits/kits/Industry%20Core%20Kit/Business%20View%20Industry%20Core%20Kit)

An example of SDK that is already used in Tractus-X is the [Portal Shared Components](https://github.com/eclipse-tractusx/portal-shared-components), however this SDK shall aim to be generic for every application.

## Installation

Install the package directly from PyPI:

```bash
pip install tractusx-sdk
```

## Roadmap

The development roadmap is the same as the industry core hub.

```
February 3 2025     R25.06             R25.09          R25.12
Kickoff              MVP                Stable          NEXT            2026 -> Beyond
| ------------------> | ----------------> | -----------> |  ----------------> | 
                Data Provision     Data Consumption    IC-HUB             + KIT Use Cases
                     SDK                 SDK             + Integrate First
                                                           Use Case (e.g. DPP) (Another usage for the SDK)
```

## What can you do with this SDK?

- You can create a frontend for your use case (with any technology) and consume the APIs.
- Also, you can create a backend in python and import the libraries.
- Furthermore, you can use this in a Jupyter notebook for example, or create your personal scripts for using the EDC, DTR and Submodel Service.
- It enables you to build your own use case logic over it, without needing to worry about versioning.
- Base yourself in the [Industry Core Hub](https://github.com/eclipse-tractusx/industry-core-hub) which provides you a "lighthouse" for using this SDK.

## Applications that use this SDK

- [Industry Core Hub](https://github.com/eclipse-tractusx/industry-core-hub):
  - [Backend](https://github.com/eclipse-tractusx/industry-core-hub/tree/main/ichub-backend): An example of how to use the SDK dataspace & industry libaries in your application.
  - [Frontend](https://github.com/eclipse-tractusx/industry-core-hub/tree/main/ichub-frontend): An example of how to use the SDK API interfaces from each microservice.
  - The use case add-ons from the IC-Hub will also use this!

- [Tractus-X SDK Services](https://github.com/eclipse-tractusx/tractusx-sdk-services)
  - [DT Pull Service](https://github.com/eclipse-tractusx/tractusx-sdk-services): Provides a service that pulls digital twins from data providers.
  - [Test Orchestrator](https://github.com/eclipse-tractusx/tractusx-sdk-services): Provides a test agent service that can check if the configuration of your data provision services is compliant with the standard schemas & syntaxis.

- Open for more collaboration!

## Why was this Tractus-X SDK Created?

Here you will find a design decision which was taken at the beginning of the industry core hub development:

[Industry Core Hub Decision Record 0002](https://github.com/eclipse-tractusx/industry-core-hub/blob/main/docs/architecture/decision-records/0002-tractus-x-sdk.md)

While developing the Industry Core Hub, in parallel we decided to create a SDK for Tractus-X.

[Industry Core Hub Decision Record 0003 Create new Repository](https://github.com/eclipse-tractusx/industry-core-hub/blob/main/docs/architecture/decision-records/0003-tractus-x-sdk-individual-repository.md) 

Having a individual SDK repository, we are creating a reusable and modular middleware/library for all use cases and applications that want to easily interact with the Tractus-X Datapaces Components required for data provision and data consumption:

- [Tractus-X Eclipse Dataspace Connector (EDC)](https://github.com/eclipse-tractusx/tractusx-edc)
- [Tractus-X Digital Twin Registry](https://github.com/eclipse-tractusx/sldt-digital-twin-registry)
- [Simple Data Backend](https://github.com/eclipse-tractusx/tractus-x-umbrella/tree/main/simple-data-backend)

And other core services like:

**Additional Services**:

- Discovery Services:
  - [Discovery Finder](https://github.com/eclipse-tractusx/sldt-discovery-finder)  
  - [BPN Discovery](https://github.com/eclipse-tractusx/sldt-bpn-discovery)
  - [EDC Discovery](https://github.com/eclipse-tractusx/portal-backend)
  
- [Portal IAM/IDP](https://github.com/eclipse-tractusx/portal-iam)

Our aim is to automate the target releases and compatibility with this systems using DevOps mechanisms.

## High Level Architecture

Providing two reusable libraries:

- [Dataspace Foundation Library](./src/tractusx_sdk/dataspace)
  - Enables your "bytes" data exchange using the EDC and the core services from Catena-X.
  - It provides tools for your exchange agnostic from your use case.
- [Industry Foundation Library](./src/tractusx_sdk/industry)
  - Enables your data exchange using the dataspace foundation library but for the usage of Digital Twins in the Digital Twin Registry.

![Architecture](./docs/media/catena-x-speedway-sdk.svg)

## Industry Core Hub Example

![context sdk](docs/media/sdk-context.png)

You can use it to build you use case application how you want, based on the industry core foundation or not:

![modular sdk](docs/media/modular-microservices-architecture.svg)

## Dataspace Architecture Patterns

This SDK will be developed based and will follow the Dataspace & Industry Usage Patterns recommended in Eclipse Tractus-X [sig-architecture](https://github.com/eclipse-tractusx/sig-architecture)

## How to Get Involved

- **Get onboarded**: [Getting started](https://eclipse-tractusx.github.io/docs/oss/getting-started/). Join the Eclipse Tractus-X open source community as a contributor!
- Attend the [official community office hours](https://eclipse-tractusx.github.io/community/open-meetings/#Community%20Office%20Hour) and raise your issue!
- Attend our [Industry Core Hub Weekly](https://eclipse-tractusx.github.io/community/open-meetings#[IC-Hub]%20Industry%20Core%20Hub%20Weekly)
- Join our [Tractus-X SDK Matrix Chat](https://matrix.to/#/#tractusx-industry-core-hub:matrix.eclipse.org)

### Found a bug?

👀 If you have identified a bug or want to fix an existing documentation, feel free to create a new issue at our project's corresponding [GitHub Issues page](https://github.com/eclipse-tractusx/industry-core-hub/issues/new/choose)

 ⁉️ Before doing so, please consider searching for potentially suitable [existing issues](https://github.com/eclipse-tractusx/industry-core-hub/issues).

🙋 **Assign to yourself** - Show others that you are working on this issue by assigning it to yourself.
<br> To do so, click the cog wheel next to the Assignees section just to the right of this issue.

### Discuss

📣 If you want to share an idea to further enhance the project, please feel free to contribute to the [discussions](https://github.com/eclipse-tractusx/industry-core-hub/discussions),
otherwise [create a new discussion](https://github.com/eclipse-tractusx/industry-core-hub/discussions/new/choose)

## Reporting a Security Issue

Please follow the [Security Issue Reporting Guidelines](https://eclipse-tractusx.github.io/docs/release/trg-7/trg-7-01#security-file) if you come across any security vulnerabilities or concerns.

## Licenses

- [Apache-2.0](https://raw.githubusercontent.com/eclipse-tractusx/tractusx-sdk/main/LICENSE) for code
- [CC-BY-4.0](https://spdx.org/licenses/CC-BY-4.0.html) for non-code
---

Thank you for using Software Development KIT! If you have any questions or need further assistance, please feel free to reach out.
