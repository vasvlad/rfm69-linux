from noolite import NooliteProtocolHandler, NooliteCommands
from random import randint


class NooliteTxDevice(object):
    STATELESS_COMMAND_MAP = {
        'bind':  NooliteCommands.Bind,
        'unbind': NooliteCommands.Unbind,
        'switch': NooliteCommands.Switch,
        'slowup': NooliteCommands.SlowUp,
        'slowdown': NooliteCommands.SlowDown,
        'slowswitch': NooliteCommands.SlowSwitch,
        'slowstop': NooliteCommands.SlowStop,
    }

    def __init__(self, addr, radio_send):
        self.addr = addr
        self.addr_hex = hex(self.addr)
        #~ self.mqtt_client = mqtt_client

        self.radio_send = radio_send

        self.device_id = "noolite_tx_" + self.addr_hex

        self.device_name = "Noolite TX " + self.addr_hex
        self.device_room = 'Noolite'

        self.controls_desc = {
                'level'  :  { 'value' : 0,
                              'meta' :  { 'type' : 'range',
                                          'order' : '1',
                                          'max' : 100,
                                        }
                            },
                'state'    : { 'value' : 0,
                            'meta': {  'type' : 'switch',
                                       'order' : '2',
                                },
                          },
                'switch'  : { 'value' : 0,
                            'meta': {  'type' : 'pushbutton' ,
                                       'order' : '4',

                                    },
                          },
                'color'  : { 'value' : '0;0;0',
                            'meta': {  'type' : 'rgb' ,
                                       'order' : '5',

                                    },
                          },
                'slowup'  : { 'value' : 0,
                            'meta': {  'type' : 'pushbutton',
                                       'order' : '6',
                                    },
                          },
                'slowdown'  : { 'value' : 0,
                            'meta': {  'type' : 'pushbutton',
                                       'order' : '7',
                                    },
                          },
                'slowswitch'  : { 'value' : 0,
                            'meta': {  'type' : 'pushbutton',
                                       'order' : '8',
                                    },
                          },
                'slowstop'  : { 'value' : 0,
                            'meta': {  'type' : 'pushbutton',
                                       'order' : '9',
                                    },
                          },
                'shadow_level'  :  { 'value' : 0,
                              'meta' :  { 'type' : 'range',
                                          'order' : '10',
                                          'max' : 100,
                                        }
                            },
                'bind'  : { 'value' : 0,
                            'meta': {  'type' : 'pushbutton',
                                       'order' : '20',
                                       'export' : '0',
                                    },
                          },
                'unbind'  : { 'value' : 0,
                            'meta': {  'type' : 'pushbutton',
                                       'order' : '21',
                                       'export' : '0',
                                    },
                          },
                'loadpreset'  : { 'value' : 0,
                            'meta': {  'type' : 'pushbutton',
                                       'order' : '7',
                                },
                          },

              }

        self.protocol_handler = NooliteProtocolHandler()
        self.flip = 0

    def get_controls(self):
        return self.controls_desc

    def encode_level(self, level):
        if level <= 0:
            return 0
        else:
            return int(round((100 if (level > 100) else level) * 1.23 + 34))



    def update_control(self, control, value, retained = False):
        self.flip = 0 if self.flip else 1


        var = {  'addr'  : self.addr_hex,
                 'flip'  : self.flip,
              }

        var['arg'] = '0'

        if control == 'state':
            if int(value):
                var['cmd'] = NooliteCommands.On
            else:
                var['cmd'] = NooliteCommands.Off
        elif control == 'level':
            var['cmd'] = NooliteCommands.SetLevel
            var['arg'] = str(self.encode_level(int(value)))
        elif control == 'loadpreset':
            var['cmd'] = NooliteCommands.LoadPreset

        elif control == 'slowup':
            var['cmd'] = NooliteCommands.SlowUp

        elif control == 'slowdown':
            var['cmd'] = NooliteCommands.SlowDown

        elif control == 'slowswitch':
            var['cmd'] = NooliteCommands.SlowSwitch

        elif control == 'slowstop':
            var['cmd'] = NooliteCommands.SlowStop
        elif control == 'shadow_level':
            var['cmd'] = NooliteCommands.ShadowSetBright
            var['arg'] = str(self.encode_level(int(value)))

        elif control == 'color':
            var['cmd'] = NooliteCommands.SetLevel

            try:
                values = value.strip().split(';')
                assert len(values) == 3
                values = tuple(int(v) for v in values)
                var['args'] = "%d;%d;%d" % values
            except:
                print "error decoding color"
                import traceback
                traceback.print_exc()
                return

        elif control in self.STATELESS_COMMAND_MAP.keys():
            #~ print "stateless: ", control, retained
            # do not send stateless commands on startup (not implemented)
            #~ if retained:
                #~ return

            var['cmd'] = self.STATELESS_COMMAND_MAP[control]

        else:

            print "unknown control "
            return



        data = self.protocol_handler.tryEncode(var)
        self.radio_send(data)

        return None



class OregonRxDevice(object):
    device_room = None
    def __init__(self, dev_type, code, channel, data = {}):
        self.dev_type = dev_type
        self.code = code


        try:
            self.channel = int(channel)
        except:
            self.channel = 0


        self.device_id = "oregon_rx_%s_%s_%s" % (self.dev_type, self.code, self.channel)

        # full list on http://jeelabs.net/projects/cafe/wiki/Decoding_the_Oregon_Scientific_V2_protocol
        #~ if self.dev_type in ('1a2d', 'fa28', 'ca2c', 'fab8', '1a3d',) or self.dev_type.endswith('acc'):
            #~ self.device_type_name = 'Temp-Hygro'
        #~ else:
        self.device_type_name = "[%s]" % self.dev_type

        self.device_name = "Oregon Sensor %s (%s-%d)" % ( self.device_type_name, self.code, self.channel)

        self.controls_desc = {}

        if 'temp' in data:
            self.controls_desc['temperature'] =   { 'value' : 0,
                                                    'meta' :  { 'type' : 'temperature',
                                                              },
                                                    'readonly' : True,
                                                  }
        if 'humidity' in data:
            self.controls_desc['humidity'] =     { 'value' : 0,
                                                   'meta' :  { 'type' : 'rel_humidity',
                                                             },
                                                   'readonly' : True,
                                                 }
        if 'comfort' in data:
            self.controls_desc['comfort'] =     { 'value' : 0,
                                                  'meta' :  { 'type' : 'text',
                                                            },
                                                  'readonly' : True,
                                                 }
        if 'rain_rate' in data:
            self.controls_desc['rain_rate'] =     { 'value' : 0,
                                                    'meta' :  { 'type' : 'rainfall',
                                                              },
                                                    'readonly' : True,
                                                 }
        if 'rain_total' in data:
            self.controls_desc['rain_total'] =     { 'value' : 0,
                                                     'meta' :  { 'type' : 'value', 'units' : 'mm',
                                                               },
                                                     'readonly' : True,
                                                 }
        if 'UV' in data:
            self.controls_desc['UV'] =     { 'value' : 0,
                                             'meta' :  { 'type' : 'text',
                                                       },
                                             'readonly' : True,
                                           }
        if 'windDir' in data:
            self.controls_desc['wind_direction'] =     { 'value' : 0,
                                                         'meta' :  { 'type' : 'value', 'units' : 'deg',
                                                                   },
                                                         'readonly' : True,
                                                 }
        if 'windSpeed' in data:
            self.controls_desc['wind_speed'] =     { 'value' : 0,
                                                   'meta' :  { 'type' : 'wind_speed',
                                                             },
                                                   'readonly' : True,
                                                 }
        if 'windAvgSpeed' in data:
            self.controls_desc['wind_average_speed'] =     { 'value' : 0,
                                                   'meta' :  { 'type' : 'wind_speed',
                                                             },
                                                   'readonly' : True,
                                                 }
        if 'pressure' in data:
            self.controls_desc['pressure'] =     { 'value' : 0,
                                                   'meta' :  { 'type' : 'atmospheric_pressure',
                                                             },
                                                   'readonly' : True,
                                                 }
        if 'forecast' in data:
            self.controls_desc['weather_forecast'] =     { 'value' : 0,
                                                           'meta' :  { 'type' : 'text',
                                                                     },
                                                           'readonly' : True,
                                                 }
        if 'lowbat' in data:
            self.controls_desc['low_battery'] =     { 'value' : 0,
                                                      'meta' :  { 'type' : 'switch', 'readonly' : '1',
                                                                },
                                                      'readonly' : True,
                                                 }



    def get_controls(self):
        return self.controls_desc



    def handle_data(self, data):
        var = {}

        if 'temp' in data:
            self.controls_desc['temperature']['value'] = data['temp']
        if 'humidity' in data:
            self.controls_desc['humidity']['value'] = data['humidity']
        if 'comfort' in data:
            self.controls_desc['comfort']['value'] = data['comfort']
        if 'rain_rate' in data:
            self.controls_desc['rain_rate']['value'] = data['rain_rate']
        if 'rain_total' in data:
            self.controls_desc['rain_total']['value'] = data['rain_total']
        if 'uv' in data:
            self.controls_desc['UV']['value'] = data['uv']
        if 'wind_dir' in data:
            self.controls_desc['wind_direction']['value'] = data['wind_dir']
        if 'wind_speed' in data:
            self.controls_desc['wind_speed']['value'] = data['wind_speed']
        if 'wind_avg_speed' in data:
            self.controls_desc['wind_average_speed']['value'] = data['wind_avg_speed']
        if 'pressure' in data:
            self.controls_desc['pressure']['value'] = data['pressure']
        if 'forecast' in data:
            self.controls_desc['weather_forecast']['value'] = data['forecast']
        if 'lowbat' in data:
            self.controls_desc['low_battery']['value'] = data['lowbat']
        return var





class Cs5211RxDevice(object):
    device_room = None
    def __init__(self, addr, data = {}):
        self.device_id = "cs5211_rx_tx_%s" % (addr)

        self.device_type_name = "[%s]" % addr
        self.device_name = "cs5211 Sensor %s" % ( addr)
        self.controls_desc = {} 
        if 'state' in data:
            self.controls_desc['state'] =   { 'value' : data['state'],
                                          'meta' :  { 'type' : 'switch',
                                                    },
                                          'readonly' : False,
                                        }
        else:
            self.controls_desc['state'] =   { 'value' : 'off',
                                          'meta' :  { 'type' : 'switch',
                                                    },
                                          'readonly' : False,
                                        }



    def get_controls(self):
        return self.controls_desc

    def handle_data(self, data):
        var = {}
        if 'state' in data:
            self.controls_desc['state']['value'] = data['state']
      
        return var

    def get_id(self):
        return self.device_id




class NooliteRxDevice(object):
    device_room = None

    def __init__(self, addr, data = {}):
        self.addr = addr
        self.addr_hex = hex(self.addr)


        self.device_id = "noolite_rx_" + self.addr_hex


        self.device_name = "Noolite Sensor %s " % (self.addr_hex)

        self.controls_desc = {}

    def decode_level(self, level):
        if level > 157:
            level = 157
        if level < 34:
            level = 34

        return int(round ((level - 34) / 1.23))


    def get_controls(self):
        return self.controls_desc


    def handle_data(self, data):
        if 'cmd' in data:
            try:
                cmd = int(data['cmd'])
            except ValueError:
                return
        else:
            return


        if 'temp' in data:
            self.controls_desc['temperature'] =   { 'value' : data['temp'],
                                                    'meta' :  { 'type' : 'temperature',
                                                              },
                                                    'readonly' : True,
                                                  }

        if 'humidity' in data:
            self.controls_desc['humidity'] =     { 'value' : data['humidity'],
                                                   'meta' :  { 'type' : 'rel_humidity',
                                                             },
                                                   'readonly' : True,
                                                 }


        if cmd in (NooliteCommands.SetLevel, NooliteCommands.ShadowSetBright):
            if 'level' in data:
                try:
                    level = int(data['level'])
                except ValueError:
                    return

                self.controls_desc['level'] =     { 'value' : str(self.decode_level(level)),
                                                       'meta' :  { 'type' : 'range',
                                                                   'max' : 100,
                                                                   'order' : '1',
                                                                 },
                                                       'readonly' : True,
                                                   }
        elif cmd in (NooliteCommands.On, NooliteCommands.Off, NooliteCommands.Switch):
            self.controls_desc.setdefault('state',  { 'value' : 0,
                                                       'meta': {  'type' : 'switch',
                                                                  'order' : '2',
                                                            },
                                                       'readonly' : True,
                                                      }, )
            val = None
            if cmd == NooliteCommands.On:
                val = '1'
            elif cmd == NooliteCommands.Off:
                val = '0'
            elif cmd == NooliteCommands.Switch:
                cur_val = self.controls_desc['state']['value']
                if cur_val == '1':
                    val = '0'
                else:
                    val = '1'

            if val is not None:
                self.controls_desc['state']['value'] = val

        elif cmd == NooliteCommands.LoadPreset:
            self.controls_desc.setdefault('state',  { 'value' : 0,
                                                      'meta': {  'type' : 'switch',
                                                                 'order' : '2',
                                                            },
                                                      'readonly' : True,
                                                     }, )
            
            self.controls_desc['state']['value'] = randint(1, 65000)








class OregonRxHandler(object):
    name = "oregon"
    def __init__(self):
        self.devices = {}

    def handle_data(self, data):
        if ('code' in data) and  ('type' in data):
            channel = data.get('channel')
            key = (data['type'], data['code'], channel)
            if key not in self.devices:
                self.devices[key] = OregonRxDevice(data['type'], data['code'], channel, data)

            device = self.devices[key]
            device.handle_data(data)

            return device

class OregonV3RxHandler(OregonRxHandler):
    name = "oregon3"


class NooliteRxHandler(object):
    name = "noo"
    def __init__(self):
        self.devices = {}

    def handle_data(self, data):
        if 'addr' in data:
            key = data['addr']
            if key not in self.devices:
                self.devices[key] = NooliteRxDevice(int(data['addr'], 16), data)
            device = self.devices[key]
            device.handle_data(data)

            return device

class Cs5211RxHandler(object):
    name = "cs5211"
    def __init__(self):
        self.devices = {}

    def handle_data(self, data):
        if 'addr' in data:
            key = data['addr']
            if key not in self.devices:
                self.devices[key] = Cs5211RxDevice(data['addr'], data['state'])
            device = self.devices[key]
            device.handle_data(data)

            return device


rx_handler_classes = (OregonRxHandler, OregonV3RxHandler, NooliteRxHandler, Cs5211RxHandler )
