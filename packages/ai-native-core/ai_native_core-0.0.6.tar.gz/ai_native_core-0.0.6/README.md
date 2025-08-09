# 打包方式

## 1.先安装打包工具

```shell
pip install setuptools wheel twine
```

## 2.在项目根目录下执行打包

```shell
python setup.py sdist bdist_wheel
```

## 3.上传到正式Pypi源

```shell
twine upload dist/*
```

## 4.成功后即可在其他项目通过

```shell
pip install ai-native-core
```

## 5.如果需要把包安装到现有的环境中

```shell
pip install .
```