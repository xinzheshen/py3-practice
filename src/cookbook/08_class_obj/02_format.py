
_formats = {
    'ymd' : '{d.year}-{d.month}-{d.day}',
    'mdy' : '{d.month}/{d.day}/{d.year}',
    'dmy' : '{d.day}/{d.month}/{d.year}'
}

class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def __format__(self, code):
        if code == '':
            code = 'ymd'
        fmt = _formats[code]
        return fmt.format(d=self)


if __name__ == '__main__':
    d = Date(2018, 8, 8)
    print(format(d))
    print(format(d, "mdy"))
    # __format__() 方法给Python的字符串格式化功能提供了一个钩子。
    #  这里需要着重强调的是格式化代码的解析工作完全由类自己决定
    print('The date is {:ymd}'.format(d))