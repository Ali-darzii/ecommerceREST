from utils.throttling import BaseThrottle


# parse_rate -> (<allowed number of requests>, <period of time in seconds>)
class OTPPostThrottle(BaseThrottle):
    scope = 'phone_login_post'

    def parse_rate(self, rate):
        return (5, 120)


class OTPPutThrottle(BaseThrottle):
    scope = 'phone_login_put'

    def parse_rate(self, rate):
        return (10, 60)


class SetPasswordThrottle(BaseThrottle):
    scope = 'set_password'

    def parse_rate(self, rate):
        return (5, 60)


class LoginThrottle(BaseThrottle):
    # phone or email
    scope = 'login'

    def parse_rate(self, rate):
        return (10, 60)
