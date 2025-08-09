import re

def check_hbdk_version():
    import hbdk
    minimal_hbdk_version = '3.49.5'
    post = hbdk.__version__.find('post')
    if post == -1:
        hbdk_version = hbdk.__version__
    else:
        hbdk_version = hbdk.__version__[0:post-1]
    v1 = re.split('\.', hbdk_version)
    v2 = re.split('\.', minimal_hbdk_version)
    v1 = [int(v) for v in v1]
    v2 = [int(v) for v in v2]

    if v1 < v2:
        raise ValueError("The current HBDK version is {}, "
                         "and the minimum required HBDK version is {}.".format(hbdk.__version__, minimal_hbdk_version))
    return hbdk.__version__
