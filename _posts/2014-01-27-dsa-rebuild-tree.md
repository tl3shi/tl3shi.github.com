---
layout: post
title: "数据结构-树重建"
description: "rebuild tree"
category: data structure
tags: [data structure, tree]
---
{% include JB/setup %}


[题目来源](http://dsa.cs.tsinghua.edu.cn/oj/problem.shtml?id=77)

> 描述
> 某二叉树的n个节点已经用[1, n]内的整数进行了编号。现给定该二叉树的中序遍历序列和后序遍历序列，试输出其对应的先序遍历序列。   
> ![](http://dsa.cs.tsinghua.edu.cn/oj/attachment/c6ed/c6edfc3788521a2516e0f446ddd9dd74919524e0.png)
> 
> 输入
> 第一行为一个整数n。
> 
> 第二、三行，即已知的中序、后序遍历序列。
> 
> 输出
> 仅一行。
> 
> 若所给的中序、后序遍历序列的确对应于某棵二叉树，则输出其先序遍历序列。否则，输出-1。
> 
> 输入样例1
> 5
> 4 2 5 1 3
> 4 5 2 3 1
> 输出样例1
> 1 2 4 5 3
> 输入样例2
> 3
> 2 3 1
> 1 2 3
> 输出样例2
> -1
> 限制
> 1 ≤ n ≤ 5000
> 
> 时间：2 sec
> 
> 空间：256MB
> 
> 输入和输出的遍历序列均为[1, n]内整数的一个排列，整数间均以空格分隔，行末没有多余空格。
> 
> 提示
> 不同遍历序列中根节点的位置。

解题
{% highlight c %}
#include <iostream>
#include <exception>

using namespace std;
template <class T>
class Node
{
public:
    T data;
    Node<T> *left;
    Node<T> *right;
    Node<T> *parent;
    Node(T d):data(d){};
    bool operator == (const Node &n)
    {
        return n.data == data;
    }
    ~Node()
    {
        //todo
    }
};

Node<int> * process(int* inorder, int * postorder, int instart, int inend, int poststart, int postend)
{
    int tmp = postorder[postend];
    Node<int> *node = new Node<int>(tmp);
    //cout << node->data << " ";
    if(postend == poststart)
    {
        if(instart == inend && inorder[instart] == tmp)
            return node;
        else
            throw std::exception();
    }
    
    int rootindex = instart;
    while(rootindex < inend)
    {
        if(tmp == inorder[rootindex])
            break;
        rootindex++;
    }
    if(rootindex == inend && inorder[rootindex] != tmp)
        throw std::exception();
    
    int leftlen = rootindex - instart;
    if(leftlen >= 1)
        node->left = process(inorder, postorder, instart, rootindex-1, poststart, poststart+leftlen-1);
    if(postend - 1 >= poststart + leftlen)
        node->right = process(inorder, postorder, rootindex+1, inend, poststart+leftlen, postend-1);
    return node;
}

void print_preorder(Node<int> *tree)
{
    cout << tree->data << " ";
    if(tree->left != NULL)
        print_preorder(tree->left);
    if(tree->right != NULL)
        print_preorder(tree->right);
}

int main()
{
    int n;
    cin >> n;
    int * inorder = new int[n];
    int * postorder = new int[n];
    int tmp = 0;
    for(int i = 0; i < n; i++)
    {
        cin >> tmp;
        inorder[i] = (tmp);
    }
    for(int i = 0; i < n; i++)
    {
        cin >> tmp;
        postorder[i] = (tmp);
    }
    
    Node<int> * tree = NULL;
    try {
        tree = process(inorder, postorder, 0, n-1, 0, n-1);
        print_preorder(tree);
    } catch (std::exception) {
        cout << "-1";
    }
    
    delete[] inorder;
    delete[] postorder;
    
    if (tree != NULL)
        delete tree;
    
    return 0;
}
{% endhighlight %}
