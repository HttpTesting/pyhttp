import hashlib
import time
import uuid
import datetime
from random import randint

"""
User-defined extension function import
"""
try:
    from httptesting.case.extfunc import Extend
except ImportError:
    Extend = object


class FUNC(Extend):
    """
    Framework function library.

    Usage:
        from httptesting.library.func import FUNC

        %{FUNC.md5(txt)}%
        %{FUNC.timestamp()}%
    """

    @staticmethod
    def md5(txt=''):
        """
        The md5 string is generated.

        Args:
            txt: The string to generate md5.
        Usage:
            ret = md5(txt)
        Return:
            ret: The md5 string is generated.
        """
        mo = hashlib.md5()
        src = txt.encode(encoding='utf-8')
        mo.update(src)

        return mo.hexdigest()

    @staticmethod
    def timestamp():
        """
        The timestamp
        """
        return int(time.time())

    @staticmethod
    def datetimestr():
        """
        Generate date-time strings.

        Args:

        Return:
            String  2019-07-16 10:50:16
        """
        datetime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        return datetime

    @staticmethod
    def uuid1():
        """
        Generate uuid1.

        Usage:
            ret = FUNC.uuid1()
        Return:
            String uuid1  example: ad7678fe-a775-11e9-907f-88b111064583
        """

        return str(uuid.uuid1()).replace('-', '')

    @staticmethod
    def mstimestamp():
        """
        Millisecond time stamp.  20 bit
        """
        time.sleep(0.3)
        ret = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        return ret

    @staticmethod
    def sleep_time(ses):
        """
        Main thread sleep time.

        Args:
            ses: seconds; Support decimals such as 0.5 or 0.8.
            1, 1 seconds, 0.5, 500 milliseconds.

        Usage:
            import time
            sleep_time(0.5) #500 milliseconds.

        Returns:
            There is no return.
        """
        try:
            ses = int(ses)
        except (ValueError, TypeError):
            ses = float(ses)
        time.sleep(ses)

    @staticmethod
    def rnd_list(lt):
        """
        To pick a random value from a list.

        Args:
            lt: A list of str.

        Usage:
            from random import randint
            value = rnd_list(['a','b','c'])

        Return:
            [] Returns a list of values.
        """
        lt = eval(lt)
        len_list = len(lt) - 1
        rint = randint(0, len_list)
        return lt[rint]

    @staticmethod
    def demo(a, b):
        return a + b
        
if __name__ == "__main__":
    a = FUNC.uuid1()
    print(a)
