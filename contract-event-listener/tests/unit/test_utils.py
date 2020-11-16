from src.utils.jmespath_json_template import JMESPathJSONTemplate


def test_JMESPATHJsonTemplate():
    data = {
        'Meta': {
            'Topic': 'Initial',
            'Receiver': 'AU',
            'Sender': 'GB',
            'Tags': ['initial', 'message', 'ping']
        },
        'Data': {
            'Text': 'Hello',
            'Length': 5
        }
    }
    template = JMESPathJSONTemplate('[Data.Text, Meta.Tags]|[]')
    assert template.render(data) == ['Hello', 'initial', 'message', 'ping']

    template = JMESPathJSONTemplate({
        'Message': {
            'Topic': 'Meta.Topic',
            'Sender': 'Meta.Sender',
            'Text': 'Data.Text',
            'URI': 'Meta.URI'
        }
    })
    assert template.render(data) == {
        'Message': {
            'Topic': 'Initial',
            'Sender': 'GB',
            'Text': 'Hello',
            'URI': None
        }
    }

    template = JMESPathJSONTemplate({
        'Message': {
            'Components': ['Meta.Sender', 'Meta.Receiver', 'Meta.URI', 'Data.Text']
        }
    })
    assert template.render(data) == {
        'Message': {
            'Components': ['GB', 'AU', None, 'Hello']
        }
    }
