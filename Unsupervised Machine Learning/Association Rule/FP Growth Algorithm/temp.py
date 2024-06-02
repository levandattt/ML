#import the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

# Đọc dữ liệu từ file CSV
def read_csv(filename):
    transactions = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            transactions.append(row)
    return transactions

# Đọc dataset từ file csv
dataset = read_csv('./Data/hashtags.csv')

class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):
        print('  ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)

def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        inTree.children[items[0]].inc(count)
    else:
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] is None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)

def createTree(dataSet, minSup=0.0000001):
    """Tạo cây FP từ tập dữ liệu nhưng không khai thác"""
    headerTable = {}

    # Lặp qua tập dữ liệu hai lần
    for trans in dataSet:  # Lần lặp đầu tiên đếm tần suất xuất hiện
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]

    for k in list(headerTable):  # Xóa các mục không đáp ứng minSup
        if headerTable[k] < minSup:
            del headerTable[k]

    freqItemSet = set(headerTable.keys())  # Tập các mục có tần suất thường xuyên
    if len(freqItemSet) == 0:
        return None, None  # Nếu không có mục nào đáp ứng hỗ trợ tối thiểu --> thoát

    for k in headerTable:
        headerTable[k] = [headerTable[k], None]  # Định dạng lại headerTable để sử dụng Node Link

    retTree = treeNode('Null Set', 1, None)  # Tạo cây
    for transSet, count in dataSet.items():  # Lặp qua tập dữ liệu lần thứ 2
        localD = {}

        for item in transSet:  # Đặt các mục giao dịch theo thứ tự
            if item in freqItemSet:
                localD[item] = headerTable[item][0]
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            updateTree(orderedItems, retTree, headerTable, count)  # Điền cây với tập mục thường xuyên theo thứ tự

    return retTree, headerTable  # Trả về cây và bảng tiêu đề

def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = 1
    return retDict

simpDat = dataset

initSet = createInitSet(simpDat)
initSet


# the FP- tree
myFPtree, myHeaderTab = createTree(initSet , 3)
myFPtree.disp()


def ascendTree(leafNode, prefixPath):
    if leafNode.parent is not None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

def findPrefixPath(basePat, treeNode):
    condPats = {}
    while treeNode is not None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats


def suggest_closest_tags_multiple(base_tags, header_table, num_suggestions=5):
    all_suggested_tags = []

    # Duyệt qua từng tag trong list các tag đã cho
    for base_tag in base_tags:
        prefix_path = findPrefixPath(base_tag, header_table[base_tag][1])
        suggested_tags = {}

        # Đếm số lần xuất hiện của mỗi tag trong các đường dẫn tiền tố
        for path in prefix_path:
            for tag in path:
                if tag not in base_tags:  # Loại bỏ các tag đã cho từ danh sách gợi ý
                    if tag not in suggested_tags:
                        suggested_tags[tag] = 1
                    else:
                        suggested_tags[tag] += 1

        # Sắp xếp các tag theo số lần xuất hiện giảm dần
        suggested_tags = sorted(suggested_tags.items(), key=lambda x: x[1], reverse=True)

        # Chỉ lấy một số tag gần nhất
        suggested_tags = [tag for tag, _ in suggested_tags[:num_suggestions]]

        # Thêm danh sách tag gần nhất vào danh sách tổng
        all_suggested_tags.extend(suggested_tags)

    return all_suggested_tags


base_tags = ["tree", "leaf","green"]
num_suggestions = 5
closest_tags = suggest_closest_tags_multiple(base_tags, myHeaderTab, num_suggestions)

# Hiển thị các tag gần nhất cho người dùng
print("Các tag gần nhất được tính toán dựa trên các tag '{}':".format(", ".join(base_tags)))
for tag in closest_tags:
    print(tag)