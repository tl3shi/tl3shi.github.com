---
layout: post
title: "[leetcode] Minimum Depth of Binary Tree 题解"
description: "[leetcode] Minimum Depth of Binary Tree 题解"
category: leetcode 
tags: [leetcode, c++, binary tree, traverse, recusion]
---
{% include JB/setup %}


题目来源：[Minimum Depth of Binary Tree](https://oj.leetcode.com/problems/minimum-depth-of-binary-tree/)

>

    Given a binary tree, find its minimum depth.
    The minimum depth is the number of nodes along the shortest path from the root
    node down to the nearest leaf node.

解题思路：

穷举所有路径即可。 

{% highlight cpp %}
	
	void depthRecursion(TreeNode *root, int curDepth, int &minDepth){
        if(root->left == NULL && root->right == NULL) 
        {
            minDepth = std::min(minDepth, curDepth+1);
            return;
        }
        if(root->left) depthRecursion(root->left, curDepth+1, minDepth);
        if(root->right) depthRecursion(root->right, curDepth+1, minDepth);
    }
    int minDepth(TreeNode *root) 
    {
        if(root == NULL) return 0;
        int result = INT_MAX;
        depthRecursion(root, 0, result);
        return result;
    }
{% endhighlight %}

 