
# 在Python3.4中，协程都是通过使用yield from和asyncio模块中的@asyncio.coroutine来实现的。asyncio专门被用来实现异步IO操作。

# # 普通同步代码实现多个IO任务
# import time
# def taskIO_1():
#     print('开始运行IO任务1...')
#     time.sleep(2)  # 假设该任务耗时2s
#     print('IO任务1已完成，耗时2s')
# def taskIO_2():
#     print('开始运行IO任务2...')
#     time.sleep(3)  # 假设该任务耗时3s
#     print('IO任务2已完成，耗时3s')
#
# start = time.time()
# taskIO_1()
# taskIO_2()
# print('所有IO任务总耗时%.5f秒' % float(time.time()-start))


def generator_1(titles):
    yield titles


def generator_2(titles):
    yield from titles
    # yield from titles 等价于
    # for title in titles:
    #     yield title


titles = ['Python','Java','C++']
for title in generator_1(titles):
    print('生成器1:',title)
for title in generator_2(titles):
    print('生成器2:',title)


# yield from功能还不止于此，它还有一个主要的功能是省去了很多异常的处理，不再需要我们手动编写，其内部已经实现大部分异常处理。
# 【举个例子】：下面通过生成器来实现一个整数加和的程序，通过send()函数向生成器中传入要加和的数字，
# 然后最后以返回None结束，total保存最后加和的总数。
def generator_3():
    total = 0
    while True:
        x = yield
        print('add', x)
        if not x:
            break
        total += x
    return total

# 委托生成器
def generator_4():
    while True:
        # yield from 建立调用方和子生成器的通道
        total = yield from generator_3() # 子生成器
        print('final result:', total)

# 调用方
def main():
    # 如果直接调用generator_3,在最后传入None后，程序退出，报StopIteration异常并返回了最后total值是５
    # g3 = generator_3()
    # g3.send(None)
    # g3.send(2)
    # g3.send(3)
    # g3.send(None)

    # 但如果通过generator_4调用，就没有这个问题
    g4 = generator_4()
    g4.send(None)
    g4.send(2)
    g4.send(3)
    g4.send(None)


main()


# 那yield from通常用在什么地方呢？在协程中，只要是和IO任务类似的、耗费时间的任务都需要使用yield from来进行中断，达到异步功能！
# 我们在上面那个同步IO任务的代码中修改成协程的用法如下
# 使用同步方式编写异步功能
# import time
# import asyncio
# @asyncio.coroutine # 标志协程的装饰器
# def taskIO_1():
#     print('开始运行IO任务1...')
#     yield from asyncio.sleep(2)  # 假设该任务耗时2s
#     print('IO任务1已完成，耗时2s')
#     return taskIO_1.__name__
# @asyncio.coroutine # 标志协程的装饰器
# def taskIO_2():
#     print('开始运行IO任务2...')
#     yield from asyncio.sleep(3)  # 假设该任务耗时3s
#     print('IO任务2已完成，耗时3s')
#     return taskIO_2.__name__
# @asyncio.coroutine # 标志协程的装饰器
# def main(): # 调用方
#     tasks = [taskIO_1(), taskIO_2()]  # 把所有任务添加到task中
#     done,pending = yield from asyncio.wait(tasks) # 子生成器
#     for r in done: # done和pending都是一个任务，所以返回结果需要逐个调用result()
#         print('协程无序返回值：'+ r.result())


# 在Python 3.4中，我们发现很容易将协程和生成器混淆(虽然协程底层就是用生成器实现的)，所以在后期加入了其他标识来区别协程和生成器。
#
# 在Python 3.5开始引入了新的语法async和await，以简化并更好地标识异步IO。
#
# 要使用新的语法，只需要做两步简单的替换：
#
# 把@asyncio.coroutine替换为async；
# 把yield from替换为await。
# 更改上面的代码如下，可得到同样的结果：
import time
import asyncio
async def taskIO_1():
    print('开始运行IO任务1...')
    await asyncio.sleep(2)  # 假设该任务耗时2s
    print('IO任务1已完成，耗时2s')
    return taskIO_1.__name__
async def taskIO_2():
    print('开始运行IO任务2...')
    await asyncio.sleep(3)  # 假设该任务耗时3s
    print('IO任务2已完成，耗时3s')
    return taskIO_2.__name__
async def main(): # 调用方
    tasks = [taskIO_1(), taskIO_2()]  # 把所有任务添加到task中
    done,pending = await asyncio.wait(tasks) # 子生成器
    for r in done: # done和pending都是一个任务，所以返回结果需要逐个调用result()
        print('协程无序返回值：'+r.result())


if __name__ == '__main__':
    start = time.time()
    loop = asyncio.get_event_loop() # 创建一个事件循环对象loop
    try:
        loop.run_until_complete(main()) # 完成事件循环，直到最后一个任务结束
    finally:
        loop.close() # 结束事件循环
    print('所有IO任务总耗时%.5f秒' % float(time.time()-start))
