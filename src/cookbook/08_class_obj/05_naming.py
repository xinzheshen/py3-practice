
"""
类的属性和方法命名规约：
第一个约定是任何以单下划线_开头的名字都应该是内部实现
"""
class A:
    def __init__(self):
        self._internal = 0 # An internal attribute
        self.public = 1 # A public attribute

    def public_method(self):
        '''
        A public method
        '''
        pass

    def _internal_method(self):
        pass

"""
使用双下划线开始会导致访问名称变成其他形式。 
比如，类B中，私有属性会被分别重命名为 _B__private 和 _B__private_method 。 
"""
class B:
    def __init__(self):
        self.__private = 0

    def __private_method(self):
        pass

    def public_method(self):
        pass
        self.__private_method()

"""这时候你可能会问这样重命名的目的是什么，
答案就是继承——这种属性通过继承是无法被覆盖的。比如C类：
这里，私有名称 __private 和 __private_method 被重命名为 _C__private 和 _C__private_method ，
这个跟父类B中的名称是完全不同的。
"""
class C(B):
    def __init__(self):
        super().__init__()
        self.__private = 1 # Does not override B.__private

    # Does not override B.__private_method()
    def __private_method(self):
        pass