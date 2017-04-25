import json
import logging


log = logging.getLogger(__name__)


class TwitterMock(object):

    posts = []

    def __init__(self):
        pass

    def PostUpdate(self, *args, **kwargs):
        self.posts.append({
            "args": args,
            "kwargs": kwargs
        })
        log.info(json.dumps(self.posts[-1], sort_keys=True))
        return {'all': 'good'}

    def lastPost(self):
        return self.posts[-1]

    def reset(self):
        del self.posts[:]

    def __call__(self, *args, **kwargs):
        return self
