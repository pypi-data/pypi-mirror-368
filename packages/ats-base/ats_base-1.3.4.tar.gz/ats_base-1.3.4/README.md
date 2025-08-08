**1. 制作requirement.txt**

pip freeze > requirement.txt

**2. 打包**

pip install --upgrade pip twine wheel setuptools

python setup.py sdist bdist_wheel

twine upload dist/* 

使用twine upload --skip-existing dist/* 来忽略已经存在的库

**3. 安装更新插件**

pip install --upgrade tsdl

**4. 参数说明**

package_dir:
告诉Distutils哪些目录下的文件被映射到哪个源码包。一个例子：package_dir = {'': 'lib'}，表示“root package”中的模块都在lib目录中。