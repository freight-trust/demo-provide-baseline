# README

The project is designed to provide an interface for ChannelNode ethereum contract.

It consists of two main functional parts:
1. ```Channel API``` - REST interface for operating with ChannelNode contract
1. ```WebSub API``` - REST interface for subscriptions to channel messages

Both of the APIs are parts of a same Flask app, therefore, there is no option to deploy them separately, but
that's not needed because API is lightweight and designed to operate under API Gateway using Lambda functions as a runtime.

Overall, the project consists of several parts:
1. ```API``` - flask app that provides REST API for subscription and channel communication
1. Processors:
  1. ```New Messages Observer``` - part of the WebSub functionality workflow, listener, watches for new received messages
  1. ```Callback Spreader``` - part of the WebSub functionality workflow, prepares individual subscriber notifications
  1. ```Callback Delivery``` - part of the WebSub functionality workflow, delivers the individual notifications


#### API Specification(OpenAPI 3.0)
```yaml
openapi: "3.0.0"
info:
  version: "1.0.0"
  title: "Ethereum Channel API"

components:
  schemas:
    Message:
      type: object
      required:
        - id
        - message
        - status
      properties:
        id:
          type: string
        message:
          type: object
          required:
            - object
            - predicate
            - subject
            - sender
            - receiver
          properties:
            object:
              type: string
            predicate:
              type: string
            subject:
              type: string
            receiver:
              type: string
            sender:
              type: string
        status:
          type: string
          enum: [received, confirmed, revoked, undeliverable]

    Subscription:
      type: object
      required:
        - hub.mode
        - hub.callback
        - hub.topic
        - hub.lease_seconds
      properties:
        hub.mode:
          type: string
          enum: [subscribe, unsubscribe]
        hub.callback:
          type: string
        hub.lease_seconds:
          type: integer
        hub.topic:
          type: string
        hub.challenge:
          type: string


  responses:
    Error:
      description: Standard error response
      content:
        application/json:
          schema:
            type: object
            properties:
              errors:
                type: array
                items:
                  type: object
                  properties:
                    detail:
                      type: string
                    source:
                      type: array
                      items: {}
                    status:
                      type: string
                    title:
                      type: string
                    code:
                      type: string
    Message:
      description: Standard message response
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Message"


paths:
  /messages/{id}:
    get:
      summary: Get message by id(transaction hash)
      parameters:
        - in: path
          name: id
          schema:
            type: string
          required: true

      responses:
        200:
          $ref: "#/components/responses/Message"
        404:
          $ref: "#/components/responses/Error"

  /messages:
    post:
      summary: Post a message from the channel
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - object
                - predicate
                - subject
                - receiver
              properties:
                object:
                  type: string
                predicate:
                  type: string
                subject:
                  type: string
                receiver:
                  type: string
                sender:
                  type: string

      responses:
        200:
          $ref: "#/components/responses/Message"
        400:
          $ref: "#/components/responses/Error"

  /participants:
    get:
      summary: Get channel participants list
      responses:
        200:
          description: Participants list
          content:
            application/json:
              schema:
                type: array
                items:
                  type: string

  /topic/{topic}:
    get:
      summary: Verify that topic exists on the channel
      parameters:
        - in: path
          name: topic
          description: Channel message topic
          schema:
            type: string
          required: true
      responses:
        200:
          description: topic string representation
          content:
            application/json:
              schema:
                type: string
        404:
          $ref: "#/components/responses/Error"

  /messages/subscriptions/by_id:
    post:
      summary: Subscribe/unsubscribe to/from a specific channel message topic
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              $ref: "#/components/schemas/Subscription"

      responses:
        200:
          description: Subscribed/unsubscribed
        400:
          $ref: "#/components/responses/Error"

  /messages/subscriptions/by_jurisdiction:
    post:
      summary: Subscribe/unsubscribe to/from a specific channel message topic prefixed with "jurisdiction."
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              $ref: "#/components/schemas/Subscription"
      responses:
        200:
          description: Subscribed/unsubscribed
        400:
          $ref: "#/components/responses/Error"
        404:
          $ref: "#/components/responses/Error"
```

#### API Configuration(Environment):
1. ```PORT``` - port on which API server runs
1. ```IGL_CONTRACT_REPO_BUCKET``` - name of the bucket that stores a contract build artifact
1. ```CONTRACT_BUILD_ARTIFACT_KEY``` - the contract build artifact key
1. ```CONTRACT_NETWORK_ID``` - numerical network id on which the contract deployed, used to retrieve a contract address from the build artifact
1. ```CONTRACT_OWNER_PRIVATE_KEY```  - private key of a wallet used to sign contract transactions
1. ```MESSAGE_CONFIRMATION_THRESHOLD``` - number of blocks ahead of a message transaction required to consider the message confirmed. This parameter reflects ethereum blockchain blocks confirmation threshold.
1. ```SENDER``` - channel participant name, two letters country code
1. ```HTTP_BLOCKCHAIN_ENDPOINT``` - blockchain node endpoint used to operate with the contract
1. ```IGL_SUBSCRIPTIONS_REPO_BUCKET``` - bucket of the bucket that stores WebSub subscriptions data
1. ```CHANNEL_URL``` - channel base URL, for example ```https://channel.au/```, must have a trailing slash, used validate channel canonical URL topics.

#### New Messages Observer Configuration(Environment):
1. ```IGL_NOTIFICATIONS_REPO_QNAME``` - name of the queue used to store WebSub notifications jobs
1. ```IGL_CHANNEL_REPO_QNAME``` - name of the queue used to hold received channel messages
1. ```RECEIVER``` - message receiver filter value used to filter channel messages that don't sent for this channel, two letters country code.  

#### Callback Spreader Configuration(Environment):
1. ```IGL_NOTIFICATIONS_REPO_QNAME``` - name of the queue used to store WebSub notifications jobs
1. ```IGL_DELIVERY_OUTBOX_REPO_QNAME``` - name of the queue used to store individual WebSub notifications delivery jobs
1. ```IGL_SUBSCRIPTIONS_REPO_BUCKET``` - name of the bucket used to store WebSub subscriptions data

#### Callback Delivery Configuration(Environment):
1. ```CHANNEL_URL``` - channel base URL, for example ```https://channel.au/```, used in a notification header.
1. ```TOPIC_BASE_SELF_URL``` - channel topics base self URL, for example ```topic/```, must not have leading slash, but must have a trailing one, used in a notification header.
1. ```IGL_DELIVERY_OUTBOX_REPO_QNAME``` - name of the queue used to store individual WebSub notifications

#### Entrypoint Args:
1. ```server``` - start API development server
1. ```callback-server``` - start callback testing utility server
1. ```new-messages-observer-processor``` - start ```New Messages Observer```
1. ```callback-spreader-processor``` - start ```Callback Spreader```
1. ```callback-delivery-processor``` - start ```Callback Delivery```
1. ```test``` - start tests
1. ```container``` - wait indefinitely


#### Channel API Serverless Deployment:
```Channel API``` docker image has ```serverless``` deployment tools installed. In order to use them you need to:
1. ```make run-channel-api-au```
1. ```make shell-channel-api-au```
1. ```npx serverless <command>```
