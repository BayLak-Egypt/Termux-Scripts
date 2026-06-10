

# 🛡️ Advanced Multi-Tracker & Snapper

# Cam-Shot اداه اصدار v1.1

"أداة احترافية متقدمة مبنية باستخدام لغتي Python و PHP لتتبع الزوار، وجلب بيانات موقعهم الجغرافي، والتقاط صور تلقائية من الكاميرا (بعد الحصول على إذن) باستخدام تقنية سرفرات المتعدده."


## 🌟 الاضافات القديمه اصدار v1.0
* 
**استخرج الايبي الحقيقي من شخص**
 
* 
**استخرج معلومات زي دوله ومكان ومزورد الخدمه**
 
* 
**سهل الاستخدم ومرن في تعديل اجزائه** 


## 🌟 الاضافات اصدار v1.1
* 
**اضافه مودل لسرفرات لسهوله تحديث واي  شخص  يمكنه صنع سكربت  سرفر  خاص بيه**
* 
**اصلاح تحسين السرعه وترتيب صحيح لتشغل دومين**

## 🛠️ المتطلبات

* Python 3.x
* PHP
## واحد منهم اختياري
* Cloudflared
* Bore
* Localtunnel
## وبقي SSH بيشتغل تلقيء   Serveo ,Pinggy
## 📥 لازم تثبت واحده من دول او تختر سرفرات ال ssh عشان يشتغل تمام


## ازاي تثبت Cloudflared

#Termux:
```pkg install cloudflared```
#Linux: 
```wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb```
```sudo dpkg -i cloudflared-linux-amd64.deb```


## ازاي تثبت Bore
#Termux:
```pkg install rust```
```cargo install bore-cli```

#Linux: 
```curl -LSfs [https://raw.githubusercontent.com/borerust/bore/main/install.sh](https://raw.githubusercontent.com/borerust/bore/main/install.sh) | sh```
```pkg install rust```
```cargo install bore-cli```


## ازاي تثبت Localtunnel

#Termux:
```pkg install nodejs```
```npm install -g localtunnel```

#Linux: 
```sudo apt install nodejs npm```
```npm install -g localtunnel```



## ازاي تثبت الاداه وتشغلها
1. اول حاجه  بتحمل مستودع كامل بتع الادوات
```git clone https://github.com/BayLak-Egypt/Termux-Scripts.git```
2. تاني حاجه تخش علي فلدر دا بطريقه دي

```cd Termux-Scripts/Cam-ShotV1.1```
3. بتشغله بطريقه دي واي مشكله تظهرلك اتبع تعليمات تثبيت ادوات سرفر لو مشكله غير مسبوقه من كود نفسها يعني  يريت تبعتلي سكرين شوت علي تيلجرام Baylaks وانشاء الله هرد في اسرع وقت بلحل
```python3 main.py```

4- اهم  حاجه لو انت تريمكس فا لازم تفعل صلاحيات التخزين بتع تريمكس مهم جدا عشان ميحصلش مشاكل اهو الامر يحب ❤️

```bash
   termux-setup-storage```

