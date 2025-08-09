import unittest

from zcc.device import ControlPointDevice


class DeviceTest(unittest.TestCase):

    identifier = 'test_device_id'

    def test_init(self):
        device = ControlPointDevice(None, DeviceTest.identifier)
        self.assertEqual(device.controller, None)
        self.assertEqual(device.identifier, DeviceTest.identifier)
        self.assertEqual(device.actions, {})
        self.assertEqual(device.properties, {})
        self.assertEqual(device.states, {})

    def test_add_action(self):
        device = ControlPointDevice(None, DeviceTest.identifier)
        device.actions = {'TurnOn': {'actionParams': {}},
                          'TurnOff': {'actionParams': {}}}
        print(device)
        self.assertEqual(device.controller, None)
        self.assertEqual(device.identifier, DeviceTest.identifier)

    def test_add_properties(self):
        device = ControlPointDevice(None, DeviceTest.identifier)
        device.properties = {'name': 'Entry Pendant',
                             'controlPointType': 'switch', 'roomId': 2, 'roomName': 'Front Door '}
        self.assertEqual(device.controller, None)
        self.assertEqual(device.identifier, DeviceTest.identifier)

    def test_add_states(self):
        device = ControlPointDevice(None, DeviceTest.identifier)
        device.states = {'controlState': {
            'switch': {...}}, 'isConnected': True}
        self.assertEqual(device.controller, None)
        self.assertEqual(device.identifier, DeviceTest.identifier)


if __name__ == '__main__':
    unittest.main()
