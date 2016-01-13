#Cookies
The cookie file is on a per user bases so that will have to be done client side.
To play the videos just send an html file with a script that does set_cookie() and allow all cookies in your browser.

``` html
<html>
<head>

    <script type="text/javascript">
        set_cookie(".funimation.com={'/': {'__cfduid': Cookie(version=0, name='__cfduid', value='d804a06fa672dd52dfd8d566dc232e7e71452607170', port=None, port_specified=False, domain='.funimation.com', domain_specified=True, domain_initial_dot=True, path='/', path_specified=True, secure=False, expires=1484143170, discard=False, comment=None, comment_url=None, rest={'HttpOnly': 'None'}, rfc2109=False)}}");
    </script>

    <script type="text/javascript">
        set_cookie("www.funimation.com={'/': {'bb_lastvisit': Cookie(version=0, name='bb_lastvisit', value='1452607170', port=None, port_specified=False, domain='www.funimation.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1484143172, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False), 'bb_lastactivity': Cookie(version=0, name='bb_lastactivity', value='0', port=None, port_specified=False, domain='www.funimation.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1484143172, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False), 'ci_session': Cookie(version=0, name='ci_session', value='a%3A6%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%226190c50333d08cff84f7267a91004d4e%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22108.162.219.186%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A8%3A%22Sony-PS3%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1452607170%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A6%3A%22userid%22%3Bs%3A7%3A%221306064%22%3B%7D87dfee2f842330dedbcf905e1c49d9ab', port=None, port_specified=False, domain='www.funimation.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1515679172, discard=False, comment='scj643|FunimationSubscriptionUser', comment_url=None, rest={}, rfc2109=False)}}");
    </script>

</head>
</html>
```
