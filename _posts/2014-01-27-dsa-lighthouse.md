---
layout: post
title: "数据结构-灯塔(LightHouse)"
description: ""
category: data structure
tags: [data structure, mergesort,]
---
{% include JB/setup %}

>灯塔(LightHouse)
>描述
>海上有许多灯塔，为过路船只照明。从平面上看，海域范围是[1, 10^7] × [1, 10^7] 。
><img src="http://dsa.cs.tsinghua.edu.cn/oj/attachment/c6c8/c6c8562b88ed7fd518cacf0264ae624f59598ed7.png" width="640"/>
>
>( 图一）
>
>如图一所示，每个灯塔都配有一盏探照灯，照亮其东北、西南两个对顶的直角区域。探照灯的功率之大，足以覆盖任何距离。灯塔本身是如此之小，可以假定它们不会彼此遮挡。
>
>
><img src="http://dsa.cs.tsinghua.edu.cn/oj/attachment/9d7f/9d7f16b4bddbee9795e12ba22fd7f88af5438aa6.png" width="640"/>
>
>（图二）
>
>若灯塔A、B均在对方的照亮范围内，则称它们能够照亮彼此。比如在图二的实例中，蓝、红灯塔可照亮彼此，蓝、绿灯塔则不是，红、绿灯塔也不是。
>
>现在，对于任何一组给定的灯塔，请计算出其中有多少对灯塔能够照亮彼此。
>
>输入
>共n+1行。
>
>第1行为1个整数n，表示灯塔的总数。
>
>第2到n+1行每行包含2个整数x, y，分别表示各灯塔的横、纵坐标。
>
>输出
>1个整数，表示可照亮彼此的灯塔对的数量。
>
>输入样例
>3
>2 2
>4 3
>5 1
>输出样例
>1
>限制
>1 ≤ n ≤ 2×10^5
>
>灯塔的坐标x, y是整数，且不同灯塔的x, y坐标均互异
>
>1 ≤ x, y ≤ 10^7
>
>提示
>注意机器中整型变量的范围
>


解题
{% highlight c%}
#include <iostream>
#include <cstdlib>

using namespace std;

class Point 
{
public:
    int x;
    int y;
    Point(){} 
    Point(int xx, int yy):x(xx),y(yy){}
    
    Point & operator = (const Point &p)
    {
        x = p.x;
        y = p.y;
        return *this;
    }
    /*
    bool operator < (const Point &p)
    {
        return x < p.x;
    }
    bool operator <= (const Point &p)
    {
        return x <= p.x;
    }
    bool operator > (const Point &p)
    {
        return x > p.x;
    }
    */

};

void swap(Point* array, int left, int right)
{
    Point tmp = array[left];
    array[left] = array[right];
    array[right] = tmp;
}

void quicksort(Point* array, int low, int high)
{
    if(low >= high)
        return;
    int left = low;
    int right = high;
    Point key = array[left];
    while(left < right)
    {
        while(array[left].x < key.x) 
            left++;
        while(array[right].x > key.x)
            right--;
        if(left <= right)
            swap(array, left++, right--);
    }
    //out left >= right
    if(low < right)
        quicksort(array, low, right);
    if(left < high)
        quicksort(array, left, high);
}

long merge(Point* array, int start, int mid, int end)
{
    //start...mid    mid---end
    long count = 0;
    Point* result = new Point[end - start]; 
    int i = start;
    int j = mid;
    int index = 0;
    while(i < mid && j < end)  
    {
        if(array[i].y < array[j].y)
        {
            result[index++] = array[i++];
            count += (end - j);
        }
        else
        {
            result[index++] = array[j++];
        }
    }
    
    while(i < mid)
    {
        result[index++] = array[i++];
    }
    while(j < end)
    {
        result[index++] = array[j++];
    }
    for(int i = 0; i < index; i++)
        array[start + i] = result[i];
    
    delete [] result;
    return count;
}

long mergesort(Point* array, int start, int end)
{
    long count = 0;
    if(end - start < 1)
        return 0;
    if(end - start == 1)
    {
        if(array[start].y > array[end].y)
            swap(array, start, end);
        else
            count++;
        return count;
    }
    int mid = (start + end) >> 1;
    count += mergesort(array, start, mid);
    count += mergesort(array, mid, end);
    count += merge(array, start, mid, end);
    return count;
}

void print_point(Point* data, int num)
{
    for(int i = 0; i < num; i++)
        cout << data[i].x << "," << data[i].y << endl;
}

int main()
{
    int num;
    cin >> num;
    Point* data = new Point[num];
    for(int i = 0; i < num; i++)
    {
        cin >> data[i].x >> data[i].y;
    }
    long count = 0;
    quicksort(data, 0, num-1);
    //print_point(data, num);
    
    count = mergesort(data, 0, num-1);
    //cout << "---" << endl;
    //print_point(data, num);
    
    cout << count;
    return 0;
}
{% endhighlight %}
