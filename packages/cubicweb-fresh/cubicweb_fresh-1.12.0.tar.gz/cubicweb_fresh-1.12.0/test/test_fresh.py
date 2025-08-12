"""template automatic tests"""

import unittest

from cubicweb.devtools.htmlparser import XMLValidator
from cubicweb_web.devtools.testlib import AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):
    vid_validators = AutomaticWebTest.vid_validators.copy()
    vid_validators.update(
        {
            "accexpense": XMLValidator,
            "accentry": XMLValidator,
        }
    )


if __name__ == "__main__":
    unittest.main()
