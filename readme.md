# PoC REST using AWS API Gateway/Labda/RDS

## Setup

1. Create variables.tf, where `profile` correspond `~/.aws/credentials` 
2. Execute `terraform apply` (aprox. 10 min)
3. Pay attention to the output API URL
4. Start playing with PoC API, for exmaple using `curl`

## API 

#### GET /

To do

#### GET /app

Get application list

- 200 array of names

#### GET /app/{app}

Get application {app}

- 200 app
- 404 app not exists

#### PUT /app/{app}

Add application {app}

- 201 created
- 404 app already exists

#### DELETE /app/{app}

Remove application {app}

- 204 app removed
- 404 app not exists

#### GET /app/{app}/cluser

Get application {app} cluster list

- 200 array of clusters
- 404 app not exists

#### GET /app/{app}/cluser

Get application {app} cluster list

- 200 array of app clusters
- 404 app not exists

#### GET /app/{app}/cluser/{cluster}

Test application {app} associated with cluster {cluster}

- 200 clusters
- 404 app or cluster not exists

#### PUT /app/{app}/cluser/{cluster}

Associate application {app} with cluster {cluster}

- 201 association created
- 404 app or cluster not exists
- 409 association already exists

#### DEL /app/{app}/cluser/{cluster}

Remove application {app} association with cluster {cluster}

- 204 association removed
- 404 app or cluster not exists

#### GET /cluster/{app}

Get cluster {cluster}

- 200 cluster
- 404 cluster not exists

#### PUT /cluster/{cluster}

Add cluster {cluster}

- 201 created
- 404 cluster already exists

#### DELETE /cluster/{cluster}

Remove cluster {cluster}

- 204 cluster removed
- 404 cluster not exists

#### GET /cluster/{cluster}/app

Get cluster {cluster} application list

- 200 array of cluster apps
- 404 cluster not exists

#### GET /cluster/{cluster}/app/{app}

Test cluster {cluster} associated with application {app}

- 200 app
- 404 app or cluster not exists

#### PUT /cluster/{cluster}/app/{app}

Associate cluster {cluster} with application {app}

- 201 association created
- 404 app or cluster not exists
- 409 association already exists

#### DEL /cluster/{cluster}/app/{app}

Remove cluster {cluster} association with application {app}

- 204 association removed
- 404 app or cluster not exists

## Examples using `curl`

1. Setup endpoint and curl
    ```bash 
    $ export $ENDPOINT=https://xxxxxxxxxxx.execute-api.eu-north-1.amazonaws.com/dev
    $ alias curl="curl -w '\nHTTP STATUS: %{http_code}\n'"
    ```
2. Get root
    ```bash 
    $ curl $ENDPOINT
    ```
3. Get app list
    ```bash
    $ curl $ENDPOINT/app
    ```
4. Add app 123
    ```bash
    $ curl -X PUT $ENDPOINT/app/123
    ```
5. Add cluster 456
    ```bash
    $ curl -X PUT $ENDPOINT/cluster/456
    ```
6. Get app cluster list
    ```bash
    $ curl $ENDPOINT/app/123/cluster
    ```
7. Attach cluster 456 to app 123
    ```bash
    curl -X PUT $ENDPOINT/app/123/cluster/456
    ```
8. Detach cluster 456 from app 123
    ```bash
    $ curl -X PUT $ENDPOINT/app/123/cluster/456
    ```

## variables.tf example

```bash
$ cat variables.tf

#AWS cconfig
variable "account_id" {
 default = "xxxxxxxxxxxxx"
}

variable "region" {
 default = "xxxxxxxxxxxxx"
}

variable "profile" {
  default = "xxxxxxxxxxxxx"
}

# RDS credentials
variable "username" {
  default = "xxxxxxxxxxxxx"
}

variable "password" {
  default = "xxxxxxxxxxxxx"
}
```

## DB schema

```sql
CREATE TABLE application (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE cluster (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE application_clusters (
    application_id INTEGER NOT NULL,
    cluster_id INTEGER NOT NULL,
    FOREIGN KEY (application_id) REFERENCES application (id),
    FOREIGN KEY (cluster_id) REFERENCES cluster (id),
    PRIMARY KEY (application_id, cluster_id)
);
```

## To do

1. Unit tests
2. SQL transactions
3. Enhance schema
4. Choose better router

## CLI exercises

### create role
```bash
$ aws iam create-role --role-name lambda_role --assume-role-policy-document file://lambda_role.json
```

### attach execute policy
```bash
$ aws iam attach-role-policy --role-name lambda_role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
```

### verify
```bash
$ aws iam get-role --role-name lambda_role
```

### create function
```bash
$ aws lambda create-function --function-name lauris --zip-file fileb://../lauris.zip --handler index.handler --runtime nodejs8.10 --role arn:aws:iam::$ACC_ID:role/lambda_role
```

### invoke
```bash
$ aws lambda invoke --invocation-type RequestResponse --function-name lauris --region $REGION --log-type Tail out.txt
```

### destroy if smoething goes wrong
```bash
$ aws lambda delete-function --function-name lauris
```

### create API GW
```bash
$ aws apigateway create-rest-api --name lauris

$ export APP_ID=siue8b4oxd
```

### get root id

aws apigateway get-resources --rest-api-id $APP_ID

### create a method
```bash
$ aws apigateway put-method --rest-api-id=$APP_ID --resource-id=$RESOURCE_ID --http-method GET --authorization-type NONE
```

### attach lambda function
```bash
$ aws apigateway put-integration \
--rest-api-id $APP_ID \
--resource-id $RESOURCE_ID \
--http-method GET \
--type AWS \
--integration-http-method POST \
--uri arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$ACC_ID:function:lauris/invocations
```

### create response model
```bash
$ aws apigateway put-method-response \
--rest-api-id $APP_ID \
--resource-id $RESOURCE_ID \
--http-method GET \
--status-code 200 \
--response-models "{\"application/json\": \"Empty\"}"
```

### deploy the API. Save as $DEPLOYMENT_ID
```bash
$ aws apigateway create-deployment \
--rest-api-id $APP_ID \
--stage-name prod
```

### grant invoke perms
```bash
$ aws lambda add-permission \
--function-name arn:aws:lambda:$REGION:$ACC_ID:function:lauris \
--statement-id apigateway-prod-1 \
--action lambda:InvokeFunction \
--principal apigateway.amazonaws.com \
--source-arn "arn:aws:execute-api:$REGION:$ACC_ID:$APP_ID/prod/GET/hello"
```

## Google findings

- [AWS Lambda Context Object in Python](https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html)
-[In Terraform, how do you specify an API Gateway endpoint with a variable in the request path?](https://stackoverflow.com/questions/39040739/in-terraform-how-do-you-specify-an-api-gateway-endpoint-with-a-variable-in-the)

- [Deploy AWS RDS + AWS Lambda + AWS API Gateway + corresponding VPC, subnets and security group with Terraform](https://github.com/chromium58/terraform-aws-example)

- [A Simple API Using AWS RDS, Lambda, and API Gateway](https://apievangelist.com/2017/11/06/a-simple-api-using-aws-rds-lambda-and-api-gateway/)

- [Zero to Productive in AWS: Lambda, RDS, Kinesis, API Gateway](https://www.captechconsulting.com/blogs/zero-to-productive-in-aws-lambda-rds-kinesis-api-gateway)

- [Full guide to developing REST API’s with AWS API Gateway and AWS Lambda](https://blog.sourcerer.io/full-guide-to-developing-rest-apis-with-aws-api-gateway-and-aws-lambda-d254729d6992)

- [Serverless and Lambdaless Scalable CRUD Data API with AWS API Gateway and DynamoDB](https://hackernoon.com/serverless-and-lambdaless-scalable-crud-data-api-with-aws-api-gateway-and-dynamodb-626161008bb2)

- [How to build an API endpoint with Node.js, AWS Lambda and AWS RDS PostgreSQL DB](https://medium.com/@timo.wagner/how-to-build-an-api-endpoint-with-node-js-aws-lambda-and-aws-rds-postgresql-db-part-3-e76f2efede4e)