---
layout: post
title: "[leetcode] Binary Tree Zigzag Level Order Traversal 题解"
description: "[leetcode] Binary Tree Zigzag Level Order Traversal 题解"
category: leetcode 
tags: [leetcode, c++, binary tree, BFS, level traverse, recursion]
---
{% include JB/setup %}


题目来源：[Binary Tree Zigzag Level Order Traversal
II](https://oj.leetcode.com/problems/binary-tree-zigzag-level-order-traversal/)

>
	
	Given a binary tree, return the zigzag level order traversal of its nodes' values. (ie, from left to right, then right to left for the next level and alternate between).
	For example:
	Given binary tree {3,9,20,#,#,15,7},
	    3
	   / \
	  9  20
	    /  \
	   15   7
	return its zigzag level order traversal as:
	[
	  [3],
	  [20,9],
	  [15,7]
	]

解题思路：

跟前面的题[Binary Tree Level Order Traversal](http://tl3shi.github.io/leetcode/binary-tree-level-order-traversal.html) 以及[Binary Tree Level Order Traversal II](http://tl3shi.github.io/leetcode/binary-tree-level-order-traversal-ii.html)。 
区别就是这个将第偶数层的结果reverse一下。
这里就只列了其中一种代码了。

####0. 常规方法, 两个queue交替
参见[Binary Tree Level Order Traversal](http://tl3shi.github.io/leetcode/binary-tree-level-order-traversal.html)。
 
####1. 单queue+隔板

前面[word ladder ii](http://tl3shi.github.io/leetcode/word-ladder-ii.html)就提到过bfs，用隔板将各层之间隔离出来。只用一个queue就能知道某层是否已经遍历完毕。

```cpp
	
	 vector<vector<int> > zigzagLevelOrder(TreeNode *root) 
    {
        vector<vector<int> > result;
        if(root == NULL) return result;
        queue<TreeNode*> q;
        q.push(root);
        int i = 0;
        while(! q.empty())
        {
            q.push(NULL);
            vector<int> level;
            while(q.front() != NULL)
            {
                auto node = q.front(); q.pop();
                level.push_back(node->val);
                if(node->left) q.push(node->left);
                if(node->right) q.push(node->right);
            }
            if(i++ & 0x1)
                std::reverse(level.begin(), level.end());
            result.push_back(level);
            q.pop();//pop NULL
        }
        return move(result);
    }
```

#### 2.递归

参见[Binary Tree Level Order Traversal](http://tl3shi.github.io/leetcode/binary-tree-level-order-traversal.html)。
 
