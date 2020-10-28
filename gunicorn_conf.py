# 并行工作进程数
workers = 4
# 监听内网端口5000
bind = '127.0.0.1:5000'
# 设置访问日志和错误信息日志路径
accesslog = '/www/wwwroot/SoraPage/gunicorn_acess.log'
errorlog = '/www/wwwroot/SoraPage/gunicorn_error.log'
# 设置日志记录水平
loglevel = 'warning'
