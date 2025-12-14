#!/bin/bash
# Server Health Monitor Script for Ali Abbas
# Runs every 5 minutes via cron to check system health
# Sends Telegram alerts to @ali_Abbas_20

# Telegram Configuration (Ali Abbas Only)
TELEGRAM_BOT_TOKEN="8460366732:AAFtL30ft9ug4l_4Dj3XArK1KYWlQQtQm6o"
TELEGRAM_CHAT_ID="6912603556"

# Server Configuration
DOMAIN="basamaljanaby.com"
APP_DIR="/home/ubuntu/app"

# Thresholds
DISK_THRESHOLD=85   # Alert if disk usage > 85%
MEMORY_THRESHOLD=90 # Alert if memory usage > 90%

# Log file
LOG_FILE="/var/log/health-monitor.log"

# Function to send Telegram message
send_telegram() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="${TELEGRAM_CHAT_ID}" \
        -d text="${message}" \
        -d parse_mode="Markdown" > /dev/null 2>&1
}

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if Docker containers are healthy
check_containers() {
    cd "$APP_DIR"
    
    # Count stopped or unhealthy containers
    stopped=$(sudo docker compose -f docker-compose.prod.yml ps -a 2>/dev/null | grep -E "Exit|unhealthy" | wc -l)
    
    if [ "$stopped" -gt 0 ]; then
        log_message "ERROR: Found $stopped stopped/unhealthy containers"
        send_telegram "🚨 *تنبيه السيرفر - Basam Al Janaby*

❌ *حاوية Docker متوقفة*
عدد الحاويات: $stopped

🔧 الحل: 
\`sudo docker compose -f docker-compose.prod.yml up -d\`"
        return 1
    fi
    
    log_message "OK: All containers healthy"
    return 0
}

# Check disk space
check_disk() {
    disk_usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
    
    if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
        log_message "ERROR: Disk usage at ${disk_usage}%"
        send_telegram "🚨 *تنبيه السيرفر - Basam Al Janaby*

💾 *مساحة القرص منخفضة*
الاستخدام: ${disk_usage}%

🔧 الحل:
\`sudo docker system prune -af\`"
        return 1
    fi
    
    log_message "OK: Disk usage at ${disk_usage}%"
    return 0
}

# Check memory usage
check_memory() {
    memory_usage=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
    swap_usage=$(free | awk '/Swap:/ {if($2>0) printf "%.0f", $3/$2 * 100; else print 0}')
    
    if [ "$memory_usage" -gt "$MEMORY_THRESHOLD" ]; then
        log_message "ERROR: Memory usage at ${memory_usage}%"
        send_telegram "🚨 *تنبيه السيرفر - Basam Al Janaby*

🧠 *استخدام الذاكرة مرتفع*
RAM: ${memory_usage}%
Swap: ${swap_usage}%

🔧 الحل: أعد تشغيل الخدمات أو رقّي السيرفر"
        return 1
    fi
    
    log_message "OK: Memory at ${memory_usage}%, Swap at ${swap_usage}%"
    return 0
}

# Check website availability
check_website() {
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://${DOMAIN}")
    
    if [ "$response" != "200" ] && [ "$response" != "301" ] && [ "$response" != "302" ]; then
        log_message "ERROR: Website returned HTTP $response"
        send_telegram "🚨 *تنبيه السيرفر - Basam Al Janaby*

🌐 *الموقع لا يستجيب*
كود HTTP: $response
الموقع: https://${DOMAIN}

🔧 الحل:
\`sudo docker compose -f docker-compose.prod.yml restart nginx frontend\`"
        return 1
    fi
    
    log_message "OK: Website responding with HTTP $response"
    return 0
}

# Check backend API
check_backend() {
    cd "$APP_DIR"
    
    # Check if backend container is running and healthy
    backend_health=$(sudo docker compose -f docker-compose.prod.yml ps backend 2>/dev/null | grep -i "healthy" | wc -l)
    
    if [ "$backend_health" -eq 0 ]; then
        log_message "ERROR: Backend is not healthy"
        send_telegram "🚨 *تنبيه السيرفر - Basam Al Janaby*

⚙️ *Backend غير صحي*

🔧 الحل:
\`sudo docker compose -f docker-compose.prod.yml restart backend\`"
        return 1
    fi
    
    log_message "OK: Backend is healthy"
    return 0
}

# Check SSL certificate expiry
check_ssl() {
    expiry_date=$(echo | openssl s_client -servername "$DOMAIN" -connect "${DOMAIN}:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    
    if [ -n "$expiry_date" ]; then
        expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null)
        current_epoch=$(date +%s)
        days_left=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        if [ "$days_left" -lt 7 ]; then
            log_message "WARNING: SSL expires in $days_left days"
            send_telegram "🚨 *تنبيه السيرفر - Basam Al Janaby*

🔐 *شهادة SSL تنتهي قريباً*
أيام متبقية: $days_left

سيتم التجديد تلقائياً عبر Certbot"
            return 1
        fi
        log_message "OK: SSL valid for $days_left more days"
    fi
    return 0
}

# Main execution
main() {
    log_message "=== Starting health check ==="
    
    errors=0
    
    check_containers || ((errors++))
    check_disk || ((errors++))
    check_memory || ((errors++))
    check_website || ((errors++))
    check_backend || ((errors++))
    check_ssl || ((errors++))
    
    if [ "$errors" -eq 0 ]; then
        log_message "=== All checks passed ✓ ==="
    else
        log_message "=== $errors issues found ==="
    fi
}

# Run main function
main
