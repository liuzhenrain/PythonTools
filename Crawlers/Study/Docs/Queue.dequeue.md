本文转载于: http://xiaorui.cc/2014/11/02/python%E4%BD%BF%E7%94%A8deque%E5%AE%9E%E7%8E%B0%E9%AB%98%E6%80%A7%E8%83%BD%E5%8F%8C%E7%AB%AF%E9%98%9F%E5%88%97/ 感谢作者的分享

双端队列（deque）是一种支持向两端高效地插入数据、支持随机访问的容器。

其内部实现原理如下：

双端队列的数据被表示为一个分段数组，容器中的元素分段存放在一个个大小固定的数组中，此外容器还需要维护一个存放这些数组首地址的索引数组 ，简单的理解，你可以想成一个大的array，分拆成几段，然后主要维护一个索引表。 大家看了下面的图应该就理解了。

![如果看不到图片请访问原文地址](pics/deque/1.png '区块事例')

deque的语法很是简单，一看就懂，只是rorate乍一看搞不明白。
![如果看不到图片请访问原文地址](pics/deque/2.png '区块事例')
deque有些不错的方法，用起来挺实用的，最少对我来说，是有用的。

\[指定大小，像queue\]

    from collections import deque
    dq=deque(maxlen=5)
    for i in range(1,100):
    dq.append(i)
    dq
    打印结果:deque([95, 96, 97, 98, 99], maxlen=5)
    
\[可以快速的做数据切割\]

    import collections
    d = collections.deque(xrange(10))
    print 'Normal        :', d
    打印结果:Normal        : deque([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    
    d = collections.deque(xrange(10))
    d.rotate(2)
    print 'Right rotation:', d
    打印结果:Right rotation: deque([8, 9, 0, 1, 2, 3, 4, 5, 6, 7])
    
    d = collections.deque(xrange(10))
    d.rotate(-2)
    print 'Left rotation :', d
    打印结果:Left rotation : deque([2, 3, 4, 5, 6, 7, 8, 9, 0, 1])

**记得以前做统计的时候，有个api做接受数据，然后存入队列里面。当时也没用redis,毕竟有网络io的效果，就用deque来搞的。 16个线程，一块做的调度，怕会出现数据安全的问题，经过测试。 在多线程下，deque双端队列是安全的，大家可以放心搞。**

    import collections
    import threading
    import time
     
    candle = collections.deque(xrange(11))
     
    def burn(direction, nextSource):
        while True:
            try:
                next = nextSource()
            except IndexError:
                break
            else:
                print '%8s: %s' % (direction, next)
                time.sleep(0.1)
        print '%8s done' % direction
        return
     
    left = threading.Thread(target=burn, args=('Left', candle.popleft))
    right = threading.Thread(target=burn, args=('Right', candle.pop))
     
    left.start()
    right.start()
     
    left.join()
    right.join()

下面是一个deque 、queue、list的性能对比，如果只是单纯的任务队列的话，又不太涉及对比，是否存在，remove的动作，那用deque再适合不过了。

    import time
    import Queue
    import collections
     
    q = collections.deque()
    t0 = time.clock()
    for i in xrange(1000000):
        q.append(1)
    for i in xrange(1000000):
        q.popleft()
    print 'deque', time.clock() - t0
     
    q = Queue.Queue(2000000)
    t0 = time.clock()
    for i in xrange(1000000):
        q.put(1)
    for i in xrange(1000000):
        q.get()
    print 'Queue', time.clock() - t0
     
    q = []
    t0 = time.clock()
    for i in xrange(1000000):
        q.append(i)
     
    for i in xrange(1000000):
        q.insert(0,i)
     
    print 'list ', time.clock() - t0

![如果看不到图片请访问原文地址](pics/deque/3.jpg '区块事例')

结果和我想的一样，deque很快，Queue也算可以，但是Queue只能做put，put的方向是不能指定的。list单纯的append算是不错的，但是如果你的应用有那种优先级的逻辑，那这样的话，你需要往前插入，用insert(0,item) 。 insert这个把item值插入到第0位，但是后面的那堆索引值，都要+1的。  这个负担可不小呀。 

Deque的缺点就是remove还有判断获取索引的时候，速度有些慢， 因为他需要执行多遍deque相关联的数据块 。不像list那样，搞一遍就行。

**如果你看到这篇文章,觉得也喜欢,请访问作者的网站,并请点击网页广告,帮助作者补充资金以继续维护主机写出更好的文章。**