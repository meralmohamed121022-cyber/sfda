# SFDA Barcode & RSD Live Scanner (Vercel Ready)

مشروع ماسح الباركود ونظام رصد متوافق 100% مع النشر على Vercel.

## هيكل الملفات:
```
vercel_app/
├── api/
│   └── index.py        # السيرفر الخلفي ودوال الـ API
├── templates/
│   └── index.html      # واجهة المستخدم الأمامية وماسح الكاميرا
├── requirements.txt    # متطلبات بايثون لـ Vercel
└── vercel.json         # إعدادات النشر على منصة Vercel
```

## خطوات الرفع على Vercel:

### الطريقة الأولى (عبر GitHub - الأسهل):
1. ارفع مجلد `vercel_app` إلى مستودع جديد على حسابك في GitHub.
2. ادخل إلى لوحة تحكم [Vercel](https://vercel.com).
3. اضغط **Add New Project** واختر المستودع من GitHub.
4. اضغط **Deploy**، وسيكون موقعك حياً على رابط Vercel مجاني!

### الطريقة الثانية (عبر موجه الأوامر CMD):
افتح مجلد المشروع في CMD ونفّذ الأمر التالي:
```bash
npx vercel
```
ثم اتبع التعليمات على الشاشة لتسجيل الدخول والرفع فوراً.
