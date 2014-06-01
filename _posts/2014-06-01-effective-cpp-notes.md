---
layout: post
title: "Effective C++ 读书笔记"
description: "Effective C++ 读书笔记"
category: 读书笔记
tags: [读书笔记, c++]
---
{% include JB/setup %}


## 0 导读

- 构造函数explicit声明，防止发生隐式转换，故意让发送隐式转换除外。
- copy构造函数、copy assignment(赋值)操作符区别
  - copy: 相同类型的对象初始化自己，**发生了新的对象被构造出来**。
  - copy assignment 赋值：从另外一个对象中拷贝其值到自己。
  - 函数传参时，若pass by value则是调用copy构造函数。
  
例如

>	
	Widget w1; //default 构造函数
	Widget w2(w1); // copy 构造
	w1 = w2; // copy assignment 赋值运算
	Widget w3 = w1; // **copy构造，有新对象w3产生**
	
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

>
	const char * p; //const data, non-const pointer, same as char const * p
	char * const p; //const pointer, non-const data
	const char* const p;// const pointer, const data
	const Widget * pw = Widget const * pw; // const data,non-const pointer
	
- const 成员函数不可以更改对象内任何non-static成员变量，mutabl声明的成员变量除外。
- const 成员函数版本和non-const版本函数重载时(实现逻辑一样)，用non-const 函数 调用相应 const函数节省编码，即*运用const成员函数实现其non-const的孪生兄弟*. 不能反过来，反过来调用const 版本时，内部调用了non-const，就有可能修改了成员。

>
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
			//必须明确指出调用const operator[](强转自己为const A&),否则会自己调用自己死循环,返回结果再去除const限制
		}
	} 
	
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
- 析构函数不要吐出异常。如果一个析构函数调用的函数有可能抛出异常，在析构函数中要try，catch住，然后吞下他们(不传播出去)或结束程序。
- 如果客户需要对某个操作函数运行期间抛出的异常做出反应, 那么 class 应该提供一个普通函数(而非在析构函数中)执行该操作.

###09 绝不在构造和析构函数中调用virtual函数
- base class构造期间virtual函数**绝不会**下降到derived classes阶层。base class构造函数执行时，derived class成员变量尚未初始化(base class都还没构造完呢)。是调用的当前类的相应的函数。会被编译器解析(resolve to) base class. 
- 运行期间类型信息(runtime type infomation,如dynamic_cast, typeid)也会把对象视为base class类型。
- 注意跟Java/C# 之类的区别。[测试代码实例](https://gist.github.com/tl3shi/a48462793ee557263cd9)

###10 另 operator = 返回一个reference to *this
- 为了实现 连锁形式的赋值, 赋值操作符(类似 +=, -=, *=, /= 等操作符)应返回一个 reference to *this. 类似Java中布局常用的里面的setXX(...).setYY(...).setXXX...

### 11 在 operator = 中处理自我赋值
- 确保当对象自我赋值时operator＝有良好的行为，技术包括比较来源对象和目标对象地址、精心周到的语句顺序，以及copy-and-swap技术。
- 确保任何函数如果操作一个以上的对象，其中多个对象是同一个独享时行外仍然正确。

>	
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
上述代码当比如 w1, w2 之前都指向同一个对象(别名/指针等)。调用w1=w2时，就会挂掉。因此在delete之前可以加上 
>
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
	
### 12 复制对象时勿忘其每个成分
- copying 函数(copy 构造,copy assignment)应该确保复制对象内的所有成员变量以及所有 base class 成分(调用基类的 copying 函数). 在为 class 添加一个成员变量后, 必须同时修改所有的构造函数 和 copying 函数. 确保(1)复制所有local变量，(2)调用所有base class内适当的copying函数。
- 不要尝试以某个 copying 函数实现另外一个 copying 函数, 应该将共同机能放进第三个函数(init之类)中, 并由两个 copying 函数共同调用.

-----

## 3 资源管理
### 13 以对象管理资源
- 资源获得时机便是初始化时机(Resource Acquisition Is Initialization; RAII).
- 两个常被使用的 RAII class 是 shared_ptr 和 auto_ptr. auto_ptr的复制动作会是它(被复制的对象)指向 NULL. 受auto_ptr管理的资源必须绝对没有一个以上的auto_ptr同时指向它。 share_ptr是RCSP(reference-counting smart pointer),智能指针无法解决循环引用问题。

>
	std::auto_ptr<A> p(..);
	std::auto_ptr<A> p2(p); // p被设为null,p2指向原来p指向的对象
	p = p2; // p2设置为null，p又指向最初是的对象	
	
- auto_ptr / shared_ptr 在其析构函数内做的是delete，非delete[], 所以不能用auto_ptr<std::string> xx(new std::string[10]);

### 14 在资源管理类中小心 copying 行为
- 复制 RAII 对象必须一并复制它所管理的资源, 资源的 copying 行为决定 RAII 对象的 copying 行为.
- 普遍常见的RAII class copying 行为是：抑制copying(extends Uncopyable)、引用计数法等。
- std::share_ptr<Resource, func>可以指定当Resource引用技术为0时的行为(删除器deleter)func，auto_ptr总是执行delete指针。

### 15 在资源管理类中提供对原始资源的访问

- APIs 往往要求访问原始资源(raw resources), 所以每一个 RAII class 应该提供一个取得其所管理资源的方法. 如share_ptr\<A\> a 当某个函数参数是A*时，不能直接传a，而通过a.get()可得到原始指针。
- 对原始资源的访问可能经由显式转换或隐式转换. 其中显式转换比较安全, 隐式转换对客户比较方便。隐式转换 operator B() const 将当前类转换成B。隐式转换有时候会带来问题，例如 vec3 * vec3, double * vec3， 可能试图想调用 vec3 * double（功能跟double * vec3差不多，但vec3 * double却没被声明定义）而这是又有一个从double 到vec3的转换函数，可能最后调用的就是vec3 * vec3的结果，而非期望的double*vec3 或者vec3 * double.

### 16 成对使用 new 和 delete 时要采用相同的形式
 
- new delete, new [] delete[] 成对使用，编译器会根据是否含有[]去解析数组个长度，进而决定调用多少次相应类型的析构函数。
- 尽量不要对数组形式做 typedef 动作, 因为在使用 new 表达式时有很大概率不能正确使用 delete. 通过使用 string, vector 等 template 可将对数组的需求降至几乎为0.

### 17 以独立语句将 newed 对象置入智能指针
- 以独立语句将newed的对象存储于智能指针内，不然若有异常抛出，可能有难以察觉的资源泄漏。
例如

>
	int privority();
	void processWidget(shared_ptr<Widget> pw, int privority);
	//调用时
	processWidget(shared_ptr<Widget>(new Widget()), priority());
	//可能的调用顺序(不同编译器传参压栈顺序可能不一致)
	1、执行new Widget() 
	2、调用 privority();
	3、构造shared_ptr;
	若在执行2时，有异常，则newed的widget不能正确释放，导致内存泄漏。改成这样就OK:
	shared_ptr<Widget> pw(new Widget());
	processWidget(pw, priority());

----

## 4 设计与声明
### 18 让接口容易被正确使用, 不容易被误用
- 好的接口很容易被正确使用, 不容易被误用. 
- "促进正确使用"的办法包括接口的一致性, 以及与内置类型的行为兼容.
- "阻止误用"的方法包括建立新类型(传递年月日的例子)、限制类型上的操作(a*b=c的例子,operator * 返回const，防止==/=混淆), 束缚对象值, 以及消除客户的资源管理责任.
- shared_ptr 支持定制删除器(custom deleter), 这可防范 DLL 问题, 可被用来自动解除互斥锁(mutex)等.

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
- 尽量以 pass-by-reference-to-const 替换 pass-by-value, 前者通常比较高效, 并可避免切割问题(slicing ,参数为base class,传递是为derived class以by value的形式传递).
- 以上规则并不适用于内置类型, 以及 STL 的迭代器和函数对象, 对它们来说, pass-by-value 往往比较适当.

### 21 必须返回对象时，别妄想返回其 reference
绝不要返回 pointer 或 reference 指向一个 local stack 对象, 或返回 reference 指向一个 heap-allocated 对象 或 返回 pointer 或 reference 指向一个 local static 对象而有可能需要多个这样的对象.  

	struct Ratinal
	{
		int n, d; //分子 denorminator,分母 numerator
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
	(a * b) == (c * d) 表达式永远为true,因为 等效于
	if (opeartor == (operator*(a, b), operator *(a, b))) 
	在调用opeator == 时, 有两个operator* 发生调用，的确两次调用都各自改变了static Rational的值，但由于返回的是reference, 在调用端看来永远都是static Rational对象的“现值”。
	
### 22 将成员变量声明为 private

- 切记将成员变量声明为 private, 这可赋予客户访问数据的一致性, 可细微划分访问控制, 允诺约束条件获得保证, 并提供 class 作者以充分的实现弹性.
- protected 并不比 public 更具有封装性.

### 23 宁以 non-member non-friend 替换 member 函数
- 宁可拿non-member non-friend 替换 member 函数, 这样可增加封装性, 包裹弹性(packaging flexibility)和机能扩充性。
- friends 函数对class private成员的访问权利和memeber函数相同，二者对封装的冲击力道也相同；封装角度看，抉择的关键不在memeber 和 non-member，而是memeber和non-member non-friend函数之间。
- namespace 和class 不同，前者可跨越多个源代码文件而后者不能。

### 24 若所有参数都需类型转换，请为此提供 non-member 函数
如果需要为某个函数所有参数(包括被 this 指针所指的那个隐喻参数)进行类型转换, 那么这个函数必须是个 non-member. 

>
	class Rational
	{
	public:
		Rational(int n, int d); // 构造函数可以不为explicit, 允许 int to Rational的隐式转换
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
	但当将operator* 移除Rational外，写成一个non-member函数时
	const Rational operator *(const Rational& lhs, const Rational &rhs)
	{
		return .....;
	}
	这样的语句也能通过 
	result = 2 * oneHalf;
	
### 25 考虑写出一个不抛异常的 swap 函数

如果std::swap缺省实现的效率不足(意味着你的class或template使用了某种pimpl:pointer to implementation)时，可以这样做：

1. 提供一个public swap成员函数，让它高效置换你的两个类型的对象值，*不能抛出异常*。
2. 在你的class 或 template所在命名空间提供一个 non-member的swap函数，并令它调用上述swap成员函数。
3. 若你正编写一个class(非class template)，为你的class 提供特化的std::swap，并另它调用swap的成员函数。
4. 如果你调用swap，确定包含using 声明式，让std::swap在你的函数内曝光，最后不加namespace 修饰，赤裸调用swap。(std::swap(a,b)这样不会调用到你实现的特化版本，直接swap的话，若找到特化版本就直接调用，没找到才用std::swap)

>
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
		；
		template<typename T>
		void swap(Widget<T> &a, Widget<T> &b)
		{
			a.swap(b);
		}
	}
	若是在写一个function template，则这样：
	template<typename T>
	void doSomething(T& obj1, T& obj2)
	{
		using std::swap;
		...
		swap(obj1, obj2);
		...
	}
	using 声明让std::swap曝光，编译器若找到std::swap的T专属特化版，则调用，没找到则std::默认的一般化的那个。
	
	
	