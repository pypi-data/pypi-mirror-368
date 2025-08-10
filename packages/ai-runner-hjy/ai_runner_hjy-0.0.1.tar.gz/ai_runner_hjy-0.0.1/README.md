# 项目初始化

## 环境变量
cp env_example/basic.env.example basic.env
cp env_example/mysql.env.example mysql.env
cp env_example/oss.env.example oss.env
cp env_example/ai.env.example ai.env

## 安装依赖（清华源）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

## 运行测试
pytest
