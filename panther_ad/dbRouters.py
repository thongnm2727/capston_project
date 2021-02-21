from panther_ad.models import Impression


class MyDBRouter(object):

    def db_for_read(self, model, **hints):
        if model == Impression:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model == Impression:
            return 'default'
        return None
