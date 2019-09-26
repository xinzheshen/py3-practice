
'''
时间复杂度O(nlogn)
pivot枢纽，low和high为起点终点
'''

#划分分区（非就地划分）
def partition(nums=list):
    pivot = nums[0]                             #挑选枢纽
    lo = [x for x in nums[1:] if x < pivot]     #所有小于pivot的元素
    hi = [x for x in nums[1:] if x >= pivot]    #所有大于pivot的元素
    return lo, pivot,hi

#快速排序
def quick_sort(nums=list):
    #被分解的Nums小于1则解决了
    if len(nums) <= 1:
        return nums

    #分解
    lo,pivot,hi = partition(nums)

    # 递归（树），分治，合并
    return quick_sort(lo) + [pivot] + quick_sort(hi)

lis = [7, 5, 0, 6, 3, 4, 1, 9, 8, 2]
print(quick_sort(lis)) #[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


'''
名字很多：归并排序/合并排序/二分排序
时间复杂度 O(logn)
递归
两个步骤：1.拆分 2.合并
'''
def merge_sort(nums=list):
    #取mid以及左右两个数组
    mid = len(nums)//2
    left_nums,right_nums = nums[:mid],nums[mid:]

    #递归分治
    if len(left_nums) > 1:
        left_nums = merge_sort(left_nums)
    if len(right_nums) > 1:
        right_nums = merge_sort(right_nums)

    #合并
    res = []
    while left_nums and right_nums:  #两个都不为空的时候
        if left_nums[-1] >= right_nums[-1]:  #尾部较大者
            res.append(left_nums.pop())
        else:
            res.append(right_nums.pop())
    res.reverse() #倒序
    return (left_nums or right_nums) + res #前面加上剩下的非空nums

lis = [7, 5, 0, 6, 3, 4, 1, 9, 8, 2]
print(merge_sort(lis)) #[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


'''
给定一个顺序表，编写一个求出其最大值的分治算法
#O(nlogn)
#基本子算法（内置算法）
#虽然也可以处理大数组，这里用于解决分治问题规模小于2时候
'''
def get_max(nums=list):
    return max(nums)

#分治法
def solve(nums):
    n = len(nums)
    if n <= 2:    #分治问题规模小于2时解决
        return get_max(nums)

    # 分解（子问题规模为 n/2）
    left_list, right_list = nums[:n//2], nums[n//2:]

    # 递归（树），分治
    left_max, right_max = solve(left_list), solve(right_list)

    # 合并
    return get_max([left_max, right_max])


# 测试数据
alist = [12,2,23,45,67,3,2,4,45,63,24,23]
# 求最大值
print(solve(alist))  # 67


'''
给定一个顺序表，判断某个元素是否在其中
'''
#O(nlogn)
#子问题算法（子问题规模为1）
def is_in_list(nums,key):
    if nums[0] == key:
        print('Yes! %d in the nums' % key)
    else:
        print('Not found')
#分治法
def solve(nums,key):
    n = len(nums)
    #N==1时解决问题
    if n == 1:
        return is_in_list(nums,key)
    #分解
    left_list,right_list = nums[:n//2],nums[n//2:]
    #递归（树），分治，合并
    res = solve(left_list,key) or solve(right_list,key)

    return res

#测试
lis = [12,2,23,45,67,3,2,4,45,63,24,23]
#查找
print(solve(lis,45)) #YES~
print(solve(lis,5))  #NOT~




'''
找出一组序列中的第 k 小的元素，要求线性时间
O(nlogn)
用快排的方法，选定pivot然后通过左右两个分组递归得出结果
'''
# 划分
def partition(nums=list):
    pi = nums[0]
    lo = [x for x in nums[1:] if x < pi]
    hi = [x for x in nums[1:] if x >= pi]
    return lo,pi,hi

# 查找第 k 小的元素
def solve(nums,key):
    #分解
    lo,pi,hi = partition(nums)

    n = len(lo)
    #解决
    if n == key:
        return pi
    #递归分治
    elif n < key:
        return solve(hi,key-n-1)
    #递归分治
    else:
        return solve(lo,key)

lis = [3, 4, 1, 6, 3, 7, 9, 13, 93, 0, 100, 1, 2, 2, 3, 3, 2]
print(solve(lis,3))#2
print(solve(lis,10))#4