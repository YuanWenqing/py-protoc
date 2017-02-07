# py-protoc
protobuf的python版本简单编译器，可编译输出ios、android、typescript使用的model，以及对应的sql语句模板、message包含的字段名常量类（java版）

## 前言
受师兄tuqc的影响，从2015年5月开始接触和使用protobuf进行项目开发。

连续几个项目开发的过程中，逐步理解和越来越认同tuqc的一个观点：逻辑设计开始于数据结构的定义，并且数据结构定义应当规范和一致。
tuqc曾在Google工作过，且protobuf有配套的grpc协议，所以我们使用protobuf作为数据定义的规范化方案。

通过使用protobuf来统一定义前后端的数据结构，可以帮助前后端对api交互逻辑的认知理解保持一致。并且，在遵循一定约定的情况下，protobuf还可以帮助进行数据结构与sql之间的映射<sup>1</sup>。

_备注：_
 1. 我不是很推荐使用ibatis等orm框架：一方面protobuf在这方面没有成熟框架；另外在大的业务线里sql语句多，管理起来比较麻烦。
 1. 仅支持对protobuf的语法做部分错误检查，因为在使用py-protoc之前，我们会先使用原生protoc为java后端编译，从而保证在py-protoc中语法没有问题。

## 支持
在我们的项目中，我们需要为java后端、ios、android、web提供统一的数据结构定义。
java后端返回的数据结构使用json序列化，ios、android、web使用统一编译产生的model类对获得的json数据进行反序列化。

protobuf本身的编译器protoc可以提供java后端需要的java类，而对于ios、android和web，protoc提供的方案过于复杂，也不适合我们的需求，所以我用python实现了一个简单的编译器，来编译输出符合我们需求的简单model类。

### 语言约定
 * ios：使用YYModel进行json反序列化。
 * web：我们使用typescript来保证js端数据结构的约束，所以生成的js model面向的也是typescript。
 * db：在java server端我们自己实现的orm框架中，我们需要处理java类的字段和db表的列之间的对应关系，为了保证数据结构的字段修改在逻辑中及时体现，编译器会额外输出每个类的字段名常量定义（即Example中的各种Naming类），从而保证代码逻辑中不必手写字段名的字符串常量。

## 参考
 * 最初用于我们项目的编译器是通过文本匹配和正则等方式进行“手工”解析的，在迁移到这个单独项目时，我参考了[proto_parser](https://github.com/LiuRoy/proto_parser)项目，改为使用ply进行相关的词法、语法解析。

