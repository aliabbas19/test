#!/bin/bash
# Install Health Monitor as Cron Job
# Run this once on the server to enable automatic monitoring

set -e

echo "============================================"
echo "Installing Health Monitor for Ali Abbas"
echo "============================================"

# Copy the monitor script
echo "1. Copying health monitor script..."
sudo cp health-monitor.sh /usr/local/bin/health-monitor.sh
sudo chmod +x /usr/local/bin/health-monitor.sh

# Create log file
echo "2. Creating log file..."
sudo touch /var/log/health-monitor.log
sudo chmod 666 /var/log/health-monitor.log

# Add cron job (runs every 5 minutes)
echo "3. Setting up cron job..."
(crontab -l 2>/dev/null | grep -v "health-monitor" ; echo "*/5 * * * * /usr/local/bin/health-monitor.sh") | crontab -

# Test the script
echo "4. Testing health monitor..."
/usr/local/bin/health-monitor.sh

echo ""
echo "============================================"
echo "✅ Health Monitor Installed Successfully!"
echo "============================================"
echo ""
echo "📱 Telegram alerts will be sent to: @ali_Abbas_20"
echo "⏰ Running every 5 minutes automatically"
echo ""
echo "Commands:"
echo "  - View logs: tail -f /var/log/health-monitor.log"
echo "  - Run manually: /usr/local/bin/health-monitor.sh"
echo "  - View cron jobs: crontab -l"
echo ""
