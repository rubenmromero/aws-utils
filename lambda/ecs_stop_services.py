#
# Modules Import
#
import boto3
import json
import os

#
# Variables Definition
#
ecs_cluster = os.environ['ECS_CLUSTER']
excluded_services = os.environ['EXCLUDED_SERVICES'].split(' ')
result = { 'stoppedServices': [ ], 'excludedServices': [ ] }

#
# Function to print the boto3 responses in JSON format
#
def print_response(response):
    return json.dumps(
        response,
        default=str,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    )

#
# Main
#
def lambda_handler(event, context):
    print("\n##### Starting execution #####\n")
    
    ecs = boto3.client('ecs')
    
    # Get all services belonging to the ECS cluster
    ecs_services = ecs.list_services(cluster=ecs_cluster)['serviceArns']
    
    for service in ecs_services:
        if os.path.basename(service) in excluded_services:
            print("\n'" + service + "' ECS service is excluded")
            result['excludedServices'].append(service)
        else:
            print("\nScaling in '" + service + "' ECS service tasks to 0...")
            response = ecs.update_service(
                cluster=ecs_cluster,
                service=service,
                desiredCount=0
            )

            print_response(response)
            result['stoppedServices'].append(service)

    print("\nFinal result:\n" + print_response(result) + "\n")
    print("\n##### Execution finished #####\n")
    return {
        'statusCode': 200,
        'body': print_response(result)
    }
