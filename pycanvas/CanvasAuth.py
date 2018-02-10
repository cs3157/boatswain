import requests

class CanvasSession():
    DEFAULT_HOSTNAME = 'https://courseworks2.columbia.edu'

    def __init__(self, headers=None, hostname=None):
        self._session = requests.Session()
        if headers is not None:
            self._session.headers = headers

        if hostname is None:
            hostname = self.DEFAULT_HOSTNAME
        self._url_fmt = hostname + '{uri}'


    @property
    def headers(self):
        return self._session.headers

    @headers.setter
    def headers(self, headers):
        self._session.headers = headers


    @property
    def url_fmt(self):
        return self._url_fmt
    
    @url_fmt.setter
    def url_fmt(self, fmt):
        self._url_fmt = fmt
        

    def _fmt(self, uri):
        return self.url_fmt.format(uri=uri)


    def _get(self, uri, *args, **kwargs):
        url = self._fmt(uri)
        return self._session.get(url, *args, **kwargs)

    def _get_iter(self, uri, *args, **kwargs):
        cur = self._fmt(uri)
        while True:
            r = self._session.get(cur, *args, **kwargs)
            yield r
            if r.links['current']['url'] == r.links['last']['url']:
                break
            cur = r.links['next']['url']


    def get_obj(self, uri, *args, **kwargs):
        r = self._get(uri, *args, **kwargs)
        return r.json()

    def get_iter(self, uri, *args, **kwargs):
        for l in self._get_iter(uri, *args, **kwargs):
            for i in l.json():
                yield i

class CanvasAuth:
    INIT_TYPE_ERR_FMT = ('Cannot initialize with non-CanvasAuth, non-string '
                        + 'object: {}')

    def __init__(self, auth):
        if isinstance(auth, CanvasAuth):
            auth._spawn(self)
        elif isinstance(auth, str):
            self.token = auth
            self.session = CanvasSession({
                'Authorization': 'Bearer {}'.format(auth),
            })
        else:
            raise TypeError(self.INIT_TYPE_ERR_FMT.fmt(auth))

    def _spawn(self, other_auth):
        other_auth.token, other_auth.session = self.token, self.session
        return other_auth

    def updateToken(self, token):
        self.token = token
        self.session.headers['Authorization'] = 'Bearer {}'.format(token)

    def getToken(self):
        return self.token
