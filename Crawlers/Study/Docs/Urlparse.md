本文转载于:http://blog.csdn.net/kittyboy0001/article/details/21552693 感谢作者的分享
# Web编程之 一 urlparse
    urldefrag(url)
    # 将url分解成去掉fragment的新url和去掉的fragment的二元组
    #return tuple(defragmented, fragment) 
    
    urljoin(base, newurl, allow_fragments=True)
    # 将url的基部件base，和newurl拼合成一个完整URL
    
    urlparse(url, schema='', allow_fragments=True)
    # 将url分解成部件的6元组
    # url     <schema>://<net_loc>/<path>;<params>?<query>#<fragment>
    # return  (schema, net_loc, path, params, query, fragment)
    
    urlsplit(url, schema='', allow_fragments=True)
    # 将url分解成部件的5元组
    # url     <schema>://<net_loc>/<path>?<query>#<fragment>
    # return  (schema, net_loc, path, query, fragment)
    
    urlunparse((schema, net_loc, path, params, query, fragment))
    # 将urltuple 6元组反解析成一个URL字符串
    
    urlunsplit((schema, net_loc, path, query, fragment))
    # 将urltuple 5元组反解析成一个URL字符串
    # return url
    

## 1.统一资源定位符
简单Web应用使用URL（统一资源定位器，Uniform Resource Locator）作为web地址。一个URL是简单的URI（统一资源标识，Uniform Resource Identifier）的一部分。 
URL使用如下的格式:

    schema://net_loc/path;params?query#fragment
其中，
    
    schema    网络协议或者下载规划
    net_loc   服务器位置（可能存在用户信息）
    path      斜杠（/）限定文件或者CGI应用程序的路径
    params    可选参数
    query     连接符（&）连接键值对
    fragment  拆分文档中的特殊锚

net_log 可以进一步拆分成多个部件，格式如下：

    user:passwd@host:port
    
其中，

    user    登录名
    passwd  用户的密码
    host    web服务器运行的机器名或地址
    port    端口号

### 1.1 urlparse
    urlparse.urlparse(urlstr, scheme='', allow_fragments=True)
函数urlparse()的作用是将URL分解成不同的组成部分，它从urlstr中取得URL，并返回元组 (scheme, netloc, path, params, query, fragment)。

如果urlstr中没有提供默认的网络协议或者下载规划时，可以使用default_scheme. 
allowFrag标识一个URL是否允许使用零部件。

### 1.2 urlunparse
    urlparse.urlunparse((schema, net_loc, path, params, query, fragment))
    urlparse.urlunparse(urltuple)

功能与urlparse相反:它拼合一个6元组(schema, net_loc, path, params, query, fragment)，

    urlunparse(urlparse(url)) === url
### 1.3 urlsplit
在urlparse中调用了urlsplit先生成(schema, net_loc, path#params, query, fragment)的5元组，然后再判断schema 如果合法，则拆分出path和params。否则设置params为空。

    def urlparse(url, scheme='', allow_fragments=True):
        tuple = urlsplit(url, scheme, allow_fragments)
        scheme, netloc, path, query, fragment = tuple
        if scheme in uses_params and ';' in path:
            path, params = _splitparams(path)
        else:
            params = ''
        return ParseResult(scheme, netloc, path, params, query, fragment)
urlparse和urlsplit的区别

    >>> from urlparse import urlparse,urlsplit
    
    >>> url='ftp://usr:passwd@yx-testing.vm:8100/path;params?query#fragment'
    >>> print urlsplit(url)
    SplitResult(scheme='ftp', netloc='usr:passwd@yx-testing.vm:8100', path='/
    path;params?query', 
    query='', fragment='fragment')
    
    >>> print urlparse(url)
    ParseResult(scheme='ftp', netloc='usr:passwd@yx-testing.vm:8100', path='/
     path', params='params?
    query', query='', fragment='fragment')
### 1.4 urlunsplit
    urlunsplit((schema, net_loc, path, query, fragment))
在urlunparse中调用了urlunsplit

    def urlunparse(data):
        scheme, netloc, url, params, query, fragment = data
        if params:
            url = "%s;%s" % (url, params)
        return urlunsplit((scheme, netloc, url, query, fragment))
### 1.5 urldefrag

返回元组(newurl, fragment), 其中newurl是片段的url部分, fragment是包含片段部分的字符串(如果有)。 
如果url中没有任何片段, 则newurl与url相同, fragment为空字符串。

    def urldefrag(url):
        """Removes any existing fragment from URL. """
        if '#' in url:
            s, n, p, a, q, frag = urlparse(url)
            defrag = urlunparse((s, n, p, a, q, ''))
            return defrag, frag
        else:
            return url, ''
### 1.6 urljoin
    urljoin(base, newurl, allow_fragments=True)   
将url的基部件base，和newurl拼合成一个完整URL

1.  如果base和newurl某一个为空，则返回另一个 
2.  如果newurl设置的为绝对路径，'/a/b.html',则将base的net_loc与newurl拼接 
3.  如果如果newurl中包含'..'，则将前面的一层路径去掉。
<pre>
    >>> from urlparse import urljoin
    >>> base='http://www.test.html/a/b/c.html'
    >>> newurl='../new.htm'
    >>> urljoin(base,newurl)
    'http://www.test.html/a/new.htm'
    
    >>> newurl='/new.htm'
    >>> urljoin(base,newurl)
    'http://www.test.html/new.htm'
    
    >>> newurl='../../x/new.htm'
    >>> urljoin(base,newurl)
    'http://www.test.html/x/new.htm'
</pre>