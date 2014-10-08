---
layout: post
title: "[leetcode] Largest Rectangle in Histogram 题解"
description: "[leetcode] Largest Rectangle in Histogram 题解"
category: leetcode 
tags: [leetcode, c++, array, stack, 分治, 线段树]
---
{% include JB/setup %}


题目来源：[Largest Rectangle in Histogram](https://oj.leetcode.com/problems/largest-rectangle-in-histogram/)

>
	Given n non-negative integers representing the histogram's bar height where the width of each bar is 1, find the area of largest rectangle in the histogram.
![](http://tl3shi.github.com/resource/blogimage/leetcode-histogram-0.png)

	Above is a histogram where width of each bar is 1, given height = [2,1,5,6,2,3].
![](http://tl3shi.github.com/resource/blogimage/leetcode-histogram_area.png)

	The largest rectangle is shown in the shaded area, which has area = 10 unit.
	For example,
	Given height = [2,1,5,6,2,3],
	return 10.

解题思路：

####0 直接穷举，剪枝即可AC


```cpp

	int largestRectangleArea1(vector<int > &height)
	{
	    int result = 0;
	    for(int i = 0; i < height.size(); ++i)
	    {
	        //height[i+1] bigger than height[i], result must be bigger than end with height[i]
	        if( i+1 < height.size() && height[i+1] >= height[i])
	            continue;
	        int min_height = height[i];
	        for(int j = i; j >= 0; --j)
	        {
	             min_height = std::min(min_height, height[j]);
	             int area = min_height * (i - j + 1);
	             result = std::max(result, area);
	        }
	    }
	    return result;
	}
```

####1. 用栈的O(n)解法

对每一个高度x,把x当作最矮的一个进行计算矩形面积，这样得到的最大的面积就是最终的结果。

>	
	For every bar ‘x’, we calculate the area with ‘x’ as the smallest bar in the rectangle. If we calculate such area for every bar ‘x’ and find the maximum of all areas, our task is done. How to calculate area with ‘x’ as smallest bar? We need to know index of the first smaller (smaller than ‘x’) bar on left of ‘x’ and index of first smaller bar on right of ‘x’. Let us call these indexes as ‘left index’ and ‘right index’ respectively.
	We traverse all bars from left to right, maintain a stack of bars. Every bar is pushed to stack once. A bar is popped from stack when a bar of smaller height is seen. When a bar is popped, we calculate the area with the popped bar as smallest bar. How do we get left and right indexes of the popped bar – the current index tells us the ‘right index’ and index of previous item in stack is the ‘left index’. Following is the complete algorithm.
	
	栈维护了一个递增(非递减)的序列，当当前索引的元素比栈顶小时，取栈顶元素（并出栈），并将这个元素的高度和当前索引端(快降低了)构成的矩形面积，栈中上升的那段都可以出栈并计算。上图中，到第2个2为止，6、5先后出栈计算（作为smalleast的一端），不可能比2后面的数组成一起构成更大的面积，因为2小了，短板在此，且6，5才是作为smalleast的一端参与计算的，出栈到之前1比当前2小，就不再出栈了，因为1作为smalleast可能与2后面的数构成更大面积的矩形(宽度更长)。算法开始前加了一个-1是为了将所有的栈都弹出并参与计算。
	
```cpp
		
	//ref: http://www.geeksforgeeks.org/largest-rectangle-under-histogram/
	//ref2: http://www.cnblogs.com/lichen782/p/leetcode_Largest_Rectangle_in_Histogram.html
	int largestRectangleArea(vector<int > &height)
	{
	    if (height.size() == 0) return 0;
	    int i = 0;
	    int maxArea = 0;
	    height.push_back(-1); // dummy one
	    stack<int> indexes;
	    while(i < height.size())
	    {
	        if(indexes.empty() || height[indexes.top()] <= height[i])
	            indexes.push(i++);
	        else
	        {
	            int t = indexes.top();
	            indexes.pop();
	            maxArea = std::max(maxArea, height[t] * (indexes.empty() ? i : i - indexes.top() - 1));
	        }
	    }
	    height.pop_back();
	    return maxArea;
	}
```

注意看上面出栈时候的写法与[maximal-rectangle](./maximal-rectangle.html)的异同。

- [ref1-leetcode_Largest_Rectangle_in_Histogram](http://www.cnblogs.com/lichen782/p/leetcode_Largest_Rectangle_in_Histogram.html)
- [ref2-largest-rectangle-under-histogram](http://www.geeksforgeeks.org/largest-rectangle-under-histogram/)

还有一个思路就是参考[maximal-rectangle](./maximal-rectangle.html)的解法2.
思路是对当前高度h, 找左边比他小的最大的index,设为i, 右边比h小最小的index,设为j,则以h为最小高度的面积应该为 
`(j-i-1)*h`.  eg : [2,5,3,4,1], 当前高度3, 则, left=0, right = 4, area = 3*(4-0-1)=9.
求left/right时思路如下：
	height[i] > height[i-1]: left[i] = i-1;
	else 从i-1开始往左, 找第一个比height[i]小数的index。
right差不多的思路。初始时，left[0:n-1]=-1, right[0:n-1]=n.

#### 2.0 分治法O(nlogn)

下面代码直接抄的[Largest Rectangular Area in a Histogram | Set 1 | GeeksforGeeks ](http://www.geeksforgeeks.org/largest-rectangular-area-in-a-histogram-set-1/).

思想就是

	分治，线段树，上图中，先找到最矮的1，最大值结果来自：
	     1) 1的左边(不包括1)；
	     2) 1的右边(不包括1)；
	     3) 包括1, 1的高度乘以整个数轴宽度；
	复杂度： T(n) = T(n-1) + O(log n), O(log n)用于查看区间内的最小值. 
	最终复杂度为O(n log n). 

```cpp

	// A utility function to find minimum of three integers
	int max(int x, int y, int z)
	{  return std::max(std::max(x, y), z); }
	 
	// A utility function to get minimum of two numbers in hist[]
	int minVal(int *hist, int i, int j)
	{
	    if (i == -1) return j;
	    if (j == -1) return i;
	    return (hist[i] < hist[j])? i : j;
	}
	 
	// A utility function to get the middle index from corner indexes.
	int getMid(int s, int e)
	{   return s + (e -s)/2; }
	 
	/*  A recursive function to get the index of minimum value in a given range of
	    indexes. The following are parameters for this function.
	 
	    hist   --> Input array for which segment tree is built
	    st    --> Pointer to segment tree
	    index --> Index of current node in the segment tree. Initially 0 is
	             passed as root is always at index 0
	    ss & se  --> Starting and ending indexes of the segment represented by
	                 current node, i.e., st[index]
	    qs & qe  --> Starting and ending indexes of query range */
	int RMQUtil(int *hist, int *st, int ss, int se, int qs, int qe, int index)
	{
	    // If segment of this node is a part of given range, then return the
	    // min of the segment
	    if (qs <= ss && qe >= se)
	        return st[index];
	 
	    // If segment of this node is outside the given range
	    if (se < qs || ss > qe)
	        return -1;
	 
	    // If a part of this segment overlaps with the given range
	    int mid = getMid(ss, se);
	    return minVal(hist, RMQUtil(hist, st, ss, mid, qs, qe, 2*index+1),
	                  RMQUtil(hist, st, mid+1, se, qs, qe, 2*index+2));
	}
	 
	// Return index of minimum element in range from index qs (quey start) to
	// qe (query end).  It mainly uses RMQUtil()
	int RMQ(int *hist, int *st, int n, int qs, int qe)
	{
	    // Check for erroneous input values
	    if (qs < 0 || qe > n-1 || qs > qe)
	    {
	        cout << "Invalid Input";
	        return -1;
	    }
	 
	    return RMQUtil(hist, st, 0, n-1, qs, qe, 0);
	}
	 
	// A recursive function that constructs Segment Tree for hist[ss..se].
	// si is index of current node in segment tree st
	int constructSTUtil(int hist[], int ss, int se, int *st, int si)
	{
	    // If there is one element in array, store it in current node of
	    // segment tree and return
	    if (ss == se)
	       return (st[si] = ss);
	 
	    // If there are more than one elements, then recur for left and
	    // right subtrees and store the minimum of two values in this node
	    int mid = getMid(ss, se);
	    st[si] =  minVal(hist, constructSTUtil(hist, ss, mid, st, si*2+1),
	                     constructSTUtil(hist, mid+1, se, st, si*2+2));
	    return st[si];
	}
	 
	/* Function to construct segment tree from given array. This function
	   allocates memory for segment tree and calls constructSTUtil() to
	   fill the allocated memory */
	int *constructST(int hist[], int n)
	{
	    // Allocate memory for segment tree
	    int x = (int)(ceil(log2(n))); //Height of segment tree
	    int max_size = 2*(int)pow(2, x) - 1; //Maximum size of segment tree
	    int *st = new int[max_size];
	 
	    // Fill the allocated memory st
	    constructSTUtil(hist, 0, n-1, st, 0);
	 
	    // Return the constructed segment tree
	    return st;
	}
	 
	// A recursive function to find the maximum rectangular area.
	// It uses segment tree 'st' to find the minimum value in hist[l..r]
	int getMaxAreaRec(int *hist, int *st, int n, int l, int r)
	{
	    // Base cases
	    if (l > r)  return INT_MIN;
	    if (l == r)  return hist[l];
	 
	    // Find index of the minimum value in given range
	    // This takes O(Logn)time
	    int m = RMQ(hist, st, n, l, r);
	 
	    /* Return maximum of following three possible cases
	       a) Maximum area in Left of min value (not including the min)
	       a) Maximum area in right of min value (not including the min)
	       c) Maximum area including min */
	    return max(getMaxAreaRec(hist, st, n, l, m-1),
	               getMaxAreaRec(hist, st, n, m+1, r),
	               (r-l+1)*(hist[m]) );
	}
	 
	// The main function to find max area
	int getMaxArea(int hist[], int n)
	{
	    // Build segment tree from given array. This takes
	    // O(n) time
	    int *st = constructST(hist, n);
	 
	    // Use recursive utility function to find the
	    // maximum area
	    return getMaxAreaRec(hist, st, n, 0, n-1);
	}
 
    int largestRectangleArea(vector<int> &height) 
    {
        if(height.size() == 0) return 0;
        return getMaxArea(&height[0], height.size());
    }
```
