import init

def at_home():
    config = init.config_read()
    for ui in config['userip']:
        pingstatus = init.ping(ui)
        if pingstatus is True:
            config['athome'] = 1
            break
        else:
            config['athome'] = 0
    init.config_update(config)
    return config['athome']


if __name__ == '__main__':
    at_home()