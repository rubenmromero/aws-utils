# AWS Utils

Utilities and resources to build and deploy Gigigo projects on Amazon Web Services.

## CloudFormation

* `project-env-2az-vpc.template` => Creation of network structure based on 2 availability zones for a new project environment
* `project-env-3az-vpc.template` => Creation of network structure based on 3 availability zones for a new project environment

### project-env-2az-vpc.template & project-env-3az-vpc.template

Enter `<Project>-<Env>-VPC` as stack name, where:

* `<Project>` matchs the `ProjectName` parameter value
* `<Env>` matchs the `Environment` parameter value

## Lambda

### ecs_manage_services.py

Function to start and stop in a scheduled way all services belonging to an ECS cluster set through the `ECS_CLUSTER` environment variable.

When a start action is performed the service is scaled out to 1 service task, and in the same way, when a stop action is performed the service is scaled in to 0 service tasks.

#### IAM Role

Create an AWS IAM role, for example called `ECS_Manage`, with at least the following permission policies:

* `ECS-ManageServices-<YYYYMMDD>` inline policy with the following JSON:

      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Sid": "Stmt1430150596000",
                  "Effect": "Allow",
                  "Action": [
                      "ecs:ListServices",
                      "ecs:DescribeServices",
                      "ecs:UpdateService"
                  ],
                  "Resource": [
                      "*"
                  ]
              }
          ]
      }

* `AWSLambdaBasicExecutionRole` managed policy

And attach it to the Lambda function.

#### Environment variables

This function requires the following environment variable to be set for its correct execution:

* `ECS_CLUSTER` => Cluster name whose services are to be started

That is:

    ECS_CLUSTER=<ecs_cluster_name>

#### Usage

The proper tags must be added to the ECS services in order to perform the start and/or stop actions based on the schedule set as the value of each tag.

The name of the tag is the action and the value is a cron expression, including numbers, ranges and enumerations. Some examples are:

Tag Name | Tag Value | Description
---- | ---- | ---
startService | 30 6 1-5 | Start the service at 6:30 UTC on business days
startService | 0 7 1-7 | Start the service at 7:00 UTC every day of the week
stopService | 30 17 1-5 | Stop the service at 17:30 UTC on business days
stopService | 0 0 2-6 | Stop the service at 0:00 UTC on business days

### ecs_stop_services.py

Function to stop all services belonging to an ECS cluster set through the `ECS_CLUSTER` environment variable, scaling in each of them to 0 service tasks.

#### IAM Role

Create an AWS IAM role, for example called `ECS_Manage`, with at least the following permission policies:

* `ECS-ManageServices-<YYYYMMDD>` inline policy with the following JSON:

      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Sid": "Stmt1430150596000",
                  "Effect": "Allow",
                  "Action": [
                      "ecs:ListServices",
                      "ecs:UpdateService"
                  ],
                  "Resource": [
                      "*"
                  ]
              }
          ]
      }

* `AWSLambdaBasicExecutionRole` managed policy

And attach it to the Lambda function.

#### Environment variables

This function requires the following environment variables to be set for its correct execution:

* `ECS_CLUSTER` => Cluster name whose services are to be stopped
* `EXCLUDED_SERVICES` => List of services to be excluded from being stopped

That is:

    ECS_CLUSTER=<ecs_cluster_name>
    EXCLUDED_SERVICES=<ecs_service_1> <ecs_service_2> <ecs_service_3> ...

### ecs_start_services.py

Function to start all services belonging to an ECS cluster set through the `ECS_CLUSTER` environment variable, scaling out each of them to 1 service tasks.

#### IAM Role

Create an AWS IAM role, for example called `ECS_Manage`, with at least the following permission policies:

* `ECS-ManageServices-<YYYYMMDD>` inline policy with the following JSON:

      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Sid": "Stmt1430150596000",
                  "Effect": "Allow",
                  "Action": [
                      "ecs:ListServices",
                      "ecs:UpdateService"
                  ],
                  "Resource": [
                      "*"
                  ]
              }
          ]
      }

* `AWSLambdaBasicExecutionRole` managed policy

And attach it to the Lambda function.

#### Environment variables

This function requires the following environment variable to be set for its correct execution:

* `ECS_CLUSTER` => Cluster name whose services are to be started

That is:

    ECS_CLUSTER=<ecs_cluster_name>

## Related Links

* [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/index.html)
* [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/index.html)
* [Amazon Elastic Container Service Documentation](https://docs.aws.amazon.com/ecs/index.html)
