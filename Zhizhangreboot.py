# -*- coding: utf-8 -*-
# Author:Caesar
# 微信机器人
# 请特别注意：在运行前，检查环境是否有 json,pathlib,itchat包
# 如果没有，请使用pip install 安装相关包

from __future__ import unicode_literals
#from threading import Timer
#import wxpy as wx
#import requests
from pathlib import Path
import itchat, time
from itchat.content import *
import json
#import httplib
import requests


#图灵机器人的API Key
appkey = "f33***********************"
userId = "******"

#图灵机器人的URL地址
tulinurl = 'http://openapi.tuling123.com/openapi/api/v2'

#当前文件路径
currentPath = Path(__file__).parent

#当前配置文件路径
path = currentPath / 'WeChatQun.txt'

#过滤文件名的非法字符
fileSign = '\\ / : * ? " < > | \n \t'.split(' ')


#图灵机器人的请求消息体
request_message = '''{
	 "reqType":0,
    "perception": {
        "inputText": {
            "text": "{message}"
        },
        "inputImage": {
            "url": "imageUrl"
        },
        "selfInfo": {
            "location": {
                "city": "{city}",
                "province": "{province}",
                "street": "{street}"
            }
        }
    },
    "userInfo": {
        "apiKey": "{appkey}",
        "userId": "{userId}"
    }
}'''.replace('{appkey}',appkey).replace('{userId}',userId)



#获取机器人自动回复的方法
def RebotReply(strs,province,city,street):
   #headers = {"Content-Type":"application/json"}
   mes = request_message.replace("{province}",province).replace('{city}',city).replace('{street}',street).replace('{message}',strs)
   mes = json.JSONDecoder().decode(mes)
   response = requests.post(tulinurl,json=mes)
   result = json.JSONDecoder().decode(response.content.decode())
   #print(mes) 
   #print(result)
   return result['results'][0]['values']['text']+'【此消息由{0}机器人回复】'.format(rebotName)

#文件夹名非法字符过滤器
def SafeFileName(strs):
  temp = str(strs)
  for filesi in fileSign:
    temp = temp.replace(filesi,'')
  
  return temp.replace(' ','')


#创建指定目录的方法
def PathCreate(paths):
  path = Path(paths).parent
  if not path.exists():
    path.mkdir()

#去除@标记的文字
def removeAtSign(strs):
  strArray = strs.split(' ')
  result=''
  for item in strArray:
    if item.startswith('@'):
      continue
    result = result + item
  return result


@itchat.msg_register([MAP, CARD, NOTE,RECORDING,ATTACHMENT,FRIENDS])
def text_reply(msg):
    #msg.user.send('%s: %s' % (msg['type'], msg['text']))
    #msg.user.send('%s: %s' % (msg['type'], msg['text']))
    print('This is text_reply type:{0},context:{1}'.format(msg['MsgType'],msg['Content']))

def sendMessage(message,toUserName):
    itchat.send(message,toUserName=toUserName)

#测试方法体
@itchat.msg_register(SHARING)
def sharing_get(msg):
    #print('%s: %s' % (msg['type'], msg['text']))
    print('%s:%s',msg['FromUserName'],msg['Content'])
    name = itchat.search_friends(nickName='Atlantis')
    print(name)
    print(msg)
    if str(msg['Content']).find('带你飞早报')!=-1:
       msg['FromUserName'] = msg['ToUserName']
       msg['ToUserName'] = name[0]['UserName']
       #itchat.send(msg,toUserName=name[0]['UserName'])
       #itchat.
       #itchat.send_raw_msg(msgType='Sharing', content=msg['Content'].replace('<msg>','').replace('</msg>',''), toUserName=name[0]['UserName'])
       #itchat.send_msg(str(msg['Content']),toUserName=name['userName'])
       #itchat.send_msg()
       #itchat.send_file
	   
#处理私聊消息的方法体
@itchat.msg_register(TEXT)
def _(msg):
    #print('%s:%s',msg['FromUserName'],msg['Content'])
    #msg.user.send('%s: %s' % (msg['type'], msg['text']))
    fromUserName = msg['FromUserName']
    TMessage = msg['Content']
    
    #print(TMessage)
    #print(TMessage.startswith('@WESENDMESSAGE'))
    if TMessage.startswith('@WESENDMESSAGE'):
        #rooms = itchat.get_chatrooms()

        with open(path,'r',encoding='utf-8') as file:
           str_room = file.read()

        rooms = str_room.split('\n')
        #name = itchat.search_chatrooms(name='资产全球配置群')
        #wename = itchat.search_chatrooms()
        #print(name)
        #print(rooms)
        content = TMessage.replace('@WESENDMESSAGE', '').strip()+'\n 【此消息由{0}机器人发送】'.format(rebotName)
        #print(message)
        #print(rooms)
        messagelist = []
         
        for room in rooms:
            sp_room = room.split(':')
            username = sp_room[0].strip()
            nickname = sp_room[1].strip()
            
            #print('send to:'+name)
            if not username.startswith('#'):
                usernames = itchat.search_chatrooms(nickname)
                if len(usernames)!=0:
                  try:
                    itchat.send_msg(content,toUserName=usernames[0]['UserName'])
                    #itchat.send_msg(content,toUserName=username[''])
                    message = time.strftime('%Y-%m-%d %H:%M:%S')+'  '+nickname+'  已发送成功'
                    messagelist.append(message)
                  except Exception as ex:
                    message = time.strftime('%Y-%m-%d %H:%M:%S')+'  '+nickname+'  发送失败'
                    messagelist.append(message)
                    #print(message)
                else:
                  message = '找不到群:'+nickname
                  messagelist.append(message)
                  
        if len(messagelist)!=0:
           print('\n'.join(messagelist))
    else:
      #pass
      reply_Message = RebotReply(TMessage,'广东','深圳','红岭街道')
      itchat.send_msg(reply_Message,toUserName=fromUserName)
    
    #print(fromUserName+':'+content)\
    #print(msg)

#处理群聊消息的方法体
@itchat.msg_register([TEXT,MAP,PICTURE, CARD, NOTE,RECORDING,ATTACHMENT,VIDEO],isGroupChat=True)
def _getChartroom(msg):
    currentTime = time.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
      fromUserName = msg['FromUserName']
      sendUserName = msg['ActualNickName']
      content = msg['Content']
      messtype = msg['Type'].upper()
      isAt = msg['isAt']
      text = msg['Text']
      fileName = msg['FileName']
      #Url = msg['Url']
      current_chatroom = itchat.search_chatrooms(userName=fromUserName)
      
      
      qun_name = current_chatroom['NickName']
      
      if isAt:
        print(currentTime+' 群\"'+qun_name+'\" 的 【'+sendUserName +' 】对您说 : '+content)
        #re.match('(\@\w*)\s ')
        ask_message = removeAtSign(content)
        reply_Message = RebotReply(ask_message,'广东','深圳','红岭街道')
        itchat.send_msg(reply_Message,fromUserName)
      elif messtype == 'TEXT':
        print(currentTime+' 群\"'+qun_name+'\" 的 【'+sendUserName +'】说 : '+content)
      elif messtype == 'PICTURE':
        imgPath =str(currentPath)+'\\' + SafeFileName(sendUserName)+ '\\' + fileName
        PathCreate(imgPath)
        #print(str(imgPath))
        text(imgPath)
        print(currentTime+' 群\"'+qun_name+'\" 的 【'+sendUserName +'】发了一张图片 : '+str(imgPath))
      elif messtype == 'VIDEO':
        videoPath = str(currentPath)+'\\' + SafeFileName(sendUserName)+ '\\' + fileName
        PathCreate(videoPath)
        text(videoPath)
        print(currentTime+' 群\"'+qun_name+'\" 的 【'+sendUserName +'】发了一段视频 : '+str(videoPath))
      elif messtype == 'ATTACHMENT':
        filePath = str(currentPath)+'\\' + SafeFileName(sendUserName)+ '\\' + fileName
        PathCreate(filePath)
        text(filePath)
        print(currentTime+' 群\"'+qun_name+'\" 的 【'+sendUserName +'】发了一份文件 : '+str(filePath))
      elif messtype == 'RECORDING':
        voicePath = str(currentPath)+'\\' + SafeFileName(sendUserName)+ '\\' + fileName
        PathCreate(voicePath)
        text(voicePath)
        print(currentTime+' 群\"'+qun_name+'\" 的 【'+sendUserName +'】发了一段语音 : '+str(voicePath)) 
      elif messtype == 'NOTE':
        print(currentTime+' 群\"'+qun_name+'\" 的 【'+sendUserName +'】'+text)
      else:
        print(currentTime+' 群\"'+qun_name+'\" 的 【'+sendUserName +'】发送消息'+messtype+' : '+str(msg))
      
    except Exception as ex:
      print(ex)
    finally:
      pass 



#windows:
itchat.auto_login(True)
  
#Linux:
#itchat.auto_login(enableCmdQR=2,hotReload=True)
try:
    chatroom_list = itchat.get_chatrooms(update=True)
    users_list = itchat.get_friends(update=True)
        #itchat.update_chatroom
        #print(name)
    print('当前群数量：'+str(len(chatroom_list))+' 包括：')
    for name in chatroom_list:
       #print(name['UserName']+' : '+name['NickName'])
       print('【'+name['NickName']+'】 人数 :'+str(name['MemberCount']))
       #print(type(name['MemberList']))
       #if name['NickName']=='梁家河学习群':
        # print(name)
       
       
    print('当前好友数量：'+str(len(users_list)))
    print('正在接收消息')
    #isRun=False
    
    #current_chatroom = itchat.search_chatrooms(userName=chatroom_list[1]['UserName'])
    
    #print(current_chatroom)
    #print(type(current_chatroom))
        
    itchat.run(True)
except Exception as ex:
  print(ex)
finally:
  itchat.logout()