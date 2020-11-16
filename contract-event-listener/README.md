# README

A single-threaded worker that reroutes for ethereum blockchain contract events according to provided configuration.

The configuration contains 3 main sections:
1. Worker: configures main worker parameters:
  1. Contract - events of which will be listened to.
  1. General - worker execution parameters.
  1. Blockchain - blockchain connection parameters.
1. Receivers - configures receivers for the events. There are 2 types of receivers:
    1. Log Receiver - outputs event payload using logger provided, STDOUT or Sentry.
    1. SQS Receiver - sends event payload to the specified queue.
1. Listeners - configures listeners that listen for a specified event of the contract and then send it to receivers.


#### Config Example

```yaml
---
  Receivers: # Receivers list
    -
      Id: MessageReceivedEventLogReceiver # receiver id, must be unique
      Type: LOG # receiver type, case sensitive
      JSON: # Event data format
        id: transactionHash # jmespath to value inside raw event payload
        message: args # jmespath to value inside raw event payload
    -
      Id: MessageReceivedEventSQLReceiver # receiver id, must be unique
      Type: SQS # receiver type, case sensitive
      QueueUrl: http://baseline-localstack:10001/queue/channel-au # SQS queue url
      JSON: # Event data format
        id: transactionHash # jmespath to value inside raw event payload
        message: args # jmespath to value inside raw event payload
    -
      Id: MessageSentEventLogReceiver
      Type: LOG
  Listeners: # Listeners list
    -
      Id: MessageReceivedEventListener # listener id, must be unique
      Event:
        Name: MessageReceivedEvent # Event name which listener listens
          Filter: # optional, https://web3py.readthedocs.io/en/stable/filters.html#event-log-filters
            fromBlock: latest
      Receivers: # Receivers to which listener sends events
        - MessageReceivedEventLogReceiver
        - MessageReceivedEventSQLReceiver
    -
      Id: MessageSentEventListener
      Event:
        Name: MessageSentEvent
      Receivers:
        - MessageSentEventLogReceiver
  Worker:
    Blockchain:
      URI: ws://baseline-ganache-cli:8585 # Blockchain node endpoint
    General:
      PollingInterval: 5 # Listeners polling interval
      ListenerBlocksLogDir: /tmp/listener-blocks-log #  Listeners last seen block files
      LoggerName: AU
    Contract:
      S3:
        Bucket: contract # contract build artifact bucket name
        Key: channel-node-participant-au/ChannelNode.json # contract build artifact key
        NetworkId: "15" # network id, must be sting
```

#### Entrypoint Args:
1. ```worker``` - launch worker in production mode
1. ```worker-debug``` - launch worker in debug mode
1. ```test``` - launch tests
1. ```container``` - wait indefinitely, useful for docker development

#### Config(Environment):
1. ```JSON_CONFIG_FILE_VALUE``` - set JSON config file content through environment
1. ```YAML_CONFIG_FILE_VALUE``` - set YAML config file content through environment
