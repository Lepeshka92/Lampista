import ui
import os
import socket
import dialogs

CONFIG = 'lampista.cfg'


class LampistaConnection(object):
    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection.bind(('', 8888))
        self.connection.settimeout(3)
        self.target = None

    def udp_request(self, data):
        try:
            self.connection.sendto(data, self.target)
            result, addr = self.connection.recvfrom(1024)
            return result.decode()
        except Exception as ex:
            return None

    def cur_mode(self):
        return self.udp_request('GET'.encode())

    def set_mode(self, mode):
        return self.udp_request(('EFF ' + str(mode)).encode())

    def set_brightness(self, val):
        return self.udp_request(('BRI ' + str(val)).encode()) is not None

    def set_speed(self, val):
        return self.udp_request(('SPD ' + str(val)).encode()) is not None

    def set_scale(self, val):
        return self.udp_request(('SCA ' + str(val)).encode()) is not None


def map_value(x, a, b, c, d):
    return (x - a) / (b - a) * (d - c) + c


@ui.in_background
def parse_response(data):
    if data and data.startswith('CURR'):
        options = data.split()[1:]
        view['modes'].selected_row = int(options[0])
        view['brightness'].value = map_value(int(options[1]), 0, 255, 0, 1)
        view['speed'].value = map_value(int(options[2]), 0, 255, 0, 1)
        view['scale'].value = map_value(int(options[3]), 0, 255, 0, 1)
    else:
        view['connect'].image = ui.Image('iob:ios7_cloud_upload_outline_32')
        dialogs.alert('Не удалось отправить команду')


def btn_connect_click(sender):
    view['connect'].image = ui.Image('iob:ios7_cloud_upload_32')
    target = view['target'].text.split(':')
    if len(target) < 2:
        target.append(8888)
    lamp.target = tuple(target)
    response = lamp.cur_mode()
    parse_response(response)
    save_config()


def slider_changed(sender):
    value = map_value(sender.value, 0, 1, 0, 255)
    if sender.name == 'brightness':
        lamp.set_brightness(value)
    elif sender.name == 'speed':
        lamp.set_speed(value)
    elif sender.name == 'scale':
        lamp.set_scale(value)


def select_mode(sender):
    response = lamp.set_mode(view['modes'].selected_row[1])
    parse_response(response)


def load_config():
    if os.path.exists(CONFIG):
        with open(CONFIG, 'r') as fd:
            view['target'].text = fd.readlines()[0]


def save_config():
    with open(CONFIG, 'w') as fd:
        fd.write(view['target'].text)


if __name__ == '__main__':
    lamp = LampistaConnection()
    view = ui.load_view()
    load_config()
    view.name = 'Lampista'
    view.present('fullscreen')

