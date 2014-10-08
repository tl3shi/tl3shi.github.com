---
layout: post
title: "[leetcode] Valid Sudoku 题解"
description: "[leetcode] Valid Sudoku 题解"
category: leetcode 
tags: [leetcode, c++, 数独]
---
{% include JB/setup %}


题目来源：[Valid Sudoku](https://oj.leetcode.com/problems/valid-sudoku/)

>
	Determine if a Sudoku is valid, according to: [Sudoku Puzzles - The Rules](http://sudoku.com.au/TheRules.aspx).
![A partially filled sudoku which is valid.](http://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Sudoku-by-L2G-20050714.svg/250px-Sudoku-by-L2G-20050714.svg.png)
>
	The Sudoku board could be partially filled, where empty cells are filled with the character '.'.
	Note: A valid Sudoku board (partially filled) is not necessarily solvable. Only the filled cells need to be validated.

解题思路：

只要里面填的数字满足3个规则就认为是valid的，同行、同列、小的9宫格不能有重复的数字。

```cpp
	
	bool isValid(vector<vector<char> > &board, int row, int col)
    {
        if(board[row][col] == '.') return true;
        for(int i = 0; i < 9; i++)
        {
            if(i != row && board[i][col] == board[row][col])//row
                return false;
            if(i != col && board[row][i] == board[row][col])//col
                return false;
            int r = 3 * (row/3) + i / 3;
            int c = 3 * (col/3) + i % 3;
            if(r != row && col != c && board[r][c] == board[row][col]) 
                return false;
        }
        return true;
    }
    
    bool isValidSudoku(vector<vector<char> > &board) 
    {
        for(int i = 0; i < 9; i++) 
            for(int j = 0; j < 9; j++)
            {
                if(! isValid(board, i, j))
                        return false;
            }
        return true;
    }
```
