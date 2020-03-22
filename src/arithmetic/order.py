

def bubble_sort(alist):
    """
    冒泡排序：重复地遍历要排序的数列，一次比较两个元素，如果他们的顺序错误就把他们交换过来。
    最优时间复杂度：O(n) （表示遍历一次发现没有任何可以交换的元素，排序结束。）
    最坏时间复杂度：O(n2)
    稳定性：稳定
    :param alist:
    :return:
    """
    length = len(alist)
    for i in range(length - 1):
        for j in range(length - i - 1):
            if alist[j] > alist[j+1]:
                alist[j], alist[j+1] = alist[j+1], alist[j]
    return alist


def selection_sort(alist):
    """
    选择排序：首先在未排序序列中找到最小（大）元素，存放到排序序列的起始位置，
    然后，再从剩余未排序元素中继续寻找最小（大）元素，然后放到已排序序列的末尾。
    以此类推，直到所有元素均排序完毕
    最优时间复杂度：O(n2)
    最坏时间复杂度：O(n2)
    稳定性：不稳定（考虑升序每次选择最大的情况）
    :param alist:
    :return:
    """
    length = len(alist)

    for i in range(length):
        min_index = i
        for j in range(i, length):
            if alist[min_index] > alist[j]:
                min_index = j

        if min_index != i:
            alist[i], alist[min_index] = alist[min_index], alist[i]

    return alist


def insert_sort(alist):
    """
    插入排序：通过构建有序序列，对于未排序数据，在已排序序列中从后向前扫描，找到相应位置并插入。
    插入排序在实现上，在从后向前扫描过程中，需要反复把已排序元素逐步向后挪位，为最新元素提供插入空间。
    最优时间复杂度：O(n) （升序排列，序列已经处于升序状态）
    最坏时间复杂度：O(n2)
    稳定性：稳定
    :param alist:
    :return:

    """
    # 从第二个位置，即下标为1的元素开始向前插入
    for i in range(1, len(alist)):
        # 从第i个元素开始向前比较，如果小于前一个元素，交换位置
        for j in range(i, 0, -1):
            if alist[j] < alist[j-1]:
                alist[j], alist[j-1] = alist[j-1], alist[j]

    return alist


def quick_sort(alist):
    """
    快速排序,又称划分交换排序:通过一趟排序将要排序的数据分割成独立的两部分，
    其中一部分的所有数据都比另外一部分的所有数据都要小，然后再按此方法对这两部分数据分别进行快速排序，
    整个排序过程可以递归进行，以此达到整个数据变成有序序列。
    步骤为：
    1.从数列中挑出一个元素，称为"基准"（pivot），
    2.重新排序数列，所有元素比基准值小的摆放在基准前面，所有元素比基准值大的摆在基准的后面（相同的数可以到任一边）。
    在这个分区结束之后，该基准就处于数列的中间位置。这个称为分区（partition）操作。
    3.递归地（recursive）把小于基准值元素的子数列和大于基准值元素的子数列排序。

    最优时间复杂度：O(nlogn)
    最坏时间复杂度：O(n2)
    稳定性：不稳定
    :param alist:
    :return:
    """
    pass


if __name__ == '__main__':
    li = [54, 26, 93, 17, 77, 31, 44, 55, 20]
    print(bubble_sort(li.copy()))
    print(selection_sort(li.copy()))
    print(insert_sort((li.copy())))

