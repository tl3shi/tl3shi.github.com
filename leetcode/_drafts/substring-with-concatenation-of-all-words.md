---
layout: post
title: "[leetcode] Substring with Concatenation of All Words 题解"
description: "[leetcode] Substring with Concatenation of All Words 题解"
category: leetcode 
tags: [leetcode, c++, DFS, 滑动窗口]
---
{% include JB/setup %}


题目来源：[Substring with Concatenation of All Words](https://oj.leetcode.com/problems/substring-with-concatenation-of-all-words/)

>
	You are given a string, S, and a list of words, L, that are all of the same length. Find all starting indices of substring(s) in S that is a concatenation of each word in L exactly once and without any intervening characters.
	For example, given:
	S: "barfoothefoobarman"
	L: ["foo", "bar"]
	You should return the indices: [0,9].
	(order does not matter).

解题思路：

####0. DFS

用一个hashmap记录需要匹配的单词数量和已经匹配的单词数量～然后DFS, 代码如下，不过超时了。

```cpp	
vector<int> findSubstring(string S, vector<string> &L) 
{
   unordered_map<string, int> origin;
   int need_count = 0;
   for(string str : L)
   {
       ++need_count;
       ++origin[str];
   }
   if(need_count == 0 || S.length() < need_count * L[0].length()) return vector<int>();
   vector<int> result; 
   unordered_map<string, int> match;
   dfs(result, origin, match, need_count, 0, 0, S, L[0].length(), S.length());
   return move(result);
}

void dfs(vector<int> &result, const unordered_map<string, int> &origin, unordered_map<string, int> &match,
       const int need_count, int match_count, int startIndex, const string S, const int each_len, const int total_len)
{
   if(startIndex > total_len)
       return;
   if(need_count == match_count)
       {result.push_back(startIndex); return;}
   for(int i = startIndex; i < total_len; i += each_len)
   {
       string word = S.substr(i, each_len);
       auto it = origin.find(word);
       if(it != origin.end())
       {
           ++match[word];
           if(match[word] <= it->second)
               dfs(result, origin, match, need_count, match_count+1, i+each_len, S, each_len, total_len);
           --match[word];
       }
   }
}
```

dfs部分改成非递归后，可以AC。

```cpp
void dfs(vector<int> &result, const unordered_map<string, int> &origin, unordered_map<string, int> &match,
        const int need_count, int match_count, int startIndex, const string S, const int each_len, const int total_len)
{
    int segment_len = each_len * need_count;
    for(int index = startIndex; index <= total_len - segment_len; index++)
    {
        match.clear(); match_count = 0;
        for(int i = index; i < index + segment_len; i += each_len)
        {
            string word = S.substr(i, each_len);
            auto it = origin.find(word);
            if(it != origin.end())
            {
                ++match[word]; ++match_count;
                if(match[word] > it->second) //culling
                    break;
                if(match_count == need_count)
                    result.push_back(index);
            }
            else //culling
                break;
        }
    }
}
```

上面解法时间复杂度是\\( O(strlen * listlen * wordlen) \\).  参考 [Discuss]()后发现有更好的
\\( O(n) \\)的解法。

####1. \\( O(n) \\) 滑动窗口解法


滑动窗口，跟[Longest Substring Without Repeating Characters](./Longest-Substring-Without-Repeating-Characters.html) 、[Minimum Window Substring](Minimum-Window-Substring.html) 类似。复杂度 \\( O(\frac{strlen}{wordlen} * wordlen) = O(n) \\)，一次扫描需要迭代 strlen/wordlen 次，偏移wordlen次。

	如"[bar][foo][the][foo][bar][man]" (只考虑这个串,下次右移1位，即考虑[arf]oothefoobarman 偏移wordlen-1次可以考虑完全)
	[barfoothefoobarman
	[barfoo]thefoobarman, foo在, 右窗口后移，发现匹配OK，左窗口index加入结果集合，匹配OK后，左窗口右移一个单词
	bar[foothefoobarman, the不在, 直接左窗口后移到the后
	barfoothe[foobarman, goon…..
	另，假设L里有两个foo,还有一个xxx
	barfoothe[xxxfoobarfoofoo]barman, 此时,foo数量大于了2，此时左窗口要移动到第1次出现地方的下一个位置，即
	barfoothexxxfoo[barfoofoo]barman, goon….

就沿用第一个解法的算法框架了，换了个函数名。其实算法框架跟上面的差不多，几个地方改下逻辑:

- 大于应该匹配的单词数量时, 移到该单词首次出现的下一个位置; 
- 得到一个结果后，左窗口右移一个单词位置；
- 单词不在辞典里，直接移动左窗口到不在辞典单词的后一个位置。

```cpp
void window(vector<int> &result, const unordered_map<string, int> &origin, unordered_map<string, int> &match,
            const int need_count, int match_count, int startIndex, const string S, const int each_len, const int total_len)
{
   for(int index = startIndex; index < each_len; index++)
   {
       match.clear(); match_count = 0;
       int windowStart = index;
       for(int i = index; i <= total_len - each_len; i += each_len)
       {
           string word = S.substr(i, each_len);
           auto it = origin.find(word);
           if(it != origin.end())
           {
               ++match[word]; ++match_count;
               if(match[word] > it->second) //culling
               {
                   //the number of word is more than it should be, the windowstart should move to the next index of the first current word  
                   while(true)
                   {
                       string tmp = S.substr(windowStart, each_len);
                       --match[tmp];
                       --match_count;
                       windowStart += each_len;
                       if(tmp == word)
                           break;
                   }
               }
               if(match_count == need_count)
               {
                   result.push_back(windowStart);
                   //remove firstword outof the window
                   string first = S.substr(windowStart, each_len);
                   --match[first];
                   --match_count;
                   windowStart += each_len;
               }
           }
           else 
           {
               match.clear();
               windowStart = i + each_len;
               match_count = 0;
           }
       }
   }
}
```

<!-- MathJax Section -->
<script type="text/javascript"
src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
