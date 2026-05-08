#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  تطبيق أذان متكامل يحتوي على أوقات الصلاة حسب الموقع الجغرافي (GPS/يدوي) باستخدام طريقة حساب أم القرى.
  يمكن تشغيل الأذان من نغمة محلية أو من بث إذاعة القرآن الكريم المباشر.
  يوفر معايرة الوقت (+/- دقائق) ووضع صامت لكل صلاة.
  الأذان لا يتوقف إلا بالضغط اليدوي على زر الإيقاف.
  التطبيق مخصص للأندرويد بواجهة عربية كاملة.

backend:
  - task: "Prayer Settings API"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم إنشاء API endpoints لحفظ وجلب إعدادات الصلاة للمستخدم (الموقع، التعديلات، الوضع الصامت، مصدر الصوت)"
      - working: true
        agent: "testing"
        comment: "✅ جميع API endpoints تعمل بشكل صحيح - تم اختبار: GET /api/ (رسالة ترحيبية)، POST /api/prayer-settings (حفظ الإعدادات)، GET /api/prayer-settings/{user_id} (جلب الإعدادات)، تحديث الإعدادات، ومعالجة الأخطاء للمستخدمين غير الموجودين. قاعدة البيانات MongoDB تحفظ وتسترجع البيانات بشكل صحيح مع جميع الحقول المطلوبة (الموقع، التعديلات، الوضع الصامت، مصدر الصوت). تم اختبار 6/6 حالات بنجاح."

frontend:
  - task: "Prayer Times Calculation"
    implemented: true
    working: "NA"
    file: "/app/frontend/utils/prayerCalculations.ts"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم تنفيذ حساب أوقات الصلاة باستخدام مكتبة adhan وطريقة أم القرى، مع دوال مساعدة لتنسيق الوقت وتطبيق التعديلات"
  
  - task: "Prayer Context & Settings Management"
    implemented: true
    working: "NA"
    file: "/app/frontend/contexts/PrayerContext.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم إنشاء Context لإدارة إعدادات الصلاة، الموقع، التعديلات، والوضع الصامت مع حفظ في AsyncStorage"
  
  - task: "Audio Playback (Radio & Local)"
    implemented: true
    working: "NA"
    file: "/app/frontend/contexts/AudioContext.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم تنفيذ تشغيل الأذان من إذاعة القرآن الكريم (http://live.mp3quran.net:8002/stream) أو نغمة محلية أو ملف مخصص"
  
  - task: "Home Screen"
    implemented: true
    working: "NA"
    file: "/app/frontend/app/(tabs)/home.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "الشاشة الرئيسية تعرض الوقت الحالي، الموقع، الصلاة القادمة، وجميع أوقات الصلاة لليوم"
  
  - task: "Prayers List Screen"
    implemented: true
    working: "NA"
    file: "/app/frontend/app/(tabs)/prayers.tsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "شاشة عرض تفصيلي لجميع أوقات الصلاة مع التعديلات والوضع الصامت"
  
  - task: "Settings Screen"
    implemented: true
    working: "NA"
    file: "/app/frontend/app/(tabs)/settings.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "شاشة الإعدادات تحتوي على: GPS/موقع يدوي، معايرة الوقت، وضع صامت، اختيار مصدر الصوت، زر اختبار الأذان"
  
  - task: "Adhan Playing Screen"
    implemented: true
    working: "NA"
    file: "/app/frontend/app/adhan-playing.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "شاشة تشغيل الأذان مع زر إيقاف يدوي كبير، منع الرجوع بزر الجهاز حتى يتم إيقاف الأذان يدوياً"
  
  - task: "App Permissions & Configuration"
    implemented: true
    working: "NA"
    file: "/app/frontend/app.json"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم إضافة أذونات Android و iOS للموقع، الإشعارات، والصوت في الخلفية"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Prayer Settings API"
    - "Prayer Times Calculation"
    - "Audio Playback (Radio & Local)"
    - "Settings Screen"
    - "Adhan Playing Screen"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      تم إنشاء تطبيق الأذان المتكامل بجميع الميزات المطلوبة:
      
      ✅ حساب أوقات الصلاة باستخدام طريقة أم القرى
      ✅ تحديد الموقع عبر GPS أو يدوي
      ✅ تشغيل الأذان من إذاعة القرآن الكريم أو نغمة محلية
      ✅ معايرة الوقت (+/- دقائق) لكل صلاة
      ✅ وضع صامت لكل صلاة
      ✅ اختيار ملف صوت مخصص من الجهاز
      ✅ شاشة تشغيل الأذان مع إيقاف يدوي فقط
      ✅ واجهة عربية كاملة
      ✅ أذونات Android المطلوبة
      
      الرجاء اختبار:
      1. Backend API endpoints (/api/prayer-settings)
      2. واجهة التطبيق والتنقل بين الشاشات
      3. حساب أوقات الصلاة (يجب أن تظهر الأوقات بناءً على الموقع)
      4. تشغيل الأذان التجريبي (زر اختبار الأذان)
      5. تغيير الإعدادات والتأكد من حفظها
  - agent: "testing"
    message: |
      ✅ اكتمل اختبار Backend API بنجاح تام!
      
      تم اختبار جميع Prayer Settings API endpoints المطلوبة:
      • GET /api/ - رسالة ترحيبية ✅
      • POST /api/prayer-settings - حفظ إعدادات الصلاة ✅
      • GET /api/prayer-settings/{user_id} - جلب إعدادات المستخدم ✅
      • تحديث الإعدادات الموجودة ✅
      • معالجة الأخطاء للمستخدمين غير الموجودين ✅
      
      قاعدة البيانات MongoDB تعمل بشكل مثالي مع حفظ واسترجاع جميع البيانات:
      - الموقع الجغرافي (latitude, longitude, city)
      - تعديلات أوقات الصلاة (+/- دقائق)
      - إعدادات الوضع الصامت لكل صلاة
      - مصدر الصوت (radio/local/custom)
      
      النتيجة: 6/6 اختبارات نجحت - Backend جاهز للاستخدام!