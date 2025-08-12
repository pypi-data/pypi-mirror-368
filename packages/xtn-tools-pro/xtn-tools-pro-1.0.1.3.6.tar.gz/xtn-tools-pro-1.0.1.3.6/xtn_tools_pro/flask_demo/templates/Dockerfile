# 使用自定义的python-environment:1.0作为基础镜像
FROM python:3.8

# 设置工作目录
WORKDIR /app

# 复制应用代码到容器中
COPY . /app

# 安装应用所需的依赖
RUN pip install -r requirements.txt

# 启动应用
CMD ["uwsgi", "--ini","uwsgi.ini"]
#CMD ["python", "{{ project_name }}.py"]
