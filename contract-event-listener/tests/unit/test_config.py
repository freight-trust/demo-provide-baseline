import pytest
from marshmallow import ValidationError
from src.config import Config


def test():
    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG'
            },
            {
                'Id': 'SQSReceiver-1',
                'Type': 'SQS',
                'JSON': {
                    'text': 'message.text'
                },
                'QueueUrl': 'QueueUrlValue',
                'Config': {
                    'AWS': {
                        'region_name': 'us-east-1'
                    },
                    'Message': {
                        'DelaySeconds': 10
                    }
                }
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1',
                    'Filter': {
                        'from_block': 'latest'
                    }
                },
                'Receivers': [
                    'LogReceiver-1',
                    'SQSReceiver-1'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {
                'S3': {
                    'Bucket': 'contract',
                    'Key': 'event-emmiter/EventEmitter.json',
                    'NetworkId': '15'
                }
            }
        }
    }
    c = Config().load(data)

    assert len(c.Receivers) == 2

    assert c.Receivers[0].Id == 'LogReceiver-1'
    assert c.Receivers[0].Type == 'LOG'
    assert c.Receivers[0].JSON is None

    assert c.Receivers[1].Id == 'SQSReceiver-1'
    assert c.Receivers[1].Type == 'SQS'
    assert c.Receivers[1].JSON == {'text': 'message.text'}
    assert c.Receivers[1].QueueUrl == 'QueueUrlValue'
    assert c.Receivers[1].Config.AWS['region_name'] == 'us-east-1'
    assert c.Receivers[1].Config.Message['DelaySeconds'] == 10

    assert len(c.Listeners) == 1
    assert c.Listeners[0].Id == 'EventListener-1'
    assert c.Listeners[0].Event.Name == 'Event-1'
    assert c.Listeners[0].Event.Filter['from_block'] == 'latest'
    assert c.Listeners[0].Receivers == [
        'LogReceiver-1',
        'SQSReceiver-1'
    ]

    assert c.Worker.Blockchain.URI == 'BlockchainURI'

    assert c.Worker.General.PollingInterval == 60
    assert c.Worker.General.LoggerName == 'DEV'

    assert c.Worker.Contract.File is None
    assert c.Worker.Contract.S3.Bucket == 'contract'
    assert c.Worker.Contract.S3.Key == 'event-emmiter/EventEmitter.json'
    assert c.Worker.Contract.S3.NetworkId == '15'

    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG'
            },
            {
                'Id': 'SQSReceiver-1',
                'Type': 'SQS',
                'JSON': {
                    'text': 'message.text'
                },
                'QueueUrl': 'QueueUrlValue',
                'Config': {
                    'AWS': {
                        'region_name': 'us-east-1'
                    },
                    'Message': {
                        'DelaySeconds': 10
                    }
                }
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1',
                    'Filter': {
                        'from_block': 'latest'
                    }
                },
                'Receivers': [
                    'LogReceiver-1',
                    'SQSReceiver-1'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {
                'File': {
                    'Address': '/contract.address',
                    'ABI': '/abi.json'
                }
            }
        }
    }

    c = Config().load(data)

    assert c.Worker.Contract.S3 is None
    assert c.Worker.Contract.File.Address == '/contract.address'
    assert c.Worker.Contract.File.ABI == '/abi.json'

    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG'
            },
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG'
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1'
                },
                'Receivers': [
                    'LogReceiver-1'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {
                'File': {
                    'Address': '/contract.address',
                    'ABI': '/abi.json'
                }
            }
        }
    }

    with pytest.raises(ValidationError) as einfo:
        c = Config().load(data)
    assert f'Receiver id duplicates found {["LogReceiver-1"]}' in einfo.value.messages["_schema"]

    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG'
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1'
                },
                'Receivers': [
                    'LogReceiver-1'
                ]
            },
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1'
                },
                'Receivers': [
                    'LogReceiver-1'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {
                'File': {
                    'Address': '/contract.address',
                    'ABI': '/abi.json'
                }
            }
        }
    }

    with pytest.raises(ValidationError) as einfo:
        c = Config().load(data)

    assert f'Listener id duplicates found {["EventListener-1"]}' in einfo.value.messages["_schema"]

    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG'
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1'
                },
                'Receivers': [
                    'LogReceiver-2'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {
                'File': {
                    'Address': '/contract.address',
                    'ABI': '/abi.json'
                }
            }
        }
    }

    with pytest.raises(ValidationError) as einfo:
        c = Config().load(data)

    assert 'Receiver "LogReceiver-2" not found' in einfo.value.messages["_schema"]

    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG'
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1'
                },
                'Receivers': [
                    'LogReceiver-1'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {}
        }
    }

    with pytest.raises(ValidationError) as einfo:
        c = Config().load(data)

    assert 'Config.Worker.Contract.S3 and Config.Worker.Contract.File are undefined' in einfo.value.messages["_schema"]

    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG'
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1'
                },
                'Receivers': [
                    'LogReceiver-1'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {
                'File': {
                    'Address': '/contract.address',
                    'ABI': '/abi.json'
                },
                'S3': {
                    'Bucket': 'contract',
                    'Key': 'event-emmiter/EventEmitter.json',
                    'NetworkId': '15'
                }
            }
        }
    }

    with pytest.raises(ValidationError) as einfo:
        c = Config().load(data)

    msg = 'Config.Worker.Contract.S3 and Config.Worker.Contract.File can\'t be defined together'
    assert msg in einfo.value.messages["_schema"]

    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'LOG',
                'JSON': 0
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1'
                },
                'Receivers': [
                    'LogReceiver-1'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {
                'File': {
                    'Address': '/contract.address',
                    'ABI': '/abi.json'
                }
            }
        }
    }

    with pytest.raises(ValidationError) as einfo:
        c = Config().load(data)

    msg = f'Type of JSON field must be [list, dict, str] not {type(0)}'
    assert msg in einfo.value.messages["_schema"]

    data = {
        'Receivers': [
            {
                'Id': 'LogReceiver-1',
                'Type': 'UNKNOWN'
            }
        ],
        'Listeners': [
            {
                'Id': 'EventListener-1',
                'Event': {
                    'Name': 'Event-1'
                },
                'Receivers': [
                    'LogReceiver-1'
                ]
            }
        ],
        'Worker': {
            'Blockchain': {
                'URI': 'BlockchainURI'
            },
            'General': {
                'PollingInterval': 60,
                'ListenerBlocksLogDir': '/tmp/blocks',
                'LoggerName': 'DEV'
            },
            'Contract': {
                'File': {
                    'Address': '/contract.address',
                    'ABI': '/abi.json'
                }
            }
        }
    }

    with pytest.raises(ValidationError) as einfo:
        c = Config().load(data)

    msg = f'Can\'t deserialize the field using any known schema: {["LogReceiver", "SQSReceiver"]}'
    assert msg == einfo.value.messages['Receivers'][0][0]
