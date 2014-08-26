---
layout: post
title: "[leetcode] Linked List Cycle II 题解"
description: "[leetcode] Linked List Cycle II 题解"
category: leetcode 
tags: [leetcode, c++, list]
---
{% include JB/setup %}


题目来源：[Linked List Cycle
II](https://oj.leetcode.com/problems/linked-list-cycle-ii/)

>

    Given a linked list, return the node where the cycle begins. If there is no cycle, return null.

解题思路：

简单的快慢指针.

{% highlight cpp %}

    ListNode *detectCycle(ListNode *head) 
    {
        if(head == NULL || head->next == NULL) return NULL;
        ListNode * fast = head;
        ListNode * slow = head;
        while(fast != NULL && fast->next != NULL)
        {
            fast = fast->next->next;
            slow = slow->next;
            if(fast == slow) //find intersection node
            {
                fast = head;
                while(fast != slow)
                {
                    fast = fast->next;
                    slow = slow->next;
                }
                return fast;
            }
        }
        return NULL;
    }
{% endhighlight %}
