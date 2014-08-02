---
layout: post
title: "[leetcode] two sum 解题"
description: "[leetcode] two sum 解题"
category: leetcode 
tags: [leetcode, c++, two-sum]
---
{% include JB/setup %}

# two sum

[leetcode link](https://oj.leetcode.com/problems/two-sum/)

>Given an array of integers, find two numbers such that they add up to a specific target number.
The function twoSum should return indices of the two numbers such that they add up to the target, where index1 must be less than index2. Please note that your returned answers (both index1 and index2) are not zero-based.
You may assume that each input would have exactly one solution.

>	Input: numbers={2, 7, 11, 15}, target=9
>	Output: index1=1, index2=2

解答1、先排序（得记录index），i->0, j->n 相加结果sum<target, i++ 否则 j—
{% highlight cpp %}
vector<int> twoSum(vector<int> &numbers, int target)
{ 
    vector<pair<int, int> > num_index_map;
    for(int i = 0; i < numbers.size(); i++)
        num_index_map.push_back(pair<int, int>(numbers[i], i+1));
    std::sort(num_index_map.begin(), num_index_map.end(), [](const pair<int,int> &a, const pair<int,int> &b){return a.first < b.first;} );
    int i = 0;
    int j = numbers.size() - 1;
    while(i < j)
    {
        int tmp = num_index_map[i].first + num_index_map[j].first;
        if( tmp == target)
        {
            vector<int> result(2); //capacity, then push back, becomes 3
            //quick sort is not stable.
            if(num_index_map[i].second < num_index_map[j].second)
            {
                result[0] = (num_index_map[i].second);
                result[1] = (num_index_map[j].second);
            }else
            {
                result[1] = (num_index_map[i].second);
                result[0] = (num_index_map[j].second);
            }
            return result;
        }else if(tmp < target)
        {
            i++;
        }else
        {
            j--;
        }
    }
    return vector<int>();
}
{% endhighlight %}
2、用map存起来～直接找对应的另一半
	
{% highlight cpp %}
vector<int> twoSum(vector<int> &numbers, int target)
{
    //!important case [0,22,4,0] 0
    unordered_map<int, int> maps;
    for(int i = 0; i < numbers.size(); i++)
    {
        int num = numbers[i];
        auto it = maps.find(target-num);
        if(it != maps.end())
        {
            vector<int> result(2);
            result[0] = i+1;
            result[1] = it->second;
            if(result[1] < result[0])
                std::swap(result[0], result[1]);
            return move(result);
        }else//do not find
        {
            maps.insert(pair<int,int>(num ,i+1));
        }
    }
    return vector<int>();
}
{% endhighlight %}
