import falcon
import json
import os

from git.repo import Repo

class TestResource(object):
    def on_get(self, req, res):

        repoPath = './IntallPlist'  #本地仓库路径
        result = 'success' #默认返回success
        msg = []
        repo = None

# 判断本地是否有仓库
        if os.path.exists(repoPath):
            repo = Repo(repoPath)
            msg.append('已有仓库')
        else:
            repo = Repo.clone_from(url='git@github.com:hillyoung/TestPlist.git', to_path=repoPath)
            msg.append('不存在仓库')
        git = repo.git
        git.checkout('*')
        remote = repo.remote()
        remote.pull()
        msg.append('完成拉取远程仓库代码')
# 判断是否传入了文件名
        name = req.params.get('name', None)
        if name is None :
            msg.append('传入无效参数')
            result = 'fail'
        else:
            msg.append('传入应用名：' + name)

            # 构造plist文件内容及相关控制逻辑
            directoryPath = repoPath + '/' + name
            if os.path.exists(directoryPath) != True:
                os.mkdir(directoryPath)

            filePath = directoryPath + '/install.plist'#plist文件相对路径
            rContent = None#用于缓存仓库中plist文件的内容
            flag = 'w'#文件的打开访问，默认以写入方式打开
            if os.path.exists(filePath):#判断仓库中是否存在plist文件
                flag = 'r+'#如果plist文件存在，则以读写的方式打开
                msg.append('存在plist文件')
            content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>items</key><array><dict><key>assets</key><array><dict><key>kind</key><string>software-package</string><key>url</key><string>https://raw.githubusercontent.com/hillyoung/AppInstaller/master/app/' + name + '/LiemsMobileEnterprise.ipa</string></dict></array><key>metadata</key><dict><key>bundle-identifier</key>		<string>net.luculent.liems.hhgs</string><key>bundle-version</key><string>1.0.1</string><key>kind</key><string>software</string><key>title</key><string>测试安装</string></dict></dict></array></dict></plist>'
            with open(filePath, flag) as flie_object:#写入plist
                if flag == 'r+':
                    rContent = flie_object.read()
                    flie_object.seek(0)
                    msg.append(rContent)
                if rContent != content:#写入plist内容
                    flie_object.write(content)
                    flie_object.close()
                    #提交plist文件
                    git.add('*')
                    git.commit('-m', '添加' + name)
                    remote.push()

        res.body = json.dumps({'result':result, 'msg':msg})
        res.status = falcon.HTTP_200 # This is the default status
        res.append_header('Access-Control-Allow-Origin','*')


class TestAPI(object):
    def on_get(self, req, res):
        res.append_header('Access-Control-Allow-Origin','*')
        # res.headers = {'Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'OPTIONS,HEAD,GET,POST','Access-Control-Allow-Headers':'x-requested-with, content-type, authorization'}
        # res.headers[] = 
        # res.headers[] = 
        # res.headers[] = 
        res.body = json.dumps({'test':'success'})
        res.status = falcon.HTTP_200 # This is the default status
app = falcon.API()

test_resource = TestResource()

app.add_route('/updatePlist', test_resource)
app.add_route('/testAPI', TestAPI())