def to24Hours(t):
    test = t.split(' ')
    if test[1] == 'PM':
        test = test[0].split(':')
        return str(int(test[0]) + 12) + test[1];
    else:
        test = test[0].split(':')
        return test[0] + test[1];

def to12Hours(t):
    ampm = 'AM'
    if t >= 1300:
        t = t - 1200
        ampm= 'PM'
    elif t >= 1200:
        ampm= 'PM'

    s = str(t);
    if len(s) == 4:
        return s[0:2] + ':' + s[2:] + ' ' + ampm;
    return s[0:1] + ':' + s[1:] + ' ' + ampm;

