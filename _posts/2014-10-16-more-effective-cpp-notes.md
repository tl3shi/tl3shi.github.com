---
layout: post
title: "More Effective C++ 读书笔记"
description: "More Effective C++ 读书笔记"
category: reading notes 
tags: [读书笔记, c++]
---
{% include JB/setup %}


## 1 仔细区别 pointers 和 references

- references必须有初值，没有null的references.
- 需要指向某个东西，绝不会改变指向其他东西，或者当实现一个操作符而其他需求无法由pointers达成，那么应该用references，不然用pointers。

## 2 最好使用c++的转型操作符

[effective-cpp-notes](./effective-cpp-notes.html)里第27条讲了.

- static_cast 强迫隐式转换(implicit conversions). 没有运行时类型检查来保证转换的安全性。
- const_cast 将某个对象的常量性去除;
- dynamic_cast 向下转型, base 转为 derived, 失败时返回null指针(转型对象为指针)或抛出bad_cast exception(转型对象为引用)。
- reinterpret_cast 不具移植性，与编译平台有关。

## 3 绝不要以多态方式处理数组

```cpp
Base array[10];
...
for(int i = 0; i < 10; i++)
	s << array[i];
```
array[i] 和 array[i+1] 之间的距离是 sizeof(Base), 如果array里面的是多态的derived object, 就会不可预期.
还有如

```cpp
delete [] array;
```
如果array里面的是多态的derived object, 结果未定义。通过base指针删除一个由derived class objects 构成的数组，结果未定义。

## 4 非必要不提供default constructor

## 5 对定制的"类型转换函数"保持警觉

两种函数允许编译器执行这样的转换:
- 单自变量constructors

	```cpp
	class Name{
	public:
		Name(const string &s);//可以把string 转换为 Name
		...
	}
	```
- 隐式类型转换操作符
	
	```cpp
	class Rational{
	public:
		operator double() const;//可将Rational转换为double
	}
	```
带来的问题是在未打算或未预期的情况下，此类函数的调用可能不正确，且难以调试。

隐式类型转换的操作符可以通过一个显示的函数调用来避免，如上面示例将```operator double() const;```换成``` double asDouble() const;``` c++中的string object 转 c-style的char\*也是显示的提供一个function **c_str()**来转换的。

构造函数可以通过关键词 **explicit** 来控制，避免编译器的隐式转换构造。

## 6 区别 increment/decrement 操作符的 前置和后置形式

```cpp
struct UPInt
{
	UPInt & operator++(); //prefix
	const UPInt opeartor++(int); //postfix ++
	UPInt & operator+=(int); //+=
}

UPInt i;
++i; // i.operator++();
i++; // i.operator++(0); 编译器默默的在后面加了一个0
```
对于后置式返回const对象原因:

```cpp
UPInt i;
i++++; //如果不是const，这样就是合法的(与内建类型不一致，内置类型是不允许的int i; i++++; error), 等于下面的调用
i.operator++(0).operator++(0); // 第2个++ 施加于第一个调用动作的返回对象上，不是原对象，即就算合法通过编译, i也只被加了1次。
```

尽量用前置式, 效率较高，后置式有临时对象生成和析构。

```cpp
const UPInt UPInt::operator++(int)
{
	UPInt old = *this;
	++(*this);
	return old;
}
```

## 7 千万不要重载 &&, || 和 , 操作符

```cpp
char * p;
...
if ((p != NULL) && strlen(p) > 10)
...

```
上述代码不用担心```strlen(p)```时 p 为 NULL, 因为 && 会短路，但若你重载了 ``` operator && ``` 函数... 则下面的调用

```cpp
if (expression1 && expression2) ... //会被编译器视为

if(expression1.operator&&(expression2)) // operator&& is a member function

or

if(operator &&(expression1, expression2)) //operator && is a global function
```
函数调用的语义没有短路的功能, 所有的参数值都必须评估完成，且c++规范并没对函数调用动作的各个参数的计算顺序有明确规定。 这样就会与内置的冲突了。 || 也一样。

逗号(,)操作符也不要重载, 下面的for最后一个表达式就用到了,操作符.
```cpp
for(int i = ..., j = ...,; i < j; ++i, --j)
```
c++规定，逗号表达式中左边会先计算，然后再右边，但整个表达式的结果是以逗号右侧的值为代表。重载时是不能达到这样的效果的。

下列操作符是不能重载的。

	.	.*	::	?:	new		delete	sizeof	typeid
	*_cast
	
可以重载的操作符是：
	
	operator new, operator delete
	operator new[], operator delete[]
	+	-	*	<< 	<<=
	,	->*		->	()	[]
	...	

注意 new 和delete operators 和 operator new, operator delete 的区别。 

## 8 了解各种不同意义的new和delete

普通意义的new 操作符, new opeartor， 如 ```string * ps = new string("hello world") ```, 包括用operator new 函数来分配内存，调用 constructor 为刚分配的内存的对象设定初值。

可以重载的是 operator new 函数 ``` void * operator new (size_t size); ``` ，可以这样调用 ```void *rawMem = operator new(sizeof(string); ```, operator new 的任务就是分配内存。  编译器看到 ``` string * ps = new string("hello world") ``` 实际上大概是这样做的:

```cpp
void * mem = operator new(sizeof(string));
call string::string("hello world") on * mem;
string * ps = static_cast<string*>(mem);

```

placement new 在已分配的(拥有指针)内存中构造对象。如

```cpp
class Widget{
public:
	Widget(int size);
	...
};
Widget * constructWidgetInBuffer(void *buffer, int widgetSize)
{
	return new (buffer) Widget(widgetSize);
}
```

总结下就是 :

- 将对象产生于heap, 请使用 new operator/expression，会分配内存且为该对象调用构造函数
- 只分配内存，调用 operator new
- 在heap objects产生时自己决定内存分配方式，自己写一个operator new，并使用new opeartor，它会调用你写的operator new
- 在已分配(拥有指针)的内存中构造对象，用 placement new

delete 也有 和 new 相对应的方式。

数组版的, 

```cpp
string * ps = new string[10];
//调用opeartor new[] 分配足够的(10个string)内存, 然后针对每个元素调用 string 的 default constructor.
delete [] ps;
//为数组每个元素调用 string destructor， 然后 调用operator delete[] 释放内存。
```

new opeartor 和 delete operator 是内置操作符，但他们所调用的内存分配/释放函数是可以定制的。


## 9 利用destructors避免泄漏资源

可以把资源的指针放入auto\_ptr中的局部对象，就算这个指针去调用某些函数发生异常时，auto\_ptr析构也会释放资源。 局部对象总是在函数结束时被析构，不管函数是如何结束(是否有异常发生， 唯一例外的是调用longjmp结束，这个缺点正式c++支持exceptions的最初的主要原因)。 

## 10 在 constructors内阻值资源泄漏

在构造函数构造过程中，如果有异常发生，得释放掉之前已经构造成功的部分资源。比较好的方法还是用auto\_ptr来管理 pointer class memebers。

## 11 禁止异常流出destructors之外

控制权基于 exception 因素离开 destructor, 此时若正有另一个 exception 处于作用状态，c++ 会自动调用 terminate 函数。全力阻止 exceptions 传出 destructors 之外，可以

- 避免terminate函数在exception传播过程中的栈展开(stack-unwinding)机制被调用
- 协助确保destructors完成其应该完成的所有事情

## 12 了解 抛出一个exception, 传递一个参数 和 调用一个虚函数 之间的差异

- exception objects 总是会被复制, 如果以 by value方式捕捉，他们甚至会被复制两次，至于传递给函数参数的对象不一定得复制
- 被抛出成为 exception 的对象，其被允许的类型转型动作比 "被传递到函数去" 的对象少。
- catch 子句以其"出现源代码顺序"被编译器检验比对，其中第一个匹配成功者执行，以某对象调用一个虚函数时，被选中执行的是最佳匹配的函数。

```cpp
void passAndThrow()
{
	Widget local; // even if static
	cin >> local;
	throw local;
}
```
上述代码中```local```对象始终都会被copy一份，local的对象会析构(static会到程序结束时才析构)，然后将copy的一份抛出。其实此exception 以by reference方式被捕捉，catch端还是只能得到local的副本。 注意copy的一份是按照静态类型copy复制的。

```cpp
...
catch(Widget &w)
{
	...
	throw; // 处理exceptioin,然后将【此】exception抛出
}
catch (Widget &w)
{
	...
	throw w;//处理exception，传播此exception的一个静态副本, 有可能是父类，抛出的子类以copy构造父类的部分。
}
```

上述的“转换类型”少说的是:

```cpp
double sqrt(double);
int i ;
double s = sqrt(i);// int 会被隐式转换为double, 然后调用sqrt(double). 

//但exception比如
try
{
	int value;
	throw value;//抛出一个int的exception
}
catch(double d) //【只】处理抛出double的exception,不会将int转换为double 然后处理
{
}
```
catch 子句匹配允许两种转换:

1. 继承架构中的类转换, 针对 base 的指针/引用 可以catch住derived的指针/引用的 exception.
2. 有型指针转为无型指针(void \*). void \* 可以捕捉任何指针的exception.

exception 处理机制是first fit, 虚函数是best fit.

## 13 以 by reference 方式捕捉 exceptions

catch by reference 可以:

- 避开如果以指针方式的话，到底是否需要delete的问题: global/static 对象的地址传出去，不需要delete，位于heap中的exception object的地址传出去，需要delete.
- 避开exception objects 对象的切割(slicing)问题.
- 保留捕捉标准exceptions的能力，标准的bad\_cast(reference 施行dynamic\_cast失败时), bad\_alloc(operator new 无法满足内存需求时), bad\_typeid(dynamic\_cast实施于一个null指针时), bad\_exception都是以对象，不是指针.
- 约束了exception objects的复制次数。

## 14 明智运用 exception specifications

不应该将templates 和 exception specifications混合使用，因为template的某种类型可能被特化/重载，进而可能抛出非specifications的异常，进而会走向unexpected之路。

Exception specifications可能会妨碍更高层次的调用者处理未预期的exception。例如:

```cpp
void logDesturction(Session *objAddr) throw(); //声明不抛出异常

void fun()
{
	try
	{
		...
		logDesturction(session);
	}catch(...)
	{}
}
```
这样，如果logDesturction内部发生了某个exception，且并没有在logDesturction里try catch住，这个非预期的exception就会导致unexpected被调用，即使```fun()```里不try了也没用。

unexpected默认实现是中止程序，可以通过```set_unexpected()```函数修改默认的实现。

## 15 了解异常处理(exception handling)的成本 

exception处理要付出代价：如果发生exception，哪些需要析构? 每个try 语句块进出点、每个catch需要处理的exception都要做记录，这些都需要代价。

如果完全确认没有exception发生，可以让编译器编译过程中放弃支持exception，以免除大小和速度的成本。

## 16 谨记 80-20 法则

程序 80% 资源/内存/CPU/IO/... 在 20% 代码上, 优化时可借助program profile 找出这20%. 

## 17 考虑使用 lazy evaluation

数据共享, 例如
```cpp
string s1 = "hello world";
string s2 = s1; //这里不急着copy construct: 成本new, strcpy 等
//都是读，s2先不copy，先和s1共享
cout << s1;
cout << s1 + s2; 

s2.convertToUpperCase(); // 等到这里，写了，才copy一份，然后改。
```

lazy fetching, 如从文件访问IO大对象，需要某个值时才去IO读。
lazy expression evaluation，例如 

```cpp 
Matrix m1 = ...
Matrix m2 = ...
Matrix m3 = m1 + m2;
....
//万一中途m3可能没有被用到之类的又这样:
m3 = m4 * m1; 
//就忘掉m3是m1+m2， 记录m4和m1的乘积, 也不急着乘.
cout << m3[4]; // 输出m3的第4行, 这样才去算
```

## 18 分期摊还预期的计算成本

利用 cache 将计算好的缓存；prefetching 如磁盘IO，将可能附近的资源也读取，内存数组扩张并不是一个一个扩张，2倍扩张。

## 19 了解临时对象的来源

