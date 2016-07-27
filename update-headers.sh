find . -name '*.py' -print0 | xargs -0 sed -i .bk 's/Copyright (c) 2014-2016/Copyright (c) 2014-2016/g'
find . -name '*.py.bk' -print0 | xargs -0 rm
