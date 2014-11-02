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


<span id="tiaokuan12"></span>
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

exception 传播可以简单的以by refernce捕捉不需要by reference-to-const 捕捉，而函数调用将一个临时对象传递给一个non-const reference参数是不允许的。 见[条款19](#tiaokuan19).

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

<span id="tiaokuan19"></span>
## 19 了解临时对象的来源

注意临时对象和局部对象(swap函数中的交换的那个临时变量)的区别. 临时对象是不可见的，出现于下面两种情况：

- 隐式类型转换(implicit type conversions) 被实施以求函数调用成功;
- 当函数返回对象时. //这个可能编译器有返回值优化

```cpp
size_t countChar(const string& str, char ch);
...
char buffer[MAX_LEN];
char c;
...
cout << countChar(buffer, c);
//上述代码中, countChar要求传入参数string&, 而实际参数为buffer[], 编译器为了保证调用成功，
//会自动产生一个string的临时对象, 将buffer作为自变量调用string的constructor. 这样countChar的str就会绑定此临时对象, countChar返回时, 此临时对象自动析构/销毁.
``` 

只有当对象以by value的方式或者reference-to-const的方式，这些类型转换才会发生，如果是一个reference-to-non-const参数，并不会发生此类转换。

```cpp
void upper(string &str)
{
}
void upper1(const string &str)
{
}
int main()
{
    char t[] = "hello world";
    upper1(t); //OK
    upper(t); //compile error
}
```
原因是, upper中传入string&, 内部str可能会改变, 而内部实际上会作用与编译器生成的那个临时对象上，与coder期望的不一致，因此c++禁止为non-const reference 参数产生临时对象。exception 除外，见[条款12](#tiaokuan12).

当函数返回一个对象时也会产生临时对象. 例如

```cpp
const Number operator+(const Number &lhs, const Number &rhs);
//该返回值是一个临时对象，调用opeartor+时，就要付出此对象的构造和析构成本
```
但编译器可能会对此产生优化，见[返回值优化](#tiaokuan20). 

<span id="tiaokuan20"></span>

## 20 协助完成 返回值优化(RVO)

```cpp
const Ratinal operator*(const Ratinal &lhs, const Ratinal &rhs)
{
	return Ratinal(lhs.n*rhs.n, lhs.d*rhs.d);
}
```

注意在 [effective cpp 读书笔记](effective-cpp-notes.html)中讲了必须返回对象时，别妄想返回其 reference。

```cpp
Rational a = 10;
Rational b(1, 2);
Rational c = a * b;
```
c++允许编译器将临时对象优化掉，即上述return 定义的对象构造于c的内存内。是否会优化由编译器所做决定。RVO= Return Value Optimization. 

## 21 利用重载技术(overload)避免隐式类型转换(implicit type conversions)

```cpp
const UPInt operator+(const UPInt &lhs, const UPInt &rhs);
....
UPInt int1, int2;
...
UPInt int3 = int1 + int2;

int3 = int1 + 10; //comment1
int3 = 10 + int1; //comment1
```
上述代码中comment1能够通过如果UPInt有一个含int的构造函数，这是编译器执行了隐式转换，中间有临时对象产生和析构。 如果要避免临时对象的话，可以重载如下函数

```cpp
const UPInt operator+(int lhs, const UPInt &rhs);
const UPInt operator+(const UPInt &lhs, int rhs);
const UPInt operator+(int lhs, int rhs);//WRONG
```
第3个是错误的，因为C++规定每个重载操作符必须至少获得一个用户自定义类型的自变量，上面的int不是。(如果是的话，岂不是1+2被重载后还不等于3了?).

## 22 考虑以操作符符合形式(op=)取代其独身形式(op)

比如

```cpp
class Rational{
...
Ratinal & operator +=(const Rational &rhs);
...
}

const Rational operator+(const Rational &lhs, const Rational &rhs)
{
	return Rational(lhs) += rhs;
	/**
	返回值优化, 上面的代码被优化的可能性比下面的代码高，具体优化由编译器实现。 --> 匿名对象总比命名对象更容易优化(临时对象消除)
	Rational result(lhs);
	return result += rhs;
	*/
}


Rational a,b,c,d,result;
result = a + b + c + d; // 可能用到3个临时对象, 每一个对应于一次operator+的调用
//or 
result = a;
result += b; // 可能直接被优化，没有临时对象产生
result += c;
result += d;
```

操作符的复合版本比其对应的独身版本有着更高效率的倾向，程序库的设计者应该两者都提供，软件开发者考虑用复合版本操作符替换独身版本。

## 23 考虑用其他的程序库

例如

如果一个程序有一个IO瓶颈，可以考虑以stdio取代iostream(类型安全)，如果程序花费在动态内存分配和释放方面，可以看看是否有其他operator new 和 operator delete的程序库。不同程序在效率、扩充性、移植性、类型安全性等的不同设计具体化，可以找找是否存在另一个功能相似的程序库在效率上有较高的设计权重。

## 24 了解 virtual functions，multiple inheritance、virtual base classes， runtime type identification的成本

拥有虚函数的类都需要vtbl的空间，大小视虚函数个数(包括继承下来的)而定。含有虚函数的对象内部都含有一个vptr。

指针/引用调用虚函数时, 首先根据对象的vptr知道vtbl，通过vtbl找出被调用的函数指针，然后调用。调用虚函数的成本真正运行时成本发生在和inlining互动的时候，inline意味着编译期，将调用端的调用动作被调用的函数本体所替换，而virtual意味着直到运行时才知道哪个函数被调用，所以虚函数事实上放弃了inline。

多重继承，虚基类可能引起更多vptr，详情后面有机会再讨论。[TODO];

RTTI 相关信息 根据class的vtbl来实现，例如在class的vtbl内增加一个条目，加上每个class所需的一份type\_info对象空间。只有当某类型拥有至少一个虚函数时才保证能够检验该类型对象的动态类型。 静态的在编译期间就可以决定了。

## 25 将 constructor 和 non-member functions 虚化


例如 从IO读取对象信息derived object 放到 用base class 的容器如list 存放，还例如 base class 声明了 clone方法返回base class的指针的纯虚函数，derived class 重写方法返回derived class 指针。

non-member functions 虚化 如

```cpp
inline ostream & operator << (ostream &s, const Base &base)
{
	return base.print(s);
}
```
然后 derived class 都重写base 声明的 print 方法。

## 26 限制某个class所能产生的对象数量

0的话private constructor, 1的话可以单例，任意的话可以这样：

```cpp
template <typename T>
class Counted
{
public:
	class TooManyObjects {}; // 抛出异常
	static int objectCount() {return numObjects;}
protected:
	Counted();
	Counted(const Counted& rhs);

	~Counted() {--numObjects;}
private:
	static int numObjects;
	static const size_t maxObjects;

	void Init();
};

template <typename T>
Counted<T>::Counted()
{
	Init();
}

template <typename T>
Counted<T>::Counted(const Counted& rhs)
{
	Init();
}
template <typename T>
void Counted<T>::Init()
{
	if(numObjects>=maxObjects)
		throw TooManyObjects();
	++numObjects;
};

template <typename T>  
int Counted<T>::numObjects=0;  //初始化为0
```
具体要对某个类(Derived)进行统计限制时，可以private继承下Counted<Derived>类(public的话，Counted得弄成vitural析构，防止有人通过父类指针删除子类对象时出错), 然后将Counted中的objectCount, 和 TooManyObject公开(using 声明)，且须设置/定义具体最大允许的数量, ```const size_t Counted<Derived>::maxObjects=10```， 不然会link错误。


## 27 要求或禁止对象产生于heap中

#### 要求对象产生于heap之中

- 析构设置为private～只能new出对象，delete封装一个public方法供手动调用，这样栈上产生对象，后面被隐式调用析构就不合法了。

- 也可以将constructor设置为private，但constructor要设置多个比如default，copy constructor都得设置private。

#### 判断某个对象是否位于heap内

```cpp
bool onHeap(const void * addr)
{
	char onTheStack;
	return addr < & onTheStack;
}
//一种可能可行的思路
```

【一般】所有系统的程序地址空间stack处于高地址，是向下增长，heap在低地址，向上增长，onTheStack 栈上的，如果 addr 比onTheStack小(更低)的话，就是堆上的地址。 但这只能针对stack、heap中的对象，还有一类static对象(包括global/namespcace scope)，无法区分，例如如果static对象在更低地址，就无法区分heap和static对象了。

较好的做法是，每次new记录到list，delete从list删除，判断时就将地址是否存在list中。封装一个抽象类，让具体要判断的对象继承此，重写operator new。 详情见 P154。

#### 禁止对象产生于heap中

对象可能有3中情况：(1) 对象直接被实例化 (2) 对象被实例化为 derived class objects中的base class成分 (3) 对象被内嵌于其他对象之中。

对于(1), 即不希望通过 "new Object" 产生对象，可以在Object类中将 operator new 设置为 private. 这样外面就调用不到了。但这会妨碍new一个derived object，new derived object时会new base，失败(2)。对于(3)是OK的。

## 28 smart pointers (智能指针)

设计一个smart pointers时要注意以下几个问题，

1. smart pointers 的构造、赋值、析构， stl的auto\_ptr 在赋值和复制时，对象拥有权会发生转移，所以 auto\_ptrs不能以by value的方式传递(STL 容器中不能放置auto\_ptr).

	```cpp
	template<class T>
	auto_ptr<T>::auto_ptr(auto_ptr<T> & rhs)
	{
		pointee = rhs.pointee; //rhs的原始指针控制权转移到this
		rhs.pointee = 0; // rhs的指针要设置为 NULL
	}
	template<class T>
	auto_ptr<T>& auto_ptr<T>::operator=(auto_ptr<T> & rhs)
	{
		if(this == &rhs)
			return *this;
		delete pointee;
		pointee = rhs.pointee;
		rhs.pointee = 0;
		return *this;
	}
	``` 
2. 实现 Dereferencing Operators: 
	
	```cpp
	template<class T>
	T& SmartPtr<T>::operator*() const
	{
		//perform "smart pointer" processing
		return *pointee;
	}
	template<class T>
	T* SmartPtr<T>::operator->() const
	{
		//perform "smart pointer" processing
		return pointee;
	}
	//for example
	SmartPtr<Tuple> entry(*pt);
	pt->display();
	//编译器会解释为
	(pt.operator->())->display();
	```
3. 测试 smart pointer 是否为 NULL: 直接用
	
	```cpp
	if(smtPtr == NULL) //...
	if(smtPtr) //...
	if(!smtPtr) //... 
	//上面的方式都会失败, 可考虑写一个隐式类型转换的函数
	opeartor void* (); // 转化void* 指针直接与 NULL 判断
	//还有
	bool operator !(); // 当 smart ptr 是null，返回true
	```

4. 将 Smart pointers 转化为 Dumb pointers, 场景：

	```cpp
	void normalize(Tuple *pt);
	SmartPtr<Tuple> pt;
	//...
	normalize(pt); // error
	normalize(&*pt); // ok, 
	//新增如下转换操作符，就可以通过
	template<class T>
	SmartPtr
	{
		...
		operator T*()
		{
			return pointee;
		}
	};
	// 加上这个转换操作符后，上面的测试smart pointer 是否为NULL 也可以通过。
	```

5. Smart Pointers 和 与继承有关的 类型转换
	
	```cpp
	void display(const SmartPtr<Base> & tmp)
	{
		...
	}
	SmartPtr<Derived> t(new Derived);
	display(t); //error, 不符合常理，一般接受base的指针也可以接受derived. //添加一下转换操作符可以解决
	template<class T>
	class SmartPtr
	{
		...
		template<class newType>
		operator SmartPtr<newType>()
		{
			return SmartPtr<newType>(pointee);
		}
	}
	//这样，编译器就会生成这样的代码, 以供转换
	SmartPtr<Derievd>::opeartor SmartPtr<Base>()
	{
		return SmartPtr<Base>(pointee);
	}
	```
	
6. Smart Pointers 和 const: 普通指针和const有3种组合，SmartPtr也要实现这样的组合，可以这样做(类似非const转const OK，const转non-const不安全，如下继承关系设计满足这样的条件)：
	
	```cpp
	template <class T>
	class SmartPtrConst
	{
		...
		protected:
			union{
				const T* constPointee;
				T* pointee;
			};
	}
	
	template<class T>
	class SmartPtr: public SmartPtrConst<T>{
		... //无 data members
	}
	```

## 29 Reference counting 引用计数

场景：GC的简单实现形式，等值对象共享省内存，加快速度， 适用于 (1) 相对多数的对象共享相对少量的实例 (2) 对象实值产生或销毁的成本很高，或他们使用很多内存。

例如一个简单版本的string 如下

```cpp
class String
{
private:
	struct StringValue
	{
		char * data;
		int refCount;
		
		StringValue(const char* initValue):refCount(1)
		{
			data = new char[strlen(initValue)+1];
			strcpy(data, initValue);
		}
		~StringValue()
		{
			delete [] data;
		}
	}
	StringValue * value;
public:
	//constructor
	String(const char* initValue): value(new StringValue(initValue)
	{}
	//copy constructor
	String(const String &rhs): value(rhs.value)
	{
		++value->refCount;
	}
	//operator =
	String & operator=(const String &rhs)
	{
		if(value == rhs.value) //同[在 operator = 中处理自我赋值](effective-cpp-notes.html)
			return *this;
		if(--value->refCount == 0) //如果没有其他引用，销毁*this
			delete value;
		value = rhs.value; //*this 共享rhs的值
		++value->refCount; 
		return *this;
	}
	
	//destructor
	~String()
	{
		if(-- value->refCount == 0)
			delete value;
	}
}
```

上述一个简答版本的reference-counted 字符串，如果加上取下标[]操作符，就麻烦了。通过[]读是OK的，但通过[]写的话，只能修改当前的，不能改其他共享的那个值，所以得重新copy一份出来，这是**copy-on-write**策略。

通过[条款30](#tiaokuan30)的proxy可以区分```operator[]```的读写动作，或者加一个标记shareable(默认为true)，当调用过```operator[]```后，就不再共享，refCount变化的时候就先判断这个标记值，copy构造时，如果shareable为true则refCount++, 不然就重新new一份value，```opeartor[]```操作时，先```value->refCount--```,然后new一份新的value，将shareable设置为false.  详情实现(抽象了模版)可以参考书本.

<span id="tiaokuan30"></span>

## 30 Proxy classes

proxy classes 场景：多维数组，左/右值区分, 压抑隐式转换。缺点是proxy若扮演返回值角色将产生临时对象，构造析构成本。

例如， 如下 Array1D 就是一个proxy class.

```cpp
template <class T>
class Array2D
{
	public:
		class Array1D
		{
			public:
				T & operator[](int index);
				const T & operator[](int index) const;
		};
		
		Array1D operator[](int index);
		const Array1D operator[](int index) const;
		...
};

Array2D<float> data(10,20);
//...
cout << data[2][5]; //OK
```

区分左/右值的proxy: 思想是，左值延缓到调用```opeartor＝```时可知道。

```cpp
class String
{
public:
	class CharProxy
	{
		public:
			CharProxy(String &str, int index); //构造
			CharProxy& operator=(const CharProxy &rhs);//左值运用
			CharProxy& operator=(char c);
			
			operator char() const; //右值运用
		private:
			String &theString;
			int charIndex;
	};
	const CharProxy operator[](int index) const
	{
		return CharProxy(const_cast<String&>(*this), index);
	}
	CharProxy operator[](int index)
	{
		return CharProxy(*this, index);
	}
};

String s1, s2;
//...
cout << s2[x]; //右值
//返回CharProxy, 调用 operator<<, 隐式转换char(CharProxy内有)，编译器就自动调用了，于是右值运用

s1[2] = 'x'; // 左值
//返回CharProxy, 调用 opeartor＝, 就知道是CharProxy内的那个operator＝(char c) 了，下面的也一样
s1[2] = s2[1]; // 左值
```

## 31 让函数根据一个以上的对象类型来觉得如何虚化

要实现的功能如下:

```cpp
//父类 
class GameObject;
//子类
class SpaceShip: public GameObject;
class SpaceStation: public GameObject;
class Asteroid: public GameObject;
//实现功能类似 collsion(GameObject &obj1, GameObject &obj2);

//在父类声明纯虚函数
struct GameObject
{
    virtual void collide(GameObject &other) = 0 ; 
}
//每个子类重写时, 还是得根据other 的type 去 if else 判断进而调用
//相应的碰撞检测逻辑, 这样做难看且不易维护
```
更好的一种做法是，利用虚函数这样做：

```cpp
struct GameObject
{
    virtual void collide(GameObject &other) = 0 ; 
    virtual void collide(SpaceShip &other) = 0 ; 
    virtual void collide(SpaceStation &other) = 0 ; 
    virtual void collide(Asteroid &other) = 0 ; 
}
//要求每个子类都重写这些方法， 例如 SpaceShip 来说
void SpaceShip::collide(GameObject &other)
{
    other.collide(*this);
}
void SpaceShip::collide(SpaceShip &other)
{
    //processing spaceship v.s spaceship
}
//...
```
上面代码中other可以运行时多态，而*this
则是静态类型SpaceShip，运行时会根据other具体类型调用与SpaceShip的collide函数实现。

还有一种解决方案就是函数指针，每个具体的类根据另一个Base的多态类型找出提前准备好的map中存好的具体函数实现的地址，然后通过函数指针调用。
更详细的可以参看书。

## 32 在未来时态下发展程序

- 提供完整的classes, 即使某些部分目前用不到，当新的需求进来，不需要回头去修改那些classes.
- 设计好接口，有利于共同的操作行为，阻止共同的错误，让classes轻易地被正确运用。
- 尽量使代码一般化(泛化)，除非有不良的巨大后果。

## 33 将非尾端类(non-leaf)设计为抽象类

- 在具体类被当作基类使用(即当该类被复用reused时)，强迫导入一个新的抽象类，这样可以防止如```operator＝```时不好操作的问题。
- 可以用组合代替继承，如 希望继承某个程序库类，可以自己写一个含有希望继承的程序库类作为成员的新类，在新类中重新实现该程序库类的接口。

## 34 如何在同一个程序中结合C++和C

C++配合C与多个C编译器产生目标文件组合成C所考虑的问题在很多方面类似，如int、double之类的大小，参数传递、调用规则等，还有不同编译器产生的目标文件是否兼容。另外还有如下几个问题需要考虑

- 名称重整(Name Mangling): ```extern "c" ``` 意味着C linkage, 告诉编译器此函数按照C的方式，不要重整函数名（C++支持重载，会把名称重整）。 [详情见这里](https://app.yinxiang.com/l/AB2AYXsT0DNFP7eFU-Ozzn3B1XD1fhSx0rc)
- Statics 的初始化：尽量在C++中撰写main。 因为static class 对象、全局对象、namespace内的对象及文件scope内的对象其constructors总是在main函数前就执行（static initialization），通过 static initilization出来的对象需要在main函数之后destruction。例如现在要在C++中调用之前C的main，可以直接在c++中用main调用C的main(改个名字)，编译器会在调用前后自动加上(可能是inline)上述的两个过程。
- 动态内存分配：new/delete, malloc/free 配对。
- 数据结构的兼容性：例如C++中含有虚的函数的struct是不能和C兼容的。

## 35 让自己习惯于标准的C++语言

标准程序库能力可区分为：支持C标准函数库、支持strings、支持国际化、支持IO、数值应用、容器和algorithms。
