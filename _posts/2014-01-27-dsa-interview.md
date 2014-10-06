---
layout: post
title: "数据结构-面试(Interview)"
description: "数据结构-面试(Interview)"
category: data structure
tags: [data structure]
---
{% include JB/setup %}

> 面试(Interview)
> 描述
> 某公司在对应聘者做过一轮笔试之后，从中选出成绩最高的n 人继续进行面试。在笔试中，每位应聘者已被分配了一个整数ID，面试时将沿用这个ID。
> 
> 为公平起见，组织者决定利用会议室外的圆桌，按以下方法“随机”确定面试顺序：第一个到达的应聘者在圆桌周围任意选择一个位置坐下；此后到达的每位应聘者都从前一应聘者出发，沿逆时针方向围圆桌走过m 人（前一应聘者算作走过的第1 人，同一人可能经过多次），并紧邻第m 人右侧就座；所有应聘者到齐后，从最后到达者出发，绕圆桌以顺时针方向为序进行面试。
> 
> ![](http://dsa.cs.tsinghua.edu.cn/oj/attachment/ebf6/ebf6c11c9abc9d574467d4583506addb6943f452.png)
> 
> 这里假定应聘者到达的时刻互异，且相对的就坐位置确定后，左、右两人之间总能插入一把椅子。
> 
> 试编写一个程序，对于任给的m 及n 个应聘者ID，确定对应的面试顺序。
> 
> 输入
> 共2行。
> 
> 第1行包含两个整数，以空格分隔，依次表示n和m。
> 
> 第2行包含n个整数，以空格分隔，表示先后到达的n个应聘者的ID。
> 
> 输出
> 共1行。以空格分隔的n个整数，分别表示顺次进行面试的应聘者的ID。
> 
> 输入样例
> 3 2
> 8 9 10
> 输出样例
> 10 8 9
> 限制
> 1 <= N <= 10^3
> 
> 1 <= m <= 2\*N
> 
> 输入的ID保证在int类型的范围内。
> 
> 提示
> 请借助列表实现
> 
> 

解题

```cpp
#include <iostream>
#include <cstdlib>
#include <fstream>
#include "assert.h"

using namespace std;
template <class T>
class list1
{
    T* data_;
    int capacity_;
    int size_;

public:
    
    typedef int iterator;

    list1(int default_size = 4)
    {
        data_ = new T[default_size];
        capacity_ = default_size;
        size_  = 0;
    }
    
    int size()
    {
        return size_;
    }

    iterator begin()
    {
        return 0;   
    }
    iterator end()
    {
      return size_;
    }
    void push_back(const T &d)
    {
        ensureSize();

        data_[size_] = d;
        size_++;
    }

    T at(iterator it)
    {
        assert(it < end());
        return data_[it];
    }

    void insert(iterator it, T d)
    {
        ensureSize();
        size_++;
        for (int i = size_-1; i > it; i--)
        {
            data_[i] = data_[i-1];
        }
        data_[it] = d;
    }

private:
    void ensureSize()
    {
        if(capacity_ == size_)
        {
            capacity_ *= 2;
            T* newdata = new T[capacity_];
            for (int i = 0 ; i < size_; i++)
            {
                newdata[i] = data_[i];
            }

            delete[] data_;
            data_ = newdata;
        }
    }
};

int main()
{
    #define list list1
    
    //ifstream in("D:/github/algorithms/xuetangx.ds/interview.PA1_b_10.in");
    //cin.rdbuf(in.rdbuf());
    //ofstream out("D:/github/algorithms/xuetangx.ds/interview.PA1_b_10.out");
    //cout.rdbuf(out.rdbuf());

    int n, m;
    cin >> n >> m;
    int* data = new int[n]; 
    for(int i = 0; i < n; i++)
    {
        cin >> data[i];
    }
    list<int> result;
    result.push_back(data[0]);
    int has_inserted = 0;
    list<int>::iterator last_index = result.begin();
    //int last_index;
    while(true)
    {
        int i = 1;
        list<int>::iterator cycle;
        cycle = last_index;
        while(true)
        {
            if(i == m)
            {
                cycle++;//insert after/right of the one
                if(cycle == result.end())
                    cycle = result.begin();
                result.insert(cycle, data[++has_inserted]);
                last_index = cycle;
                break;
            }
            i++;
            cycle++;
            if(cycle == result.end())
                cycle = result.begin();
        }
        if(result.size() == n)
            break;
    }
    int output = 0;
    while(true)
    {
        #ifdef list1
         cout << *last_index << " ";
         #else
          cout << result.at(last_index) << " ";
        #endif // list
        
        if(++output == n)
            break;
        if(last_index == result.begin())
            last_index = result.end();
        last_index --;
    }
    delete[] data;
    return 0;
}
```
