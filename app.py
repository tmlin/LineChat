##Flask初始化
from flask import Flask, send_from_directory, request, abort
from datetime import datetime
import os,random
import paho.mqtt.client as mqtt
app = Flask(__name__)

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))
def publish(topic,message):
  client.publish(topic,message)   
client_id=f"tmlin-{random.randint(0,10000)}"
client = mqtt.Client(client_id)
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.mqttdashboard.com", 1883, 60)
topic="20230313/ESP32/AIOT"

    
def listener(event):
  print("事件型別: "+event.event_type)  #'put' or 'patch'
  print("事件路徑: "+event.path) 
  print("資料內容: ",end="")
  print(event.data)  
  print("資料型別: ",end="")
  print(type(event.data))
  #if event.path=="/36": 
  #   line_bot_api.push_message("Ud903f9000fafd94f9ac23387217f78de",TextSendMessage(text="感測器:"+str(event.data)))

#Line初始化  
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    FollowEvent,MessageEvent,TextMessage,TextSendMessage, 
    ImageSendMessage, FlexSendMessage,
    StickerMessage,StickerSendMessage,
    ConfirmTemplate,TemplateSendMessage,
    MessageAction,URIAction,LocationMessage,ButtonsTemplate,
    FlexSendMessage, BubbleContainer, ImageComponent) 
import re,json  
#你的LINE存取代碼 access code  
line_bot_api = LineBotApi('dzzEP8ta0f+nD85xgfNg3+B36LZAB6LUkUeL9IZHZj041oyL28U+4rF2iX4C5V36y/dD4ZFDjv2aDD0nfMknuXokS/12WKUwD1/O1xTeOzBLh8vfRA9qMP/D3OJ5wK5TTLPz8hTJ55tGGNskaXHrZAdB04t89/1O/w1cDnyilFU=')
  #line_bot_api.set_webhook_endpoint(<webhook_endpoint_URL>)
  #line_bot_api.get_webhook_endpoint()
#你的LINE頻道密鑰 secret
handler = WebhookHandler('fbcb058bf1da7b75c8cb89812138af2d')
render_url="https://line-48vn.onrender.com//callback"  
#flex_contents=json.loads(open("flex/hotel.json").read())
flex_send_message = FlexSendMessage(
    alt_text='hello',
    contents=BubbleContainer(
        direction='ltr',
        hero=ImageComponent(
            url=render_url + "/static/images/girl.jpg",
            aspect_ratio='20:13',
            aspect_mode='cover',
            action=URIAction(uri='http://example.com', label='label')
        )
    )
)
def showProfile(id):
  profile = line_bot_api.get_profile(id)
  print('訊息發送者:', id)
  print('姓名:', profile.display_name)  
  print('大頭照網址:',profile.picture_url)
  print('狀態消息:',profile.status_message)
  return(profile.display_name,profile.picture_url,profile.status_message)

def reply_text(token,id,txt): 
  if txt in "whoami" or txt in "我是誰":
    (name,photo,status)=showProfile(id)
    value="你是:"+name+"&心聲:"+status
    line_bot_api.reply_message(token, TextSendMessage(text=value))
    #line_bot_api.reply_message(token, [TextSendMessage(text=value),ImageSendMessage(original_content_url =photo_url ,preview_image_url =photo_url)])
  elif txt in "mygirl 女朋友":  
    line_bot_api.reply_message(token, ImageSendMessage(original_content_url = render_url + "/static/images/girl.jpg", preview_image_url = render_url + "/static/images/girl.jpg"))
  elif "led" in txt:
    args=txt.split("/")
    if len(args)==7:
      publish(topic,txt)
      value="開燈" if args[6]=="1" else "關燈"
    else:
      value="格式錯誤?"       
    line_bot_api.reply_message(token, TextSendMessage(text=value))
  elif txt in "light" or txt in "點燈":
    ask = ButtonsTemplate(
    text="點亮LED燈選單", 
    actions=[MessageAction(label="開燈", text="1/tmlin/st00/led/14/value/1"),
             MessageAction(label="關燈", text="1/tmlin/st00/led/14/value/0"),
             MessageAction(label="取消", text="Cancel")])
    temp_msg = TemplateSendMessage(alt_text='點燈訊息',template=ask)
    line_bot_api.reply_message(token, temp_msg) 
  elif txt=="vr36":
    publish(topic,"1/tmlin/st00/vr/36/detect/1")
    line_bot_api.reply_message(token, TextSendMessage(text="啟動感測器"))
  elif txt=="xvr36":
    publish(topic,"1/tmlin/st00/vr/36/detect/0")     
    line_bot_api.reply_message(token, TextSendMessage(text="關閉感測器"))
  elif txt=="hotel":
    #line_bot_api.push_message(id,FlexSendMessage(alt_text='hello',contents=flex_contents))  
    line_bot_api.push_message(id,flex_send_message)
  else:
    #value=getFirebase("Chat",txt)
    value="查無資料"
    line_bot_api.reply_message(token, TextSendMessage(text=value))

#Flask路由處理
@app.route("/index.html")
@app.route("/")
def index():
    return "歡迎到聊天機器人123"
    
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')    

@app.route("/led")    
def led():
  id=request.args.get("id")
  sw=request.args.get("sw")
  if id and sw:
    message=f"1/tmlin/st00/led/{id}/value/{sw}" 
    publish(topic,message)
    return "開燈" if sw=="1" else "關燈"
  return "格式錯誤?"

#Line訊息事件處理
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.default()
def default(event):
    print('捕捉到事件：', event)
    
#處理「被加入好友」訊息
@handler.add(FollowEvent)
def followed(event):
    id = event.source.user_id
    print("歡迎新好友")
    showProfile(id)[0]    
    
#處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  id = event.source.user_id
  txt=event.message.text
  reply_text(event.reply_token, id, txt)  
  
#處理貼圖訊息
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(event.reply_token, StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id))  
            
#處理地點訊息
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    addr=event.message.address         # 地址
    lat=str(event.message.latitude)    # 緯度
    lon=str(event.message.longitude)   # 經度
    if addr is None:
      msg='收到GPS座標：({lat}, {lon})\n謝謝您！'
    else:
      msg='收到GPS座標：({lat}, {lon})。\n地址：{addr}\n謝謝您！'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)