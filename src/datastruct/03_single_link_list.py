

class Node(object):
    def __init__(self, elem):
        self.elem = elem
        self.next = None


class SingleLinkList(object):
    def __init__(self, node=None):
        self.__head = node

    def is_empty(self):
        return self.__head == None

    def length(self):
        cur = self.__head
        count = 0
        while cur != None:
            count += 1
            cur = cur.next
        return count

    def travel(self):
        cur = self.__head
        while cur != None:
            print(cur.elem, end=" ")
            cur = cur.next

    def add(self):
        # 链表头部添加元素, 头插法
        pass

    def append(self, item):
        # 链表尾部添加元素，尾插法
        node = Node(item)
        if self.is_empty():
            self.__head = node
        else:
            cur = self.__head
            while cur.next != None:
                cur = cur.next
            cur.next = node

    def insert(self):
        pass

    def remove(self):
        pass

    def search(self):
        pass

    def reverse(self):
        cur = self.__head
        h = self.__head
        pre = None
        while cur:
            h = cur
            tmp = cur.next
            cur.next = pre
            pre = cur
            cur = tmp
        while h:
            print(h.elem)
            h = h.next


if __name__ == '__main__':
    li = SingleLinkList()
    print(li.is_empty())
    print(li.length())

    li.append(1)
    print(li.is_empty())
    print(li.length())

    li.append(2)
    li.append(3)
    li.append(4)
    li.append(5)
    li.append(6)
    li.travel()
    li.reverse()
