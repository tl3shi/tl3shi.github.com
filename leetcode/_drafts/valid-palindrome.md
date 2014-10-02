---
layout: post
title: "[leetcode] Valid Palindrome 题解"
description: "[leetcode] Valid Palindrome 题解"
category: leetcode 
tags: [leetcode, c++, 回文]
---
{% include JB/setup %}


题目来源：[Valid Palindrome](https://oj.leetcode.com/problems/valid-palindrome/)

>

    Given a string, determine if it is a palindrome, considering only alphanumeric
    characters and ignoring cases.
    For example,
    "A man, a plan, a canal: Panama" is a palindrome.
    "race a car" is not a palindrome.
    Note:
    Have you consider that the string might be empty? This is a good question to
    ask during an interview.
    For the purpose of this problem, we define empty string as valid palindrome.

解题思路：

搞清题意只check数字和字母，忽略大小写。

{% highlight cpp %}
	
	bool isa2zorNum(char c)
{% endhighlight %}
