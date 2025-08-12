# acme-portal-sdk

> **Important:** This SDK is currently in alpha and primarily for demonstration purposes. APIs may still change frequently.

SDK to provide data and actions for `acme-portal` `VSCode` [extension](https://github.com/blackwhitehere/acme-portal).

Rather than embedding a pre-defined logic in `acme-portal` extension, the SDK
allows to define sources of data and behaviour for extension functionality. As such, the extension servers as UI layer to the implementation provided by SDK objects.

[AI wiki](https://deepwiki.com/blackwhitehere/acme-portal-sdk/)

## Problem

A repeatable source of pain while working on software is that deployment processes are highly specific to a given project. While the application may be written in a well known language or framework, the deployment process is usually specialized to a given application, team and company making it difficult for new and existing team members to understand how to just "ship" their code.

`acme-portal` and `acme-portal-sdk` attempt to address that problem by proposing a standard UI & workflow of deploying a python application.
However, rather than dictating an exact deployment implementation, the two packages jointly define only high level deployment concepts and allow users to customize the implementation.

In a way, they attempt to make the deployment process as frictionless and intuitive as possible, without simplifying the deployment to a restrained set of practices.

`acme-portal-sdk` contains abstract interfaces expected by the `VSCode` `acme-portal` extension. It also contains a specific implementation for a python application based on the `prefect` orchestration library. Users of the SDK can easily extend the abstract interfaces to their projects. Some standard implementation schemes like one based on e.g. `airflow` can be made part of SDK in the future.

## Concepts

To the end of clarifying deployment process, the SDK defines the following concepts:

* `Flow` - (often named in various frameworks as `Workflow` / `Job` / `DAG`) is a unit of work in an application. It can also be though of as an `executable script` or `entrypoint`. A `Flow` can have sub-elements like `Steps` / `Tasks` / `Nodes`, but those are not tracked by the SDK. Flows form a basis of what unit of computation is deployed. In this way an application is composed of multiple related `Flows` maintained by the team, with a desire to deploy them independently of each other.
* `Deployment` - is a piece of configuration defined in an execution environment (e.g. `Prefect`/`Airflow` Server, a remote server, some AWS Resources) that defines how to run a unit of work (a `Flow`). `Deployment` is then capable of orchestrating physical resources (by e.g. submitting requests, having execute permissions) and generally use environment resources to perform computation.
* `Environment` - (sometimes called `Namespace`, `Version`, `Label`) is a persistent identifier of an application version run in a given `Deployment`. Popular `Environment` names used are `dev`, `tst`, `uat`, `prod`. Environment names are useful to communicate release state of a given feature (and its code changes) in an application release cycle. They give meaning to statements like "those changes are in `dev` only", "this feature needs to be tested in `uat`", etc.

Having those concepts defined the SDK defines the following actions:

* `Find Flows` - scan code or configration to find `Flows` which can be deployed
* `Find Deployments` - find existing `Flow` deployment information 
* `Deploy` - uses information about the `Flow` together with additional deployment configuration to create a `Deployment` in an initial, starting environment (e.g. `dev`).
* `Promote` - having completed required validation steps on deployment outputs in a given environment, the code version used in source `Deployment` can be deployed to a target environment (e.g. from `dev` to `uat`)

The `acme-portal` VSCode extension then displays flow and deployment infromation and provides UI elements (buttons, forms) / VSCode tasks to trigger `Deploy` and `Promote` actions.

The SDK and `acme-portal` are intended to complement use of CICD pipelines in cases where deployments can not be fully automated.

For explanation on how to configure your project to work with `acme-portal` using the SDK, checkout [Configuring SDK for your project](user/user-guides.md#configuring-sdk-for-your-project)

For explanation of the features provided by default `prefect` based implementation checkout [Default functionality of `prefect` based implementation](user/features.md#default-functionality-of-prefect-based-implementation)

See guide [Using default `prefect` based functionality](user/user-guides.md#using-default-prefect-based-functionality) for how to configure your project to work with `acme-portal` using the default `prefect` based implementation. You can view a sample project using it under [`acme-prefect`](https://github.com/blackwhitehere/acme-prefect).