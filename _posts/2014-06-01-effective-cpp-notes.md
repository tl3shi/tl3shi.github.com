---
layout: post
title: "Effective C++ 读书笔记"
description: "Effective C++ 读书笔记"
category: reading notes 
tags: [读书笔记, c++]
---
{% include JB/setup %}


## 0 导读

- 构造函数explicit声明，防止发生隐式转换，故意让发生隐式转换除外。
- copy构造函数、copy assignment(赋值)操作符区别
  - copy: 相同类型的对象初始化自己，**发生了新的对象被构造出来**。
  - copy assignment 赋值：从另外一个对象中拷贝其值到自己。
  - 函数传参时，若pass by value则是调用copy构造函数。
  
例如

```	cpp
Widget w1; //default 构造函数
Widget w2(w1); // copy 构造
w1 = w2; // copy assignment 赋值运算
Widget w3 = w1; // **copy构造，有新对象w3产生**
//注意这个跟类成员初始化列表的区别，初始化列表是copy构造函数；而在类构造函数里面通过＝赋值，是先调用了default构造函数，然后才copy assignment的。
```

##1  让自己习惯C++

###01 视C++为一个语言联邦 

对内置(C-like)类型在函数传参时pass by value比pass by reference更高效，当用OO的c++自定义类型(存在构造/析构等)pass by reference to const 更好，STL里的迭代器和函数对象是用C指针实现的，因此pass by value更好。

###02 尽量以const,enum,inline替换#define

- **宁可用编译器替换预处理器**，预处理器进行宏替换,如#define PI 3.1415 若错误发生时，可能错误信息提到的是3.1415，而非PI,加到debug难度。
- class专属static const 的整数类型(int char bool)可以声明时给初值定义(in class初值设定)
- enum hack 可完成in class初值设定
- \#include必需, \#ifdef/\#ifndef 仍扮演控制编译的重要角色.

###03 尽可能使用const

- const指针时注意区分含义，const出现在\*左边，被指物是常量，出现在\*右边,表示指针是常量. 

```cpp
const char * p; //const data, non-const pointer, same as 
char const * p
char * const p; //const pointer, non-const data
const char* const p;// const pointer, const data
const Widget * pw = Widget const * pw; // const data,non-const pointer
```
	
- const 成员函数不可以更改对象内任何non-static成员变量，mutable 声明的成员变量除外。
- const 成员函数版本和non-const版本函数重载时(实现逻辑一样)，用non-const 函数 调用相应 const函数节省编码，即*运用const成员函数实现其non-const的孪生兄弟*. 不能反过来，反过来调用const 版本时，内部调用了non-const，就有可能修改了成员。

```cpp
class A
{
	...
public:
	const char & operator[](size_t pos) const 
	{
	}
	char & operator[](size_t pos)
	{
		return const_cast<char&>(static_cast<const A &>(*this)[pos]);
		//*this 加上const，再调用const op[]
		//必须【明确】指出调用const operator[](强转自己为const A&),否则会自己调用自己死循环,返回结果再去除const限制
	}
} 
```
	
### 04 确定对象使用前已被初始化

- 类成员初始化通过在构造函数定义用:初始化列表形式给出，在进入构造函数函数体之前已被初始化。初始化列表的形式比在构造函数体内通过赋值(=)更高效，**赋值时会先调用default构造函数，然后再进行赋值(copy assignment)**，而初始化列表直接调用copy构造函数。[测试代码](https://gist.github.com/tl3shi/36b70a11d6cfb7727e67)
- 成员初始化顺序：base class, derived class, 成员变量按照其**声明**次序(非初始列表顺序)。

-----


## 2 构造/析构/赋值运算

### 05 了解C++默默编写并调用哪些函数

- **需要**(代码中有调用)时，编译器才会生成如下函数：default构造、析构函数(非vitual除非其base class含有vitual 析构)、copy构造、copy assignment操作符，public的。
- 当自定义构造函数时，编译器将不自动生成。
- 编译器生成的copy构造，内部简单地调用每个non-static成员的copy构造，对内置类型，会copy每个bits来构造初始化。
- 类含有*reference成员或const成员*时，编译器不自动生成copy assignment ， base class 的copy assignment为private时，也不自动生成。

### 06 若不想使用编译器自动生成的函数，就应该明确拒绝

- 例如不想让别人调用copy构造或者copy assignment，将二者手动设置为private，其他类就调用不了了。*BUT*member 函数和 friend函数还是可以调用，可以只private声明，不定义函数体，这时member或者friend调用时就得到link error。*成员函数声明为private并且故意不实现*
- 写一个super class，将其copy/ copy assignment设置为private，可以将上述link error提前到编译期间。任何试图调用copy/copy assignment时，编译器生成版本将试图调用其super class对应函数，而super class中是private，因此编译不通过。如boost中的noncopyable.

### 07 为多态基类声明 virtual 析构

- polymorphic (带多态性质的)base classes应该声明一个virtual 析构函数；如果class带有任何virtual 函数，应该拥有一个virtual析构函数。
- classes设计目的如果不是作为base class使用，或不是为了多态条件时，不应该声明virtual 析构函数。产生指向虚表(函数指针的数组)的指针增加类空间大小。

### 08 别让异常逃离析构函数

- 析构函数不要吐出异常。如果一个析构函数调用的函数有可能抛出异常，在析构函数中要try，catch住，然后吞下他们(不传播出去)或结束程序。(**因为抛出异常后，控制权离开析构函数，可能发生资源泄漏，另外若连续有两个异常的话，程序默认会直接终止或不明确的行为。**)
- 如果客户需要对某个操作函数运行期间抛出的异常做出反应, 那么 class 应该提供一个普通函数(而非在析构函数中)执行该操作.

###09 绝不在构造和析构函数中调用virtual函数

- base class构造期间virtual函数**绝不会**下降到derived classes阶层。base class构造函数执行时，derived class成员变量尚未初始化(base class都还没构造完呢)，是调用的当前类的相应的函数，会被编译器解析(resolve to) base class. 
- 运行期间类型信息(runtime type infomation,如dynamic_cast, typeid)也会把对象视为base class类型。
- 析构函数也一样。
- 注意跟Java/C# 之类的区别。[测试代码实例](https://gist.github.com/tl3shi/a48462793ee557263cd9)

###10 另 operator = 返回一个reference to *this

- 为了实现 连锁形式的赋值, 赋值操作符(类似 +=, -=, *=, /= 等操作符)应返回一个 reference to *this. 类似Java中布局常用的里面的setXX(...).setYY(...).setXXX...

### 11 在 operator = 中处理自我赋值

- 确保当对象自我赋值时operator＝有良好的行为，技术包括比较来源对象和目标对象地址、精心周到的语句顺序，以及copy-and-swap技术。
- 确保任何函数如果操作一个以上的对象，其中多个对象是同一个对象时行外仍然正确。

```cpp	
class Widget
{
	...
	private:
		Bitmap* pb;//指向heap中分配得到的对象
}
Widget & Widget::operator=(const Widget &rhs)
{
	delete pb; //!! 当rhs 和 this是同一个对象时，就挂了。
	pb = new Bitmap(*rhs.pb);//非异常安全，若此处发生异常，widget会持有一个指向被删除的bitmap
	return *this;
}
```
上述代码当比如 w1, w2 之前都指向同一个对象(别名/指针等)。调用w1=w2时，就会挂掉。因此在delete之前可以加上 

```cpp
if (this == &rhs) return *this; //导入新的control flow, prefetching、caching、pipelining等指令效率会降低
//或者也可以
Wdiget & Widget::operator=(const Widget & rhs)
{
	Bitmap * pOrig = pb; 
	pb = new Bitmap(*rhs.pb);
	delte pOrig;
	return *this
}
//copy and swap
Wdiget & Widget::operator=(const Widget & rhs)
{
	Widget temp(rhs);
	swap(*this, temp);// 交换*this 和 temp的数据
	return *this
}	
```
	
### 12 复制对象时勿忘其每个成分

- copying 函数(copy 构造,copy assignment)应该确保复制对象内的所有成员变量以及所有 **base class** 成分(调用基类的 copying 函数). 在为 class 添加一个成员变量后, 必须同时修改所有的构造函数 和 copying 函数. 确保(1)复制所有local变量，(2)调用所有base class内适当的copying函数。
- 不要尝试以某个 copying 函数实现另外一个 copying 函数(copy assignment 调用 copy构造意思是试图构造已经存在的对象, copy调用copy assignment 一样不合理 因为copy构造新对象，assignment是实施于以初始化的对象), 应该将共同机能放进第三个函数(init之类)中, 并由两个 copying 函数共同调用.

-----

## 3 资源管理

### 13 以对象管理资源

- 资源获得时机便是初始化时机(Resource Acquisition Is Initialization; RAII).
- 两个常被使用的 RAII class 是 shared\_ptr 和 auto\_ptr. auto\_ptr的复制动作会是它(被复制的对象)指向 NULL. 受auto\_ptr管理的资源必须绝对没有一个以上的auto\_ptr同时指向它。 share\_ptr是RCSP(reference-counting smart pointer), 智能指针无法解决循环引用问题。

```cpp
	std::auto_ptr<A> p(..);
	std::auto_ptr<A> p2(p); // p被设为null,p2指向原来p指向的对象
	p = p2; // p2设置为null，p又指向最初是的对象
```	
	
- auto\_ptr / shared\_ptr 在其析构函数内做的是```delete```，非```delete[]```, 所以不能用 ```auto_ptr<std::string> xx(new std::string[10]);```

### 14 在资源管理类中小心 copying 行为

- 复制 RAII 对象必须一并复制它所管理的资源, 资源的 copying 行为决定 RAII 对象的 copying 行为.
- 普遍常见的RAII class copying 行为是：抑制copying(extends Uncopyable)、引用计数法等。
- std::share\_ptr<Resource, func>可以指定当Resource引用技术为0时的行为(删除器deleter)func，auto\_ptr总是执行delete指针。

### 15 在资源管理类中提供对原始资源的访问

- APIs 往往要求访问原始资源(raw resources), 所以每一个 RAII class 应该提供一个取得其所管理资源的方法. 如share_ptr\<A\> a 当某个函数参数是A*时，不能直接传a，而通过a.get()可得到原始指针。
- 对原始资源的访问可能经由显式转换或隐式转换. 其中显式转换比较安全, 隐式转换对客户比较方便。隐式转换 operator B() const 将当前类转换成B。隐式转换有时候会带来问题，例如 vec3 * vec3, double * vec3， 可能试图想调用 vec3 * double（功能跟double * vec3差不多，但vec3 * double却没被声明定义）而这是又有一个从double 到vec3的转换函数，可能最后调用的就是vec3 * vec3的结果，而非期望的double*vec3 或者vec3 * double.

### 16 成对使用 new 和 delete 时要采用相同的形式
 
- new delete, new [] delete[] 成对使用，编译器会根据是否含有[]去解析数组个长度，进而决定调用多少次相应类型的析构函数。 (对于内置类型的话，不需要记录调用多少次析构函数，有的编译器可能就不多花费4个字节来记录长度，因此用new数组，直接delete应该也没问题。但记住自己别这么写代码就行。详情可以参考下这里[C++ 中的 new/delete 和 new[]/delete[]](https://app.yinxiang.com/shard/s29/sh/8a97eba8-9238-4679-8279-b186a8d060c0/a2de9eaa4d5fa2958aa748f1a117e13d))
- 尽量不要对数组形式做 typedef 动作, 因为在使用 new 表达式时有很大概率不能正确使用 delete. 通过使用 string, vector 等 template 可将对数组的需求降至几乎为0.

### 17 以独立语句将 newed 对象置入智能指针

- 以**独立语句**将newed的对象存储于智能指针内，不然若有异常抛出，可能有难以察觉的资源泄漏。
例如

```cpp
int privority();
void processWidget(shared_ptr<Widget> pw, int privority);
//调用时
processWidget(shared_ptr<Widget>(new Widget()), priority());
/*
可能的调用顺序(不同编译器对参数核算的顺序可能不一致)
1、执行new Widget() 
2、调用 privority();
3、构造shared_ptr;
若在执行2时，有异常，则newed的widget不能正确释放，导致内存泄漏。改成这样就OK:
*/
shared_ptr<Widget> pw(new Widget());
processWidget(pw, priority());
```
----

## 4 设计与声明

### 18 让接口容易被正确使用, 不容易被误用

- 好的接口很容易被正确使用, 不容易被误用. 
- "促进正确使用"的办法包括接口的一致性, 以及与内置类型的行为兼容.
- "阻止误用"的方法包括建立新类型(传递年月日的例子)、限制类型上的操作(a*b=c的例子,operator * 返回const，防止==/=混淆), 束缚对象值, 以及消除客户的资源管理责任.
- shared\_ptr 支持定制删除器(custom deleter), 这可防范 cross-DLL(一个dll new，另一个delete，shared\_ptr的delete是来自new的那个dll中的)问题, 可被用来自动解除互斥锁(mutex)等.

### 19 设计 class 犹如设计 type

class 的设计就是 type 的设计, 在定义一个新 type 之前, 请考虑以下几个问题:

- 新 type 的对象应该如何被创建和销毁? 
- 对象的初始化和对象的赋值该有什么样的差别? 
- 新的type的对象若被pass by value 意味着什么?
- 新的type的合法值?
- 新type需要配合某个继承图系(inheritance graph)吗? 
- 新 type 需要什么样的转换? T2 T1::operator() 或者  T1(const T2 &t) non-explicit-one-argument? 
- 什么样的操作符和函数对此新 type 而言是合理的?
- 什么样的标准函数应该被驳回? private 构造、copy assignment 等.
- 谁该取用新 type 的成员? 访问控制，public protected?...
- 什么是新 type 的 未声明接口(undeclared interface)? 
- 新 type 有多么一般化? 是否考虑 class template.

### 20 宁以 pass-by-reference-to-const 替换 pass-by-value

- 尽量以 pass-by-reference-to-const 替换 pass-by-value, 前者通常比较高效, 并可避免切割问题(slicing, 参数为base class,传递是为derived class以by value的形式传递).
- 以上规则并不适用于内置类型, 以及 STL 的迭代器和函数对象, 对它们来说, pass-by-value 往往比较适当. 详情见[C++ 传参时传内置类型时用传值(pass by value)方式效率较高](http://www.tanglei.name/pass-by-value-when-using-c-like-parameter-is-better-than-pass-by-referene/)

### 21 必须返回对象时，别妄想返回其 reference

绝不要返回 pointer 或 reference 指向一个 local stack 对象, 或返回 reference 指向一个 heap-allocated 对象 或 返回 pointer 或 reference 指向一个 local static 对象而有可能需要多个这样的对象.  

```cpp
struct Ratinal
{
	int n, d; //分子 denorminator, 分母 numerator
	...
}
const Rational & operator(const Rational &a, const Rational &b)
{
	Rational result(a.n*b.n, a.d*b.d);
	return result;
	//以上代码 在stack上 构造一个Rantional, 函数返回前 会被析构掉，没有copy～ 
	//或者这样, 但有由谁来delete?
	Rational * result = new Ratinoal(a.n*b.n, a.d*b.d);
	return *result;
	//当这样的调用代码
	Rational w, x, y, z;
	w = x * y * z;
	// 两次调用operator* ,new 了 2个，中间那个怎么delete?
}
//又或者
const Rational & operator(const Rational &a, const Rational &b)
{
	static Rational result;
	result = ...;
	return result;
}
//上面问题先不考虑static关于线程安全的问题，但就是这样的调用
Rational a, b, c, d;
if ((a * b) == (c * d))
{}
else
{}
/*
(a * b) == (c * d) 表达式永远为true,因为 等效于
if (opeartor == (operator*(a, b), operator *(a, b))) 
在调用opeator == 时, 有两个operator* 发生调用，的确两次调用都各自改变了static Rational的值，但由于返回的是reference, 在调用端看来永远都是static Rational对象的“现值”。
*/
```
	
### 22 将成员变量声明为 private

- 切记将成员变量声明为 private, 这可赋予客户访问数据的一致性, 可细微划分访问控制, 允诺约束条件获得保证, 并提供 class 作者以充分的实现弹性.
- protected 并不比 public 更具有封装性.

### 23 宁以 non-member non-friend 替换 member 函数

- 宁可拿non-member non-friend 替换 member 函数, 这样可增加封装性, 包裹弹性(packaging flexibility)和机能扩充性。
- friends 函数对class private成员的访问权利和memeber函数相同，二者对封装的冲击力道也相同；封装角度看，抉择的关键不在memeber 和 non-member，而是memeber和non-member non-friend函数之间。
- namespace 和 class 不同，前者可跨越多个源代码文件而后者不能。

### 24 若所有参数都需类型转换，请为此提供 non-member 函数

如果需要为某个函数所有参数(包括被 this 指针所指的那个隐喻参数)进行类型转换, 那么这个函数必须是个 non-member. 

```cpp
class Rational
{
public:
	Rational(int n = 0, int d = 1); // 构造函数可以不为explicit, 允许 int to Rational的隐式转换
	int numberator() const;
	int denorminator() const;
	//member 函数
	const Rational operator *(const Rational &rhs) const;
private:
	...
}
//这样调用
Rational oneEighth(1, 8);
Rational oneHalf(1, 2);
Rational result = oneHalf * oneEight; //OK
result = result * oneHalf; // OK
result = oneHalf * 2; // OK oneHalf.operator*(2), 2被隐式转换成Rational,若构造函数声明为explict，该语句也Error.
result = 2 * oneHalf; // Error 2.opeator*(oneHalf), 2 没有对应相应的class，也找不到global里一个接受int 和 Rational作为参数的non-member operator* 的函数
//但当将operator* 移除Rational外，写成一个non-member函数时
const Rational operator *(const Rational& lhs, const Rational &rhs)
{
	return .....;
}
这样的语句也能通过 
result = 2 * oneHalf;
```
	
### 25 考虑写出一个不抛异常的 swap 函数

如果std::swap缺省实现的效率不足(意味着你的class或template使用了某种pimpl:pointer to implementation)时，可以这样做：

1. 提供一个public swap成员函数，让它高效置换你的两个类型的对象值，*不能抛出异常*。
2. 在你的class 或 template所在命名空间提供一个 non-member的swap函数，并令它调用上述swap成员函数。
3. 若你正编写一个class(非class template)，为你的class 提供特化的std::swap，并另它调用swap的成员函数。
4. 如果你调用swap，确定包含using 声明式，让std::swap在你的函数内曝光，最后不加namespace 修饰，赤裸调用swap。(std::swap(a,b)这样不会调用到你实现的特化版本，直接swap的话，若找到特化版本就直接调用，没找到才用std::swap)

```cpp
namespace WidgetStuff
{
	template<typename T>
	class Widget {
		public:
			void swap(Widget & other)
			{
				using std::swap;
				swap(pImpl, other.Impl);
			}
		private:
			WidgetImple* pImp;
	};
	template<typename T>
	void swap(Widget<T> &a, Widget<T> &b)
	{
		a.swap(b);
	}
}
//若是在写一个function template，则这样：
template<typename T>
void doSomething(T& obj1, T& obj2)
{
	using std::swap;
	...
	swap(obj1, obj2);
	...
}
	using 声明让std::swap曝光，编译器若找到std::swap的T专属特化版，则调用，没找到则std::默认的一般化的那个。
```
	
-----

## 5 实现

### 26 尽可能延后变量定义式出现的时间

尽可能延后变量定式的出现，这样可增加程序的清晰度并改善程序的效率。如之前定义了某个T，而中途因某些逻辑return/throw exception等，会造成这个T的构造和析构的开销。

### 27 尽量少做转型动作

- 旧式转型(old-style casts):
	- (T)expression // C 语言风格的转型动作: 将 expression 转型为 T
	- T(expression)	// 函数风格的转型动作: 将 expression 转型为 T
- C++ 提供的新式转型(new-style / C++-style casts):
	- const_cast<T>(expression)	 : 去除对象的常量性(cast away the constness).
	- dynamic_cast<T>(expression) :	 用来执行 安全向下转型(safe downcasting), 也就是用来决定某对象是否归属继承体系中的某个类型. 在转型时可能**耗费重大**的运行成本.
	- reinterpret_cast<T>(expression):	执行低级转型, 实际动作(及结果)可能取决于编译器.
	- static_cast<T>(expression) : 强迫隐式转换(implicit conversions), 如
      non-const 转型为 const, int 转型为 double, 将 point-to-base 转为
      point-to-derived, 或者上述多种转换的反向转换，但无法将const 转为 non-const.
- 单一对象(如Dereived对象)可能拥有一个以上的地址（如以Base\*指向它的地址和以Derived\*指向它的地址)，这对C，Java,C#都不可能，但C++可以。
- static_cast<Base>(*this).method(); 这句在Dereived class中写的。这样做是将this独享的base class成分建立一个副本，在副本的基础上调用method()。
- 如果可以，尽量避免转型，尤其注意dynamic_cast。
- 如果转型是必要的，试着将其隐藏某个函数背后，客户随后可以调用该函数，而不需要将转型放进他们自己的代码内。
- 宁可使用c++-style的转型，更容易识别出来，也分门别类的职掌。

### 28 避免返回handles指向对象内部成分

Reference、指针、迭代器都是所谓的handles，返回一个代表对象内部的数据的handle，可能导致虽然调用const成员函数却还是造成对象状态被更改。

```cpp
class GUIObject{...};
class Rectangle
{
public:
	const Point& upperLeft(){return ...};//return private ..
private:
...
}
const Rectangle boundingBox(const GUIObject &obj);//by value
//客户有可能这样使用
GUIObject *gui;
...
const Point * pUpperLeft = &(boundingBox(\*gui).upperLeft());
```

这样做的结果就是：对boundingBox(\*gui)的调用将得到一个Rectangle的匿名临时对象(假设为tmp),然后通过tmp调用uppperLeft得到一个指向tmp内部Point的reference，然后pUpperLeft指向那个Point对象。结果，语句执行完，tmp对象被销毁/析构,而pUpperLeft此时指向一个不存在的对象。

避免返回handles指向对象内部，遵守这个条约可增封装性，帮助const成员函数的行为像个const，并将发生dangling handles的可能性降低。

### 29 为 异常安全  而努力是值得的

- 异常安全函数(Exception-safe functions)即使异常也不会资源泄漏或数据结构破坏，提供三个保证之一：
	- 基本承诺：若异常被抛出，程序内任何事务仍保持有效状态。没有任何对象或数据结构会因此而被破坏，所有对象处于一种内部前后一致的状态。
	- 强烈保证：若异常被抛出，程序状态不改变，若函数调用成功就完全成功，若失败程序应该恢复到调用前的状态。
	- 不抛出(nothrow)保证：承诺不抛出异常，例如作用于内置类型(int等)身上的所有操作都提供nothrow保证。
- 强烈保证 往往能够以 copy-and-swap 实现出来，但并非所有函数都可实现或具备现实意义。copy-and-swap 关键: 修改对象数据的副本，然后在一个不抛出异常的操作中置换(swap)原对象和副本，若在修改动作中有异常抛出, 原对象仍保持未改变状态。
- 函数提供的异常安全保证通常只等于其所调用的各个函数异常安全保证中的最弱者。(木桶/短板原理)

### 30 透彻了解 inlining 的里里外外

- inline 函数背后的整体观念是将“对此函数的每一个调用”都以函数本地替换之，inline可能会造成代码膨胀导致额外换页行为，降低高速缓存装置的命中率。所有inline应该限制在小型被频繁调用的函数身上。若inline函数本体很小，编译器针对函数本体所产生的代码可能比针对函数调用的所产生的代码更小。
- inline只是对编译器的一个申请，不是强制命令，这项申请也可能是隐喻方式提出（例如
  class Person里一个age()方法return private的age, 在class的定义式内直接呈现出函数本体)
- **大多数**C++的inline是在编译期完成的，也可能在链接期，少量如基于.NET CLI(Common Language Infrastructure)的托管环境(managed environments)可在运行期inlining.
- 编译器不对通过函数指针进行的调用进行inline，例如

```cpp
inline void f(){...}
void (* pf)() = f;
...;
f(); //被 inlined
pf(); // 不被inlined，函数指针的方式
```	

- 大部分调试器对inline函数没办法，并不知道在一个并不存在的函数内设定断点。
- template的具体化与inline无关，不要只因为function template出现在头文件就将它们声明为inline
- inline 函数无法随程序库的升级而升级.若f是一个inline的函数，客户将f的本体编进其程序中，一旦f改变，那么用到的f的客户端程序都要重新编译，而若f是non-inline的，若修改了，只要重新链接就好，若是动态链接，升级版函数甚至悄无声息就被应用程序吸纳。

### 31 将文件的编译依存关系降至最低

- 编译器在编译期间必须要知道对象的大小(Java等中不存在)。
- 如果能够使用object reference 或 object pointers可以完成任务，就不要使用objects，可以只靠一个声明式就定义出指向该类型的reference或pointer，而如果定义某类型的object，就必须要用到该类型的定义式。
- 支持编译依存最小化的构想是：相依于声明式, 不要依赖于定义式. 基于此构想的两个手段是 Handle classes 和 Interface classes.
- 程序库头文件应该以完全且仅有声明式(full and declaration-only forms)的形式存在. 这种做法不论是否涉及到 templates 都适用.

----

## 6 继承与面向对象设计

### 32 确定你的public 继承塑模出 is-a 关系

public 继承意味着 is-a, 适用于base classes的每一件事情也一定适用于derived
class身上，因为每一个derived class对象也都是一个base class对象。（Liskov
Substitution Principle）

### 33 避免遮掩继承而来的名称

- derived class内的名称会遮掩base class的名称(名称，not 签名)。
- 为了让被遮掩的名称重见天日，可使用using 声明式或者转交(forwarding functios)。

```cpp
class Base
{
private:
   int x;
public:
   virtual void mf1() = 0;
   virtual void mf1(int);
   virtual void mf2();
   void mf3();
   void mf3(double);
   ...
};
class Derived: public Base
{
public:
   //using Base::mf1;
   //using Base::mf3;
   virtual void mf1();
   void mf3();
   void mf4();
   ...
};
Derived d;
int x;
d.mf1(); // OK
d.mf1(x); // Error, Derived::mf1() 遮盖了 base::mf1
d.mf2(); // OK
d.mf3(); // OK
d.mf3(1.4); // Error, Derived::mf3 遮盖了base::mf3
若用using 声明式(取消注释掉的两句代码)，则上面两个OK
//转交函数
若Derived以private集成Base，而Derived只想继承mf1那个无参数的版本，using声明式就不行了，可用forwarding function。
class Derived: private Base
{
public:
   virtual vid mf1()
   {
       Base::mf1(); //转交函数，暗自inline
   }
};
...
Derived d;
int x;
d.mf1(); // OK, Derived::mf1调用
d.mf1(x); //Error, Base::mf1()遮盖了
```

### 34 区分接口继承和实现继承

- Derived class override的Base class 的virtual方法是对象也可以显示调用Base
  class的方法，这样调用：derived->Base::func();
- 接口继承和实现继承不同. 在 public 继承下, derived classes 总是继承 base class 的接口.
- pure virtual 函数只具体指定接口继承, 纯虚函数也能提供自己的实现，调用时需要在子类中通过父类名显示调用。
- 简朴的(非纯) impure vitual 函数具体指定接口继承以及缺省实现继承.
- non-virtual 函数具体指定接口以及强制性的实现继承.

### 35  考虑 virtual 函数以外的其他选择

- 使用NVI(non-virtual-interface)手法，模版方法(Template  Method)设计模式的一种特殊形式，以public  non-virtual成员函数调用private/protected 的virtual函数。
- 将virtual 函数替换为"函数指针成员变量"，是Strategy
  设计模式的一种表现形式，也可以用std::tr1::function<> 封装成函数对象。
- 将继承体系内的virtual函数替换为另一个继承体系内的virtual函数，传统的Strategy设计模式实现手法。

### 36 绝不重新定义继承而来的non-virtual函数

绝不重新定义继承而来的non-virtual函数.

```cpp
class B
{
public:
   void mf();
   ...
};
class D : public B
{
public:
   void mf(); // hides B::mf, 名字隐藏
};
//客户端调用代码
D x;
B * pB = &x;
pB->mf(); // 调用 B::mf()
D * pD = &x;
pD->mf(); // 调用 D::mf()
//同一个对象，调用”同一个“方法得到不同的结果！
//non-virtual函数如B::mf(),
//D::mf()都是静态绑定，通过pB调用的non-virtual函数永远都是B定义的版本。（virtual函数是动态绑定）

```

### 37 绝不重新定义继承而来的缺省参数

如36所说，不要重新定义继承而来的non-virtual函数，这里继承一个带有缺省参数值的virtual函数也是错误的。
因为virtual函数是动态绑定的，缺省参数是静态绑定的，静态类型是被声明时的类型，动态类型是指目前所指对象的实际类型。

[详细案例介绍](http://www.tanglei.name/donot-redefine-default-para-from-super-class/)

### 38 通过复合塑模出has-a或根据某物实现出

(Model "has-a" or "is-implemented-in-terms-of" throught composition)

- 复合(composition)的意义和 public 继承完全不同
- 在应用域(application domain), 复合意味着 has-a(有一个). 在实现域(implementation domain), 复合意味着 is-implemented-in-terms-of(根据某物实现出). 

### 39 明智而谨慎地使用private继承

- Private继承以为着is-implemented-in-terms-of(根据某物实现出)，通常比复合的级别低，但是当derived
  class 需要访问protected base class (base
  class的public、protected继承下来都变成private的)
  的成员，或需要重新定义继承而来的virtual函数时，可能设计成private继承。尽可能用复合，必要时才使用private 继承。
- 和复合不同， private继承可以造成EBO(empty base
  optimization,空白基类最优化, empty base 可能含有static成员方法等)，这对致力于对象尺寸最小化的程序开发者而言可能很重要。[关于EBO资料整理](https://app.yinxiang.com/shard/s29/sh/79b16930-4d50-4d58-a275-7ce6b55b4431/d6f7d6473dfa243329fd4f079869d86f)

### 40 明智而谨慎地使用多重继承

- C++解析重载函数调用的规则：在看到是否有个函数可取用之前，首先确认这个函数对此调用而言是否是最佳匹配，找出最佳匹配后才检验其是否可访问(private等权限控制)。
- 多重继承比单一继承复杂，它可能会导致新的歧义性，以及对virtual继承的需要。
- virtual继承会增加大小，速度和初始化（及赋值）复杂度等等成本，[关于Virtual
  继承相关材料](http://www.phpcompiler.org/articles/virtualinheritance.html)
- 多重继承的确有正当用途，其中一个情节涉及“public继承某个Interface
  class”和“private继承某个协助实现的class”两两组合。

## 7 模板和泛型编程

### 41 了解隐式接口和编译器多态

- classes 和 templates 都支持接口(Interfaces)和多态(polymorphism).
- 对classes而言接口是显示的，以函数签名为中心，多态则通过virtual函数发生于运行期.
- 对template而言，接口是隐式的，奠基于有效表达式，多态则是通过template具现化和函数重载解析(function
  overloading resolution)发生于编译期。

### 42 了解typename的双重意义

- 声明template参数时，前缀关键字class和typename是一样的，可互换；
- 请使用关键字typename标识嵌套从属类型名称，但不得在base class
  lists（基类列，继承时列表）或memeber initialization
  list（成员初始值列）内以它作为base class修饰符。

### 43 学习处理模版化基类的名称

- template<>置于class定义式最前面标识这既不是template也不是标准class，而是个全特化版的class
  template。即普通template满足不了一般要求，需要提供另外一个替代以前的template，这样就可以让编译器选择模版时用此特化版的。
- base class template
  有可能被特化，而那个特化版本可能不提供和一般性template相同的接口，因此编译器往往拒绝在templatized
  base class内寻找来自基类base class 的某个方法名称。此时可以
    - 在derived class template内通过“this->”指涉base class
    template内的成员名称，假设其将继承下来。
    - using 声明式，告诉编译器让其进入base class作用域查找(跟名称遮掩不一样)
    - 显示加上base class前缀。
- 以上方法只是从可视角度出发，给编译器承诺base class
  template的任何特化版本都将支持一般泛化版本所提供的接口，但的确有这样一个特化版本的class
  template时，若没有定义某个接口，对此调用那个接口仍然会编译失败的。

### 44 将参数无关的代码抽离template

- template 生成多个 classes 和多个函数, 所以任何 template代码都不该与某个造成膨胀的 template 参数产生依存关系.
- 因非类型模板参数(non-type template parameters)而造成的代码膨胀(就是上面说的这种情况), 往往可以消除, 做法是以函数或
class 成员变量替换 template 参数.
- 因类型参数(type parameters)而造成的代码膨胀, 往往可降低, 做法是让带有完全相同的二进制表述(binary representation)的具现类型(instatiation
types)共享实现码. 

### 45 运用成员函数模版接受所有兼容类型

- 请使用 member function templates(成员函数模板)生成”可接收所有兼容类型”的函数.
- 如果你声明 member templates 用于”泛化 copy 构造” 或 “泛化 assignment 操作”, 你还是需要声明正常的 copy 构造函数和 copy assignment 操作符.

### 46 需要类型转换时请为模版定义非成员函数

- template实参推导过程中从不将隐式类型转换函数、构造函数而发生的隐式类型转换，纳入考虑范围。
- 当我们编写一个class
  template时，而它所提供的“与此template相关的”函数支持“所有参数之隐式类型转换”时，请考虑将那些函数定义为“class
  template内部的friend函数”。

### 47 请使用traits classes表现类型信息

- traits广泛应用于标准程序库，如iterator_traits,
  除了iterator_category，还有value_type, char_traits, numeric_limits等，使用一个traits class：
    - 建立一组重载函数或函数模版，彼此间的差异只在于各自的traits参数，令每个函数实现码与其接受之traints信息相应和。
    - 建立一个控制函数或函数模板，它调用上述那些重载函数并传递traits
      class提供的信息。
- Traits
  classes获得类型相关信息在编译期可用，它们以templates和templates特化来实现。
- 整合重载技术后，traits classes 有可能在编译期对类型进行if...else...测试。

### 48 认识template元编程

- template metaprogramming(TMP,
  模板元编程)可将工作由运行期迁往编译期，因而得以实现早起错误侦测和更高的执行效率。(编译时间肯定增长)
- TMP可被用来生成“基于政策选择组合”(based on combinations of policy
  choices)的客户定制代码，也可以用来避免生成对某些特殊类型并不合适的代码。
- 模板元编程阶乘示例

```cpp
#include <iostream>
using namespace std;
template <int T>
struct F
{
   enum{value = T * F<T-1>::value};
};
template<>
struct F<0>
{
   enum{value = 1};
};
int main()
{
   cout << F<5>::value << endl;
   return 0;
}
```

## 8 定制new和delete

STL 容器使用的heap内存是由容器所拥有的分配器对象（allocator
objects）管理，不是new和delete直接管理，该章不讨论STL分配器。

### 49 了解new-handler的行为

- new-handler是当operator new
  抛出异常以反映一个未满足内存需求之前首先调用的一个客户指定的处理函数。原型如下,
  throw()表示该函数不抛出任何异常。

```cpp
    namespace std
    {
        typedef void (*new_handler)();
        new_handler set_new_handler(new_handler p) throw();
        //返回马上要被替换掉的handler
    }
```

- 良好设计的new-handler函数应该做到：
    - 让更多内存可被使用：使得operator new内的下一次内存分配动作可能成功
    - 安装另一个new-handler,
      若目前的new-handler无法取得更多的内存，可尝试换一个
    - 卸除new-handler: 将null传给set_new_handler，卸载后operator
      new失败时会抛出异常
    - 抛出bad_alloc(或派生自bad_alloc)的异常, 这样的异常不会被operator new
      捕捉，因此会传播到内存所求处
    - 不返回，直接abort或exit。
- set_new_handler允许客户指定一个函数，在内存分配无法得到满足时被调用
- nothrow new
  是一个颇为局限的工具，因为它只适用于当次的内存分配，后继的构造函数调用可能还是会抛出异常。
- 可以采取某种机制让某个class专属的new_handler，只需在这个class提供自己的new_handler和operator
  new 即可。

### 50 了解new delete的合理替换时机

替换编译器提供的new/delete的原因常常有

- 用来检测运用上的错误，如自定义new超额分配内存，在额外空间放人byte
  patterns(签名signatrures)以检测内存是否完整出错。
- 强化效能，编译器提供的版本是针对任意需求的，可以自己定制一个满足特定需求的。如Boost的Pool库针对小型对象的分配器。
- 收集使用上的统计数据、弥补缺省分配器中的非最佳齐位(suboptimal alignment),
  相关对象成簇集等。

### 51 编写new、delete时需固守常规

```cpp
void * operator new(std::size_t size) throw(std::bad_allc)
{
   using namespace std;
   if(size == 0)
       size == 1;
   while(true)
   {
       尝试分配size bytes
       if(分配成功)
           return (指向分配得到的内存的指针)
       //分配失败
       new_handler global_handler = set_new_handler(0);//得到之前的handler
       set_new_handler(global_hander);
       if(global_handler) 
           (*global_handler)();//调用
       else
           throw std::bad_alloc();
   }
}
```
    
- operator new
  应该包含一个无穷循环，在其中尝试分配内存，无法满足内存分配需求则调用new-handler。且有能力处理0bytes的申请。class 专属版本的还应该处理“比正确大小更大的(错误)的内存申请”
- operator delete 应该在收到null指针时不做任何处理。class
  专属版本的应该处理“比正确大小更大的（错误）的内存申请”
- 针对class X而设计的operator
  new，其行为典型地只为大小刚好为sizeof(X)的对象而设计，如万一被继承，有可能base
  class的operator new被调用以分配derived
  class对象，即为以上说的比正确大小更大的错误的申请的一种情况。所以专属版本应该在判断size!=sizeof(class)时用默认的::operator
  new(size)进行处理(delete类似)。

### 52 写了placement new 也要写placement delete

- 当你写一个placement operator new，请确定也写了相应的placement operator
  delete，若没有，可能会存在内存泄漏
- 当声明placement new 和 placement
  delete，请确定不要无意识地掩盖了他们的正常版本(名字掩盖)
- 缺省下C++默认的在global域下提供的operator new:

```cpp
    void * operator new(std::size_t) throw(std::bad_alloc); //normal new
    void * operator new(std::size_t, void*) throw(); //placement new
    void * operator new(std::size_t, const std::nothrow_t&) throw(); //nothrow
    new
```

- Widget * pw = new Widget; new 成功了，而Widget默认的构造函数失败了，运行时系统会找到与new匹配的delete函数去delete，若没找到就啥也不做就泄漏内存了。

## 9 杂项讨论

### 53 不要忽视编译器的警告

- 严肃对待编译器发出的警告信息. 努力在你的编译器的最高(最严格)警告级别下争取
“无任何警告” 的荣誉.
- 不要过度依赖编译器的报警能力, 不同的编译器对待事情的态度并不相同，一旦移植到另一个编译器上, 你原本依赖的警告信息有可能消失.

### 54 55 TR1, Boost

- [TR1](http://en.wikipedia.org/wiki/C%2B%2B_Technical_Report_1)
- [C++11](http://zh.wikipedia.org/wiki/C%2B%2B11)
- [Ten C++11 Features Every C++ Developer Should Use](http://www.codeproject.com/Articles/570638/Ten-Cplusplus-Features-Every-Cplusplus-Developer)
