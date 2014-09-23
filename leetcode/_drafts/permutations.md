---
layout: post
title: "[leetcode] Permutations 题解"
description: "[leetcode] Permutations 题解"
category: leetcode 
tags: [leetcode, c++, 排列组合, permutation]
---
{% include JB/setup %}


题目来源：[Permutations](https://oj.leetcode.com/problems/permutations/)

>
	Given a collection of numbers, return all possible permutations.
	For example,
	[1,2,3] have the following permutations:
	[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], and [3,2,1].

解题思路：

####0. 置换法

递归, 一个一个与第一个交换。

{% highlight cpp %}
	
	void dfs(vector<vector<int> > &result, vector<int> &num, int start)
    {
        if(start >= num.size()) // >= ">"also should be put in, for the last ele.
        {
            result.push_back(num);
            return;
        }
        for(int i = start; i < num.size(); i++)
        {
            std::swap(num[i], num[start]);
            dfs(result, num, start+1);
            std::swap(num[i], num[start]);
        }
    }
    vector<vector<int> > permute(vector<int> &num) 
    {
        vector<vector<int> > result;
        dfs(result, num, 0);
        return move(result);
    }
{% endhighlight %}

####1. 增量构造法

可以跟 [combinations](TODO_PRE/combinations.html) 类似, 一个一个往里面加。

{% highlight cpp %}
	
	void dfs(vector<vector<int> > &result, const vector<int> &num, vector<int> &path )
    {
        if(path.size() == num.size())
        {
            result.push_back(path);
            return;
        }
        for(int i = 0; i < num.size(); i++)
        {
            if(std::find(path.begin(), path.end(), num[i]) == path.end())
            {
                path.push_back(num[i]);
                dfs(result, num, path);
                path.pop_back();
            }
        }
    }
    vector<vector<int> > permute(vector<int> &num) 
    {
        vector<vector<int> > result;
        vector<int> path;
        dfs(result, num, path);
        return move(result);
    }
{% endhighlight %}


####2. nextPermunation

参考 [permutations-ii](TODO_PRE/permutations-ii.html).