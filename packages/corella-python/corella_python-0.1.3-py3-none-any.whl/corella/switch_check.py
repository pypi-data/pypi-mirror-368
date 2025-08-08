def switch_check(level='inform',
                 message=None):
    
    if level == 'inform':
        print('inform test')
    elif level == 'warn':
        print('warning test')
    else:
        print('abort test')