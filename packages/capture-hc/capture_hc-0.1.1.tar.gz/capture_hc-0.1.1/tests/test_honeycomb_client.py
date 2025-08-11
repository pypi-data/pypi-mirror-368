import unittest
from unittest.mock import patch, MagicMock
from capture_hc.honeycomb_client import HoneycombClient

class TestHoneycombClient(unittest.TestCase):
    @patch('capture_hc.honeycomb_client.libhoney')
    def test_send_event(self, mock_libhoney):
        client = HoneycombClient('fakekey', 'fakedataset')
        mock_event = MagicMock()
        mock_libhoney.new_event.return_value = mock_event
        fields = {'foo': 'bar', 'baz': 123}
        client.send_event(fields)
        mock_libhoney.new_event.assert_called_once()
        for k, v in fields.items():
            mock_event.add_field.assert_any_call(k, v)
        mock_event.send.assert_called_once()
        mock_libhoney.flush.assert_called_once()

    @patch('capture_hc.honeycomb_client.libhoney')
    def test_timed_decorator(self, mock_libhoney):
        client = HoneycombClient('fakekey', 'fakedataset')
        mock_event = MagicMock()
        mock_libhoney.new_event.return_value = mock_event
        extra_fields = {'alert_name': 'test_func'}
        @client.timed(extra_fields)
        def dummy(event=None):
            event.add_field('custom', 42)
            return 'done'
        result = dummy()
        self.assertEqual(result, 'done')
        mock_libhoney.new_event.assert_called_once()
        mock_event.add_field.assert_any_call('alert_name', 'test_func')
        mock_event.add_field.assert_any_call('custom', 42)
        mock_event.add_field.assert_any_call('duration_ms', unittest.mock.ANY)
        mock_event.add_field.assert_any_call('function_name', 'dummy')
        mock_event.send.assert_called_once()
        mock_libhoney.flush.assert_called_once()

if __name__ == '__main__':
    unittest.main() 