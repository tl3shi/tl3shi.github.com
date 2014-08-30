---
layout: post
title: "[leetcode] Convert Sorted Array to Binary Search Tree  题解"
description: "[leetcode] Convert Sorted Array to Binary Search Tree  题解"
category: leetcode 
tags: [leetcode, c++, BST, tree]
---
{% include JB/setup %}


题目来源：[Convert Sorted Array to Binary Search Tree ](https://oj.leetcode.com/problems/convert-sorted-array-to-binary-search-tree/)

>
    
    Given an array where elements are sorted in ascending order, convert it to a
height balanced BST.

解题思路：

递归即可。

{% highlight cpp %}
	
	TreeNode * convert(vector<int> &num, int start, int end)
    {
        if(start == end) return new TreeNode(num[start]);
        int mid = start + ((end - start)>>1);
        TreeNode * root = new TreeNode(num[mid]);
        if (start <= mid-1)
            root->left = convert(num, start, mid-1);
        if(mid+1 <= end)
            root->right = convert(num, mid+1, end);
        return root;
    }
    TreeNode *sortedArrayToBST(vector<int> &num) 
    {
        if(num.size() == 0) return NULL;
        return convert(num, 0, num.size()-1);
    }
{% endhighlight %}

