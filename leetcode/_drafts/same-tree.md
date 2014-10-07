---
layout: post
title: "[leetcode] Same Tree 题解"
description: "[leetcode] Same Tree 题解"
category: leetcode 
tags: [leetcode, c++, binary tree, recursion]
---
{% include JB/setup %}


题目来源：[Same Tree ](https://oj.leetcode.com/problems/same-tree/)

>
	Given two binary trees, write a function to check if they are equal or not.
	Two binary trees are considered equal if they are structurally identical and the nodes have the same value.

解题思路：

思路跟上题[对称树](http://tl3shi.github.io/leetcode/symmetric-tree.html)一样, 仍分递归和迭代两种方法。

####0. 递归

{% highlight cpp %}
	
	bool isSameTreeRecursion(TreeNode *p, TreeNode *q) 
    {
        if(p == NULL && q == NULL) return true;
        if(p == NULL || q == NULL) return false;
        if(p->val != q->val) return false;
        return isSameTree(p->left, q->left) && isSameTree(p->right, q->right);
    }
{% endhighlight %}

####1. 迭代

{% highlight cpp %}
	
	bool isSameTree(TreeNode *p, TreeNode *q) 
    {
        stack<TreeNode*> stacks;
        stacks.push(p); stacks.push(q);
        while(! stacks.empty())
        {
            auto n1 = stacks.top(); stacks.pop();
            auto n2 = stacks.top(); stacks.pop();
            if(n1 == NULL && n2 == NULL) continue;
            if(n1 == NULL || n2 == NULL) return false;
            if(n1->val != n2->val) return false;
            stacks.push(n1->left);
            stacks.push(n2->left);
            stacks.push(n1->right);
            stacks.push(n2->right);
        }
        return true;
    }
{% endhighlight %}
