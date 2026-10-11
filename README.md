# SFDA Barcode & RSD Live Scanner (Vercel Ready)

مشروع ماسح الباركود ونظام رصد وسولار متوافق 100% مع النشر على Vercel لجلب أسعار وبيانات الأدوية الرسمية من هيئة الغذاء والدواء السعودية (SFDA).

## هيكل الملفات:
```
vercel_app/
├── api/
│   └── index.py        # السيرفر الخلفي ودوال الـ API مع دعم البروكسي
├── templates/
│   └── index.html      # واجهة المستخدم الأمامية وماسح الكاميرا
├── requirements.txt    # متطلبات بايثون لـ Vercel
├── vercel.json         # إعدادات النشر على منصة Vercel
└── README.md
```

## ملاحظة هامة جداً بشأن الحظر الجغرافي (Geo-blocking):
سيرفرات هيئة الغذاء والدواء السعودية (البورت `9002`) تحجب الاتصالات القادمة من خارج المملكة. ونظراً لأن خوادم Vercel تقع في الولايات المتحدة وأوروبا، يتطلب الاتصال تفعيل **بروكسي سعودي (Saudi Proxy)**.

### كيفية ضبط البروكسي السعودي على Vercel:
1. ادخل إلى مشروعك على [Vercel Dashboard](https://vercel.com/dashboard).
2. اذهب إلى **Settings** > **Environment Variables**.
3. أضف المتغير التالي:
   - **Key:** `SAUDI_PROXY`
   - **Value:** عنوان البروكسي السعودي الخاص بك، مثلاً:
     - `http://username:password@saudi-proxy-host:port`
     - أو `socks5://username:password@saudi-proxy-host:port`
4. أعد نشر المشروع (**Redeploy**).

### فحص حالة الاتصال والبروكسي:
يمكنك زيارة الرابط التالي بعد النشر للتأكد من حالة الربط:
`https://your-app.vercel.app/api/health`

---

## خطوات الرفع على Vercel:
1. افتح حسابك على [Vercel](https://vercel.com).
2. اضغط **Add New Project** واختر المستودع `meralmohamed121022-cyber/sfda`.
3. في قسم **Environment Variables** أضف `SAUDI_PROXY` بالبيانات الخاصة بك.
4. اضغط **Deploy**.
